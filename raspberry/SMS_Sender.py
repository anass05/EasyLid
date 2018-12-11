import serial

class SMS_Sender:
    
	def __init__(self, pin):
        
		self.pin=pin
		self.ser = serial.Serial('/dev/SMS',115200,rtscts=True,timeout=2)
		buffer = ''
		self.ser.write(b'ATE\r')
		buffer = self.ser.read(6).decode("utf-8")
		self.ser.reset_input_buffer()

		self.ser.write(b'AT+CPIN?\r')
		buffer = self.ser.read(22).decode("utf-8")
		self.ser.reset_input_buffer()
		if buffer != '\r\n+CPIN: READY\r\n\r\nOK\r\n':
			code_pin = 'AT+CPIN="'+pin+'"\r'
			self.ser.write(bytes(code_pin, "utf-8"))
			buffer = self.ser.read(22).decode("utf-8")
			self.ser.reset_input_buffer()

		while buffer != '\r\nOK\r\n':
			self.ser.write(b'AT\r')
			buffer = self.ser.read(6).decode("utf-8")
			self.ser.reset_input_buffer()
			
		self.ser.write(b'AT+CMGF?\r')
		buffer = self.ser.read(14).decode("utf-8")
		self.ser.reset_input_buffer()

		if buffer != '\r\n+CMGF: 1\r\n':
			self.ser.write(b'AT+CMGF=1\r')
			buffer = self.ser.read(6).decode("utf-8")
			self.ser.reset_input_buffer()


	def send(self,number,message):

		self.num='AT+CMGS="'+number+'"\r'
		self.ser.write(bytes(self.num,"utf-8"))
		buffer = self.ser.read(10).decode("utf-8")
		self.ser.reset_input_buffer()
        
		self.ser.write(bytes(message,"utf-8")+bytes(chr(26),"utf-8")+b'\r')
		buffer = self.ser.read(10).decode("utf-8")
		self.ser.reset_input_buffer()

	def __del__(self):
		self.ser.close()
