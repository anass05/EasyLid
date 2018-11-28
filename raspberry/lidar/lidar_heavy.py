from rplidar import RPLidar
import time
import sys
print(str(sys.argv))

lidar = RPLidar('/dev/ttyUSB0')
path = 'outputs/test1'
outputFile = open(path,'w')

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)

time.sleep(5);
for i, scan in enumerate(lidar.iter_scans()):
 print('%d: Got %d measurments' % (i, len(scan)))
 outputFile.write(''.join(str(x) for x in scan))
 outputFile.write('\n')
 if i > 3:
  break

outputFile.close()
lidar.stop()
lidar.stop_motor()
lidar.disconnect()
