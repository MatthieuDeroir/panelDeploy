from pymongo import MongoClient
from instructions import Instructions
from bson import ObjectId
from time import sleep
import datetime
import subprocess
import gpio
from config import ip, port, add, pi, time_before_update
from ping import ping
from telnet import telnet

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
               "cat /sys/class/thermal/thermal_zone0/temp", "sleep 15"]

# initialisation du PANEL pour post
PANEL = {"isOpen": False,
         "name": "Init",
         "screen": True,
         "online": True,
         "state": True,
         "temperature": 0,
         "index": 0,
         "date": datetime.datetime.utcnow()}

putPANEL = {"door_1": False,
            "door_2": False,
         "name": "Init",
         "screen": True,
         "online": False,
         "state": False,
         "temperature": 0,
         "index": 0,
         "date": datetime.datetime.utcnow()}

hasBeenDisconnected = False
bug = False
status = False
bug_count = 0

while (1):
    if bug_count > 0:
        bug_count -= 1
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")

    # to handle disconnection with server
    ping_value = ping(ip)
    telnet_value = telnet()
    while ping_value or not telnet_value:
        print(ping_value)
        if (ping_value or not telnet_value) and not hasBeenDisconnected:
            print('### DISCONNECTED FROM SERVER ###')
            print('### DISABLING SCREEN DISPLAY ###')
            process = subprocess.Popen(bashCommand[0].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            hasBeenDisconnected = True
            print('put request successful')
        elif not (ping_value and not telnet_value) and hasBeenDisconnected:
            print('### RECONNECTED TO SERVER ###')
            inst = db.instructions.find()
            hasBeenDisconnected = False
            updatedInstructions = db.instructions.find_one_and_update({"_id": ObjectId(inst[pi]["_id"])},
                                                                         {"$set":
                                                                              {'instruction': False}
                                                                          })
        ping_value = ping(ip)
        telnet_value = telnet()

    # collection fetching
    panelLogs, instructions, panels = db.panellogs, Instructions(db.instructions.find()), db.panels.find()

    print(panelLogs)
    print(instructions)
    print(panels)

    # fetching instructions into a class
    # getting panel measures
    # Temp function
    process = subprocess.Popen(bashCommand[2].split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print("temperature fetched")
    temperature = int(output) / 1000

    # fetching input from gpio ports
    door_1, door_2, online, button = gpio.update_input()

    # if test button on, force screen display for 15 seconds
    if button:
        turn_on_display = subprocess.Popen(bashCommand[1].split(), stdout=subprocess.PIPE)
        sleep_fifteen = subprocess.Popen(bashCommand[3].split(), stdout=subprocess.PIPE)
        turn_off_display = subprocess.Popen(bashCommand[0].split(), stdout=subprocess.PIPE)

    # printing results
    print("Door 1 :", door_1)
    print("Door 2 :", door_2)
    print("Power :", online)

    # checking if anything goes wrong
    if not (online) or (temperature >= 80):
        bug = True
    else:
        bug = False

    # put request to panel state
    if not ping_value or telnet_value:
        print('put request to panels collection')
        putPANEL = db["panels"].find_one_and_update(
            {"_id": ObjectId(panels[pi]['_id'])},
            {"$set":
                 {'state': status,
                  'temperature': temperature,
                  'door_1': not door_1,
                  'door_2': not door_2,
                  'screen': online,
                  'bug': bug,
                  'date': current_time},
             }, upsert=True
        )
        print('put request successful')

    # applying instructions
    if (instructions.table[pi]['instruction'] != panels[pi]['state']):
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
            if not ping_value or telnet_value:
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
            if not ping_value or telnet_value:
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
    if not bug:
        sleep(time_before_update)
    elif bug and bug_count is 0:
        bug_count = 60
        PANEL = {"door_1": putPANEL['door_1'],
                 "door_2": putPANEL['door_2'],
                 "name": putPANEL['name'],
                 "screen": putPANEL['screen'],
                 "online": putPANEL['online'],
                 "state": status,
                 "temperature": putPANEL['temperature'],
                 "index": putPANEL['index'],
                 "date": datetime.datetime.utcnow()}
