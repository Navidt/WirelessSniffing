import numpy as np
from time import time
from typing import Tuple
from scipy.spatial.transform import Rotation as R
from grid import *
#set camera as parent

Vector = Tuple[float, float, float]
#Quaternion rotation
Rotation = Tuple[float, float, float, float]
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
    print(weight)
    coeffs = generateCoefficients(line)
    for i in range(3):
      rows[i] = add(rows[i], scale(weight, coeffs[i][0]))
      svalues[i] += weight * coeffs[i][1]
  left = np.matrix(rows)
  right = np.array(svalues)
  return np.linalg.solve(left, right)


#number of consevituve unsampled regions
def getUnsampledRegions(radianRotations: list[float], bins: int) -> float:
  regions =  [0] * bins
  for radians in radianRotations:
    regions[int((radians + np.pi) * bins / (2 * np.pi))] += 1
  #find the greatest consecutive zero region assuming the list is circular
  maxRegion = 0
  currentRegion = 0
  for region in regions:
    if region == 0:
      currentRegion += 1
    else:
      if currentRegion > maxRegion:
        maxRegion = currentRegion
      currentRegion = 0
  if currentRegion == len(regions):
    maxRegion = currentRegion
  elif currentRegion != 0:
    for region in regions:
      if region == 0:
        currentRegion += 1
      else:
        break
    if currentRegion > maxRegion:
      maxRegion = currentRegion
  return maxRegion

def getSampleWeight(rotations: list[Rotation]) -> float:
  radianRotations = []
  for rotation in rotations:
    radians = rotationToYRotation(rotation)
    radianRotations.append(radians)
  #they should at least each cover a third of the circle
  if getUnsampledRegions(radianRotations, 3) != 0:
    return 0
  unsamlpedRegions = getUnsampledRegions(radianRotations, 12)
  #My thinking is if the max unsampled regions is halved, then the weight should quadruple since reductions in unsampled regions become more and more difficult
  return 1 - (unsamlpedRegions / 4)**2

def getEstimate(grid):
  bestSignal = -500
  bestLocation = (0, 0)
  for space in grid.spaces.values():
    if space.average > bestSignal:
      bestSignal = space.average
      bestLocation = space.center
  print(bestLocation, bestSignal)
  return bestLocation

def getMaxReading(space):
  maxReading = space.readings[0]
  for reading in space.readings:
    if reading[2] > maxReading[2]:
      maxReading = reading
  return maxReading

def newGetEstimate(grid):
  lines = []
  weights = []
  for space in grid.spaces.values():
    rotations = list(map(lambda r: r[1], space.readings))
    weight = getSampleWeight(rotations)
    if weight == 0:
      continue
    bestReading = getMaxReading(space)
    vector = R.from_quat(bestReading[0]).apply((0, 0, -1))
    lines.append((space.center, vector))
    weights.append(weight)
  if len(lines) == 0:
    return None
  return solveLines(lines, weights)


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