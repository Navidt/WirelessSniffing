from grid import *
from arena import *
from algoritms import *
from scipy.spatial.transform import Rotation as R
class Indicator():
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
      cameraPosition = (self.camera.data.position.x, self.camera.data.position.y, self.camera.data.position.z)
      self.currentSpace = self.grids[self.device].getSpaceForPosition(cameraPosition)
      print("CHANGING SPACE")
    self.updateCircle()
    

  def __init__(self, camera, scene, grids=None, startDevice=None):
    self.camera = camera
    self.grids = grids
    self.device = startDevice
    self.scene = scene
    cameraPosition = (self.camera.data.position.x, self.camera.data.position.y, self.camera.data.position.z)
    self.currentSpace = self.grids[self.device].getSpaceForPosition(cameraPosition)
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