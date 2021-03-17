import time
from uPID import *
from sensor_T import *

sensor = sensor_T()
pid = uPID(sensor)

for i in range(10):
    print(pid.read())
    time.sleep(1)
