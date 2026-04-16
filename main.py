import os
import datetime
import subprocess

def main():
    if os.name == "posix":
        get_linux_devs()
    elif os.name == "nt":
        get_win_devs()

# Returns list of network devices for linux OS
def get_linux_devs():
    command = 'nmcli -t -f "DEVICE","TYPE","STATE","CONNECTION" d s'     
    try:
        output = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as cpe:
        output = cpe.output
    finally:
        for line in output.splitlines():
            device = line.decode().split(":")
            print(f"Device name: {device[0]}")
            print(f"Device type: {device[1]}")
            print(f"Device Status: {device[2]}")
            print(f"Device Connection: {device[3] if device[3] != 
                                        "" else "none"}")

# Returns list of network devices for Windows OS
def get_win_devs():
    pass

#print(os.name)
#print(datetime.datetime.now())


class network_device:
    
    def __init__(self, name, state, type, connection):
        name = self.name
        state = self.state
        type = self.type
        connection = self.connection

    def connect_device():
        pass
        
    def disconnect_device():
        pass

if __name__=="__main__":
    main()