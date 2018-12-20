import os
import sys

if(len(sys.argv) != 2):
	    sys.exit('arguments not respected\n data_counter.py <anomaly type>')

typeF = sys.argv[1]


total = 0
for file in os.listdir("outputs/"+typeF):
    file = os.path.join("outputs/"+typeF, file)
    file = open(file,"r")
    file = file.read()
    rotations = file.split("\n")
    total += len(rotations)

print(str(total) + ' rotations')