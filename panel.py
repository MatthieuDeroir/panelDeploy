from pymongo import MongoClient
from instructions import Instructions
from bson import ObjectId
from time import sleep
import datetime
import subprocess
import gpio
from config import ip, port, add, pi, time_before_update
from ping import ping


# TODO: replace with host VPN IP adress and Mongodb port when on RP
client = MongoClient(add)
print("connected to MongoDB")

# database connexion
db = client.portNS
print('Connected to Database portNS')
# db.authentificate = (user, password)

oldInstruction = ""

print("Python app running\n"
      "Connected to MongoDB\nIP : " + ip + " \nPort : " + str(port))

# init bash command for hdmi control
bashCommand = ["xset -display :0 dpms force off", "xset -display :0 dpms force on",
               "cat /sys/class/thermal/thermal_zone0/temp"]
#bashCommand = ["ls", "ls", "ls"]


# initialisation du PANEL pour post
PANEL = {"isOpen": False,
         "name": "Init",
         "screen": True,
         "online": True,
         "state": True,
         "temperature": 0,
         "index": 0,
         "date": datetime.datetime.utcnow()}

hasBeenDisconnected = False
bug = False
status = False

while (1):

    # to handle disconnection with server
    resp = ping(ip)
    while resp:
        resp = ping(ip)
        print(resp)
        if resp and not hasBeenDisconnected:
            print('### DISCONNECTED FROM SERVER ###')
            print('### DISABLING SCREEN DISPLAY ###')
            process = subprocess.Popen(bashCommand[0].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            hasBeenDisconnected = True
        elif not resp and hasBeenDisconnected:
            print('### RECONNECTED TO SERVER ###')
            print('### ENABLING SCREEN DISPLAY ###')
            process = subprocess.Popen(bashCommand[1].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            hasBeenDisconnected = False



    # collection fetching
    panelLogs, instructions, panels = db.panellogs, Instructions(db.instructions.find()), db.panels.find()
    
    print(panelLogs)
    print(instructions)
    print(panels)


    # fetching instructions into a class
    # getting panel measures
    # TODO: functions to get measures from panel instruments
    #
    # Temp function
    process = subprocess.Popen(bashCommand[2].split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print("temperature fetched")
    temperature = int(output) / 1000

    door_1, door_2, online = gpio.update_input()
    # printing results
    print("Door 1 :", door_1)
    print("Door 2 :", door_2)
    print("Power :", online)


    # checking if anything goes wrong
    if not (door_1 and door_2) or not (online) or (temperature >= 80):
        bug = True
    else:
        bug = False


    print("Bug :", bug)

    # put request to panel state
    print('put request to panels collection')
    putPANEL = db["panels"].find_one_and_update(
        {"_id": ObjectId(panels[pi]['_id'])},
        {"$set":
             {'state': status,
              'temperature': temperature,
              'door_1': not door_1,
              'door_2': not door_2,
              'screen': online,
              'bug': bug},
         }, upsert=True
    )
    print('put request successful')



    # applying instructions
    if (instructions.table[pi]['instruction'] != panels[pi]['state']) or bug:
        if instructions.table[pi]['instruction']:
            # script on
            print('### HDMI PORT ENABLED ###')
            process = subprocess.Popen(bashCommand[1].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            # print(output, error)
            # updating old status with new instructions
            status = True
            PANEL = {"door_1": putPANEL['door_1'],
                     "door_2": putPANEL['door_2'],
                     "name": putPANEL['name'],
                     "screen": putPANEL['screen'],
                     "online": putPANEL['online'],
                     "state": status,
                     "temperature": putPANEL['temperature'],
                     "index": putPANEL['index'],
                     "date": datetime.datetime.utcnow()}
            postPANEL = panelLogs.insert_one(PANEL).inserted_id
            # changing LED states
            gpio.change_output(status)
            # last log
            print('#################################')
            print('Last log :')
            for key, value in PANEL.items():
                print('---------------------------------')
                print(key, ":", value)
            print('#################################')
        elif not instructions.table[pi]['instruction']:
            # script off
            print('### HDMI PORT DISABLED ###')
            process = subprocess.Popen(bashCommand[0].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            # print(output, error)
            # updating old status with new instructions
            status = False
            PANEL = {"door_1": putPANEL['door_1'],
                     "door_2": putPANEL['door_2'],
                     "name": putPANEL['name'],
                     "screen": putPANEL['screen'],
                     "online": putPANEL['online'],
                     "state": status,
                     "temperature": putPANEL['temperature'],
                     "index": putPANEL['index'],
                     "date": datetime.datetime.utcnow()}
            postPANEL = panelLogs.insert_one(PANEL).inserted_id
            # changing LED states
            gpio.change_output(status)
            # last log
            print('#################################')
            print('Last log :')
            for key, value in PANEL.items():
                print('---------------------------------')
                print(key, ":", value)
            print('#################################')
    else:
        status = panels[pi]['state']

    print("Status :", panels[pi]['state'])



    # if bug:
    # postPANEL = panelLogs.insert_one(PANEL).inserted_id
    # wait time before update
    sleep(time_before_update)
