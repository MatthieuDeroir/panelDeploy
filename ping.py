import subprocess

def ping(host):
    command = ['ping', '-c', '1', '-t', '1', host]
    # timestr = re.compile("time=[0-9]+ms").findall(str(ping.communicate()[0]))
    # print(timestr)
    return subprocess.call(command)

