import serial

Numeros = ['"+33663073229"','"+3363583484"','"+33688770694"','"+33615707196"','"+33662562275"','"+33649867289"', '"+33675988393"', '"+33626362813"','"+33622855216"', '"+33768857259"', '"+33673486901"', '"+33782993005"', '"+33768255751"', '"+33659621072"', '"+33642859205"', '"+33604409859"', '"+33689213937"']
Noms = ["Mrs Chanthery","Mr Hladik","Mrs Moore","Yandika","Vincent", "Azzedine", "Baptiste", "Thibaud", "Aurelien", "Eunhwan", "Jonathan", "Ninni", "Abdelilah", "Amaury", "Tanguy", "David", "Christine"]

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

for i in range(17):
	num='AT+CMGS='+Numeros[i]+'\r'
	print(num)
	ser.write(bytes(num,"utf-8"))
	buffer = ser.read(10).decode("utf-8")
	print(buffer)
	ser.reset_input_buffer()
	msg='Hello '+Noms[i]+"! Welcome to this third review! Enjoy our amazing presentation. This message was sent from Team Tokyo's car."
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
