import subprocess, os
from config import port, backend_port, ip, frontend_port, timeout




def telnet():
    # telnet command to test different ports used by the server
    # grep -c return value greater than 0 if successful
    bdd = "{echo -e '\02~NH02';}  | timeout --signal=9 " + timeout + " telnet " + ip + " " + str(port) + " | " \
                                                                                            "(set -o pipefail && tee -a log.txt) | grep -c Connected"
    frontend = "{echo -e '\02~NH02';}  | timeout --signal=9 " + timeout + " telnet " + ip + " " + str(frontend_port) + " | " \
                                                                                                          "(set -o pipefail && tee -a log.txt) | grep -c Connected"
    backend = "{echo -e '\02~NH02';}  | timeout --signal=9 " + timeout + " telnet " + ip + " " + str(backend_port) + " | " \
                                                                                                        "(set -o pipefail && tee -a log.txt) | grep -c Connected"

    rbdd = subprocess.Popen(bdd.split(), stdout=subprocess.PIPE, shell=True)

    # reverse up and down value on linux
    up_value = 0
    down_value = 1

    if rbdd is up_value:
        print("Database return value : " + str(rbdd))
        print("Database port is responding. MongoDB is UP !")
    elif rbdd is down_value:
        print("ERROR")
        print("Database return value : " + str(rbdd))
        print("Database port is not responding. MongoDB is probably DOWN !")
    else:
        print("TIMEOUT")
        print("Database return value : " + str(rbdd))
        print("Database port is not responding. MongoDB is probably DOWN !")

    rfrontend = subprocess.Popen(frontend.split(), stdout=subprocess.PIPE, shell=True)

    if rfrontend is up_value:
        print("Frontend return value : " + str(rfrontend))
        print("Frontend port is responding. Frontend is UP !")
    elif rbdd is down_value:
        print("ERROR")
        print("Frontend return value : " + str(rfrontend))
        print("Frontend port is not responding. Frontend is probably DOWN !")
    else:
        print("TIMEOUT")
        print("Frontend return value : " + str(rfrontend))
        print("Frontend port is not responding. Frontend is probably DOWN !")

    rbackend = subprocess.Popen(backend.split(), stdout=subprocess.PIPE, shell=True)


    if rbackend is up_value:
        print("Backend return value : " + str(rbackend))
        print("Backend port is responding. Backend is UP !")
    elif rbackend is down_value:
        print("ERROR")
        print("Backend return value : " + str(rbackend))
        print("Backend port is not responding. Backend is probably DOWN !")
    else:
        print("TIMEOUT")
        print("Backend return value : " + str(rbackend))
        print("Backend port is not responding. Backend is probably DOWN !")

    error = rbdd or rfrontend or rbackend
    print(error)

    # if any of the return value is 1 meaning there is an error somewhere it returns 1
    return error


telnet()
