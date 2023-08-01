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