import os

#folder/anomaly name
typeF = "normal"
pat = "F:/studies/insa/projet/EasyLid/raspberry/"

#Read all files and concatenate all roations in a single array called AllROts
#Each rotation has 360 point seperated by ',' that's why it's called a csv file..
total = 0
allRots = []
for file in os.listdir(pat+"outputs/"+typeF):
    file = os.path.join(pat+"outputs/"+typeF, file)
    file = open(file,"r")
    file = file.read()
    rotations = file.split("\n")
    allRots += rotations
    total += len(rotations)

#show how many rotation we have in total
print(str(total) + ' rotations')
print(str(len(allRots)) + ' rotations')
print(allRots[0][:-2])

#write all data we have in AllRots in a csv file
#sometimes we get empty lines in reading so we remove them
i = 0
with open(typeF+'.csv', 'w') as f:
    for item in allRots:
        if item and not item.isspace():
            f.write("%s\n" % item[:-2])
        else:
            print('space in line '+str(i))
        i = i+1