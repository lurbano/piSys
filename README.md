# piSensors
Attaching using a Raspberry Pi as a data logger with different sensors:
1) DS18B20 temperature sensor using 1Wire

* Author: Lensyl Urbano
* https://montessorimuddle.org

# Wiring

## Temperature
Standard wiring diagram at: https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/

Components:
* 4.7 k Ohm or 10 K Ohm resistor

Pins:
* GPIO 4: 1Wire uses GPIO 4 by default.
** More details (and how to use other pins for 1Wire): https://pinout.xyz/pinout/1_wire#
* 3v3: for 3.3V power
* GND: ground


# Software: Set up Raspberry Pi SD Card

[Set up instructions](PI_SETUP.md)
* Use these [instructions](PI_SETUP.md) to install the operating system on your Pi and allow it to connect to your local network.

* [Optional]: You can set up the 1-Wire interface on the SD Card by adding the line `dtoverlay=w1-gpio` to the ***config.txt*** file. Or you can set it up when you connect the pi as described below:


# Set up Pi Interfaces
Once logged in to the pi:

## Enable Interfaces
run `raspi-config` and enable needed interfaces (see https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20):
```console
sudo raspi-config
```
Enable Interfaces
* 1-Wire for:
** Temperature sensor


## REBOOT pi
 ```console
sudo reboot
```


# Installing this software: 
From your home directory clone the github repository.
```console
git clone https://github.com/lurbano/piSensors.git
```

# Setting up Server
## Install Tornado Webserver

Setting up the tornado server used for Websockets
```console
sudo pip3 install tornado
```

### Starting server
Go to the folder *~/piSensors/webServer/* and run the command
```console
sudo python3 server.py
```

### The webpage
The webpage will be at the pi's ip address (which should be printed to the screen when you start the server) and on port 8060 so if your ip address is 192.168.1.234, open up your browser and go to:
> http://192.168.1.234:8060

### Starting up on boot
** IMPORTANT **: the directory with the files needs to be in the pi home directory (e.g. */home/pi/rpi-led-strip*) with this setup. You can change this but be sure to put the full path to the commands. (From: https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup)

EDIT */etc/rc.local* (the easy way)
```console
sudo nano /etc/rc.local
```

ADD THE LINE (before `exit 0` ).
```
sudo /usr/bin/python3 /home/pi/piSensors/webServer/server.py  2> /home/pi/rpi-led-strip/error.log &
```

Save and exit (Ctrl-S and Ctrl-X) and then restart the Pi from the command line:
```console
sudo reboot
```


### If you need to kill the server
* https://unix.stackexchange.com/questions/104821/how-to-terminate-a-background-process
```console
pgrep -a python3
```
* this will give you the process id, the name line of the command, and a number 'nnn'. Find the one that has 'python3 server.py'. To kill use:
```console
sudo kill nnn
```



# [EXAMPLE] Adding things to be controlled by the webpage
The code below shows the whole process for creating the Hello World button.

## Add hello world button
*webServer/templates/index.html*: Add HTML for a button (#hello) and a span (#HelloResponse) where we will put the response from the server.
```HTML
<input type="button" id="hello" value="Hello World">
<span id="HelloResponse"></span>
```

## Add javascript
To listen for when someone clicks the Hello World button:
*webserver/static/ws-client.js* near bottom of file
```js
$("#hello").click(function(){
    let msg = '{"what": "hello"}';
    ws.send(msg);
});
```

Here we're sending the dict {"what": "hello"} to the server.


## Have the server act
It has to figure out what to do when it gets the message: msg = {"what": "hello"} in *webserver/server.py*. the write_message method sends the dictionary object `{"info": "hello", "reply":r}` back to the browser (client).
```.py
			if msg["what"] == "hello":
				r = 'Say what?'
				self.write_message({"info": "hello", "reply":r})
```

## Update the webpage

Now we go back to the *webserver/static/ws-client.js* to add some code to deal with the response from the server. Inside the ws.onmessage function add:

```js
if (sData.info == 'hello'){
  r = sData.reply.toString();
  $("#HelloResponse").html(r);
}
```

# Other examples
The `Start Timer` button follows the same steps as the Hello World button, but in addition it:

1) Collects information from two other inputs (minutes and seconds)

2) Runs a timer function (`basicTimer`, which is imported from another file *basic.py*) asynchronously, so that it could be running but the server can still do other stuff.

3) *basic.py* has the code for the `basicTimer` function.

The `Reboot Pi` button shows you how you could live dangerously and run terminal commands from your python script to, in this case, reboot the Pi.

# Refs:
OLED:
* http://codelectron.com/setup-oled-display-raspberry-pi-python/
* https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi/usage

Temperature Sensor: DS18B20
* https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20
* https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/
