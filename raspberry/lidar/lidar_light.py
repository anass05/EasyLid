from rplidar import RPLidar
import time
import sys
import signal
from threading import Thread
import threading
import os


class Lidar(Thread):
  def __init__(self, lidar):
    Thread.__init__(self)
    self.shutdown_flag = threading.Event()
    self.lidar=lidar
    print(str(len(sys.argv)))
    if len(sys.argv)==1:
      self.type='outputs/normal'
      self.size=25
    elif len(sys.argv)==2:
      self.type='outputs/'+str(sys.argv[1])
      self.size=25
    else:
      self.type='outputs/'+str(sys.argv[1])
      self.size=int(str(sys.argv[2]))


  def run(self):
    info = self.lidar.get_info()
    print(info)
    health = self.lidar.get_health()
    print(health)
    if not os.path.exists('outputs'):
       os.makedirs('outputs')
    if not os.path.exists(self.type):
       os.makedirs(self.type)
    
    fileName=time.strftime("%Y%m%d%H%M%S")
    savedTurns=0
    outputFile = open(self.type+'/'+fileName,'w')
    time.sleep(5);
    for i, scan in enumerate(self.lidar.iter_scans()):
      if self.shutdown_flag.is_set():
        print('please wait, lidar is shuting down')
        outputFile.close()
        break
      else:
        print('%d: Got %d measurments' % (i, len(scan)))
       # print('Ultrason %d' % (ULT_AG))
        if i%5 == 4:
          lidarTab = []
          for i in range(360):
            lidarTab.append(0)
          
          for x in scan:
            lidarTab[int(x[1])]=x[2]
          outputFile.write(''.join(str(x)+', ' for x in lidarTab))
          #outputFile.write('(%d, %d, %d, %d, %d, %d)'%(ULT_AG,ULT_AD,ULT_AC,ULT_DG,ULT_DD,ULT_DC))
          outputFile.write('\n')
          savedTurns += 1
          if savedTurns >= self.size:
            outputFile.close()
            fileName=time.strftime("%d%m%Y%H%M%S")
            savedTurns=0
            outputFile = open(self.type+'/'+fileName,'w')


'''
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
'''