from rplidar import RPLidar
import time
import sys
import signal

isRunning = 1
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    isRunning = 0
    time.sleep(1)
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()
    sys.exit(0)

lidar = RPLidar('/dev/ttyUSB0')

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)
signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
#signal.pause()
time.sleep(5);
for i, scan in enumerate(lidar.iter_scans()):
 if isRunning == 0:
  print('breaking')
  break
 else:
  print('%d: Got %d measurments' % (i, len(scan)))

