from arena import *
import time
import math
from scipy.spatial.transform import Rotation as R
def colorFlip(color):
    return (255 - color[0], 255 - color[1], 255 - color[2])

def difference(v1, v2):
  return (v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)

def makeButton(position, buttonColor, text, action, scene):
    buttonSleepDelay = 0.5
    def callback(s, evt, msg):
        if evt.type == "mousedown":
            t = time.time()
            if (t - callback.lastTimePressed) < buttonSleepDelay:
                return
            callback.lastTimePressed = t
            action(s, evt, msg)
    callback.lastTimePressed = time.time()
    button = Box(
        object_id=f"Button{text}",
        position=position,
        width=0.15,
        height=0.05,
        depth=0.05,
        color = Color(*buttonColor),
        evt_handler=callback,
        click_listener=True
    )
    print("New button made")
    scene.add_object(button)
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

def makePacketArrow(position, directionVector, color, ttl: float, text: str, scene: Scene, persist=False):
  textRotation = alignTextWithVector(directionVector)
  rotation = rotationFromVector(directionVector)
  secretParent = Entity(
    position = position,
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