from grid import *
from arena import *
from algoritms import *
from scipy.spatial.transform import Rotation as R
class Indicator():
  def changeSpace(self, newSpace):
    self.currentSpace = newSpace
    center = newSpace.center
    xOffset = self.grids[self.device].xWidth / 2
    yOffset = self.grids[self.device].yWidth / 2
    zOffset = self.grids[self.device].zWidth / 2
    p1 = Position(center[0] + xOffset, center[1] + yOffset, center[2] + zOffset)
    p2 = Position(center[0] + xOffset, center[1] + yOffset, center[2] - zOffset)
    p3 = Position(center[0] + xOffset, center[1] - yOffset, center[2] + zOffset)
    p4 = Position(center[0] + xOffset, center[1] - yOffset, center[2] - zOffset)
    p5 = Position(center[0] - xOffset, center[1] + yOffset, center[2] + zOffset)
    p6 = Position(center[0] - xOffset, center[1] + yOffset, center[2] - zOffset)
    p7 = Position(center[0] - xOffset, center[1] - yOffset, center[2] + zOffset)
    p8 = Position(center[0] - xOffset, center[1] - yOffset, center[2] - zOffset)
    self.spaceBoundaries[0].data.start = p1
    self.spaceBoundaries[0].data.end = p2
    self.spaceBoundaries[1].data.start = p1
    self.spaceBoundaries[1].data.end = p3
    self.spaceBoundaries[2].data.start = p1
    self.spaceBoundaries[2].data.end = p5
    self.spaceBoundaries[3].data.start = p2
    self.spaceBoundaries[3].data.end = p4
    self.spaceBoundaries[4].data.start = p2
    self.spaceBoundaries[4].data.end = p6
    self.spaceBoundaries[5].data.start = p3
    self.spaceBoundaries[5].data.end = p4
    self.spaceBoundaries[6].data.start = p3
    self.spaceBoundaries[6].data.end = p7
    self.spaceBoundaries[7].data.start = p4
    self.spaceBoundaries[7].data.end = p8
    self.spaceBoundaries[8].data.start = p5
    self.spaceBoundaries[8].data.end = p6
    self.spaceBoundaries[9].data.start = p5
    self.spaceBoundaries[9].data.end = p7
    self.spaceBoundaries[10].data.start = p6
    self.spaceBoundaries[10].data.end = p8
    self.spaceBoundaries[11].data.start = p7
    self.spaceBoundaries[11].data.end = p8
    for line in self.spaceBoundaries:
      self.scene.update_object(line)
  def updateCircle(self):
    for i, angleBin in enumerate(self.currentSpace.angleBins):
      if len(angleBin) == 0:
        color = Color(255, 0, 0)
      else:
        color = Color(0, 255, 0)
      self.segmentMarkers[i].data.color = color
      self.scene.update_object(self.segmentMarkers[i])
  def update(self):
    rotation = self.camera.data.rotation
    rot = R.from_quat((rotation.x, rotation.y, rotation.z, rotation.w))
    v = rot.apply((0, 0, -0.1))
    end = Position(v[0], -v[2], 0)
    self.arrow.data.end = end
    self.scene.update_object(self.arrow)
    cameraPosition = (self.camera.data.position.x, self.camera.data.position.y, self.camera.data.position.z)
    newSpace = self.grids[self.device].getSpaceForPosition(cameraPosition)
    if newSpace != self.currentSpace:
      self.changeSpace(newSpace)
      print("CHANGED SPACE")
    self.updateCircle()
    
  def __init__(self, camera, scene, grids=None, startDevice=None):
    self.camera = camera
    self.grids = grids
    self.device = startDevice
    self.scene = scene
    self.spaceBoundaries = []
    for i in range(12):
      self.spaceBoundaries.append(Line(
        start=(0, 0, 0),
        end=(0, 0, 0),
        color=(0, 0, 0),
      ))
      scene.add_object(self.spaceBoundaries[i])
    cameraPosition = (self.camera.data.position.x, self.camera.data.position.y, self.camera.data.position.z)
    self.changeSpace(self.grids[self.device].getSpaceForPosition(cameraPosition))
    self.centerCircle = Circle(
      position=(0, 0.4, -1),
      radius=0.02,
      color=(70, 0, 100),
      parent=self.camera.object_id
    )
    self.arrow = Line(
      start=(0, 0, 0),
      end=(0, 0.1, 0),
      color=(0,255,0),
      parent=self.centerCircle.object_id
    )
    scene.add_object(self.centerCircle)
    scene.add_object(self.arrow)
    self.segmentMarkers = []
    self.segments = len(self.currentSpace.angleBins)
    for i, angleBin in enumerate(self.currentSpace.angleBins):
      angle = np.pi * 2 / self.segments * i
      position = (0.15 * np.cos(angle), -0.15 * np.sin(angle), 0)
      if len(angleBin) == 0:
        color = (255, 0, 0)
      else:
        color = (0, 255, 0)
      circle = Circle(
        position=position,
        radius=0.02,
        color=color,
        parent=self.centerCircle.object_id
      )
      self.segmentMarkers.append(circle)
      scene.add_object(circle)
    scene.run_forever(self.update, interval_ms=300)
    scene.run_tasks()