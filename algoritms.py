import numpy as np
from time import time
from typing import Tuple
from scipy.spatial.transform import Rotation as R
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

def getSampleWeight(rotations: list[Rotation]) -> float:
  radianRotations = []
  for rotation in rotations:
    radians = rotationToYRotation(rotation)
    radianRotations.append(radians)
  if getUnsampledRegions(radianRotations, 3) != 0:
    return 0
  unsamlpedRegions = getUnsampledRegions(radianRotations, 12)
  return 1 - unsamlpedRegions / 12

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

print(rotationToYRotation((0, 0.4794255, 0, 0.8775826)))

print(np.arctan2(1,0))