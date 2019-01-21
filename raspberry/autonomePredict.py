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
from SMS_Sender import SMS_Sender


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
    Messages reçus :
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
    
    Messages envoyés :
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
    obstacleAvantDroit = False
    obstacleAvantDroitOld = False
    obstacleAvantGauche = False
    obstacleAvantGaucheOld = False
    obstacleAvantCentre = False
    obstacleAvantCentreOld = False
    obstacleAvantCentreProche = False
    obstacleAvantCentreProcheOld = False
    # arriere voiture
    obstacleDroite = False
    obstacleDroiteOld = False
    obstacleDroiteProche = False
    obstacleDroiteProcheOld = False
    obstacleGauche = False
    obstacleGaucheOld = False
    obstacleGaucheProche = False
    obstacleGaucheProcheOld = False
    obstacleArriere = False
    obstacleArriereOld = False
    
    differentielD = False
    differentielG = False

    lastActionD = True
    lastActionG = False

    # distance max
    # avant voiture
    distanceobstacleAvantDroit = 30
    distanceobstacleAvantGauche = 30
    distanceobstacleAvantCentre = 150
    distanceobstacleAvantCentreProche = 30
    #arriere voiture
    distanceobstacleDroite = 75
    distanceobstacleDroiteProche = 20
    distanceobstacleGauche = 75
    distanceobstacleGaucheProche = 20
    distanceobstacleArriere = 30

    
    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus
        self.shutdown_flag = threading.Event()

    def run(self):
        self.speed_cmd = 30
        self.move = 0
        self.turn = 0
        self.enable = 0
        sms = SMS_Sender("0000")
        
        while not(self.shutdown_flag.is_set()):
            
            msg = self.bus.recv()
            #Ultrasons renvoient 0 par erreur, si jamais 0, valeur filtrée           
            #------------------------------------------------- LECTURE MESSAGE ----------------------------------------------------
            #ID 000
            if msg.arbitration_id == US1:
                
                # ultrason avant gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                if distance < MySend.distanceobstacleAvantGauche and distance > 0:
                    MySend.obstacleAvantGauche=True
                elif distance == 0:
                    None
                else:
                    MySend.obstacleAvantGauche=False
                
                # ultrason avant droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                if distance < MySend.distanceobstacleAvantDroit and distance > 0:
                    MySend.obstacleAvantDroit = True
                elif distance == 0:
                    None
                else:
                    MySend.obstacleAvantDroit = False
            
                # ultrason avant centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                # obstacle très proche à l'avant pour arrêt d'urgence
                if distance<MySend.distanceobstacleAvantCentreProche and distance > 0:
                    MySend.obstacleAvantCentreProche = True
                    MySend.obstacleAvantCentre = False
                # obstacle détecté à l'avant
                elif distance < MySend.distanceobstacleAvantCentre:
                    MySend.obstacleAvantCentre = True
                    MySend.obstacleAvantCentreProche = False
                elif distance == 0:
                    None 
                else:
                    MySend.obstacleAvantCentre = False
                    MySend.obstacleAvantCentreProche = False
            #ID 001        
            elif msg.arbitration_id == US2:
                
                # ultrason latéral gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                # obstacle très proche à gauche pour arrêt d'urgence
                if distance<MySend.distanceobstacleGaucheProche and distance > 0:
                    MySend.obstacleGaucheProche = True
                    MySend.obstacleGauche = False
                # obstacle détecté à gauche
                elif distance < MySend.distanceobstacleGauche:
                    MySend.obstacleGauche = True
                    MySend.obstacleGaucheProche = False
                elif distance == 0:
                    None 
                else:
                    MySend.obstacleGauche = False
                    MySend.obstacleGaucheProche = False

                
                # ultrason latéral droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                # obstacle très proche à droite pour arrêt d'urgence
                if distance<MySend.distanceobstacleDroiteProche and distance > 0:
                    MySend.obstacleDroiteProche = True
                    MySend.obstacleDroite = False
                # obstacle détecté à droite
                elif distance < MySend.distanceobstacleDroite:
                    MySend.obstacleDroite = True
                    MySend.obstacleDroiteProche = False
                elif distance == 0:
                    None 
                else:
                    MySend.obstacleDroite = False
                    MySend.obstacleDroiteProche = False
                
                
                # ultrason arriere centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                if distance < MySend.distanceobstacleArriere and distance > 0:
                    MySend.obstacleArriere = True
                elif distance == 0:
                    None
                else:
                    MySend.obstacleArriere = False       
            #ID 100 
            elif msg.arbitration_id == MS:
                # position volant
                position_volant = int.from_bytes(msg.data[0:2], byteorder='big')

            #------------------------------------------------- DETECTION OBSTACLE ----------------------------------------------------
            
            #verifie si deux détections d'affilée pour augmenter la fiabilité, éliminer une détection isolée
            AvantGaucheOK = MySend.obstacleAvantGaucheOld == MySend.obstacleAvantGauche
            AvantDroitOK = MySend.obstacleAvantDroitOld == MySend.obstacleAvantDroit
            AvantCentreOK = MySend.obstacleAvantCentreOld == MySend.obstacleAvantCentre
            AvantCentreProcheOK = MySend.obstacleAvantCentreProcheOld == MySend.obstacleAvantCentreProche
            GaucheOK = MySend.obstacleGaucheOld == MySend.obstacleGauche
            GaucheProcheOK = MySend.obstacleGaucheProcheOld == MySend.obstacleGaucheProche
            DroitOK = MySend.obstacleDroiteOld == MySend.obstacleDroite
            DroitProcheOK = MySend.obstacleDroiteProcheOld == MySend.obstacleDroiteProche
            ArriereCentreOK = MySend.obstacleArriereOld == MySend.obstacleArriere

            
            # detection obstacle proche dans ce cas on s'arrête
            if (MySend.obstacleAvantGauche and AvantGaucheOK) or (MySend.obstacleAvantDroit and AvantDroitOK) or (MySend.obstacleAvantCentreProche and AvantCentreProcheOK) or (MySend.obstacleGaucheProche and GaucheProcheOK) or (MySend.obstacleDroiteProche and DroitProcheOK) or (MySend.obstacleArriere and ArriereCentreOK):
                self.move = 0
                self.enable = 0
                MySend.differentielD = False
                MySend.differentielG = False

            # cul de sac -> reculer
            elif (MySend.obstacleAvantCentre and AvantCentreOK) and (MySend.obstacleGauche and GaucheOK) and (MySend.obstacleDroite and DroitOK):
                self.move = -1
                self.enable = 1
                MySend.differentielD = False
                MySend.differentielG = False

            # tourner a droite
            elif (MySend.obstacleAvantCentre and AvantCentreOK and ((MySend.obstacleGauche and GaucheOK) or (MySend.lastActionD and not(MySend.obstacleDroite) and DroitOK))):
                self.move = 1
                self.enable = 1
                MySend.differentielD = True
                MySend.lastActionD = True
                MySend.lastActionG = False
                #s'arrêter avant la butée du moteur
                if (position_volant < VOL_DROIT-50):
                    self.turn = -1
                else:
                    self.turn = 0
                    
            #tourner à gauche
            elif (MySend.obstacleAvantCentre and AvantCentreOK and ((MySend.obstacleDroite and DroitOK) or (MySend.lastActionG and not(MySend.obstacleGauche) and GaucheOK))):
                self.move = 1
                self.enable = 1
                MySend.differentielG = True
                MySend.lastActionD = False
                MySend.lastActionG = True
                #s'arrêter avant la butée du moteur
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
            #réactualisation des valeurs de détection d'obstacle    
            MySend.obstacleAvantCentreOld = MySend.obstacleAvantCentre
            MySend.obstacleAvantDroitOld = MySend.obstacleAvantDroit
            MySend.obstacleAvantGaucheOld = MySend.obstacleAvantGauche
            MySend.obstacleAvantCentreProcheOld = MySend.obstacleAvantCentreProche
            MySend.obstacleDroiteOld = MySend.obstacleDroite
            MySend.obstacleDroiteProcheOld = MySend.obstacleDroiteProche
            MySend.obstacleGaucheOld = MySend.obstacleGauche
            MySend.obstacleGaucheProcheOld = MySend.obstacleGaucheProche
            MySend.obstacleArriereOld = MySend.obstacleArriere
            
            #---------------------------- CALCUL COMMANDES ----------------------------------------------------
            
            if self.enable:
                #commande du volant
                cmd_turn = 50 + int(self.turn*50) | 0x80
                #commande des roues pour tourner à droite
                if MySend.differentielD :
                    cmd_mv_droit = (60 - self.move*self.speed_cmd) | 0x80   
                    cmd_mv_gauche = (50 + self.move*self.speed_cmd) | 0x80
                #commande des roues pour tourner à gauche
                elif MySend.differentielG:
                    cmd_mv_droit = (40 + self.move*self.speed_cmd) | 0x80   
                    cmd_mv_gauche = (50 - self.move*self.speed_cmd) | 0x80
                #commande des roues pour tout droit
                else:
                    cmd_mv_droit = (50 + self.move*self.speed_cmd) | 0x80
                    cmd_mv_gauche = (50 + self.move*self.speed_cmd) | 0x80
            else:
                cmd_turn = 50 + int(self.turn*50) & ~0x80
                cmd_mv_droit = (50 + self.move*self.speed_cmd) & ~0x80
                cmd_mv_gauche = (50 + self.move*self.speed_cmd) & ~0x80
            
            #------------------------------------------------- ENVOI MESSAGE CAN ----------------------------------------------------
            if Lidar.leafStop==1:
                print('SENDING AN SMS')
                msg = can.Message(arbitration_id=MCM,data=[0, 0, 0,0,0,0,0,0],extended_id=False)
                self.bus.send(msg)
                sms.send("+33781565844", "Oh no, there is a leaf on the LiDAR!")
                sys.exit()
            else if Lidar.startDetection:
                msg = can.Message(arbitration_id=MCM,data=[cmd_mv_gauche, cmd_mv_droit, cmd_turn,0,0,0,0,0],extended_id=False)
                self.bus.send(msg)