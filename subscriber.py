import paho.mqtt.client as mqtt
import time
import signal
import sys

def signal_handler(sig, frame):
    clientSubscribe.loop_stop()
    print("Exiting")
    sys.exit(0)

def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))


signal.signal(signal.SIGINT, signal_handler)
clientSubscribe = mqtt.Client("PlantReader")
clientSubscribe.connect("192.168.178.30") 

clientSubscribe.loop_start()
clientSubscribe.unsubscribe("#")
clientSubscribe.subscribe("PLANTNET/+")

clientSubscribe.on_message = on_message 
 
time.sleep(60)
clientSubscribe.loop_stop()