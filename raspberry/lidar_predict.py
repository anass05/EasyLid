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

  def run(self):
    x_model = keras.Sequential([
        keras.layers.Flatten(input_shape=(360,)),
        keras.layers.Dense(128, activation=tf.nn.relu),
        keras.layers.Dense(4, activation=tf.nn.softmax)
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
    normalcounter = 0.0
    leafcounter = 0.0
    leafCounterstop = 0
    for i, scan in enumerate(self.lidar.iter_scans()):
      counter += 1
      if self.shutdown_flag.is_set() or Lidar.leafStop == 1:
        print('please wait, lidar is shuting down')
        rate=normalcounter/(normalcounter+leafcounter)
        print(normalcounter)
        print(leafcounter)
        print(rate)
        break
      else:
        if counter > 2:
          lidarTab = []
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
              Lidar.leafStop=1
              print('You pressed Ctrl+C!')
              time.sleep(5)
              self.lidar.stop()
              self.lidar.stop_motor()

