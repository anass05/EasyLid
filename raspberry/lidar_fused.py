#Lidar Imports
import sys
#sys.path.insert(0,'../lidar')
from rplidar import RPLidar
import time

import signal
from threading import Thread
import threading
path = 'outputs/test1'
outputFile = open(path,'w')


#Can imports
import can
import os
import struct

HOST = ''                # Symbolic name meaning all available interfaces
PORT = 6666              # Arbitrary non-privileged port

MCM = 0x010
MS = 0x100
US1 = 0x000
US2 = 0x001
OM1 = 0x101
OM2 = 0x102

ULT_AG = 0
'''
    Messages envoyés :
    - ultrason avant gauche
    header : UFL payload : entier, distance en cm
    - ultrason avant centre
    header : UFC payload : entier, distance en cm
    - ultrason avant droite
    header : UFR payload : entier, distance en cm
    - ultrason arriere gauche
    header : URL payload : entier, distance en cm
    - ultrason arriere centre
    header : URC payload : entier, distance en cm
    - ultrason arriere droite
    header : URR payload : entier, distance en cm
    - position volant
    header : POS payload : entier, valeur brute du capteur
    - vitesse roue gauche
    header : SWL payload : entier, *0.01rpm
    - vitesse roue droite
    header : SWR payload : entier, *0.01rpm
    - Niveau de la batterie
    header : BAT payload : entier, mV
    - Pitch
    header : PIT payload : float, angle en degrée
    - Yaw
    header : YAW payload : float, angle en degrée
    - Roll
    header : ROL payload : float, angle en degrée
    
    Messages reçus :
    - Modification de la vitesse
    header : SPE payload : valeur entre 0 et 50
    - Control du volant (droite, gauche)
    header : STE paylaod : left | right | stop
    - Contra l de l'avancée
    header : MOV payload : forward | backward | stop
    '''

class MySend(Thread):
    
    detectObstacle = False
    detectObstacleOld = False
    detectObstacleAD = False
    detectObstacleAG = False
    detectObstacleAC = False
    detectObstacleACproche = False
    differentiel = False
    distanceDetectObstacleAD = 30
    distanceDetectObstacleAG = 30
    distanceDetectObstacleACproche = 30
    distanceDetectObstacleAC = 150
    
    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus
        self.shutdown_flag = threading.Event()
    
    def run(self):
        
        self.speed_cmd = 30
        self.move = 0
        self.turn = 0
        self.enable = 0
        
        while not self.shutdown_flag.is_set() :
            
            msg = self.bus.recv()
            
            # print(msg.arbitration_id, msg.data)
            # print("Reading")
            
            
            
            st = ""
            
            if msg.arbitration_id == US1:
                
                # ultrason avant gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                global ULT_AG
                ULT_AG = distance
                message = "UFL:" + str(distance)+ ";"
                if distance < MySend.distanceDetectObstacleAG and distance > 0:
                    MySend.detectObstacleAG=True
                else: MySend.detectObstacleAG=False
                print(message)
                
                # ultrason avant droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                message = "UFR:" + str(distance)+ ";"
                if distance < MySend.distanceDetectObstacleAD and distance > 0:
                    MySend.detectObstacleAD = True
                else: MySend.detectObstacleAD = False
                print(message)
            
                # ultrason avant centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "URC:" + str(distance)+ ";"
                if distance < MySend.distanceDetectObstacleACproche and distance > 0:
                    MySend.detectObstacleACproche = True
                elif distance<MySend.distanceDetectObstacleAC and distance > 0:
                    MySend.detectObstacleAC = True
                else:
                    MySend.detectObstacleAC = False
                    MySend.detectObstacleACproche = False

                print(message)
                MySend.detectObstacleOld = MySend.detectObstacle
                MySend.detectObstacle = MySend.detectObstacleAC #pour l'instant on regarde que les obstacles en face
            
            elif msg.arbitration_id == MS:
                # position volant
                position_volant = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "POS:" + str(position_volant)+ ";"
                #print(message)
            
                # detection obstacle lointain avec ultrason avant centre; dans ce cas on tourne à droite
                if MySend.detectObstacle and not(MySend.detectObstacleAG) and not(MySend.detectObstacleAD) and not(MySend.detectObstacleACproche):
                    self.move = 1
                    self.enable = 1
                    differentiel = False
                    if ( MySend.detectObstacle == MySend.detectObstacleOld ): #checke que c'est une valeur plausible et pas juste une erreur de passage
                        self.move = 1
                        self.enable = 1
                        differentiel = True
                        if (position_volant > 1350):
                            self.turn = -1
                        else:
                            self.turn = 0
                # detection obstacle proche dans ce cas on s'arrête
                elif MySend.detectObstacleAG or MySend.detectObstacleAD or MySend.detectObstacleACproche:
                    self.move = 0
                    self.enable = 0
                # si pas d'obstacle on va tout droit
                else:
                    self.move = 1
                    self.enable = 1
                    differentiel = False
                    # permet de "rester droit"
                    if (position_volant < 1600):
                        self.turn = 1
                    elif (position_volant > 1700):
                        self.turn = -1
                    else:
                        self.turn = 0
    
                #calcul des commandes de mouvement
                if self.enable:
                    if differentiel :
                        cmd_mv_droit = (50 - self.move*self.speed_cmd - 10) | 0x80   #marche arrière
                        cmd_mv_gauche = (50 + self.move*self.speed_cmd) | 0x80
                    else:
                        cmd_mv_droit = (50 + self.move*self.speed_cmd) | 0x80
                        cmd_mv_gauche = (50 + self.move*self.speed_cmd) | 0x80
                    cmd_turn = 50 + self.turn*20 | 0x80
                else:
                    cmd_mv_droit = (50 + self.move*self.speed_cmd) & ~0x80
                    cmd_mv_gauche = (50 + self.move*self.speed_cmd) & ~0x80
                    cmd_turn = 50 + self.turn*20 & 0x80
            
            #if (st!=""):print(st)
            
                msg = can.Message(arbitration_id=MCM,data=[cmd_mv_gauche, cmd_mv_droit, cmd_turn,0,0,0,0,0],extended_id=False)
                self.bus.send(msg)



# Lidar Thread


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
        outputFile.write(''.join(str(x) for x in scan))
        outputFile.write('\n')

lidar = RPLidar('/dev/ttyUSB0')

threadLidar=Lidar(lidar)

print('Bring up CAN0....')
os.system("sudo /sbin/ip link set can0 down")
os.system("sudo /sbin/ip link set can0 up type can bitrate 400000")
time.sleep(0.1)

try:
 bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
except OSError:
 print('Cannot find PiCAN board.')
 exit()

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

    
    threadLidar.start()
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')
    
    newsend.start()

    
    threadLidar.join()
    newsend.join()
