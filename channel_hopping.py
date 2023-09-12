from scapy.all import *
from raspberrypi_helpers import *
from time import sleep

availableChannels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 149, 153]

def getMACAddresses():
  macAddresses = {}
  for channel in availableChannels:
    def processPacket(pkt):
      print("Channel:", channel)
      if not pkt.haslayer(Dot11):
        return
      if pkt.addr2 in macAddresses.keys():
        if channel in macAddresses[pkt.addr2].keys():
          macAddresses[pkt.addr2][channel] += 1
        else:
          macAddresses[pkt.addr2][channel] = 1
      else:
        macAddresses[pkt.addr2] = {channel: 1}
    sniffer = AsyncSniffer(iface="wlan1", prn=processPacket, store=False)
    sniffer.start()
    sleep(3)
    sniffer.stop()
  return macAddresses


if __name__ == "__main__":
  print(getMACAddresses())