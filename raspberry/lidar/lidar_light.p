from rplidar import RPLidar
import time
import sys
import signal

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()

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
 print('%d: Got %d measurments' % (i, len(scan)))

