from indicator import Indicator
from arena_helpers import makeButton
class Interface:
  def __init__(self, camera, scene, grids):
    self.camera = camera
    self.grids = grids
    self.scene = scene
    self.selectedDevice = list(grids.keys())[0]
    self.indicator = Indicator(camera, scene, grids, self.selectedDevice)
  
