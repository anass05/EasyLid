# coding: utf-8
import sys
sys.path.insert(0,'../can')
from threading import Thread
import time
import can
import os
import struct

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 6666              # Arbitrary non-privileged port

MCM = 0x010
MS = 0x100
US1 = 0x000
US2 = 0x001
OM1 = 0x101
OM2 = 0x102


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
    differentiel = False
    distanceDetectObstacleAD = 50
    distanceDetectObstacleAG = 50
    distanceDetectObstacleAC = 200
    i = 0
	
    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus
        
    def run(self):
        
        self.speed_cmd = 50
        self.move = 0
        self.turn = 0
        self.enable = 0
        
        while True :
            msg = self.bus.recv()

          # print(msg.arbitration_id, msg.data)
          # print("Reading")
            MySend.i=MySend.i+1
           
            st = ""

            if msg.arbitration_id == US1:
                # ultrason avant gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
               #print(distance)
                message = "UFL:" + str(distance) + ";"
                #print(distance)
                if distance < MySend.distanceDetectObstacleAG and distance > 0:
                    MySend.detectObstacleAG=True
                else: MySend.detectObstacleAG=False
                    # ultrason avant droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                message = "UFR:" + str(distance)+ ";"
                #print(distance)
                if distance < MySend.distanceDetectObstacleAD and distance > 0:
                    MySend.detectObstacleAD=True
                else: MySend.detectObstacleAD=False
                # ultrason avant centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "URC:" + str(distance)+ ";"
                if MySend.i%10 ==0:
                    print('-> '+ str(distance))
                #print("------------------")
                if distance < MySend.distanceDetectObstacleAC and distance > 0:
                    MySend.detectObstacleAC=True
                else: MySend.detectObstacleAC=False
                MySend.detectObstacleOld = MySend.detectObstacle
                #MySend.detectObstacle = MySend.detectObstacleAG or MySend.detectObstacleAD or MySend.detectObstacleAC
                MySend.detectObstacle = MySend.detectObstacleAC
                
            elif msg.arbitration_id == MS:
                # position volant
                position_volant = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "POS:" + str(position_volant)+ ";"
                #print(message)
                  
            if MySend.detectObstacle:
                self.move = 1
                self.enable = 1
                differentiel = False
                #print("send cmd move stop")
                if ( MySend.detectObstacle == MySend.detectObstacleOld ):
                    self.move = 1
                    self.enable = 1
                    differentiel = True
                    if (position_volant > 1340):
                        self.turn = -1
                        #print("turn right detected")
                    else:
                        self.turn = 0
            else:
                #print("send cmd move forward")
                self.move = 1
                self.enable = 1
                differentiel = False
                if (position_volant<1600):
                    self.turn = 1
                elif (position_volant>1700):
                    self.turn = -1
                else:
                    self.turn = 0

                    
            if self.enable:
                if differentiel :
                    cmd_mv_droit = (50 - self.move*self.speed_cmd) | 0x80
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
            #print(msg)
            self.bus.send(msg)



# Echo server program


if __name__ == "__main__":

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
    newsend.start()

    newsend.join()
