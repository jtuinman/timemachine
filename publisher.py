import paho.mqtt.client as mqtt
import time
import signal
import sys
import json

def signal_handler(sig, frame):
    clientSubscribe.loop_stop()
    print("Exiting")
    sys.exit(0)

def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))


signal.signal(signal.SIGINT, signal_handler)

clientPublish = mqtt.Client("TestPublish")
clientPublish.connect("192.168.178.30")


test = "lol"
message = {
        "timestamp": test
        }

jsonDump = json.dumps(message)
topic="PLANTNET/LIGHT"
clientPublish.publish(topic, jsonDump)
print(jsonDump)

test = "Ha!"
message = {
        "timestamp": test
        }

jsonDump = json.dumps(message)
topic="PLANTNET/LIGHT"
clientPublish.publish(topic, jsonDump)
print(jsonDump)

time.sleep(10)
clientPublish.loop_stop()