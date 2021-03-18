import json
import board
from digitalio import DigitalInOut, Direction
import asyncio
import time

defaultPidSettings = {
    "Kp": -1,
    "Ki": 0,
    "Kd": -100,
    "set": 25,
    "units": "°C",
    "dt": 5
}

class uPID:
    def __init__(self, sensor, server=None, pidDir='./pid/', relayPin=board.D26):
        self.pidDir = pidDir
        self.logDir = pidDir + "log/"
        self.logFile = self.logDir + "activeLog.dat"

        self.settings = defaultPidSettings

        self.settingsFile = pidDir + "settings.json"

        self.saveSettings()

        self.sensor = sensor
        self.server = server

        self.relayPin = relayPin
        self.power = DigitalInOut(self.relayPin)
        self.power.direction = Direction.OUTPUT
        self.power.value = False

    def target(self, val):
        self.target_value = val
        self.startTime = time.time()
        while True:
            T = self.read()
            dt = round((time.time()-self.startTime)/60, 1)
            print(f'{time.ctime(time.time())}: dt={dt}: {T}')
            if T < self.target_value:
                if self.power.value == False:
                    self.power.value = True
            else:
                if (self.power.value == True):
                    self.power.value = False
            time.sleep(12)

    async def aTarget(self, val):
        dt = 3
        self.target_value = val
        self.sensor.startTime = time.time()
        self.sensor.log = []
        self.sensor.timeLeft = 0
        #self.sensor.startTime = self.startTime
        self.runPID = True
        while self.runPID:
            m = await asyncio.gather(
                self.sensor.aRead( True, True, 'live'),
                asyncio.sleep(dt)
            )
            print(m)

    # def controller(self):
    #     while True:
    #         T = self.read()




    def turnOn(self):
        self.power.value = True

    def turnOff(self):
        self.power.value = False

    def read(self):
        return self.sensor.read()

    def log(self):
        pass


    def saveSettings(self):
        with open(self.settingsFile, "w") as f:
            f.write(json.dumps(self.settings))

    def readSettings(self):
        with open(self.settingsFile, "r") as f:
            self.settings = json.load(f)
