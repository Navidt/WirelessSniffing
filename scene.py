from arena import *
from typing import Tuple
from scapy.all import AsyncSniffer, Dot11, ls, Raw, IP, TCP, getmacbyip
from raspberrypi_helpers import *
from arena_helpers import *
from algoritms import *
from grid import *
from indicator import Indicator
from interface import Interface
def user_left_callback(scene, camera: Camera, msg):
  print(camera.object_id, "left")
  Globals.interfaces[camera.object_id].scrub()
  del Globals.interfaces[camera.object_id]

def user_join_callback(scene: Scene, camera: Camera, msg):
  Globals.interfaces[camera.object_id] = Interface(camera, scene, Globals.grids)
  return

def end_program_callback(scene: Scene):
    # print("cancelling")
    # for address, grid in Globals.grids.items():
    #   grid.saveToFile(f"data-{address}.txt")
    ids = list(Globals.scene.all_objects.values())
    for obj in ids:
      print("OOPS")
      print(obj)
      Globals.scene.delete_object(obj)
    return

spaceDimensions = (0.5, 1, 0.5)
mainUsername = "Navid"
# dev_mac = "5c:e9:1e:88:71:b1"  # RPi security camera MAC address
# dev_mac = "e4:5f:01:d3:40:c6"
validMacs = ["44:a5:6e:a1:32:fa", "e4:5f:01:d3:40:c6", "5c:e9:1e:88:71:b1"]
validMacs = ["e4:5f:01:d3:40:c6", "7a:9d:dc:82:de:53"]
# validMacs = ["7a:9d:dc:82:de:53"]
# validMacs = ["5c:e9:1e:88:71:b1"]
# dev_mac = "44:a5:6e:a1:32:fa"
channel_n = 153  # Channel to listen on
iface_n = "wlan1"  # Interface for network adapter
class Globals():
  #dictionary of camera ids to indicators
  interfaces: dict[str: Indicator] = {}
  #dictionary of mac address text marking the device in the scene
  macMarkers: dict[str: Object] = {}
  #dictionary of positions to the selected device's signal grid
  spaceMarkers: dict[Vector: Object] = {}
  #dictionary of positions to the selected device's direction markers
  spaceArrows: dict[Vector: Object] = {}
  #dictionary of all rssi readings, mapping the mac address of the grid of the readings 
  grids: dict[str: Grid] = {}
  #dictionary of all mac addresses to the best channel to listen on
  channels: dict[str: int] = {}
  selectedMac = None
  scene = Scene(host='arenaxr.org', scene='packet_sniffer2', end_program_callback=end_program_callback, user_join_callback=user_join_callback, user_left_callback=user_left_callback)
Globals.grids[validMacs[0]] = Grid(*spaceDimensions)

packetsProcessed = 0
def processPacket(pkt):
  global packetsProcessed
  if not pkt.haslayer(Dot11):
    return
  if pkt.addr2 == None:
    return
  # print(pkt.addr2)
  if pkt.addr2 not in validMacs:
    return
  user = None
  for k, v in Globals.scene.users.items():
     if v.displayName == mainUsername:
        user = v
        break
  if user == None:
     return
  packetsProcessed += 1
  if packetsProcessed == 50:
    print("P", pkt.addr2)
    packetsProcessed = 0
  reading = ((user.data.position.x, user.data.position.y - 0.1, user.data.position.z), (user.data.rotation.x, user.data.rotation.y, user.data.rotation.z, user.data.rotation.w), pkt.dBm_AntSignal)
  if not pkt.addr2 in Globals.grids:
    # if reading[2] < -40:
      # return
    Globals.grids[pkt.addr2] = Grid(*spaceDimensions)
  Globals.grids[pkt.addr2].addReading(reading)
  # print(rotationToYRotation(reading[1]), reading[2])
  visualizePacket(pkt.addr2, pkt.addr1, Globals.macMarkers, Globals.scene)

@Globals.scene.run_forever(interval_ms=5000)
def reloadEstimates():
  print("Reloading")
  for mac in Globals.grids.keys():
    print("Mac:", mac)
    reloadEstimate(mac)

