import configparser
import logging
import os
import sys

from flask import Flask, jsonify
import time
from escape_library import OutputPin, CaravanLoggingHandler

rpi_complete_mode = False
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    rpi_complete_mode = True
except Exception:
    GPIO = False


## Logger setup
logger = logging.getLogger(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
entriesHandler = CaravanLoggingHandler()
logger.addHandler(logging.StreamHandler())
logger.addHandler(entriesHandler)
logger.setLevel(logging.INFO)


app = Flask(__name__)

### Flask methods
@app.route('/')
def hello_world():
    return config['Escape']['port']

##switching an output pin to high or low
@app.route('/switch/<pinname>/<newstate>')
def flask_set_switch(pinname, newstate):
    logger.info(pinname)
    pin = outputpins[pinname]
    to_on = newstate == "1"
    logger.info("Got web request to turn pin " + pin.name + (" ON" if to_on else " OFF"))
    try:
        if to_on:
            pin.turn_on()
        else:
            pin.turn_off()
    except Exception as e:
        logger.error("Got exception trying to turn pin, " + str(e))
    return jsonify(result="ok")

##Init stuff
configfilename = "escape.conf"
configfile = (os.path.join(os.getcwd(), configfilename))    
config = configparser.ConfigParser()
try:
    with open(configfile,'r') as configfilefp:
        config.read_file(configfilefp)
except:
    print("Could not read " + configfile)
    sys.exit()


##Init all pins
fastenseatbeltlight = OutputPin(config.getint("Escape", "seatbeltlightpin"), "Fasten seatbelt light")
time.sleep(0.5)
magnet = OutputPin(config.getint("Escape", "magnetpin"), "Magnet")
time.sleep(0.5)
cabinet = OutputPin(config.getint("Escape", "cabinetpin"), "Cabinet")
time.sleep(0.5)
outputpins = {fastenseatbeltlight.name:fastenseatbeltlight, magnet.name:magnet, cabinet.name:cabinet}    

if rpi_complete_mode:
    logger.error("RPi found, running on Pi mode")
else:
    logger.error("RPi NOT found. Running in fake mode")

debug = config.getboolean("Escape", "debug")
if debug:
    logger.error("Running in debug mode, app will restart.")
    if rpi_complete_mode:
        logger.error("This might cause weird behaviour on the Pi, so please don't do that")

logger.error("Starting app complete")

app.run(debug=config.getboolean("Escape", "debug"),host="0.0.0.0",port=config.getint("Escape", "port"),threaded=True)