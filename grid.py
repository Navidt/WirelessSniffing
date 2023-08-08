from typing import Tuple
from algoritms import *
import numpy as np
class GridSpace():
  def __init__(self, center, angleBinCount, readings=None):
    if readings == None:
      readings = []
    self.center = center
    self.angleBinCount = angleBinCount
    self.angleBins = []
    for i in range(angleBinCount):
      self.angleBins.append([])
    self.angleAverages = [0] * angleBinCount
    self.angleTotals = [0] * angleBinCount
    self.readings = readings
    self.total = 0
    self.maxAverage = None
    self.minAverage = None
    for reading in readings:
      # print(reading)
      self.total += reading[2]
    if len(readings) > 0:
      self.average = self.total / len(readings)
    else:
      self.average = 0
  
  def addReading(self, reading):
    self.total += reading[2]
    self.readings.append(reading)
    angle = rotationToYRotation(reading[1])
    angleBin = int(angle / (2 * np.pi / self.angleBinCount))
    # print(angleBin)
    # print(list(map(lambda x: len(x), self.angleBins)))
    self.angleBins[angleBin].append(reading)
    self.angleTotals[angleBin] += reading[2]
    self.angleAverages[angleBin] = self.angleTotals[angleBin] / len(self.angleBins[angleBin])
    if self.maxAverage == None or self.maxAverage < self.angleAverages[angleBin]:
      self.maxAverage = self.angleAverages[angleBin]
    if self.minAverage == None or self.minAverage > self.angleAverages[angleBin]:
      self.minAverage = self.angleAverages[angleBin]
    self.average = self.total / len(self.readings)
  
  def serialize(self):
    string = f"{self.center[0]},{self.center[1]},{self.center[2]},{self.average}\n"
    for reading in self.readings:
      string += f"{reading[0][0]},{reading[0][1]},{reading[0][2]},{reading[1][0]},{reading[1][1]},{reading[1][2]},{reading[1][3]},{reading[2]}\n"
    return string
  

class Grid():
  def __init__(self, xWidth, yWidth, zWidth, center=(0, 0, 0), angleBinCount=12) -> None:
    self.origin = (center[0] - xWidth / 2, center[1] - yWidth / 2, center[2] - zWidth / 2)
    self.spaces: dict[Tuple[float, float, float], GridSpace] = {}
    self.xWidth = xWidth
    self.yWidth = yWidth
    self.zWidth = zWidth
    self.angleBinCount = angleBinCount
  
  def getCoordsForPosition(self, position):
    xOffset = position[0] - self.origin[0]
    yOffset = position[1] - self.origin[1]
    zOffset = position[2] - self.origin[2]
    spaceCoords = (xOffset // self.xWidth, yOffset // self.yWidth, zOffset // self.zWidth)
    return spaceCoords
    
  def getSpaceForPosition(self, position):
    spaceCoords = self.getCoordsForPosition(position)
    if spaceCoords not in self.spaces.keys():
      self.addSpace(spaceCoords)
    return self.spaces[spaceCoords]
  
  def addReading(self, reading):
    position = reading[0]
    self.getSpaceForPosition(position).addReading(reading)

  def addSpace(self, spaceCoords):
    centerX = (spaceCoords[0] + 0.5) * self.xWidth + self.origin[0]
    centerY = (spaceCoords[1] + 0.5) * self.yWidth + self.origin[1]
    centerZ = (spaceCoords[2] + 0.5) * self.zWidth + self.origin[2]
    self.spaces[spaceCoords] = GridSpace((centerX, centerY, centerZ), self.angleBinCount)
  
  def addReadings(self, readings):
    for reading in readings:
      self.addReading(reading)
  
  def serialize(self):
    string = ""
    for space in self.spaces.values():
      string += space.serialize() + "\n"
    return string
  def saveToFile(self, fileName):
    with open(fileName, "w") as file:
      file.write(self.serialize())
  def deserialize(self, string):
    for spaceText in string.split("\n\n"):
      lines = spaceText.split("\n")
      for line in lines:
        if line == "":
          continue
        values = line.split(",")
        if len(values) == 4:
          #first entry
          pass
        else:
          self.addReading(((float(values[0]), float(values[1]), float(values[2])), (float(values[3]), float(values[4]), float(values[5]), float(values[6])), float(values[7])))
  def loadFromFile(self, fileName):
    with open(fileName, "r") as file:
      self.deserialize(file.read())
  