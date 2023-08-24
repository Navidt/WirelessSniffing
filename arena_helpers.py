from arena import *
from time import time
import math
from typing import Tuple
from scipy.spatial.transform import Rotation as R
from grid import *
import asyncio
def colorFlip(color):
    return (255 - color[0], 255 - color[1], 255 - color[2])

def difference(v1, v2):
  return (v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)

def makeBaseDoubleTapButton(obj, singleAction, doubleAction, scene: Scene):
  buttonSleepDelay = 0.3
  doubleTapThreshold = 800
  async def checkTaps(evt):
    await scene.sleep(doubleTapThreshold)
    if callback.taps == 1:
      singleAction()
    elif callback.taps == 2:
      doubleAction()
    callback.taps = 0
  def callback(s, evt, msg):
    if evt.type != "mousedown":
      return
    t = time()
    if (t - callback.lastTimePressed) < buttonSleepDelay:
      return
    callback.lastTimePressed = t
    callback.taps += 1
    asyncio.create_task(checkTaps(evt))
  callback.lastTimePressed = time()
  callback.taps = 0
  scene.add_object(obj)
  scene.update_object(obj, click_listener=True, evt_handler=callback)
  return obj

def makeBaseButton(obj, action, scene):
  buttonSleepDelay = 0.3
  def callback(s, evt, msg):
    if evt.type == "mousedown":
      t = time()
      if (t - makeBaseButton.lastTimePressed) < buttonSleepDelay:
        return
      makeBaseButton.lastTimePressed = t
      action(s, evt, msg)
  makeBaseButton.lastTimePressed = time()
  scene.add_object(obj)
  scene.update_object(obj, click_listener=True, evt_handler=callback)
  print(obj)
  return obj

def makeButton(position, buttonColor, text, action, scene):
  button = Box(
    object_id=f"Button{text}",
    position=position,
    width=0.15,
    height=0.05,
    depth=0.05,
    color = Color(*buttonColor),
  )
  print("New button made")
  makeBaseButton(button, action, scene)
  textColor = Color(*colorFlip(buttonColor))
  text = Text(object_id=f"Text{text}", position=(0, 0, 0.03), scale=(0.1, 0.1, 0.1), value=text, color=textColor, parent=button.object_id)
  scene.add_object(text)
  return button

def normalize(vector):
  magnitude = (vector[0]**2 + vector[1]**2 + vector[2]**2)**0.5
  return (vector[0] / magnitude, vector[1] / magnitude, vector[2] / magnitude)

def alignTextWithVector(vector):
  if vector[0] < 0:
    vector = (-vector[0], -vector[1], -vector[2])
  vector= normalize(vector)
  zRotation = math.asin(vector[1])
  yRotation = math.atan2(-vector[2], vector[0])
  return R.from_euler('zy', [zRotation, yRotation]).as_quat()

def rotationFromVector(vector):
  #returns a quaternion rotation that takes the vector (0, 1, 0) to the given vector
  a = (vector[2], 0, -vector[0])
  w = (vector[0]**2 + vector[1]**2 + vector[2]**2)**0.5 + vector[1]
  magnitude = (a[0]**2 + a[1]**2 + a[2]**2 + w**2)**0.5
  return (a[0] / magnitude, a[1] / magnitude, a[2] / magnitude, w / magnitude)

def makeSpaceArrow(tailPosition, directionVector, color, scene, persist=False):
  arrowHeight = 0.1
  arrowTipHeight = 0.02
  normalizedDirectionVector = normalize(directionVector)
  tipRotation = rotationFromVector(normalizedDirectionVector)
  tipPosition = add(tailPosition, scale(arrowHeight + arrowTipHeight, normalizedDirectionVector))
  #shaft position wrt tip position
  shaftPosition = (0, (arrowHeight + arrowTipHeight) * -0.5, 0)
  arrowTip = Cone(
    position = tipPosition,
    material = Material(color=color),
    rotation = tipRotation,
    height = arrowTipHeight,
    radiusTop = 0,
    radiusBottom = arrowTipHeight,
  )
  arrowShaft = Cylinder(
    position = shaftPosition,
    material = Material(color=color),
    radius=0.01,
    height=arrowHeight,
    parent=arrowTip.object_id
  )
  scene.add_object(arrowTip)
  scene.add_object(arrowShaft)
  return arrowTip

