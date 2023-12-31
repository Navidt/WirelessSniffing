import numpy as np
from time import time
from typing import Tuple
from scipy.spatial.transform import Rotation as R
from grid import *
#set camera as parent

Vector = Tuple[float, float, float]
#Quaternion rotation
Rotation = Tuple[float, float, float, float]

Reading = Tuple[Vector, Rotation, float]

def dot(a: Vector, b: Vector):
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def scale(s: float, v: Vector):
  return (s * v[0], s * v[1], s * v[2])
def add(a: Vector, b: Vector):
  return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def subtract(a: Vector, b: Vector):
  return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def rotationToYRotation(rotation: Rotation):
  rot = R.from_quat(rotation)
  vec = rot.apply((0, 0, -1))
  return np.arctan2(vec[2], vec[0])

def generateCoefficients(
    line: Tuple[Vector, Vector]
    ) -> list[Tuple[Vector, float]]:
  a = line[0]
  n = scale(1 / np.linalg.norm(line[1]), line[1])
  result = []
  for j in range(3):
    r1 = scale(n[j]*(1 - dot(n, n)), n)
    r2 = scale(n[j], n)
    row = subtract(add(r1, r2), generateCoefficients.units[j])
    s = n[j]*dot(n, a)*(2 - dot(n, n)) - a[j]
    result.append((row, s))
  return result
generateCoefficients.units = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
def solveLines(lines: list[Tuple[Vector, Vector]], weights: list[float] = None):
  rows = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
  svalues = [0, 0, 0]
  for i, line in enumerate(lines):
    if weights == None:
      weight = 1
    else:
      weight = weights[i]
    coeffs = generateCoefficients(line)
    for i in range(3):
      rows[i] = add(rows[i], scale(weight, coeffs[i][0]))
      svalues[i] += weight * coeffs[i][1]
  left = np.matrix(rows)
  right = np.array(svalues)
  return np.linalg.solve(left, right)


#number of consevituve unsampled regions
def getUnsampledRegions(bins: list[list]) -> float:
  #find the greatest consecutive zero region assuming the list is circular
  maxRegion = 0
  currentBin = 0
  for bin in bins:
    if len(bin) == 0:
      currentBin += 1
    else:
      if currentBin > maxRegion:
        maxRegion = currentBin
      currentBin = 0
  if currentBin == len(bins):
    maxRegion = currentBin
  elif currentBin != 0:
    for bin in bins:
      if len(bin) == 0:
        currentBin += 1
      else:
        break
    if currentBin > maxRegion:
      maxRegion = currentBin
  return maxRegion

def getSampleWeight(bins: list[list[Reading]]) -> float:
  unsamlpedRegions = getUnsampledRegions(bins)
  #My thinking is if the max unsampled regions is halved, then the weight should quadruple since reductions in unsampled regions become more and more difficult
  # return max(1 - (unsamlpedRegions / 3)**2, 0)
  if unsamlpedRegions < 3:
    return 1
  else:
    return 0

def getEstimate(grid):
  bestSignal = -500
  bestLocation = (0, 0, 0)
  for space in grid.spaces.values():
    if len(space.readings) < 10:
      continue
    if space.average > bestSignal:
      bestSignal = space.average
      bestLocation = space.center
  return bestLocation

def getMaxReading(space):
  maxReading = space.readings[0]
  for reading in space.readings:
    if reading[2] > maxReading[2]:
      maxReading = reading
  return maxReading

def newGetEstimate(grid):
  print("HI")
  lines = []
  weights = []
  for space in grid.spaces.values():
    weight = getSampleWeight(space.angleBins)
    # print("HI")
    # print(weight)
    print("Space:", space.center, "Weight:", weight, "Average:", space.average, "Readings:", len(space.readings))
    if weight == 0:
      continue
    bestReading = getMaxReading(space)
    vector = R.from_quat(bestReading[1]).apply((0, 0, -1))
    lines.append((bestReading[0], scale(10, vector)))
    weights.append(weight)
  if len(lines) < 2:
    return None
  position = solveLines(lines, weights)
  return ((position[0], position[1], position[2]), lines)


if __name__ == "__main__":
  #make an array of random rotations about the y axis represented as quaternions
  testRotations = []
  for num in range(5, 24):
    for i in range(num):
      # testRotations.append(R.random().as_quat())
      testRotations.append(R.from_euler('y', np.pi * i * 2 / num).as_quat())
    # del testRotations[int(i / 2)]
    # del testRotations[int(i / 2)]
    # del testRotations[int(i / 2)]
    # for rotation in testRotations:
      # print(rotationToYRotation(rotation))
    print(num, ":", getSampleWeight(testRotations))