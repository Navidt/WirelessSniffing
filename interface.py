from indicator import Indicator
from arena_helpers import makeBaseDoubleTapButton
from arena import *
class Interface:
  def goForward(self):
    print("GOING FORWARD")
    self.selectedDeviceIndex = (self.selectedDeviceIndex + 1) % len(self.grids)
    self.selectedDevice = list(self.grids.keys())[self.selectedDeviceIndex]
    self.indicator.changeDevice(self.selectedDevice)
    self.macText.data.text = self.selectedDevice
    self.scene.update_object(self.macText)

  def goBackward(self):
    print("GOING BACKWARD")
    self.selectedDeviceIndex = (self.selectedDeviceIndex - 1) % len(self.grids)
    self.selectedDevice = list(self.grids.keys())[self.selectedDeviceIndex]
    self.indicator.changeDevice(self.selectedDevice)
    self.macText.data.text = self.selectedDevice
    self.scene.update_object(self.macText)

  def __init__(self, camera, scene, grids):
    self.camera = camera
    self.grids = grids
    self.scene = scene
    self.selectedDeviceIndex = 0
    self.selectedDevice = list(grids.keys())[0]
    print("h0")
    self.indicator = Indicator(camera, scene, grids, self.selectedDevice)
    print("h0.5")
    self.shell = Tetrahedron(
      position=(0,0,0),
      parent=camera.object_id,
      material=Material(color=(255, 0, 0), opacity=0.0, transparent=True),
    )
    self.button = Circle(
      color=(255, 0, 0),
      parent=self.shell.object_id,
      position=(0, 0, -1),
      radius=0.1
    )
    print("h1")
    self.scene.add_object(self.shell)
    # self.scene.add_object(self.invisibleWrapper)
    print("h2")
    # self.button = Circle(
      # color=(255, 0, 0),
      # parent=self.invisibleWrapper.object_id,
      # position=(0, -0.7, -1),
      # radius=0.2
    # )
    makeBaseDoubleTapButton(self.button, self.goForward, self.goBackward, scene)
    self.macText = Text(
      text=self.selectedDevice,
      parent=self.shell.object_id,
      position=(0, -0.55, -1),
      scale=(0.2, 0.2, 0.2),
    )
    self.scene.add_object(self.macText)
  def scrub(self):
    self.indicator.scrub()
  def __del__(self):
    print("Deleting boundari")
    # del self.indicator
