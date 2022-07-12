# MAIN LOOP CONFIG #
# VM IP
ip = '192.168.100.76'

# Database or API port
port = 27017

# Database url
add = 'mongodb://' + ip + ':' + str(port) + '/'

# Panel Index : 0 for Indret, 1 fort UB Aval, 2 for UB Amont
pi = 0

# Loop refresh rate
time_before_update = 1

# GPIO CONFIG #
# GPIO indexes
indexes = {
    'door_1': 2,
    'door_2': 3,
    'screen': 22,
    'led_1': 17,
    'led_2': 27
}