def makePacketArrow(position, directionVector, color, ttl: float, text: str, scene: Scene, persist=False):
  textRotation = alignTextWithVector(directionVector)
  rotation = rotationFromVector(directionVector)
  secretParent = Entity(
    position = position,
    persist=persist,
    ttl=ttl,
    scale=(0.5, 0.5, 0.5)
  )
  frontCone = Cone(
      position = (0, 0, 0),
      height = 0.05,
      radiusTop = 0,
      radiusBottom = 0.05,
      material=Material(color=color, opacity=1, transparent=True),
      rotation = rotation,
      ttl = ttl,
      persist = persist,
      parent = secretParent.object_id
  )
  middleCone = Cone(
      position = (0,-0.075,0),
      material=Material(color=color, opacity=2/3, transparent=True),
      height = 0.05,
      radiusTop = 0,
      radiusBottom = 0.05,
      ttl = ttl,
      parent = frontCone.object_id,
      persist = persist
  )
  backCone = Cone(
      position = (0,-0.15,0),
      material=Material(color=color, opacity=1/3, transparent=True),
      height = 0.05,
      radiusTop = 0,
      radiusBottom = 0.05,
      ttl = ttl,
      parent = frontCone.object_id,
      persist = persist
  )
  text = Text(
      text = text,
      position = (-0.05,0.1,0),
      scale = (0.15, 0.15, 0.15),
      rotation = (textRotation[0], textRotation[1], textRotation[2], textRotation[3]),
      material=Material(color=(255, 255, 255), opacity=1, transparent=True),
      parent = secretParent.object_id,
      ttl = ttl,
      persist = persist
  )
  scene.add_object(secretParent)
  scene.add_object(frontCone)
  scene.add_object(middleCone)
  scene.add_object(backCone)
  scene.add_object(text)
  return secretParent

def repeat_task(func, interval_ms, scene) -> asyncio.Task:
  """Add a task to the event loop that repeats every `interval_ms` milliseconds. Pass a synchronous function to `func`."""
  async def run():
    while True:
      start = time()
      func()
      end = time()
      target_time = max(0, interval_ms - (end - start))
      await scene.sleep(target_time)
  return asyncio.create_task(run())

def visualizePacket(originMac: str, destMac: str, macMarkers: dict[str: Grid], scene: Scene):
  return
  #nextTimes is a dictionary from the mac address tuple to the next time a packet can be visualized
  #numberOfPackets is a dictionary from the mac address tuple to the number of packets that will be visualized
  if not originMac in macMarkers.keys() or not destMac in macMarkers.keys():
    return
  tupleKey = (originMac, destMac)
  if not tupleKey in visualizePacket.numberOfPackets.keys():
    visualizePacket.numberOfPackets[tupleKey] = 1
  if tupleKey in visualizePacket.nextTimes.keys() and time() < visualizePacket.nextTimes[tupleKey]:
    visualizePacket.numberOfPackets[tupleKey] += 1
    return
  startLocation = macMarkers[originMac].data.position
  endLocation = macMarkers[destMac].data.position
  if startLocation.distance_to(endLocation) < 0.1:
    visualizePacket.numberOfPackets[tupleKey] += 1
    return
  animationDuration = max(startLocation.distance_to(endLocation) * 2000, 2000)
  visualizePacket.nextTimes[tupleKey] = time() + 0.5
  print("Packets:", visualizePacket.numberOfPackets[tupleKey])
  numPackets = visualizePacket.numberOfPackets[tupleKey]
  packetObject = makePacketArrow(startLocation, difference(endLocation, startLocation), (255, 0, 0), animationDuration / 2000, f"{numPackets} pkts", scene)
  packetObject.dispatch_animation(
    Animation(
      property="position",
      start=startLocation,
      end=endLocation,
      easing="linear",
      duration=animationDuration
    )
  )
  scene.run_animations(packetObject)
  visualizePacket.numberOfPackets[tupleKey] = 0
visualizePacket.nextTimes: dict[Tuple[str, str], float] = {}
visualizePacket.numberOfPackets: dict[Tuple[str, str], int] = {}
