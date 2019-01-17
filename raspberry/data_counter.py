import os
import sys

if(len(sys.argv) != 2):
	    sys.exit('arguments not respected\n data_counter.py <anomaly type>')

#Récupère le nom du type de données à compter
typeF = sys.argv[1]


total = 0
#Lit toutes les lignes de tous les fichiers et compte le nombre données
for file in os.listdir("outputs/"+typeF):
    file = os.path.join("outputs/"+typeF, file)
    file = open(file,"r")
    file = file.read()
    rotations = file.split("\n")
    total += len(rotations)

print(str(total) + ' rotations')
