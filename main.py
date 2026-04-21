import os
import sys
import datetime
import subprocess
import time
import threading
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

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

class PyNetworkTimer(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.setWindowTitle("PyNetwork Timer")
        self.setWindowIcon(QIcon("placedholder_icon.jpg"))

        self.setGeometry(500, 500, 452, 400)
        self.initUI()

    def initUI(self):
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        tab = QTabWidget(self)
        tab_layout = QGridLayout()
        tab.setLayout(tab_layout)
        status_page = QWidget(tab)
        status_page_layout = QGridLayout()
        status_page.setLayout(status_page_layout)
# hold list of Network Device Objects
        device_list= []
        if os.name == "posix":
            status_page_layout.addWidget(QLabel("Select Networks to Connect/Disconnect on schedule:"),0,0,1,3)
            i=1
            j=0
            for line in get_linux_devs().splitlines():
                split_line = line.decode().split(":")
                
                device = NetworkDevice(split_line[0],split_line[1],split_line[2],
                                   split_line[3])
                device_list.append(device)
                checkbox = QCheckBox(text=split_line[0])
                status_page_layout.addWidget(checkbox, i, j,
                                             alignment=Qt.AlignmentFlag.AlignLeft)
                i += 1
                if( i % 4 == 3):
                     j += 1
                     i = 1
                if(len(get_linux_devs().splitlines()) == 1):
                     status_page_layout.addWidget(QLabel(""), j, i, 1, 2)
                elif(len(get_linux_devs().splitlines()) == 2):
                    status_page_layout.addWidget(QLabel(""), j, i)
            status_page_layout.addWidget(QLabel(""))
            status_page_layout.setRowStretch((j+1),1)
            status_page_layout.addWidget(QLabel(QTime.currentTime().toString("hh:mm:ss")),j+2,0,1,2)
            schedule_on = QPushButton("Start Schedule")
            schedule_off = QPushButton("Stop Schedule")
            status_page_layout.addWidget(schedule_on,j+2,1)
            status_page_layout.addWidget(schedule_off,j+2,2)
            

        elif os.name == "nt":
            get_win_devs()

        schedule_page = QWidget(tab)
        interval_testing = []
        schedule_page_layout = QFormLayout()
        schedule_page.setLayout(schedule_page_layout)
        table = QTableWidget(schedule_page)
        table.setRowCount(len(interval_testing))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Start Time", "End time","Date","Day of Week"])
        schedule_page_layout.addWidget(table)
        add_button = QPushButton("Add Interval")
        remove_button = QPushButton("Remove Interval")
        add_button.clicked.connect(lambda: self.add_button_click(table, interval_testing))
        remove_button.clicked.connect(lambda: self.remove_button_click(table, interval_testing))
        schedule_page_layout.addWidget(remove_button)
        schedule_page_layout.addWidget(add_button)
        schedule_on.clicked.connect(lambda: self.schedule_on_click(table, interval_testing))
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
            
    def add_button_click(self, table, intervals):
         table.insertRow(table.rowCount())
         interval_dropdown = QComboBox()
         interval_dropdown.addItems(['Monday','Tuesday','Wednesday','Thursday',
                                    'Friday', 'Saturday', 'Sunday'])
         interval_date = QDateEdit(self)
         interval_date.editingFinished.connect(interval_date.update)
         for i in range(0,4):
            table.setItem((table.rowCount()-1), i, QTableWidgetItem())
            if i == 0:
                table.setCellWidget((table.rowCount()-1), i, QTimeEdit(self))
            elif i == 1:
                table.setCellWidget((table.rowCount()-1), i, QTimeEdit(self))
            elif i == 2:
                 table.setCellWidget((table.rowCount()-1), i, interval_date)
            elif i == 3:
                 table.setCellWidget((table.rowCount()-1), i, interval_dropdown)
         return intervals.append(["","","",""])
    
    def schedule_on_click(self, table, intervals):
        for i in range(0, table.rowCount()):
            for j in range(4):
                if(table.item(i,j) is None) :
                     intervals[i][j] = ""
                elif j in range(3):
                     intervals[i][j] = table.cellWidget(i,j).text()
                elif j == 3:
                     intervals[i][j] = table.cellWidget(i,j).currentText()
        print(intervals)
        self.schedule_run_loop()

    def schedule_run_loop(self):
         pass

    def schedule_off_click(self):
         pass

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
               
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = PyNetworkTimer()
    window.show()
    app.exec()
