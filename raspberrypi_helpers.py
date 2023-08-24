import shlex
import subprocess
def changeChannel(channel_num):
  """Change the channel network adapter listens on"""
  print("Changing to Channel ", str(channel_num))
  command = "sudo iwconfig wlan1 channel " + str(channel_num)
  command = shlex.split(command)
  subprocess.Popen(command, shell=False)