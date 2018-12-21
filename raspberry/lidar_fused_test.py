#Lidar Imports
from rplidar import RPLidar
import time
import sys
import signal
from threading import Thread
import threading

#Can imports
#sys.path.insert(0,'../../can')
import can
import os
import struct
from lidar_light import Lidar
from autonome3 import MySend

HOST = ''                # Symbolic name meaning all available interfaces
PORT = 6666              # Arbitrary non-privileged port

MCM = 0x010
MS = 0x100
US1 = 0x000
US2 = 0x001
OM1 = 0x101
OM2 = 0x102

VOL_GAUCHE=0
VOL_DROIT=0
VOL_CENTRE=0
print('Bring up CAN0....')
os.system("sudo /sbin/ip link set can0 down")
os.system("sudo /sbin/ip link set can0 up type can bitrate 400000")
os.system("sudo ifconfig can0 txqueuelen 1000")
time.sleep(0.1)

try:
    bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
except OSError:
    print('Cannot find PiCAN board.')
    exit()
lidar = RPLidar('/dev/ttyUSB0')
threadLidar=Lidar(lidar)
newsend = MySend(bus)

def signal_handler(sig, frame):
  print('You pressed Ctrl+C!')
  threadLidar.shutdown_flag.set()
  newsend.shutdown_flag.set()
  os.system("cansend can0 010#00000000")
  time.sleep(5)
  lidar.stop()
  lidar.stop_motor()
  lidar.disconnect()

if __name__ == "__main__":
    

    #gauche
    msg = can.Message(arbitration_id=MCM,data=[0, 0, 0xE4,0,0,0,0,0],extended_id=False)
    bus.send(msg)
    time.sleep(0.75)
    msg = can.Message(arbitration_id=MCM,data=[0, 0, 0,0,0,0,0,0],extended_id=False)
    bus.send(msg)
    time.sleep(0.5)
    msg1=bus.recv()
    while not (msg1.arbitration_id == MS):
        msg1=bus.recv()
    VOL_GAUCHE = int.from_bytes(msg1.data[0:2], byteorder='big')

    bus = can.interface.Bus(channel='can0', bustype='socketcan_native')

    #droit
    msg = can.Message(arbitration_id=MCM,data=[0, 0, 0x80,0,0,0,0,0],extended_id=False)
    bus.send(msg)
    time.sleep(0.75)
    msg = can.Message(arbitration_id=MCM,data=[0, 0, 0,0,0,0,0,0],extended_id=False)
    bus.send(msg)
    msg2=bus.recv()
    time.sleep(0.5)
    while not(msg2.arbitration_id == MS):
        msg2=bus.recv()
    VOL_DROIT = int.from_bytes(msg2.data[0:2], byteorder='big')

    VOL_CENTRE = int((VOL_GAUCHE+VOL_DROIT)/2)

    print(VOL_DROIT)
    print(VOL_GAUCHE)
    print(VOL_CENTRE)


 
    newsend.start()
    threadLidar.start()
    signal.signal(signal.SIGINT, signal_handler)
    threadLidar.join()
    newsend.join()
