import configparser
import logging
import os
import sys

from flask import Flask, render_template, jsonify
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

## Constants
STATE_NORMAL = 10
STATE_KEYTIME = 11
STATE_AFTER_KEYTIME = 12
STATE_START = 13
readeable_states = {STATE_START:'Standby',STATE_NORMAL:'Entree',STATE_KEYTIME:'Badkamer',STATE_AFTER_KEYTIME:'Eindspel'}

app = Flask(__name__)


def state_machine_standby():
    global state
    state = STATE_START ## standby
    logger.info("Now going into state " + readeable_states[state])
    pin1.turn_off()
    pin2.turn_off()
    pin3.turn_off()
    pin4.turn_off()
    pin5.turn_off()
    pin6.turn_off()
    pin7.turn_off()
    pin8.turn_off()        

def state_machine_state1():
    global state
    state = STATE_NORMAL
    logger.info("Now going into state " + readeable_states[state])
    pin1.turn_off()
    pin2.turn_on()
    pin3.turn_off()
    pin4.turn_on()
    pin5.turn_off()
    pin6.turn_on()
    pin7.turn_off()
    pin8.turn_on()    

def state_machine_state2():
    global state
    state = STATE_KEYTIME
    logger.info("Now going into state " + readeable_states[state])
    pin1.turn_on()
    pin2.turn_on()
    pin3.turn_on()
    pin4.turn_on()
    pin5.turn_off()
    pin6.turn_off()
    pin7.turn_off()
    pin8.turn_off() 

def state_machine_finalstate():
    global state
    state = STATE_AFTER_KEYTIME
    logger.info("Now going into state " + readeable_states[state])
    pin1.turn_off()
    pin2.turn_off()
    pin3.turn_off()
    pin4.turn_off()
    pin5.turn_on()
    pin6.turn_on()
    pin7.turn_on()
    pin8.turn_on() 

### Flask methods
@app.route('/')
def hello_world():
    return render_template("index.html",
        outputpins = outputpins,
        refresh_state=config.getint("Escape", "refresh_browser_time"))
    ##return config['Escape']['port']

##switching an output pin to high or low
@app.route('/switch/<pinname>/<newstate>')
def flask_set_switch(pinname, newstate):
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

@app.route('/state')
def flask_state():
    outputpinstates = {pinname: pin.is_on for (pinname, pin) in outputpins.items()}
    return jsonify(state=readeable_states[state],
                   outputpins=outputpinstates,
                   logs=entriesHandler.get_last_entries()
                   )

@app.route('/state/<newstate>')
def flask_set_state(newstate):
    logger.info("Got web request for state " + newstate)
    if newstate == readeable_states[STATE_START]:
        state_machine_standby()
    elif newstate == readeable_states[STATE_NORMAL]:
        state_machine_state1()
    elif newstate == readeable_states[STATE_KEYTIME]:
        state_machine_state2()
    else:
        state_machine_finalstate()
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
pin1 = OutputPin(config.getint("Escape", "pin1"), "Pin1")
time.sleep(0.5)
pin2 = OutputPin(config.getint("Escape", "pin2"), "Pin2")
time.sleep(0.5)
pin3 = OutputPin(config.getint("Escape", "pin3"), "Pin3")
time.sleep(0.5)
pin4 = OutputPin(config.getint("Escape", "pin4"), "Pin4")
time.sleep(0.5)
pin5 = OutputPin(config.getint("Escape", "pin5"), "Pin5")
time.sleep(0.5)
pin6 = OutputPin(config.getint("Escape", "pin6"), "Pin6")
time.sleep(0.5)
pin7 = OutputPin(config.getint("Escape", "pin7"), "Pin7")
time.sleep(0.5)
pin8 = OutputPin(config.getint("Escape", "pin8"), "Pin8")
time.sleep(0.5)
outputpins = {pin1.name:pin1, pin2.name:pin2, pin3.name:pin3, pin4.name:pin4, pin5.name:pin5, pin6.name:pin6, pin7.name:pin7, pin8.name:pin8 }    


## Default setting is state_normal. By running reset we set all the switches in the correct
## order.
state_machine_standby()
state = STATE_START

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