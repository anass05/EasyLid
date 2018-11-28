from rplidar import RPLidar
import time
import sys
import signal
from threading import Thread
import threading

class Lidar(Thread):
  def __init__(self, lidar):
    Thread.__init__(self)
    self.shutdown_flag = threading.Event()
    self.lidar=lidar
  def run(self):
    info = self.lidar.get_info()
    print(info)
    health = self.lidar.get_health()
    print(health)
    
    time.sleep(5);
    for i, scan in enumerate(self.lidar.iter_scans()):
      if self.shutdown_flag.is_set():
        print('please wait, lidar is shuting down')
        break
      else:
        print('%d: Got %d measurments' % (i, len(scan)))

lidar = RPLidar('/dev/ttyUSB0')

threadLidar=Lidar(lidar)

def signal_handler(sig, frame):
  print('You pressed Ctrl+C!')
  threadLidar.shutdown_flag.set()
  time.sleep(5)
  lidar.stop()
  lidar.stop_motor()
  lidar.disconnect()

if __name__ == "__main__":
  threadLidar.start()
  signal.signal(signal.SIGINT, signal_handler)
  print('Press Ctrl+C')
  threadLidar.join()
