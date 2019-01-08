from rplidar import RPLidar
import time
import sys
import signal
from threading import Thread
import threading
import numpy as np
import tensorflow as tf
from tensorflow import keras



class Lidar(Thread):
  leafStop=0

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
    x_model = keras.Sequential([
        keras.layers.Flatten(input_shape=(360,)),
        keras.layers.Dense(128, activation=tf.nn.relu),
        keras.layers.Dense(2, activation=tf.nn.softmax)
    ])


    checkpoint_path = "/EasyLid/raspberry/cp.ckpt"
    x_model.load_weights(checkpoint_path)
    
    x_model.summary()

    info = self.lidar.get_info()
    print(info)
    health = self.lidar.get_health()
    print(health)
    
    time.sleep(5);
    counter = 0
    normalcounter = 0
    leafcounter = 0
    leafCounterstop = 0
    for i, scan in enumerate(self.lidar.iter_scans()):
      counter += 1
      if self.shutdown_flag.is_set():
        print('please wait, lidar is shuting down')
        print(normalcounter)
        print(leafcounter)
        break
      else:
       # print('%d: Got %d measurments' % (i, len(scan)))
       # print('Ultrason %d' % (ULT_AG))
        if counter > 2:
          lidarTab = []
          #print("saving")
          for i in range(360):
            lidarTab.append(0)
          
          for x in scan:
            lidarTab[int(x[1])]=x[2]
        
          non_existing_test = np.array([lidarTab])
          x_predictions = x_model.predict(non_existing_test)
          if x_predictions.argmax() == 0:
              print("normal")
              normalcounter+= 1
              leafCounterstop = 0
          else:
              print("leaf")
              leafcounter+= 1
              leafCounterstop+=1
          if(leafCounterstop>=2):
              print("on doit stop")
              Lidar.leafStop=1
              self.shutdown_flag.set()

          
          '''outputFile.write(''.join(str(x)+', ' for x in lidarTab))
          #outputFile.write('(%d, %d, %d, %d, %d, %d)'%(ULT_AG,ULT_AD,ULT_AC,ULT_DG,ULT_DD,ULT_DC))
          outputFile.write('\n')
          savedTurns += 1
          if savedTurns >= self.size:
            outputFile.close()
            fileName=time.strftime("%d%m%Y%H%M%S")
            savedTurns=0
            outputFile = open(self.type+'/'+fileName,'w')
            print("saved")'''


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
  threadLidar.join()
