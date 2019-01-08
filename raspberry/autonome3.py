# coding: utf-8
import sys
sys.path.insert(0,'../can')
from threading import Thread
import time
import can
import os
import struct
import threading
from lidar_predict import Lidar


HOST = ''                # Symbolic name meaning all available interfaces
PORT = 6666              # Arbitrary non-privileged port

MCM = 0x010
MS = 0x100
US1 = 0x000
US2 = 0x001
OM1 = 0x101
OM2 = 0x102
VOL_GAUCHE=0
VOL_DROIT=0
VOL_CENTRE=0

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


    # boolean 
    # avant voiture
    detectObstacleAVD = False
    detectObstacleAVDold = False
    detectObstacleAVG = False
    detectObstacleAVGold = False
    detectObstacleAVC = False
    detectObstacleAVCold = False
    detectObstacleAVCproche = False
    detectObstacleAVCprocheold = False
    # arriere voiture
    detectObstacleARD = False
    detectObstacleARDold = False
    detectObstacleARDproche = False
    detectObstacleARDprocheold = False
    detectObstacleARG = False
    detectObstacleARGold = False
    detectObstacleARGproche = False
    detectObstacleARGprocheold = False
    detectObstacleARC = False
    detectObstacleARCold = False
    
    differentielD = False
    differentielG = False

    lastActionD = True
    lastActionG = False

    # distance max
    # avant voiture
    distanceDetectObstacleAVD = 30
    distanceDetectObstacleAVG = 30
    distanceDetectObstacleAVC = 150
    distanceDetectObstacleAVCproche = 30
    #arriere voiture
    distanceDetectObstacleARD = 75
    distanceDetectObstacleARDproche = 20
    distanceDetectObstacleARG = 75
    distanceDetectObstacleARGproche = 20
    distanceDetectObstacleARC = 30

    
    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus
        self.shutdown_flag = threading.Event()

    def run(self):
        		
        self.speed_cmd = 30
        self.move = 0
        self.turn = 0
        self.enable = 0
        
        while not(self.shutdown_flag.is_set()):
            
            msg = self.bus.recv()
            
            # #print(msg.arbitration_id, msg.data)
            # print("Reading")
            
            st = ""
            
            #------------------------------------------------- LECTURE MESSAGE ----------------------------------------------------
            #000
            if msg.arbitration_id == US1:
                
                # ultrason avant gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "AVG:" + str(distance) + ";"
                #print(message)
                if distance < MySend.distanceDetectObstacleAVG and distance > 0:
                    MySend.detectObstacleAVG=True
                elif distance == 0:
                    None
                else:
                    MySend.detectObstacleAVG=False
                
                # ultrason avant droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                message = "AVD:" + str(distance)+ ";"
                #print(message)
                if distance < MySend.distanceDetectObstacleAVD and distance > 0:
                    MySend.detectObstacleAVD = True
                elif distance == 0:
                    None
                else:
                    MySend.detectObstacleAVD = False
            
                # ultrason avant centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "AVC:" + str(distance)+ ";"
                #print(message)
                if distance<MySend.distanceDetectObstacleAVCproche and distance > 0:
                    MySend.detectObstacleAVCproche = True
                    MySend.detectObstacleAVC = False
                elif distance < MySend.distanceDetectObstacleAVC:
                    MySend.detectObstacleAVC = True
                    MySend.detectObstacleAVCproche = False
                elif distance == 0:
                    None 
                else:
                    MySend.detectObstacleAVC = False
                    MySend.detectObstacleAVCproche = False
            #001        
            elif msg.arbitration_id == US2:
                
                # ultrason arriere gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "ARG:" + str(distance)+ ";"
                #print(message)
                if distance<MySend.distanceDetectObstacleARGproche and distance > 0:
                    MySend.detectObstacleARGproche = True
                    MySend.detectObstacleARG = False
                elif distance < MySend.distanceDetectObstacleARG:
                    MySend.detectObstacleARG = True
                    MySend.detectObstacleARGproche = False
                elif distance == 0:
                    None 
                else:
                    MySend.detectObstacleARG = False
                    MySend.detectObstacleARGproche = False

                
                # ultrason arriere droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                message = "ARD:" + str(distance)+ ";"
                #print(message)
                if distance<MySend.distanceDetectObstacleARDproche and distance > 0:
                    MySend.detectObstacleARDproche = True
                    MySend.detectObstacleARD = False
                elif distance < MySend.distanceDetectObstacleARD:
                    MySend.detectObstacleARD = True
                    MySend.detectObstacleARDproche = False
                elif distance == 0:
                    None 
                else:
                    MySend.detectObstacleARD = False
                    MySend.detectObstacleARDproche = False
                
                
                # ultrason arriere centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "ARC:" + str(distance)+ ";"
                #print(message)
                if distance < MySend.distanceDetectObstacleARC and distance > 0:
                    MySend.detectObstacleARC = True
                elif distance == 0:
                    None
                else:
                    MySend.detectObstacleARC = False       
            #100 
            elif msg.arbitration_id == MS:
                # position volant
                position_volant = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "POS:" + str(position_volant)+ ";"
                ##print(message)

            #------------------------------------------------- DETECTION OBSTACLE ----------------------------------------------------
            AVGOK = MySend.detectObstacleAVGold == MySend.detectObstacleAVG
            AVDOK = MySend.detectObstacleAVDold == MySend.detectObstacleAVD
            AVCOK = MySend.detectObstacleAVCold == MySend.detectObstacleAVC
            AVCprocheOK = MySend.detectObstacleAVCprocheold == MySend.detectObstacleAVCproche
            ARGOK = MySend.detectObstacleARGold == MySend.detectObstacleARG
            ARGprocheOK = MySend.detectObstacleARGprocheold == MySend.detectObstacleARGproche
            ARDOK = MySend.detectObstacleARDold == MySend.detectObstacleARD
            ARDprocheOK = MySend.detectObstacleARDprocheold == MySend.detectObstacleARDproche
            ARCOK = MySend.detectObstacleARCold == MySend.detectObstacleARC

            
            # detection obstacle proche dans ce cas on s'arrête
            if (MySend.detectObstacleAVG and AVGOK) or (MySend.detectObstacleAVD and AVDOK) or (MySend.detectObstacleAVCproche and AVCprocheOK) or (MySend.detectObstacleARGproche and ARGprocheOK) or (MySend.detectObstacleARDproche and ARDprocheOK) or (MySend.detectObstacleARC and ARCOK):
                self.move = 0
                self.enable = 0
                MySend.differentielD = False
                MySend.differentielG = False

            # cul de sac -> reculer
            elif (MySend.detectObstacleAVC and AVCOK) and (MySend.detectObstacleARG and ARGOK) and (MySend.detectObstacleARD and ARDOK):
                self.move = -1
                self.enable = 1
                MySend.differentielD = False
                MySend.differentielG = False

            # tourner a droite
            elif (MySend.detectObstacleAVC and AVCOK and ((MySend.detectObstacleARG and ARGOK) or (MySend.lastActionD and not(MySend.detectObstacleARD) and ARDOK))):
                self.move = 1
                self.enable = 1
                MySend.differentielD = True
                MySend.lastActionD = True
                MySend.lastActionG = False
                if (position_volant < VOL_DROIT-50):
                    self.turn = -1
                else:
                    self.turn = 0
                    
            #tourner à gauche
            elif (MySend.detectObstacleAVC and AVCOK and ((MySend.detectObstacleARD and ARDOK) or (MySend.lastActionG and not(MySend.detectObstacleARG) and ARGOK))):
                self.move = 1
                self.enable = 1
                MySend.differentielG = True
                MySend.lastActionD = False
                MySend.lastActionG = True
                if (position_volant > VOL_GAUCHE+50):
                    self.turn = 1
                else:
                    self.turn = 0
                                    
            # si pas d'obstacle on va tout droit
            else:
                self.move = 1
                self.enable = 1
                MySend.differentielD = False
                MySend.differentielG = False
                # permet de "rester droit"
                if (position_volant < VOL_CENTRE-50):
                    self.turn = 1
                elif (position_volant > VOL_CENTRE+50):
                    self.turn = -1
                else:
                    self.turn = 0
                    
            MySend.detectObstacleAVCold = MySend.detectObstacleAVC #pour l'instant on regarde que les obstacles en face
            MySend.detectObstacleAVDold = MySend.detectObstacleAVD
            MySend.detectObstacleAVGold = MySend.detectObstacleAVG
            MySend.detectObstacleAVCprocheold = MySend.detectObstacleAVCproche
            MySend.detectObstacleARDold = MySend.detectObstacleARD
            MySend.detectObstacleARDprocheold = MySend.detectObstacleARDproche
            MySend.detectObstacleARGold = MySend.detectObstacleARG
            MySend.detectObstacleARGprocheold = MySend.detectObstacleARGproche
            MySend.detectObstacleARCold = MySend.detectObstacleARC
            
            #------------------------------------------------- CALCUL COMMANDES ----------------------------------------------------
            
            if self.enable:
                cmd_turn = 50 + int(self.turn*50) | 0x80
                ##print(cmd_turn)
                if MySend.differentielD :
                    cmd_mv_droit = (60 - self.move*self.speed_cmd) | 0x80   #marche arrière
                    cmd_mv_gauche = (50 + self.move*self.speed_cmd) | 0x80
                elif MySend.differentielG:
                    cmd_mv_droit = (40 + self.move*self.speed_cmd) | 0x80   
                    cmd_mv_gauche = (50 - self.move*self.speed_cmd) | 0x80 #marche arrière
                else:
                    cmd_mv_droit = (50 + self.move*self.speed_cmd) | 0x80
                    cmd_mv_gauche = (50 + self.move*self.speed_cmd) | 0x80
            else:
                cmd_turn = 50 + int(self.turn*50) & ~0x80
                cmd_mv_droit = (50 + self.move*self.speed_cmd) & ~0x80
                cmd_mv_gauche = (50 + self.move*self.speed_cmd) & ~0x80
            
            #------------------------------------------------- ENVOI MESSAGE CAN ----------------------------------------------------
            if Lidar.leafStop==1:
                msg = can.Message(arbitration_id=MCM,data=[0, 0, 0,0,0,0,0,0],extended_id=False)
                self._is_running = False
            else:
                msg = can.Message(arbitration_id=MCM,data=[cmd_mv_gauche, cmd_mv_droit, cmd_turn,0,0,0,0,0],extended_id=False)
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


    #gauche
    msg = can.Message(arbitration_id=MCM,data=[0, 0, 0xE4,0,0,0,0,0],extended_id=False)
    bus.send(msg)
    time.sleep(0.75)
    msg = can.Message(arbitration_id=MCM,data=[0, 0, 0,0,0,0,0,0],extended_id=False)
    bus.send(msg)
    time.sleep(0.5)
    msg1=bus.recv()
    while not (msg1.arbitration_id == MS):
        msg1=bus.recv()
    VOL_GAUCHE = int.from_bytes(msg1.data[0:2], byteorder='big')

    bus = can.interface.Bus(channel='can0', bustype='socketcan_native')

    #droit
    msg = can.Message(arbitration_id=MCM,data=[0, 0, 0x80,0,0,0,0,0],extended_id=False)
    bus.send(msg)
    time.sleep(0.75)
    msg = can.Message(arbitration_id=MCM,data=[0, 0, 0,0,0,0,0,0],extended_id=False)
    bus.send(msg)
    msg2=bus.recv()
    time.sleep(0.5)
    while not(msg2.arbitration_id == MS):
        msg2=bus.recv()
    VOL_DROIT = int.from_bytes(msg2.data[0:2], byteorder='big')

    VOL_CENTRE = int((VOL_GAUCHE+VOL_DROIT)/2)

    print(VOL_DROIT)
    print(VOL_GAUCHE)
    print(VOL_CENTRE)


    newsend = MySend(bus)
    newsend.start()

    newsend.join()

