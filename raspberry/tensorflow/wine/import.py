import os

typeF = "feuille"
pat = "F:/studies/insa/projet/EasyLid/raspberry/"

total = 0
allRots = []
for file in os.listdir(pat+"outputs/"+typeF):
    file = os.path.join(pat+"outputs/"+typeF, file)
    file = open(file,"r")
    file = file.read()
    rotations = file.split("\n")
    allRots += rotations
    total += len(rotations)


print(str(total) + ' rotations')
print(str(len(allRots)) + ' rotations')
print(allRots[0][:-2])

i = 0
with open(typeF+'.csv', 'w') as f:
    for item in allRots:
        if item and not item.isspace():
            f.write("%s\n" % item[:-2])
        else:
            print('space in line '+str(i))
        i = i+1