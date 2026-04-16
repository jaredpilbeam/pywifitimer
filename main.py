import os
import datetime
import subprocess

# Returns list of network devices for linux OS
def get_linux_devs():
    command = 'nmcli -t -f "DEVICE","TYPE","STATE","CONNECTION" d s'     
    try:
        output = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as cpe:
        output = cpe.output
    finally:
        return output
        
# Returns list of network devices for Windows OS
def get_win_devs():
    pass

# stores disconnection interval
class Interval:
    def __init__(self, start_time, end_time, day_of_month="", month="", year="",
                 day_of_week=""):
        self.day_of_month = day_of_month
        self.month = month
        self.year = year
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time

# stores network devices, their states and connections.
class NetworkDevice:
    def __init__(self, name, type, state, connection):
        self.name = name
        self.state = state
        self.type = type
        self.connection = connection if connection != "" else "none"


    def connect_device():
        pass
        
    def disconnect_device():
        pass

    def __str__(self):
        return f"""Name: {self.name} State: {self.state} Type: {self.type} 
        Connection: {self.connection} """
    
def main():
# hold list of Network Device Objects
    device_list= []

# for Linux OS, create Network Device Objects
    if os.name == "posix":
        for line in get_linux_devs().splitlines():
            split_line = line.decode().split(":")
            device = NetworkDevice(split_line[0],split_line[1],split_line[2],split_line[3])
            device_list.append(device)
        for value in device_list:
               print(value)

    elif os.name == "nt":
        get_win_devs()

if __name__=="__main__":
    main()