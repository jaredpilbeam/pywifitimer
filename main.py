import os
import sys
import datetime
import subprocess
import time
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QTabWidget, 
                             QFormLayout, QGridLayout, QLineEdit,QCheckBox, 
                             QTableWidget, QTableWidgetItem)
from PyQt6.QtGui import QIcon

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
        # command = "Get-NetAdapter | Format-list -Property "Name",
        #  "MediaConnectionState", "Status", "ifDesc"
        pass

class PyNetworkTimer(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.setWindowTitle("PyNetwork Timer")
        self.setWindowIcon(QIcon("placedholder_icon.jpg"))
        widget = QWidget()
        main_layout = QGridLayout()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        self.setGeometry(500, 500, 500, 500)

        tab = QTabWidget(self)
    
        test_page = QWidget(self)
        test_page_layout = QGridLayout()
        test_page.setLayout(test_page_layout)

# hold list of Network Device Objects
        device_list= []
        if os.name == "posix":
            for line in get_linux_devs().splitlines():
                split_line = line.decode().split(":")
                device = NetworkDevice(split_line[0],split_line[1],split_line[2],
                                   split_line[3])
                device_list.append(device)
                test_page_layout.addWidget(QCheckBox(text=split_line[0]))
        elif os.name == "nt":
            get_win_devs()

        test_page2 = QWidget(self)
        interval_testing = [[0,0,0,0,0,0],[0,0,0,0,0,0]]
        layout = QFormLayout()
        test_page2.setLayout(layout)
        table = QTableWidget()
        table.setRowCount(len(interval_testing))
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Start Time", "End time","Day","Month",
                                         "Year","Day of Week"])

        tab.addTab(test_page, "TEST")
        tab.addTab(test_page2, "TEST2")

        main_layout.addWidget(tab, 0,0,2,1)
        


    # Returns list of network devices for linux OS
  
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

    def connect(self):
            command = f"nmcli device connect {self.name}"
            subprocess.check_output(command, shell=True)
            print(f"Device {self.name} has been connected.")
            
    def disconnect(self):
            command = f"nmcli device disconnect {self.name}"
            subprocess.check_output(command, shell=True)
            print(f"Device {self.name} has been disconnected.")

    def populate_status_tab(self):
        test_page = QWidget(self)
        layout = QGridLayout()
        test_page.setLayout(layout)

    def __str__(self):
        return f"""Name: {self.name} State: {self.state} Type: {self.type} 
        Connection: {self.connection}"""
    

    # for Linux OS, create Network Device Objects
    

    interval = Interval("14:01","19:59","0","0","0","0")
    now = datetime.datetime.now()
    compare_start_time = now.replace(hour=
                                    int(interval.start_time.split(":")[0]),
                                    minute=
                                    int(interval.start_time.split(":")[1]))
    compare_end_time = now.replace(hour=
                                    int(interval.end_time.split(":")[0]),
                                    minute=
                                    int(interval.end_time.split(":")[1]))

                
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = PyNetworkTimer()
    window.show()
    app.exec()