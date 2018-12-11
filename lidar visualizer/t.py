import os
import sys
import math
from matplotlib import pyplot as plt

if(len(sys.argv) != 2):
	    sys.exit('arguments not respected\n t.py <file_name>')

fileName = sys.argv[1]
file = open(fileName,"r")
file = file.read()

rotations = file.split("\n");
#del rotations[-1]
choice = 0

while choice != -1:

	print("we detected",len(rotations),"rotations")
	choice = int(input())

	if choice >= 0 and choice < len(rotations):

		arr = rotations[choice].split(",")
		del arr[-1]

		arr.pop(0)
		x = []
		y = []
		i = 0

		for val in arr:
			x.append(math.sin(math.radians(i))*float(val)/10.0)
			y.append(math.cos(math.radians(i))*float(val)/10.0)
			i += 1

		plt.plot(x,y,'r.')

		plt.plot([0],[0],'bo')
		#20181207140853
		plt.title("displaying LIDAR\'s data that was recorded in "+fileName[4:6]+"/"+fileName[6:8]+'/'+fileName[:4]+" "+fileName[8:10]+":"+fileName[10:12]+":"+fileName[12:14])
		plt.xlabel("distance in centimeters")
		plt.ylabel("distance in centimeters")
		
		plt.show()

