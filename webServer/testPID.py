from uPID import *
from sensor_T import *

sensor = sensor_T()
pid = uPID(sensor)

print(pid.read())
