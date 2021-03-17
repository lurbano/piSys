import time
import asyncio
from subprocess import Popen
import glob
import pprint

# TEMPERATURE SENSOR
class sensor_T:

    def __init__(self, server):

        #Thermometer setup
        Popen(['modprobe', 'w1-gpio'])
        Popen(['modprobe', 'w1-therm'])

        self.base_dir = '/sys/bus/w1/devices/'
        self.device_folder = glob.glob(self.base_dir + '28*')[0]
        self.device_file = self.device_folder + '/w1_slave'

        self.server = server
        self.log = []
        self.task = None
        self.taskType = None

    def cancelTask(self):
        print("Canceling last task.")
        if self.task:
            self.task.cancel()
            self.taskType = None

    def read(self):
        l_yes = False
        while (not l_yes):
            with open(self.device_file) as f:
                lns = f.readlines()
                if (lns[0].strip()[-3:] == 'YES'):
                    l_yes = True
                    equals_pos = lns[1].find('t=')
                    if equals_pos != -1:
                        T_str = lns[1][equals_pos+2:]
                        T_C = float(T_str) / 1000.0
                #print(lns[0])
                #print(lns[1])
            time.sleep(0.25)
        return T_C

    async def aRead(self, getTime=False, log=False, update="live"):
        l_yes = False
        while (not l_yes):
            with open(self.device_file) as f:
                lns = f.readlines()
                if (lns[0].strip()[-3:] == 'YES'):
                    l_yes = True
                    equals_pos = lns[1].find('t=')
                    if equals_pos != -1:
                        T_str = lns[1][equals_pos+2:]
                        T_C = float(T_str) / 1000.0
                #print(lns[0])
                #print(lns[1])
            await asyncio.sleep(0.01)

        message = {}
        message["S"] = T_C
        message["units"] = '°C'

        if getTime:
            message["t"] = time.ctime(time.time())
        if log:
            m = {"x": T_C, "t":round(time.time()-self.startTime, 4)}
            self.log.append(m)
            if update == "live":
                m['timeLeft'] = self.timeLeft
                m["info"] = "logUp"
                self.server.write_message(m)
        message["info"] = "S-one"
        self.server.write_message(message)
        return message

    async def aMonitor(self, dt):
        self.taskType = "monitor"
        print("monitor: dt=", dt)
        while 1:
            await asyncio.gather(
                asyncio.sleep(dt),
                self.aRead( True, False, 'live')
            )

    async def aLog(self, t, dt, update="live"):
        # self.log = logger("logT", t, dt, self.aRead, self)
        # data = await self.log.logData()

        self.timeLeft = t
        message = {}
        message["info"] = "logT"
        message['start'] = time.ctime(time.time())
        #message['logData'] = []
        self.startTime = time.time()

        self.log = []   #reset log

        while self.timeLeft >= 0:
            await asyncio.gather(
                asyncio.sleep(dt),
                self.aRead( True, True, update)
            )
            self.timeLeft -=dt

        message['logData'] = self.log
        if update != "live":
            self.server.write_message(message)
        #pprint.pprint(message)




class logger:
    def __init__(self, info, t, dt, readFunc, caller):
        self.info = info            # type of data: e.g. "logT"
        self.t = t                  # how long
        self.dt = dt                # timestep
        self.readFunc = readFunc    # function that reads the data from sensor
        self.caller = caller        # the instance that is using this logger

        self.timeLeft = t
        self.data = []

    async def logData(self):
        self.startTime = time.time()
        while self.timeLeft >= 0:
            await asyncio.gather(
                asyncio.sleep(dt),
                self.readFunc()
            )
