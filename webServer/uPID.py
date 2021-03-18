import json
import RPi.GPIO


defaultPidSettings = {
    "Kp": -1,
    "Ki": 0,
    "Kd": -100,
    "set": 30,
    "units": "°C",
    "dt": 5
}

class uPID:
    def __init__(self, sensor, pidDir='./pid/'):
        self.pidDir = pidDir
        self.logDir = pidDir + "log/"
        self.logFile = self.logDir + "activeLog.dat"

        self.settings = defaultPidSettings

        self.settingsFile = pidDir + "settings.json"

        self.saveSettings()

        self.sensor = sensor

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
