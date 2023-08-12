from grid import *
from arena import *
from algoritms import *
from scipy.spatial.transform import Rotation as R
from arena_helpers import *
class Indicator():
  def changeDevice(self, newDevice):
    self.device = newDevice
    self.currentSpace = self.grids[self.device].getSpaceForPosition((self.camera.data.position.x, self.camera.data.position.y, self.camera.data.position.z))
    self.updateCircle()
  def changeSpace(self, newSpace):
    self.currentSpace = newSpace
    center = newSpace.center
    print("Center:", center, "Location:", self.camera.data.position)
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
    maxAverage = self.grids[self.device].maxAverage
    minAverage = self.grids[self.device].minAverage
    if maxAverage == minAverage:
      maxAverage = self.currentSpace.maxAverage
      minAverage = self.currentSpace.minAverage
    maxDifference = 0
    maxMarkerIndex = None
    for i, angleBin in enumerate(self.currentSpace.angleBins):
      if len(angleBin) == 0:
        color = Color(255, 0, 0)
        radius = 0.01
      else:
        color = Color(0, 0, 255)
        difference = self.currentSpace.angleAverages[i] - minAverage
        if difference > maxDifference:
          maxDifference = difference
          maxMarkerIndex = i
        if maxAverage == minAverage:
          radius = 0.02
        else:
          radius = 0.02 + 0.04 * difference / (maxAverage - minAverage)
      self.segmentMarkers[i].data.color = color
      self.segmentMarkers[i].data.radius = radius
    if maxMarkerIndex != None:
      self.segmentMarkers[maxMarkerIndex].data.color = Color(0, 255, 0)
    self.scene.update_objects(self.segmentMarkers)
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
        color = (0, 0, 255)
      circle = Circle(
        position=position,
        radius=0.01,
        color=color,
        parent=self.centerCircle.object_id
      )
      self.segmentMarkers.append(circle)
    scene.add_objects(self.segmentMarkers)
    self.loopedTask = repeat_task(self.update, 300, scene)
  def scrub(self):
    for boundary in self.spaceBoundaries:
      print("Boundary:", boundary.object_id)
      self.scene.delete_object(boundary)
    self.loopedTask.cancel()
  def __del__(self):
    # for boundary in self.spaceBoundaries:
    #   print("Boundary:", boundary.object_id)
    #   self.scene.delete_object(boundary)
    # self.loopedTask.cancel()
    return