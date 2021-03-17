import json

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

        self.settings = defaultPidSettings

        self.settingsFile = pidDir + "settings.json"

        self.saveSettings()


    def saveSettings(self):
        with open(self.settingsFile, "w") as f:
            f.write(json.dumps(self.settings))

    def readSettings(self):
        with open(self.settingsFile, "r") as f:
            self.settings = json.load(f)
