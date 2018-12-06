import serial

Numeros = ['"+33604414835"','"+33781565844"','"+33773123218"','"+33650142578"','"+33604468945"']
Noms = ["Valentine","Camille","Anass","Antoine","Gabriel"]

ser = serial.Serial('/dev/SMS',115200,rtscts=True,timeout=2)
print(ser.name)
buffer = ''
ser.write(b'ATE\r')
buffer = ser.read(6).decode("utf-8")
print(buffer)
ser.reset_input_buffer()

ser.write(b'AT+CPIN?\r')
buffer = ser.read(22).decode("utf-8")
print(buffer)
ser.reset_input_buffer()
if buffer != '\r\n+CPIN: READY\r\n\r\nOK\r\n':
	ser.write(b'AT+CPIN="0000"\r')
	buffer = ser.read(22).decode("utf-8")
	ser.reset_input_buffer()

while buffer != '\r\nOK\r\n':
	ser.write(b'AT\r')
	buffer = ser.read(6).decode("utf-8")
	ser.reset_input_buffer()

ser.write(b'AT+CMGF?\r')
buffer = ser.read(14).decode("utf-8")
print(buffer)
ser.reset_input_buffer()

if buffer != '\r\n+CMGF: 1\r\n':
	ser.write(b'AT+CMGF=1\r')
	buffer = ser.read(6).decode("utf-8")
	print(buffer)
	ser.reset_input_buffer()

while buffer != '\r\nOK\r\n':
	ser.write(b'AT\r')
	buffer = ser.read(6).decode("utf-8")
	print(buffer)
	ser.reset_input_buffer()

for i in range(5):
	num='AT+CMGS='+Numeros[i]+'\r'
	print(num)
	ser.write(bytes(num,"utf-8"))
	buffer = ser.read(10).decode("utf-8")
	print(buffer)
	ser.reset_input_buffer()
	msg='Hi '+Noms[i]+'! This message was sent automatically <3 <3.'
	print(msg)
	ser.write(bytes(msg,"utf-8")+bytes(chr(26),"utf-8")+b'\r')
	buffer = ser.read(10).decode("utf-8")
	print(buffer)
	ser.reset_input_buffer()

	while buffer != '\r\nOK\r\n':
		ser.write(b'AT\r')
		buffer = ser.read(6).decode("utf-8")
		print(buffer)
		ser.reset_input_buffer()
	print(i)
ser.close()
