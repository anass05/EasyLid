from rplidar import RPLidar
import time
import sys
import signal
from threading import Thread
import threading
path = 'outputs/test1'
outputFile = open(path,'w')

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
        outputFile.close()
        break
      else:
        print('%d: Got %d measurments' % (i, len(scan)))
        print('Ultrason %d' % (ULT_AG))
        if i%10 == 0:
         outputFile.write(''.join(str(x) for x in scan))
         #outputFile.write('(%d, %d, %d, %d, %d, %d)'%(ULT_AG,ULT_AD,ULT_AC,ULT_DG,ULT_DD,ULT_DC))
         outputFile.write('\n')

lidar = RPLidar('/dev/LIDAR')

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
  threadLidar.join()
