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
    #sans argument dossier normal 25 ligne par fichier
    if len(sys.argv)==1:
      self.type='outputs/normal'
      self.size=25
    #1er argument dossier de stockage
    elif len(sys.argv)==2:
      self.type='outputs/'+str(sys.argv[1])
      self.size=25
    else:
      #2 arguments dossier de stockage + nombre de lignes
      self.type='outputs/'+str(sys.argv[1])
      self.size=int(str(sys.argv[2]))


  def run(self):
    info = self.lidar.get_info()
    print(info)
    health = self.lidar.get_health()
    print(health)
    #créer les dossiers si non existant
    if not os.path.exists('outputs'):
       os.makedirs('outputs')
    if not os.path.exists(self.type):
       os.makedirs(self.type)
    #nom du fichier 
    fileName=time.strftime("%Y%m%d%H%M%S")
    savedTurns=0
    outputFile = open(self.type+'/'+fileName,'w')
    time.sleep(5);
    #compteur pour le nombre de lignes
    counter = 0
    # parcours des datas du lidar
    for i, scan in enumerate(self.lidar.iter_scans()):
      counter += 1
      if self.shutdown_flag.is_set():
        print('please wait, lidar is shuting down')
        outputFile.close()
        break
      else:
        #on ne prend pas la première valeur qui ne comporte pas toujours 360 points
        if counter > 2:
          lidarTab = []
          #init d'un tableau avec 360 zeros
          for i in range(360):
            lidarTab.append(0)
          #int(x[i]) renvoie l'angle, correspond a l'indice du tableau, x[2] renvoie la distance
          for x in scan:
            lidarTab[int(x[1])]=x[2]
          outputFile.write(''.join(str(x)+', ' for x in lidarTab))
          outputFile.write('\n')
          savedTurns += 1
          if savedTurns >= self.size:
            outputFile.close()
            fileName=time.strftime("%Y%m%d%H%M%S")
            savedTurns=0
            outputFile = open(self.type+'/'+fileName,'w')
            print("saved")
