from rplidar import RPLidar
import time
import sys
import signal
from threading import Thread

class Lidar(Thread):
  def __init__(self, lidar):
    Thread.__init__(self)
    self.lidar=lidar
        
  def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    self.lidar.stop()
    self.lidar.stop_motor()
    self.lidar.disconnect()
    sys.exit(0)
		
  def run(self):
    info = self.lidar.get_info()
    print(info)
    health = self.lidar.get_health()
    print(health)
    signal.signal(signal.SIGINT, self.signal_handler)
    print('Press Ctrl+C')
    time.sleep(5);
    for i, scan in enumerate(self.lidar.iter_scans()):
      print('%d: Got %d measurments' % (i, len(scan)))
	 		
if __name__ == "__main__":
  lidar = RPLidar('/dev/ttyUSB0')
  threadLidar=Lidar(lidar)
  threadLidar.start()
  threadLidar.join()



