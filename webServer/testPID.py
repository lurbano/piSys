import time
from uPID import *
from sensor_T import *

sensor = sensor_T()
pid = uPID(sensor)

pid.target(25)
# pid.turnOn()
# for i in range(10):
#     print(pid.read())
#     time.sleep(1)
# pid.turnOff()
print("done")
