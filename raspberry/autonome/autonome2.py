# coding: utf-8
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
           
            st = ""

            if msg.arbitration_id == US1:
                # ultrason avant gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                print(distance)
                message = "UFL:" + str(distance) + ";"
                print(distance)
                if distance < 100:
                    MySend.detectObstacle=True
                # ultrason avant droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                message = "UFR:" + str(distance)+ ";"
                print(distance)
                if distance < 100:
                    MySend.detectObstacle=True
                # ultrason avant centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "URC:" + str(distance)+ ";"
                print(distance)
                print("------------------")
                if distance < 100:
                    MySend.detectObstacle=True
            '''elif msg.arbitration_id == US2:
                # ultrason arriere gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "URL:" + str(distance)+ ";"
                # ultrason arriere droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                message = "URR:" + str(distance)+ ";"
                # ultrason arriere centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "UFC:" + str(distance)+ ";"
            elif msg.arbitration_id == MS:
                # position volant
                angle = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "POS:" + str(angle)+ ";"
                # Niveau de la batterie
                bat = int.from_bytes(msg.data[2:4], byteorder='big')
                message = "BAT:" + str(bat)+ ";"
                # vitesse roue gauche
                speed_left = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "SWL:" + str(speed_left)+ ";"
                # vitesse roue droite
                # header : SWR payload : entier, *0.01rpm
                speed_right= int.from_bytes(msg.data[6:8], byteorder='big')
                message = "SWR:" + str(speed_right)+ ";"'''



            if MySend.detectObstacle:
                self.move = 0
                self.enable = 0
                print("send cmd move stop")
            else:
                print("send cmd move forward")
                self.move = 1
                self.enable = 1

                
            if self.enable:
                cmd_mv = (50 + self.move*self.speed_cmd) | 0x80
                cmd_turn = 50 + self.turn*20 | 0x80
            else:
                cmd_mv = (50 + self.move*self.speed_cmd) & ~0x80
                cmd_turn = 50 + self.turn*20 & 0x80   

            #if (st!=""):print(st)

            msg = can.Message(arbitration_id=MCM,data=[cmd_mv, cmd_mv, cmd_turn,0,0,0,0,0],extended_id=False)
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
