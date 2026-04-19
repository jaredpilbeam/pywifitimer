import os
import sys
import datetime
import subprocess
import time
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QTabWidget, 
                             QFormLayout, QGridLayout, QCheckBox, QTableWidget, 
                             QTableWidgetItem, QPushButton)
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

        self.setGeometry(500, 500, 648, 500)
        self.initUI()

    def initUI(self):
        widget = QWidget()
        self.main_layout = QGridLayout()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)
        tab = QTabWidget(self)
        status_page = QWidget(self)
        status_page_layout = QGridLayout()
        status_page.setLayout(status_page_layout)
# hold list of Network Device Objects
        device_list= []
        if os.name == "posix":
            for line in get_linux_devs().splitlines():
                split_line = line.decode().split(":")
                device = NetworkDevice(split_line[0],split_line[1],split_line[2],
                                   split_line[3])
                device_list.append(device)
                status_page_layout.addWidget(QCheckBox(text=split_line[0]))
        elif os.name == "nt":
            get_win_devs()

        schedule_page = QWidget(self)
        interval_testing = []
        schedule_page_layout = QFormLayout()
        schedule_page.setLayout(schedule_page_layout)
        table = QTableWidget(schedule_page)
        table.setRowCount(len(interval_testing))
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Start Time", "End time","Day","Month",
                                         "Year","Day of Week"])
        schedule_page_layout.addWidget(table)
        add_button = QPushButton("Add Interval")
        remove_button = QPushButton("Remove Interval")
        start_test_button = QPushButton("TEST transfer to list of lists")
        add_button.clicked.connect(lambda: self.add_button_click(table, interval_testing))
        remove_button.clicked.connect(lambda: self.remove_button_click(table, interval_testing))
        start_test_button.clicked.connect(lambda: self.start_test_click(table, interval_testing))
        schedule_page_layout.addWidget(remove_button)
        schedule_page_layout.addWidget(add_button)
        schedule_page_layout.addWidget(start_test_button)
       
        tab.addTab(status_page, "Status")
        tab.addTab(schedule_page, "Schedule")
        self.main_layout.addWidget(tab, 0, 0, 2, 1)

    def remove_button_click(self,table, interval_testing):
        if(len(interval_testing) > 0 and table.currentRow() != -1):
            delete_rows_set = set()
            for item in table.selectedItems():
                delete_rows_set.add(item.row())
            delete_rows_list = list(delete_rows_set)
            delete_rows_list.sort()
            delete_rows_list.reverse()
            for i in delete_rows_list:
                 table.removeRow(i)
                 interval_testing.pop(i)
        else: 
             pass
            
    def add_button_click(self, table, interval_testing):
         table.insertRow(table.rowCount())
         for i in range(0,6):
              table.setItem((table.rowCount()-1), i, QTableWidgetItem(" "))
         return interval_testing.append(["","","","","",""])
    
    def start_test_click(self, table, interval_testing):
        for i in range(0, table.rowCount()):
            for j in range(0, 6):
                if(table.item(i,j) is None) :
                     interval_testing[i][j] = ""
                else:interval_testing[i][j] = table.item(i,j).text()

                     

   
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
        status_page = QWidget(self)
        layout = QGridLayout()
        status_page.setLayout(layout)

    def __str__(self):
        return f"""Name: {self.name} State: {self.state} Type: {self.type} 
        Connection: {self.connection}"""
    
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
