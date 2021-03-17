from sensor_T import *
import asyncio

sT = sensor_T(None)
T = sT.read()
print(T)
