from rplidar import RPLidar
import time
import sys
import signal
from threading import Thread
import threading
import numpy as np
import tensorflow as tf
from tensorflow import keras

'''
This Class shows anomalies in realtime nothing less nothing more
'''

class Lidar(Thread):
  leafStop=0
#initialising lidar class
  def __init__(self, lidar):
    Thread.__init__(self)
    self.shutdown_flag = threading.Event()
    self.lidar=lidar

#initialise the model, it must be the same as the model you trained it with... obviously
  def run(self):
    x_model = keras.Sequential([
        keras.layers.Flatten(input_shape=(360,)),
        keras.layers.Dense(180, activation=tf.nn.relu),
        keras.layers.Dense(90, activation=tf.nn.relu),
        keras.layers.Dense(4, activation=tf.nn.softmax)
        ])

#load the trained model
    checkpoint_path = "/EasyLid/raspberry/cp.ckpt"
    x_model.load_weights(checkpoint_path)
#show a summary, it's pretty useless but whatever
#you can comment it if you don't want to see that table each time
    x_model.summary()

    info = self.lidar.get_info()
    print(info)
    health = self.lidar.get_health()
    print(health)
    
    time.sleep(5);
    counter = 0
    normalcounter = 0.0
    leafcounter = 0.0
    #start getting data from the LiDAR
    for i, scan in enumerate(self.lidar.iter_scans()):
      counter += 1
      if self.shutdown_flag.is_set():
        print('please wait, lidar is shuting down')
        rate=normalcounter/(normalcounter+leafcounter)
        print("normal situations = "+str(normalcounter))
        print("leaf situations = "+str(leafcounter))
        print("accuracy = "+str(normalcounter)+"/"+str(normalcounter+leafcounter))
        print("accuracy = "+str(rate*100)+"%")
        break
      else:
       #we skip the 2 first revolution cause they are usualy wrong as the LiDAR's motor didn't acheive it's optimal speed
        if counter > 2:
          lidarTab = []
          for i in range(360):
            lidarTab.append(0)
          
          for x in scan:
            lidarTab[int(x[1])]=x[2]
        #get the 360 point and put them in a numpy array
          non_existing_test = np.array([lidarTab])

          train_max = non_existing_test.max()
          non_existing_test /= train_max
          
          x_predictions = x_model.predict(non_existing_test)
          #normal = 0 mirror = 1 feuille = 2 feuilleLoin = 3
          if x_predictions.argmax() == 0:
              print("normal "+str(x_predictions.max()))
              normalcounter+= 1
          elif x_predictions.argmax() == 1:
              print("mirror "+str(x_predictions.max()))
              leafcounter+= 1
          elif x_predictions.argmax() == 2:
              print("leaf "+str(x_predictions.max()))
              leafcounter+= 1
          elif x_predictions.argmax() == 3:
              print("weird leaf "+str(x_predictions.max()))
              leafcounter+= 1

#Change variable LIDAR with ttyUSB0
lidar = RPLidar('/dev/LIDAR')
threadLidar=Lidar(lidar)

#this function detects when the user has pressed CTRL + C
#without this function the programe will crash as the lidar's motor won't stop and 
#bad things will happen later, this function stops reading data from lidar 
#befor estopping the lidar

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
