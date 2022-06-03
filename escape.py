import configparser
import logging
import os
import pygame

from flask import Flask, render_template, jsonify
import time
import atexit
import sys
import re

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
    return 'Hello world'


##Init stuff
configfilename = "escape.conf"
configfile = (os.path.join(os.getcwd(), configfilename))
config = ConfigParser.SafeConfigParser()

app.run(debug=config.getboolean("Escape", "debug"),host="0.0.0.0",port=config.getint("Escape", "port"),threaded=True)