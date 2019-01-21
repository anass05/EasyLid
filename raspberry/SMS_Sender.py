import serial

class SMS_Sender:
    
	def __init__(self, pin):
        
		self.pin=pin
		
		#Initialise la communication série avec le module SMS
		#/dev/SMS est un raccourci vers le port USB du module SMS, cela est parametré dans un fichier .rules de /etc/udev/
		#Baudrate = 115200
		#Control de flux hardware activé
		self.ser = serial.Serial('/dev/SMS',115200,rtscts=True,timeout=2)
		buffer = ''
		#Désactive l'écho du module SMS
		self.ser.write(b'ATE\r')
		#Vide le buffer d'entrée de la liaison série
		buffer = self.ser.read(6).decode("utf-8")
		self.ser.reset_input_buffer()

		#Vérifie si le pin a été rentré
		self.ser.write(b'AT+CPIN?\r')
		buffer = self.ser.read(22).decode("utf-8")
		self.ser.reset_input_buffer()
		
		#Si ce n'est pas le cas, entre le code pin
		if buffer != '\r\n+CPIN: READY\r\n\r\nOK\r\n':
			code_pin = 'AT+CPIN="'+pin+'"\r'
			self.ser.write(bytes(code_pin, "utf-8"))
			buffer = self.ser.read(22).decode("utf-8")
			self.ser.reset_input_buffer()
		
		#Attends que le module SMS soit prêt à recevoir une nouvelle commande
		while buffer != '\r\nOK\r\n':
			self.ser.write(b'AT\r')
			buffer = self.ser.read(6).decode("utf-8")
			self.ser.reset_input_buffer()
			
		#Vérifie si le module SMS est en mode envoi de texte
		self.ser.write(b'AT+CMGF?\r')
		buffer = self.ser.read(14).decode("utf-8")
		self.ser.reset_input_buffer()

		#Si ce n'est pas le cas, le met en mode envoi de texte
		if buffer != '\r\n+CMGF: 1\r\n':
			self.ser.write(b'AT+CMGF=1\r')
			buffer = self.ser.read(6).decode("utf-8")
			self.ser.reset_input_buffer()


	def send(self,number,message):

		#Entre le numero auquel envoyer le message
		self.num='AT+CMGS="'+number+'"\r'
		self.ser.write(bytes(self.num,"utf-8"))
		buffer = self.ser.read(10).decode("utf-8")
		self.ser.reset_input_buffer()
        
        #Ecrit le message puis l'envoi
		self.ser.write(bytes(message,"utf-8")+bytes(chr(26),"utf-8")+b'\r')
		buffer = self.ser.read(10).decode("utf-8")
		self.ser.reset_input_buffer()

	def __del__(self):
		#Ferme la communication série
		self.ser.close()
