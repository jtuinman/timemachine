import configparser
import os

from flask import Flask, render_template, jsonify

rpi_complete_mode = False
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    rpi_complete_mode = True
except Exception:
    GPIO = False

app = Flask(__name__)


### Flask methods
@app.route('/')
def hello_world():
    config.read(configfile)
    return config['DEFAULT']['debug']


##Init stuff
configfilename = "escape.conf"
configfile = (os.path.join(os.getcwd(), configfilename))    
config = configparser.ConfigParser()

app.run(debug=False,host="0.0.0.0",port=3000,threaded=True)
##app.run(debug=config.getboolean("Escape", "debug"),host="0.0.0.0",port=config.getint("Escape", "port"),threaded=True)