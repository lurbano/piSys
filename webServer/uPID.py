import json
import board
from digitalio import DigitalInOut, Direction
import asyncio
import time
import neopixel

defaultPidSettings = {
    "relayPin": 26,
    "Kp": -1,
    "Ki": 0,
    "Kd": -100,
    "target": 25,
    "units": "°C",
    "dt": 5,
    "pidDir": './pid/',
    "logFileName": 'active.log',
    "isRunning": False
}
defaultPidSettings["logDir"] = defaultPidSettings["pidDir"] + "dataLogs/"

defaultPidSettings["logFile"] = defaultPidSettings["logDir"] + defaultPidSettings["logFileName"]

defaultPidSettings["settingsFile"] = defaultPidSettings["pidDir"] + "settings.json"

class uPID:
    def __init__(self, sensor, server=None, pidDir=defaultPidSettings["pidDir"], relayPin=board.D26, logFileName=defaultPidSettings["logFileName"]):

        self.settings = defaultPidSettings.copy()
        self.pidDir = pidDir
        self.logDir = self.settings["logDir"]
        self.logFile = self.settings["logFile"]
        self.settingsFile = self.settings["settingsFile"]

        #self.saveSettings()

        self.sensor = sensor
        self.server = server

        self.relayPin = relayPin
        self.power = DigitalInOut(self.relayPin)
        self.power.direction = Direction.OUTPUT
        self.power.value = False

        self.task = None

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

    async def aTarget(self, val, dt):
        self.target_value = val
        print(f"Target set: {self.target_value}")
        self.sensor.startTime = time.time()
        self.sensor.log = []
        self.sensor.timeLeft = 0
        #self.sensor.startTime = self.startTime
        self.runPID = True
        print(f'dt: {dt}')
        while self.runPID:
            m = await asyncio.gather(
                self.sensor.aRead( True, True, 'live'),
                asyncio.sleep(dt)
            )
            print(m[0]["S"])
            T = m[0]["S"]
            if T < self.target_value:
                if self.power.value == False:
                    self.power.value = True
            else:
                if (self.power.value == True):
                    self.power.value = False

    async def aTarget2(self, val, dt, ledPix=None):
        self.target_value = val
        print(f"Target set: {self.target_value}")
        self.startTime = time.time()
        self.log = []

        self.runPID = True
        print(f'dt: {dt}')
        ledPix.pixels[0] = (0, 0, 100)
        ledPix.pixels.show()

        while self.runPID:
            tstepInitial = time.time()
            T = await self.sensor.aRead_basic()
            print(T)
            if T < self.target_value:
                if self.power.value == False:
                    self.power.value = True
            else:
                if (self.power.value == True):
                    self.power.value = False

            if ledPix:
                if self.power.value:
                    ledPix.pixels[1] = (100, 0, 0)
                else:
                    ledPix.pixels[1] = (0, 100, 0)
                ledPix.pixels.show()

            msg = {}
            msg["info"] = "PidUp"
            msg["x"] = T
            msg["t"] = round(time.time()-self.startTime, 4)
            msg["on"] = self.power.value
            if self.server:
                self.server.write_message(msg)

            #self.logData(msg)

            print(msg)
            dmt = time.time() - tstepInitial
            timeLeft = dt - dmt
            if (timeLeft > 0):
                await asyncio.sleep(timeLeft)



    # def controller(self):
    #     while True:
    #         T = self.read()




    def turnOn(self):
        self.power.value = True

    def turnOff(self):
        self.power.value = False

    def read(self):
        return self.sensor.read()

    def logData(self, msg):
        #print(self.logFile)
        with open(self.logFile, "a") as f:
            f.write(f'{msg["t"]},{msg["x"]},{int(msg["on"])}\n')


    def saveSettings(self):
        with open(self.settingsFile, "w") as f:
            f.write(json.dumps(self.settings))

    def readSettings(self):
        with open(self.settingsFile, "r") as f:
            self.settings = json.load(f)


class pidController:
    def __init__(self, main_loop=None):
        self.main_loop = main_loop
        self.settings = defaultPidSettings.copy()
        self.readSettings()

    async def runPID(self, sensor, server,
               ledPix = None,
               target_val = None,
               dt = None):
        self.sensor = sensor
        self.server = server
        self.ledPix = ledPix

        if not target_val:
            self.target = float(self.settings["target"])
        else:
            self.target = float(target_val)

        if not dt:
            self.dt = float(self.settings['dt'])
        else:
            self.dt = float(dt)

        self.startTime = time.time()
        self.log = []

        self.runPID = True
        if self.ledPix:
            ledPix.pixels[0] = (0, 0, 100)
            ledPix.pixels.show()

        while self.runPID:
            await asyncio.gather(
                asyncio.sleep(self.dt),
                self.pidStep()
            )

        #self.pid = uPID(sensor, server)

    async def pidStep(self):
        tstepStart = time.time()
        T = await self.sensor.aRead_basic()
        print(T)

        if T < self.target:
            if self.power.value == False:
                self.power.value = True
        else:
            if (self.power.value == True):
                self.power.value = False

        if ledPix:
            if self.power.value:
                ledPix.pixels[1] = (100, 0, 0)
            else:
                ledPix.pixels[1] = (0, 100, 0)
            ledPix.pixels.show()

        msg = {}
        msg["info"] = "PidUp"
        msg["x"] = T
        msg["t"] = round(time.time()-self.startTime, 4)
        msg["on"] = self.power.value
        if self.server:
            self.server.write_message(msg)
        print(msg)

        # dmt = time.time() - tstepStart
        # timeLeft = dt - dmt
        # if (timeLeft > 0):
        #     await asyncio.sleep(timeLeft)



    async def getSettings(self):
        await self.writeSettings()
        for i in range(10):
            await asyncio.gather(
                asyncio.sleep(2),
                self.hello()
            )

    async def writeSettings(self):
        with open(self.settings["settingsFile"], "w") as f:
            f.write(json.dumps(self.settings))

    def readSettings(self):
        with open(self.settings["settingsFile"], "r") as f:
            sets = json.load(f)

        if sets["isRunning"]:
            print("loading existing settings")
            self.settings = sets

        print("Settings")
        print(self.settings)

        self.setRelayPin(self.settings["relayPin"])

        print("Settings Sets")

    def setRelayPin(self, n):
        pin = 'D' + str(n)
        self.relayPin = getattr(board, pin)
        self.power = DigitalInOut(self.relayPin)
        self.power.direction = Direction.OUTPUT
        self.power.value = False

    async def hello(self):
        print("hello")

# def getBoardPin(n):
#     pins ={
#         17: board.D17,
#         25: board.D25,
#         26: board.D26
#     }
#     return pins.get(n, f"Pin number ({n}) not in list (def getBoardPin(n)")

# pid_step = 0
# async def pidController():
#     for i in range(20):
#         m = await asyncio.gather(
#             print("hello"),
#             asyncio.sleep(1)
#         )
#
# class PIDClient:
#
#     def __inti__(self, main_loop):
#         #main_loop.add_callback(pidController)
#         a=1
