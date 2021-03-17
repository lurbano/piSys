#! /usr/bin/python3

# From: https://www.hackster.io/dataplicity/control-raspberry-pi-gpios-with-websockets-af3d0c

import os.path
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import tornado.gen
import RPi.GPIO as GPIO
import time
import subprocess
import json
import sys
import argparse
import asyncio
#from numpy import arange, mean
import numpy as np

#from ledController import *
#from ledPixels import *
#from oledU import *
from basic import *

# TEMPERATURE SENSOR (1/2)
from sensor_T import *
sensor = None
# TEMPERATURE SENSOR (END)

# LEDs (1/2)
try:
	from ledPixels import *

	nPix = 20
	ledPin = board.D18

	# get number of pixels from the command line
	parser = argparse.ArgumentParser()
	parser.add_argument("-n", "--nPix", help = "Number of pixels")
	args = parser.parse_args()

	if args.nPix:
		try:
			nPix = int(args.nPix)
		except:
			print("using default (20) pixels: -nPix 20")
	ledPix = ledPixels(nPix, ledPin)
except:
	ledPix = False
print("ledPix:", ledPix)
# LED's (END)

#Tornado Folder Paths
settings = dict(
	template_path = os.path.join(os.path.dirname(__file__), "templates"),
	static_path = os.path.join(os.path.dirname(__file__), "static")
	)

#pyPath = '/home/pi/rpi-led-strip/pyLED/'

#Tonado server port
PORT = 8060

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		print ("[HTTP](MainHandler) User Connected.")
		self.render("index.html")


class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print ('[WS] Connection was opened.')
		self.write_message('{"who": "server", "info": "on"}')
		#self.oled = oledU(128,32)

		# LEDs
		if ledPix:
			self.write_message({"info": "LEDsActive", "active": "show", "nPix": nPix})
			print("LED's Active")
		else:
			self.write_message({"info": "LEDsActive", "active": "hide"})
			print("LED's Inactive")
		# LEDs (END)


	async def on_message(self, message):
		print ('[WS] Incoming on_message:', message)
		try:
			msg = json.loads(message)
			if msg["what"] == "server":
				if msg["opts"] == "off":
					sys.exit("Stopping server")

			# TEMPERATURE SENSOR (2/2)
			global sensor
			if msg["what"] == "checkS":
				if not sensor:
					sensor = sensor_T(self)
				asyncio.create_task(sensor.aRead())

			if msg["what"] == 'monitor':
				if not sensor:
					sensor = sensor_T(self)
				else:
					sensor.cancelTask()
				dt = float(msg['dt'])
				sensor.task = asyncio.create_task(sensor.aMonitor(dt))

			if msg["what"] == "logT":
				if not sensor:
					sensor = sensor_T(self)
				else:
					sensor.cancelTask()
				sensor = sensor_T(self)
				t = float(msg["t"])
				dt = float(msg["dt"])
				update = msg["update"]
				sensor.task = asyncio.create_task(sensor.aLog( t, dt, update))

			# TEMPERATURE SENSOR (END)

			# LEDs
			if msg["what"] == "LEDs":

				if msg["activate"]:
					if ledPix:
						nPix = msg["nPix"]
						print(f'Activating {nPix} neoPixels')
				else:
					print(f'Deactivating LEDs')

			if msg["what"] == "nPixSet":

				if ledPix:
					nPix = int(msg["nPix"])
					print(f'Activating {nPix} neoPixels')
					ledPix.clear()
					ledPix.nPixSet(nPix)
					ledPix.initCodeColor()



			# LEDs (END)



			if msg["what"] == "hello":
				r = 'Say what?'
				self.write_message({"info": "hello", "reply":r})

			if msg["what"] == "timer":
				m = float(msg["minutes"])
				s = float(msg["seconds"])
				task = asyncio.create_task(basicTimer(self, m, s))


			if msg["what"] == "reboot":
				subprocess.Popen('sleep 5 ; sudo reboot', shell=True)
				main_loop.stop()


		except Exception as e:
			print(e)
			print("Exception: Error with data recieved by server")
			print(message)


	def on_close(self):
		print ('[WS] Connection was closed.')


application = tornado.web.Application([
  (r'/', MainHandler),
  (r'/ws', WSHandler),
  ], **settings)


if __name__ == "__main__":
	try:
		http_server = tornado.httpserver.HTTPServer(application)
		http_server.listen(PORT)
		print("hello")
		main_loop = tornado.ioloop.IOLoop.instance()

		print ("Tornado Server started")

		# get ip address
		cmd = "hostname -I | cut -d\' \' -f1"
		IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
		print('IP: '+ IP +":" + str(PORT))
		#oled.write('IP: '+ IP, 3)
		cmd = 'iwgetid | sed \'s/.*://\' | sed \'s/"//g\''
		wifi = subprocess.check_output(cmd, shell=True).decode("utf-8")
		#oled.write(wifi, 2)
		print(wifi)


		main_loop.start()




	except:
		print ("Exception triggered - Tornado Server stopped.")

#End of Program