def getColor(min, max, signal):
  ratio = 0
  if min == max:
    ratio = 0.5
  else:
    ratio = (signal - min) / (max - min)
  return (int(255*(1 - ratio)), int(255*ratio), 0)

def clearGrid(mac: str):
  for obj in Globals.spaceMarkers.values():
    # print(obj)
    Globals.scene.delete_object(obj)
    # Globals.scene._publish(obj, "delete")
  Globals.spaceMarkers.clear()
  Globals.macMarkers[mac].data.color = Color(0, 0, 0)
  Globals.scene.update_object(Globals.macMarkers[mac])
  return

@Globals.scene.run_forever(interval_ms=10000)
def reloadGrid():
  global Globals
  if Globals.selectedMac == None:
    return
  Globals.macMarkers[Globals.selectedMac].data.color = Color(0, 255, 0)
  Globals.scene.update_object(Globals.macMarkers[Globals.selectedMac])
  grid = Globals.grids[Globals.selectedMac]
  bestSignal = max(grid.spaces.values(), key=lambda space: space.average).average
  worstSignal = min(grid.spaces.values(), key=lambda space: space.average).average
  for space in grid.spaces.values():
    position = space.center
    color = getColor(worstSignal, bestSignal, space.average)
    if position not in Globals.spaceMarkers.keys():
      marker = Box(
        object_id=f"{position}",
        position=position,
        width=spaceDimensions[0]/ 20,
        height=spaceDimensions[1] / 20,
        depth=spaceDimensions[2] / 20,
        material=Material(color=color),
        # persist=True#, opacity=1, transparent=True),
      )
      Globals.scene.add_object(marker)
      Globals.spaceMarkers[position] = marker
    else:
      marker = Globals.spaceMarkers[position]
      marker.data.material.color = color
      Globals.scene.update_object(marker)
    if getUnsampledRegions(space.angleBins) < 3:
      if position in Globals.spaceArrows.keys():
        Globals.scene.delete_object(Globals.spaceArrows[position])
        del Globals.spaceArrows[position]
      angle = space.angleFromBin(space.maxBin)
      Globals.spaceArrows[position] = makeSpaceArrow(position, (np.cos(angle), 0, np.sin(angle)), (0, 255, 0), Globals.scene)
  return

async def changeSelectedMac(newMac: str):
  if Globals.selectedMac != None:
    clearGrid(Globals.selectedMac)
  if Globals.selectedMac != newMac:
    Globals.selectedMac = newMac
    reloadGrid()
  else:
    Globals.selectedMac = None

def reloadEstimate(mac):
  if not mac in Globals.grids.keys():
    return
  grid = Globals.grids[mac]
  bestLocation = getEstimate(grid)
  """
  result = newGetEstimate(grid)
  if result == None:
    return
  bestLocation, lines = result
  for line in lines:
    start = line[0]
    end = add(line[0], line[1])
    print("Start:", start, "End:", end)
    Globals.scene.add_object(Line(
      start=Position(start[0], start[1], start[2]),
      end=Position(end[0], end[1], end[2]),
      color=Color(255, 0, 0),
      object_id=f"line{start[0]}"
    ))
  """
  if not mac in Globals.macMarkers.keys():
    def callback(s, evt, msg):
      print("HEYOOOOOOO", mac)
      Globals.scene.event_loop.loop.create_task(
        changeSelectedMac(mac)
      )
    Globals.macMarkers[mac] = makeButton(bestLocation, (0, 0, 0), mac, callback, Globals.scene)
  else:
    Globals.macMarkers[mac].data.position = Position(bestLocation[0], bestLocation[1], bestLocation[2])
    Globals.scene.update_object(Globals.macMarkers[mac])
  # reloadGrid()


allChannels = [11, 108]
channelIndex = 0
# @scene.run_forever(interval_ms=10000)
def channelHop():
  channelIndex = (channelIndex + 1) % len(allChannels)
  changeChannel(allChannels[channelIndex])

@Globals.scene.run_after_interval(interval_ms=3000)
def start():
  print("Starting")
  t = AsyncSniffer(iface=iface_n, prn=processPacket, store=0)
  t.daemon = True
  t.start()
  # Globals.scene.run_forever(reloadEstimates, 5000)

changeChannel(channel_n)

Globals.scene.run_tasks()
