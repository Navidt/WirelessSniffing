from indicator import Indicator
from arena_helpers import makeBaseDoubleTapButton
from arena import *
class Interface:
  def goForward(self):
    self.selectedDeviceIndex = (self.selectedDeviceIndex + 1) % len(self.grids)
    self.indicator.changeDevice(list(self.grids.keys())[self.selectedDeviceIndex])

  def goBackward(self):
    self.selectedDeviceIndex = (self.selectedDeviceIndex - 1) % len(self.grids)
    self.indicator.changeDevice(list(self.grids.keys())[self.selectedDeviceIndex])

  def __init__(self, camera, scene, grids):
    self.camera = camera
    self.grids = grids
    self.scene = scene
    self.selectedDeviceIndex = 0
    self.selectedDevice = list(grids.keys())[0]
    self.indicator = Indicator(camera, scene, grids, self.selectedDevice)
    self.shell = Tetrahedron(
      position=(0,0,0),
      parent=camera.object_id,
      material=Material(color=(255, 0, 0), opacity=0.0, transparent=True),
    )
    self.invisibleWrapper = Circle(
      material=Material(color=(255, 0, 0), opacity=0.0, transparent=True),
      parent=self.shell.object_id,
      position=(0, 0, -1),
      radius=0.3
    )
    self.button = Circle(
      color=(255, 0, 0),
      parent=self.invisibleWrapper.object_id,
      position=(0, -0.7, -1),
      radius=0.2
    )
    makeBaseDoubleTapButton(self.button, self.goForward, self.goBackward, scene)
