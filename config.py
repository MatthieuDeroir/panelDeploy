# MAIN LOOP CONFIG #
# Panel Index : 0 for Indret, 1 fort UB Aval, 2 for UB Amont
pi = 1

# VM IP
ip = '192.168.100.81'

# Database or API port
port = 27017

# Frontend port
frontend_port = 3000

# Backend port
backend_port = 4000

# Database url
add = 'mongodb://' + ip + ':' + str(port) + '/'

# Loop refresh rate
time_before_update = 1

# Time before port check timeout
timeout = '5'

# GPIO CONFIG #
# GPIO indexes
indexes = {
    'door_1': 4,
    'door_2': 17,
    'screen': 27,
    'led_1': 22,
    'led_2': 10,
    'button': 11
}

# Server side IP check config
# Indret network
ipIndret = '10.190.62.21'
panelIndret = '10.190.62.20'
routerIndret = '10.190.62.9'

# Aval network
ipAval = '10.190.60.21'
panelAval = '10.190.60.20'
routerAval = '10.190.60.9'

# Amont network
ipAmont = '10.190.61.21'
panelAmont = '10.190.61.20'
routerAmont = '10.190.61.9'

#! SHEBANG
shebang = "#!/bin/bash"

