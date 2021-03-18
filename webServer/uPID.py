import json
# import RPi.GPIO as gpio
import board
from digitalio import DigitalInOut, Direction


defaultPidSettings = {
    "Kp": -1,
    "Ki": 0,
    "Kd": -100,
    "set": 30,
    "units": "°C",
    "dt": 5
}

class uPID:
    def __init__(self, sensor, pidDir='./pid/', relayPin=board.D26):
        self.pidDir = pidDir
        self.logDir = pidDir + "log/"
        self.logFile = self.logDir + "activeLog.dat"

        self.settings = defaultPidSettings

        self.settingsFile = pidDir + "settings.json"

        self.saveSettings()

        self.sensor = sensor

        self.relayPin = relayPin
        power = DigitalInOut(self.relayPin)
        power.direction = Direction.OUTPUT
        power.value = False
        # gpio.setwarnings(False)
        # gpio.setmode(gpio.BCM)
        # gpio.setup(self.relayPin, gpio.OUT)


    def turnOn(self):
        #gpio.output(self.relayPin, gpio.HIGH)
        power.value = True

    def turnOff(self):
        #gpio.output(self.relayPin, gpio.LOW)
        power.value = False

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
