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
class GridSpace():
  def __init__(self, center, readings=[]):
    self.center = center
    self.readings = readings
    self.total = 0
    for reading in readings:
      # print(reading)
      self.total += reading[2]
    self.average = self.total / len(readings)
  def addReading(self, reading):
    self.total += reading[2]
    self.readings.append(reading)
    self.average = self.total / len(self.readings)
class Grid():
  def __init__(self, xWidth, yWidth, zWidth, center=(0, 0, 0)) -> None:
    self.origin = (center[0] - xWidth / 2, center[1] - yWidth / 2, center[2] - zWidth / 2)
    self.spaces = {}
    self.xWidth = xWidth
    self.yWidth = yWidth
    self.zWidth = zWidth
  def addReading(self, reading):
    position = reading[0]
    xOffset = position[0] - self.origin[0]
    yOffset = position[1] - self.origin[1]
    zOffset = position[2] - self.origin[2]
    spaceCoords = (int(xOffset / self.xWidth), int(yOffset / self.yWidth), int(zOffset / self.zWidth))
    if spaceCoords in self.spaces.keys():
      self.spaces[spaceCoords].addReading(reading)
    else:
      centerX = (spaceCoords[0] + 0.5) * self.xWidth + self.origin[0]
      centerY = (spaceCoords[1] + 0.5) * self.yWidth + self.origin[1]
      centerZ = (spaceCoords[2] + 0.5) * self.zWidth + self.origin[2]
      self.spaces[spaceCoords] = GridSpace((centerX, centerY, centerZ), [reading])
  def addReadings(self, readings):
    for reading in readings:
      self.addReading(reading)

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
validMacs = ["5c:e9:1e:88:71:b1"]
# dev_mac = "44:a5:6e:a1:32:fa"
channel_n = 44  # Channel to listen on
iface_n = "wlan1"  # Interface for network adapter
class Globals():
  #dictionary of mac address text marking the device in the scene
  macMarkers: dict[str: Grid] = {}
  #dictionary of positions to the selected device's signal grid
  spaceMarkers: dict[Tuple[float, float, float]: Object] = {}
  #dictionary of all rssi readings, mapping the mac address of the grid of the readings 
  grids = {}
  selectedMac = None
  scene = Scene(host='arenaxr.org', scene='packet_sniffer2', end_program_callback=end_program_callback)
# Globals.selectedMac = dev_mac
#Size of sphere should be proportional to number of packets
def visualizePacket(originMac: str, destMac: str):
  #nextTimes is a dictionary from the mac address tuple to the next time a packet can be visualized
  #numberOfPackets is a dictionary from the mac address tuple to the number of packets that will be visualized
  if not originMac in Globals.macMarkers.keys() or not destMac in Globals.macMarkers.keys():
    return
  tupleKey = (originMac, destMac)
  if not tupleKey in visualizePacket.numberOfPackets.keys():
    visualizePacket.numberOfPackets[tupleKey] = 1
  if tupleKey in visualizePacket.nextTimes.keys() and time.time() < visualizePacket.nextTimes[tupleKey]:
    visualizePacket.numberOfPackets[tupleKey] += 1
    return
  startLocation = Globals.macMarkers[originMac].data.position
  endLocation = Globals.macMarkers[destMac].data.position
  if startLocation.distance_to(endLocation) < 0.1:
    visualizePacket.numberOfPackets[tupleKey] += 1
    return
  animationDuration = max(startLocation.distance_to(endLocation) * 2000, 2000)
  visualizePacket.nextTimes[tupleKey] = time.time() + 0.5
  print("Packets:", visualizePacket.numberOfPackets[tupleKey])
  numPackets = visualizePacket.numberOfPackets[tupleKey]
  packetObject = makePacketArrow(startLocation, difference(endLocation, startLocation), (255, 0, 0), animationDuration / 2000, f"{numPackets} pkts", Globals.scene)
  packetObject.dispatch_animation(
    Animation(
      property="position",
      start=startLocation,
      end=endLocation,
      easing="linear",
      duration=animationDuration
    )
  )
  Globals.scene.run_animations(packetObject)
  visualizePacket.numberOfPackets[tupleKey] = 0
visualizePacket.nextTimes: dict[Tuple[str, str], float] = {}
visualizePacket.numberOfPackets: dict[Tuple[str, str], int] = {}

packetsProcessed = 0
def processPacket(pkt):
  global packetsProcessed
  # ls(pkt)
  # print("hi:", pkt)
  # if TCP in pkt:
  #     tcp_sport=pkt[TCP].sport
  #     tcp_dport=pkt[TCP].dport
  #     print(tcp_sport, tcp_dport)
  # if IP in pkt:
  #   ip_src=pkt[IP].src
  #   print(ip_src)
  #   ip_dst=pkt[IP].dst
  #   if ip_src == "192.168.40.24":
  #     print("DST:", ip_dst)
  if not pkt.haslayer(Dot11):
    return
  if pkt.addr2 == None:
    return
  if pkt.addr2 not in validMacs:
    return
  # if pkt.dBm_AntSignal < -40:
  #   return
  # print(pkt.addr2)
  # if pkt.addr2 != dev_mac:
  #   if pkt.addr2 == "5c:e9:1e:88:71:b1":
  #     print("Other:", pkt.addr1)
  #   # print("BOOM: ", Raw(pkt).load)
  #   # print(pkt.payload)
  #   # print(pkt.payload.payload.payload)
  #   return
  # print(pkt.addr1)
  # ls(pkt)
  # print(pkt.addr1)
  # if pkt.addr2 != "e4:5f:01:d3:40:c6" and pkt.addr2 != "b4:b0:24:17:d1:7e":
  #   return
  # print(pkt.addr2)
  # print(pkt.addr2, pkt.dBm_AntSignal)
  user = None
  for k, v in Globals.scene.users.items():
     if v.displayName == mainUsername:
        user = v
        break
  if user == None:
     return
  # print("h1")
  # print(pkt.addr2)
  packetsProcessed += 1
  if packetsProcessed == 50:
    print("P")
    packetsProcessed = 0
  # print(pkt.addr2)
  reading = ((user.data.position.x, user.data.position.y - 0.1, user.data.position.z), (user.data.rotation.x, user.data.rotation.y, user.data.rotation.z, user.data.rotation.w), pkt.dBm_AntSignal)
  if not pkt.addr2 in Globals.grids:
    # if reading[2] < -40:
      # return
    Globals.grids[pkt.addr2] = Grid(*spaceDimentions)
  Globals.grids[pkt.addr2].addReading(reading)
  visualizePacket(pkt.addr2, pkt.addr1)

# @Globals.scene.run_forever(interval_ms=5000)
def reloadEstimates():
  for mac in Globals.grids.keys():
    print("Mac:", mac)
    reloadEstimate(mac)
  # reloadEstimate(dev_mac)

def getColor(min, max, signal):
  ratio = 0
  if min == max:
    ratio = 0.5
  else:
    ratio = (signal - min) / (max - min)
  return Color(int(255*(1 - ratio)), int(255*ratio), 0)

def clearGrid(mac):
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
  # global Globals.selectedMac, Globals.spaceMarkers
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

async def changeSelectedMac(newMac):
  if Globals.selectedMac != None:
    clearGrid(Globals.selectedMac)
  if Globals.selectedMac != newMac:
    Globals.selectedMac = newMac
    reloadGrid()
  else:
    Globals.selectedMac = None

def getEstimate(grid):
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
