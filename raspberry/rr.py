# coding: utf-8
import sys
sys.path.insert(0,'../can')
from threading import Thread
import time
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
    
    detectObstacleAD = False
    detectObstacleAG = False
    detectObstacleAC = False
    detectObstacleAR = False
    distanceDetectObstacle = 50

    cmd_mv_droit = 0;
    cmd_mv_gauche = 0;
    cmd_turn = 0;
    position_volant = 0;
    
    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus
    
    def run(self):
        
        self.speed_cmd = 30
        self.move = 0
        self.turn = 0
        self.enable = 0
        
        while True :
            
            msg = self.bus.recv()
            
            # print(msg.arbitration_id, msg.data)
            # print("Reading")
            
            st = ""
            
            #------------------------------------------------- DETECTION DES OBSTACLES ----------------------------------------------------
            
            if msg.arbitration_id == US1:
                
                # ultrason avant gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "UFL:" + str(distance) + ";"
                if distance < MySend.distanceDetectObstacle and distance > 0:
                    MySend.detectObstacleAG=True
                elif distance == 0:
                    None
                else:
                    MySend.detectObstacleAG=False
                
                # ultrason avant droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                message = "UFR:" + str(distance)+ ";"
                if distance < MySend.distanceDetectObstacle and distance > 0:
                    MySend.detectObstacleAD = True
                elif distance == 0:
                    None
                else:
                    MySend.detectObstacleAD = False
            
                # ultrason avant centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "UFR:" + str(distance)+ ";"
                if distance < MySend.distanceDetectObstacle and distance > 0:
                    MySend.detectObstacleAC = True
                elif distance == 0:
                    None
                else:
                    MySend.detectObstacleAC = False


            elif msg.arbitration_id == US2:
               # ultrason derriere
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "UFR:" + str(distance)+ ";"
                if distance < MySend.distanceDetectObstacle and distance > 0:
                    MySend.detectObstacleAR = True
                elif distance == 0:
                    None
                else:
                    MySend.detectObstacleAC = False

            elif msg.arbitration_id == MS:
                # position volant
                self.position_volant = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "POS:" + str(self.position_volant)+ ";"
                #print(message)

            #------------------------------------------------- REACTION TO OBSTACLES ----------------------------------------------------
    
            if not(self.detectObstacleAC):
                if not(self.detectObstacleAG) and not(self.detectObstacleAD):
                    self.marcheAvant()
                if not(self.detectObstacleAG) and self.detectObstacleAD:
                    self.tourneGauche()
                if self.detectObstacleAG and not(self.detectObstacleAG):
                    self.tourneDroit()
                if self.detectObstacleAG and self.detectObstacleAG:
                    self.marcheAvant()

            #------------------------------------------------- CALCUL ET ENVOI COMMANDES ----------------------------------------------------
            
            if self.enable:
                self.cmd_turn = 50 + self.turn*20 | 0x80
                self.cmd_mv_droit = (50 + self.move*self.speed_cmd) | 0x80
                self.cmd_mv_gauche = (50 + self.move*self.speed_cmd) | 0x80
            else:
                self.cmd_turn = 50 + self.turn*20 & 0x80
                self.cmd_mv_droit = (50 + self.move*self.speed_cmd) & ~0x80
                self.cmd_mv_gauche = (50 + self.move*self.speed_cmd) & ~0x80
            
            #------------------------------------------------- ENVOI MESSAGE CAN ----------------------------------------------------
            
            msg = can.Message(arbitration_id=MCM,data=[cmd_mv_gauche, cmd_mv_droit, cmd_turn,0,0,0,0,0],extended_id=False)
            self.bus.send(msg)


    def marcheAvant(self):
        self.move = 1
        self.enable = 1
        if (self.position_volant < 1600):
            self.turn = 1
        elif (self.position_volant > 1700):
            self.turn = -1
        else:
            self.turn = 0

    def tourneDroit(self):
        self.move = 1
        self.enable = 1
        if (self.position_volant > 1350):
            self.turn = -1
        else:
            self.turn = 0

    def tourneGauche(self):
        self.move = 1
        self.enable = 1
        if (self.position_volant < 1600):
            self.turn = 1
        else:
            self.turn = 0

    def stopInit(self):
        self.move = 0
        self.enable = 0
        if (self.position_volant < 1600):
            self.turn = 1
        elif (self.position_volant > 1700):
            self.turn = -1
        else:
            self.turn = 0



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
