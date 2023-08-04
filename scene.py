from arena import *
import numpy as np
from typing import Tuple
from scapy.all import AsyncSniffer, Dot11, ls, Raw, IP, TCP, getmacbyip
import subprocess, shlex
from arena_helpers import *
import time

def end_program_callback(scene: Scene):
    # print("cancelling")
    ids = list(Globals.scene.all_objects.values())
    for obj in ids:
      print(obj)
      Globals.scene.delete_object(obj)
# type Reading = Tuple[Tuple(float, float, float), Tuple(float, float, float, float), float]
spaceDimentions = (0.1, 0.1, 0.1)

mainUsername = "Navid"
# dev_mac = "5c:e9:1e:88:71:b1"  # RPi security camera MAC address
  # dev_mac = "ec:2c:e2:a7:3a:af"
  # dev_mac = "7e:7d:e4:76:27:fc"
# dev_mac = "b4:b0:24:17:d1:7e"
# dev_mac = "44:12:44:69:f4:62"
iphone = "b8:7b:c5:00:6e:89"
# dev_mac = "e4:5f:01:d3:40:c6"
validMacs = ["44:a5:6e:a1:32:fa", "e4:5f:01:d3:40:c6", "5c:e9:1e:88:71:b1"]
# validMacs = ["5c:e9:1e:88:71:b1"]
# dev_mac = "44:a5:6e:a1:32:fa"
channel_n = 48  # Channel to listen on
iface_n = "wlan1"  # Interface for network adapter
class Globals():
  #dictionary of mac address text marking the device in the scene
  macMarkers: dict[str: Object] = {}
  #dictionary of positions to the selected device's signal grid
  spaceMarkers: dict[Vector: Object] = {}
  #dictionary of all rssi readings, mapping the mac address of the grid of the readings 
  grids: dict[str: Grid] = {}
  selectedMac = None
  scene = Scene(host='arenaxr.org', scene='packet_sniffer2', end_program_callback=end_program_callback)
# Globals.selectedMac = dev_mac
#Size of sphere should be proportional to number of packets


packetsProcessed = 0
def processPacket(pkt):
  global packetsProcessed
  if not pkt.haslayer(Dot11):
    return
  if pkt.addr2 == None:
    return
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
    print("P")
    packetsProcessed = 0
  reading = ((user.data.position.x, user.data.position.y - 0.1, user.data.position.z), (user.data.rotation.x, user.data.rotation.y, user.data.rotation.z, user.data.rotation.w), pkt.dBm_AntSignal)
  if not pkt.addr2 in Globals.grids:
    # if reading[2] < -40:
      # return
    Globals.grids[pkt.addr2] = Grid(*spaceDimentions)
  Globals.grids[pkt.addr2].addReading(reading)
  visualizePacket(pkt.addr2, pkt.addr1, Globals.macMarkers, Globals.scene)

# @Globals.scene.run_forever(interval_ms=5000)
def reloadEstimates():
  for mac in Globals.grids.keys():
    print("Mac:", mac)
    reloadEstimate(mac)

def getColor(min, max, signal):
  ratio = 0
  if min == max:
    ratio = 0.5
  else:
    ratio = (signal - min) / (max - min)
  return Color(int(255*(1 - ratio)), int(255*ratio), 0)

def clearGrid(mac: str):
  for obj in Globals.spaceMarkers.values():
    # print(obj)
    # Globals.scene.delete_object(obj)
    Globals.scene._publish(obj, "delete")
  Globals.spaceMarkers.clear()
  Globals.macMarkers[mac].data.color = Color(0, 0, 0)
  Globals.scene.update_object(Globals.macMarkers[mac])
  return

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
        width=spaceDimentions[0]/ 10,
        height=spaceDimentions[1] / 10,
        depth=spaceDimentions[2] / 10,
        material=Material(color=color),
        # persist=True#, opacity=1, transparent=True),
      )
      Globals.scene.add_object(marker)
      Globals.spaceMarkers[position] = marker
    else:
      marker = Globals.spaceMarkers[position]
      marker.data.material.color = color
      Globals.scene.update_object(marker)
  return

async def changeSelectedMac(newMac: str):
  if Globals.selectedMac != None:
    clearGrid(Globals.selectedMac)
  if Globals.selectedMac != newMac:
    Globals.selectedMac = newMac
    reloadGrid()
  else:
    Globals.selectedMac = None

def getEstimate(grid: Grid):
  bestSignal = -500
  bestLocation = (0, 0)
  for space in grid.spaces.values():
    if space.average > bestSignal:
      bestSignal = space.average
      bestLocation = space.center
  print(bestLocation, bestSignal)
  return bestLocation

def reloadEstimate(mac):
  if not mac in Globals.grids.keys():
    return
  grid = Globals.grids[mac]
  bestLocation = getEstimate(grid)
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
def changeChannel(channel_num):
  """Change the channel network adapter listens on"""
  print("Changing to Channel ", str(channel_num))
  command = "sudo iwconfig wlan1 channel " + str(channel_num)
  command = shlex.split(command)
  subprocess.Popen(command, shell=False)

allChannels = [11, 108]
channelIndex = 0
# @scene.run_forever(interval_ms=10000)
def channelHop():
  channelIndex = (channelIndex + 1) % len(allChannels)
  changeChannel(allChannels[channelIndex])

@Globals.scene.run_after_interval(interval_ms=10000)
def start():
  Globals.scene.run_forever(reloadEstimates, 5000)

changeChannel(channel_n)
t = AsyncSniffer(iface=iface_n, prn=processPacket, store=0)
t.daemon = True
t.start()
Globals.scene.run_tasks()
