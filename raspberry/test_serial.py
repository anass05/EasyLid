import serial
import sys
from time import sleep

ser = serial.Serial('/dev/ttyUSB0',115200,rtscts=True,timeout=2)
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

for i in range(20):
	ser.write(b'AT+CMGS="+33768857259"\r')
	buffer = ser.read(10).decode("utf-8")
	print(buffer)
	ser.reset_input_buffer()
	ser.write(b'Coucou '+bytes(str(i),"utf-8")+bytes(chr(26),'utf-8')+b'\r')
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
