# from pymongo import MongoClient

from instructions import Instructions
from bson import ObjectId
from time import sleep
from datetime import datetime
import subprocess
# import gpio
from config import config
from ping import ping
import requests
import json
from req import *

# panel index
pi = 0

# change this variable to modify the time between each update
time_before_update = 1

#
print("Python app running\n"
      "Connected to API\nIP : " + config['ip'] + " \nPort : " + str(config['port']))

# init bash command for hdmi control
bashCommand = ["xrandr --output HDMI-1 --off", "xrandr --output HDMI-1 --auto",
               "cat /sys/class/thermal/thermal_zone0/temp"]

# init
data = {
    "isOpen": False,
    "name": "Init",
    "screen": True,
    "online": True,
    "state": True,
    "temperature": 0,
    "index": 0,
    "date": str(datetime.now())
}

hasBeenDisconnected = False
bug = False
status = False

headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

while (1):

    # to handle disconnection with server
    resp = ping(config.ip)
    print(resp)

    while resp:
        resp = ping(config.ip)
        if resp and not hasBeenDisconnected:
            print('### DISCONNECTED FROM SERVER ###')
            print('### DISABLING HDMI ###')
            process = subprocess.Popen(bashCommand[0].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            hasBeenDisconnected = True
        elif not resp and hasBeenDisconnected:
            print('### RECONNECTED TO SERVER ###')
            print('### ENABLING HDMI ###')
            process = subprocess.Popen(bashCommand[1].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            hasBeenDisconnected = False

    # collection fetching
    instructions = req("get", 'http://' + config['ip'] + str(config['port']) + '/instructions')
    panels = req("get", 'http://' + config['ip'] + str(config['port']) + '/panels')
    # fetching instructions into a class
    panelInst = Instructions(instructions.json())

    # getting panel measures
    # TODO: functions to get measures from panel instruments
    #
    # Temp function
    process = subprocess.Popen(bashCommand[2].split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    temperature = int(output) / 1000
    door_1, door_2, online = gpio.update_input()
    # printing results
    print("Door 1 :", door_1)
    print("Door 2 :", door_2)
    print("Les portes sont fermées" if door_1 and door_2 else "Au moins une porte est ouverte")
    print("Power :", online)

    # checking if anything goes wrong
    if not (door_1 and door_2) or not (online) or (temperature >= 80):
        bug = True
    else:
        bug = False
    print("Bug :", bug)

    # put request to panel state
    data = {'state': status,
            'temperature': temperature,
            'door_1': not door_1,
            'door_2': not door_2,
            'screen': online,
            'bug': bug,
            'index': 1 + pi,
            'date': str(datetime.now()),
            'name': panels.json()[pi]['name']
            },

    put = req("put", 'http://' + config['ip'] + str(config['port']) + '/panel/' +
              panels.json()[pi]['_id'], data, headers)


    # applying instructions
    if (panelInst.table[pi]['instruction'] != panels.json()[pi]['state']) or bug:
        if panelInst.table[pi]['instruction']:
            # script on
            print('### HDMI PORT ENABLED ###')
            process = subprocess.Popen(bashCommand[1].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            print(output, error)
            # updating old status with new instructions
            status = True
            data = {
                    'state': status,
                    'temperature': temperature,
                    'door_1': not door_1,
                    'door_2': not door_2,
                    'screen': online,
                    'bug': bug,
                    "index": pi + 1,
                    "date": str(datetime.now()),
                    "name": panels.json()[pi]['name']
                    },
            post = req("post", 'http://' + config['ip'] + str(config['port']) + '/panelLogs', json.dumps(data),
                       headers)
            # changing LED states
            gpio.change_output(status)
            # last log
        elif not panelInst.table[pi]['instruction']:
            # script off
            print('### HDMI PORT DISABLED ###')
            process = subprocess.Popen(bashCommand[0].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            print(output, error)
            # updating old status with new instructions
            status = False
            data = {
                    'state': status,
                    'temperature': temperature,
                    'door_1': not door_1,
                    'door_2': not door_2,
                    'screen': online,
                    'bug': bug,
                    "index": pi + 1,
                    "date": str(datetime.now()),
                    "name": panels.json()[pi]['name']
                    },
            post = req("post", 'http://' + config['ip'] + str(config['port']) + '/panelLogs', json.dumps(data),
                       headers)

            # changing LED states
            gpio.change_output(status)
    else:
        status = panels.json()[pi]['state']

    print("Status :", panels.json()[pi]['state'])

    # if bug:
    # postPANEL = panelLogs.insert_one(data).inserted_id
    # wait time before update
    sleep(time_before_update)
