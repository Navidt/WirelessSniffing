from grid import *
from arena import *
from scipy.spatial.transform import Rotation as R
class Indicator():
  def reload(self):
    print("reload")
    self.centerCircle = Circle(
      position=(0, 0.6, -1),
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
  def updateArrowPosition(self):
    # print("hi")
    rotation = self.camera.data.rotation
    rot = R.from_quat((rotation.x, rotation.y, rotation.z, rotation.w))
    v = rot.apply((0, 0, -0.1))
    end = Position(v[0], -v[2], 0)
    print(end)
    self.arrow.data.end = end
    print(self.arrow)
    self.scene.update_object(self.arrow)

  def __init__(self, segments, camera, scene, grids=None, startCoords=None, startDevice=None):
    self.camera = camera
    self.grids = grids
    self.device = startDevice
    self.coords = startCoords
    self.segmentIndicators = []
    self.scene = scene
    self.reload()
    scene.run_forever(self.updateArrowPosition, interval_ms=300)
    scene.run_tasks()