import os
import sys
from datetime import datetime
import subprocess
import time
import threading
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class PyNetworkTimer(QWidget):
# Initialize the primary window widget
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.setWindowTitle("PyNetwork Timer")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(452, 400)
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        self.schedule_running = False
        self.schedule_on = QPushButton("Start Schedule")
        self.schedule_off = QPushButton("Stop Schedule")
        self.device_list= []
        self.connection_state = False
        self.initUI()
# Initialize the UI
    def initUI(self):
        tab = QTabWidget(self)
        tab_layout = QGridLayout()
        tab.setLayout(tab_layout)
# Initialize the Status Page
        status_page = QWidget(tab)
        self.status_page_layout = QGridLayout()
        status_page.setLayout(self.status_page_layout)
        (self.status_page_layout.addWidget
            (QLabel("Select Network Device(s) to schedule:"),0,0))
        self.status_line = QLabel("Schedule not running")
# Populate the status page checkboxes based on available network devices      
        if os.name == "posix":
            self.populate_status_page(self.get_linux_devs())
        elif os.name == "nt":
            self.populate_status_page(self.get_win_devs())
 # Populate the schedule page       
        schedule_page = QWidget(tab)
        schedule_interval = []
        schedule_page_layout = QGridLayout()
        schedule_page.setLayout(schedule_page_layout)
        table = QTableWidget(schedule_page)
        table.setRowCount(len(schedule_interval))
        table.setColumnCount(4)
        (table.setHorizontalHeaderLabels
            (["Start Time", "End time","Date","Day of Week"]))
        schedule_page_layout.addWidget(table, 0,0,1,2)
        add_button = QPushButton("Add Interval")
        remove_button = QPushButton("Remove Interval")
        interval_type = QComboBox()
        interval_type.addItems(['Daily','Weekly','By Date'])
        (add_button.clicked.
         connect(lambda: self.add_button_click(table,
                                               schedule_interval,
                                               interval_type.currentText())))
        (remove_button.clicked.
            connect(lambda: self.remove_button_click(table, schedule_interval)))
        schedule_page_layout.addWidget(interval_type,1,0)
        schedule_page_layout.addWidget(add_button,1,1)
        schedule_page_layout.addWidget(remove_button,2,0,1,2)
        (self.schedule_on.clicked.
            connect(lambda: self.schedule_on_click(table, schedule_interval)))
        self.schedule_off.clicked.connect(lambda: self.schedule_off_click())
        tab.addTab(status_page, "Status")
        tab.addTab(schedule_page, "Schedule")
        self.main_layout.addWidget(tab, 0, 0, 2, 1)
# Update the list of devices to get updated connection statuses
    def update_devs(self):
        self.device_list = []
        if os.name == "posix":
            lines = self.get_linux_devs().splitlines()
        elif os.name == "nt":
            lines = self.get_win_devs().splitlines()
        for line in lines:
            split_line = line.decode().split(":")
            if (split_line[1] == "ethernet" or split_line[1] == "wifi"):
                device = NetworkDevice(split_line[0],split_line[1],
                        split_line[2])
                self.device_list.append(device)
# Remove interval button on schedule tab
    def remove_button_click(self,table, schedule_interval):
        if(len(schedule_interval) > 0 and table.currentRow() != -1):
            delete_rows_set = set()
            for item in table.selectedItems():
                delete_rows_set.add(item.row())
            delete_rows_list = list(delete_rows_set)
            delete_rows_list.sort()
            delete_rows_list.reverse()
            for i in delete_rows_list:
                 table.removeRow(i)
                 schedule_interval.pop(i)
# Add removal button on schedule tab       
    def add_button_click(self, table, intervals, interval_type_text):
        table.insertRow(table.rowCount())
        interval_dropdown = QComboBox()
        interval_dropdown.addItems(['Monday','Tuesday','Wednesday','Thursday',
                                    'Friday', 'Saturday', 'Sunday'])
        today = QDate.currentDate()
        interval_date = QDateEdit(self)
        interval_date.setDisplayFormat("MM/dd/yyyy")
        interval_date.setMinimumDate(today)
        interval_date.editingFinished.connect(interval_date.update)
        start_time = QTimeEdit(self)
        start_time.setTime(QTime().fromString("12:00 AM","h:mm AP"))
        end_time = QTimeEdit(self)
        end_time.setTime(QTime().fromString("12:01 AM","h:mm AP"))
        (start_time.timeChanged.
            connect(lambda: end_time.setMinimumTime(start_time.time())))
        (end_time.timeChanged.
            connect(lambda: start_time.setMaximumTime(end_time.time())))
        if interval_type_text == "Daily":
            for i in range(0,4):
                table.setItem((table.rowCount()-1), i, QTableWidgetItem())
                if i == 0:
                    table.setCellWidget((table.rowCount()-1), i, start_time)
                elif i == 1:
                    table.setCellWidget((table.rowCount()-1), i, end_time)
                elif i == 2 or 3:
                    table.removeCellWidget((table.rowCount()-1), i)
        elif interval_type_text == "By Date":
            for i in range(0,4):
                table.setItem((table.rowCount()-1), i, QTableWidgetItem())
                if i == 0:
                    table.setCellWidget((table.rowCount()-1), i, start_time)
                elif i == 1:
                    table.setCellWidget((table.rowCount()-1), i, end_time)
                elif i == 2:
                    table.setCellWidget((table.rowCount()-1), i, interval_date)
                elif i == 3:
                    table.removeCellWidget((table.rowCount()-1), i )
        elif interval_type_text == "Weekly":
            for i in range(0,4):
                table.setItem((table.rowCount()-1), i, QTableWidgetItem())
                if i == 0:
                    table.setCellWidget((table.rowCount()-1), i, start_time)
                elif i == 1:
                    table.setCellWidget((table.rowCount()-1), i, end_time)
                elif i == 2:
                    table.removeCellWidget((table.rowCount()-1), i)
                elif i == 3:
                    table.setCellWidget((table.rowCount()-1),
                                         i, 
                                         interval_dropdown )
        return intervals.append(["","","",""])
# Schedule start button on status page 
    def schedule_on_click(self, table, intervals):
        if self.schedule_running == True:
            return
        for i in range(0, table.rowCount()):
            for j in range(4):
                try:
                    if j in range(2):
                        intervals[i][j] = table.cellWidget(i,j).time()
                    elif j == 2:
                        intervals[i][j] = table.cellWidget(i,j).date()
                    elif j == 3:
                        intervals[i][j] = table.cellWidget(i,j).currentText()
                except AttributeError:
                     intervals[i][j] = ""
        self.schedule_thread = threading.Thread(target=self.schedule_run_loop,
                                                args=(intervals,))
        self.schedule_running = True
        self.schedule_thread.start()

    def day_of_week_encode(self, dow_number):
        match dow_number:
            case 1:
                return "Monday"
            case 2:
                return "Tuesday"
            case 3:
                return "Wednesday"
            case 4:
                return "Thursday"
            case 5:
                return "Friday"
            case 6:
                return "Saturday"
            case 7:
                return "Sunday" 
# main loop that runs on its own thread when schedule is started
    def schedule_run_loop(self, intervals):
        def schedule_interval_check(start_time,end_time):
            if now.time() >= start_time and now.time() < end_time:
                self.connection_state = True
                for checkbox in self.checkboxes:
                    for device in self.device_list:
                        try:
                            if os.name=="posix":
                                if checkbox.isChecked() and (checkbox.text()
                                      == device.type and device.connection 
                                          != "none"):
                                    device.disconnect_network(device.name)
                                if not checkbox.isChecked() and (checkbox.text()
                                      == device.type and device.connection !=
                                          "connected"):
                                    device.connect_network(device.name)

                            elif os.name=="nt":
                                if checkbox.isChecked() and (checkbox.text()
                                      == device.name and device.connection 
                                        != "none"):
                                    device.disconnect_network(device.name)
                                if not checkbox.isChecked() and (checkbox.text()
                                      == device.name and device.connection
                                          == "none"):
                                    device.connect_network(device.name)

                        except subprocess.CalledProcessError:
                            self.status_line.setText("""Error, Disconnection 
                                                     failed""")
                self.status_line.setText(f"""Disconnected. Next reconnection 
                                         at :{(end_time).toString("h:mm AP")}
                                        """)
                return self.connection_state 
            else: return
            
        while self.schedule_running != False:
            self.update_devs() 
            now = QDateTime.currentDateTime()
            current_dow = self.day_of_week_encode((now.date()).dayOfWeek())
            for interval in intervals:
                schedule_interval_check(interval[0],
                                        interval[1])
                if interval[2] == "" and interval[3] == "" and (self.connection_state
                      is True):
                    break
                elif interval[2] == "" and interval[3] != "" and (current_dow
                 == interval[3]) and self.connection_state is True:
                    break
                elif interval[2] != "" and interval[3] == "" and (now.date() 
                == interval[2]) and self.connection_state is True:
                    break  
            for device in self.device_list:
                if self.connection_state != True:
                    if device.connection == "none":
                        device.connect_network(device.name) 

                self.status_line.setText("Reconnected, waiting for next "
                "scheduled disconnection.")
        time.sleep(1)
# schedule stop button on status page
    def schedule_off_click(self):
        if self.schedule_running == False:
            return
        self.schedule_running = False
        self.schedule_thread.join()
        if os.name == "posix":
            self.update_devs()
        elif os.name == "nt":
            self.update_devs()
        for device in self.device_list:
            if device.connection == "none":
                device.connect_network(device.name)
        self.status_line.setText("Schedule not running")

    def populate_status_tab(self):
        status_page = QWidget(self)
        layout = QGridLayout()
        status_page.setLayout(layout)

    def get_linux_devs(self):
        command = 'nmcli -t -f "DEVICE","TYPE","STATE" d s'     
        try:
            output = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as cpe:
            output = cpe.output
        return output
            
    def get_win_devs(self):
        def get_windev_attribute(attribute):
            attribute_command = ("Get-NetAdapter | ForEach-Object {$_." + 
            f"{attribute}" + ".Trim()}")
            try:
                attribute_output = subprocess.check_output(["powershell",
                                                    "-Command",
                                                      attribute_command],
                                                      creationflags=0x08000000)
            except subprocess.CalledProcessError as cpe:
                attribute_output = cpe.attribute_output
            return attribute_output
        
        name_output = get_windev_attribute("ifDesc")
        type_output = get_windev_attribute("NdisPhysicalMedium")
        connection_output = get_windev_attribute("Status")
        if type_output == 9:
            type_output = "wifi"
        elif type_output == 14:
            type_output = "ethernet"
        else: 
            type_output = "other"
        if connection_output == "Up":
            connection_output = "connected"
        else: connection_output = "none"

        return name_output+":"+type_output+":"+connection_output
# populates the status page with checkboxes for each device  
    def populate_status_page(self,get_dev_func):
            if os.name == "posix":
                i=1
                j=0
                index = 0
                self.checkboxes=[]
                for line in get_dev_func.splitlines():
                    split_line = line.decode().split(":")
                    if (split_line[1] == "ethernet" or split_line[1] == "wifi"):
                        device = NetworkDevice(split_line[0],split_line[1],
                                        split_line[2])
                        self.device_list.append(device)
                        self.checkboxes.append(QCheckBox(text=split_line[1]))
                        self.checkboxes[index].setChecked(True)
                        (self.status_page_layout.
                         addWidget(self.checkboxes[index],
                                   i,
                                   j,
                                   alignment=Qt.AlignmentFlag.AlignLeft))
                        index += 1
                    i += 1
                    if( i % 4 == 3):
                        j += 1
                        i = 1
                    if(len(get_dev_func.splitlines()) == 1):
                        self.status_page_layout.addWidget(QLabel(""),
                                                            j,
                                                            i,
                                                            1,
                                                            2)
                    elif(len(get_dev_func.splitlines()) == 2):
                        self.status_page_layout.addWidget(QLabel(""), j, i)
                    self.status_page_layout.addWidget(self.status_line,j+6,0,1,4)
                    self.status_page_layout.addWidget(self.schedule_on,j+7,1,1,2)
                    self.status_page_layout.addWidget(self.schedule_off,j+7,3,1,2)

            elif os.name == "nt": 
                i=1
                j=0
                index = 0
                self.checkboxes=[]
                names, types, connections = get_dev_func
                names = (names.decode("utf-8")).splitlines()
                types = (types.decode("utf-8")).splitlines()
                connections = (connections.decode("utf-8")).splitlines()

                for k in range(0,len(names)):
                    if "Ethernet" in names[k] or "Wi-Fi" in names[k] :
                        device = NetworkDevice(names[k],
                                                types[k],
                                                  connections[k])
                        self.device_list.append(device)
                        self.checkboxes.append(QCheckBox(text=names[k]))
                        self.checkboxes[index].setChecked(True)
                        status_page_layout.addWidget(self.checkboxes[index], 
                                                     i, 
                                                     j,
                                                    alignment=(Qt.AlignmentFlag.
                                                               AlignLeft))
                        index += 1
                        i += 1
                    if( i % 4 == 3):
                        j += 1
                        i = 1
                    if(len(names) == 1):
                        status_page_layout.addWidget(QLabel(""), j, i, 1, 2)
                    elif(len(names) == 2):
                        status_page_layout.addWidget(QLabel(""), j, i)

                self.status_line = QLabel("Schedule not running")
                status_page_layout.setRowStretch((j+1),1)
                status_page_layout.addWidget(QLabel(""),j+2,1,5,4)
                status_page_layout.addWidget(self.status_line,j+6,0,1,4)
                status_page_layout.addWidget(schedule_on,j+7,1,1,2)
                status_page_layout.addWidget(schedule_off,j+7,3,1,2)

class NetworkDevice:
    def __init__(self, name, type, connection):
        self.name = name
        self.type = type
        self.connection = connection 
        if self.connection == "Disabled" or self.connection == "disconnected":
            self.connection = "none"

    def connect_network(self,name):
        if os.name == "posix":
            command = f"nmcli device connect {name}"
            subprocess.check_output(command, shell=True)

        elif os.name == "nt":
            command = f"Enable-NetAdapter -Name \"{name}\""
            subprocess.check_output(["powershell",
                                      "-ExecutionPolicy",
                                        "Bypass",
                                          "-Command",
                                            command],
                                            creationflags=0x08000000)
     
    def disconnect_network(self,name):
        if os.name == "posix":
            command = f"nmcli device disconnect {name}"
            subprocess.check_output(command, shell=True)

        elif os.name == "nt":
            command = f"Disable-NetAdapter -Name \"{name}\" -Confirm:$false "
            subprocess.check_output(["powershell",
                                      "-ExecutionPolicy",
                                        "Bypass",
                                          "-Command",
                                            command],
                                            creationflags=0x08000000)

    def __str__(self):
        return f"""Name: {self.name} Type: {self.type} 
        Connection: {self.connection}"""
# overriding the show function to start window in center of primary display         
def show(self):
    geo = self.frameGeometry()
    geo.moveCenter(self.mainWindow.geometry().center())
    geo.moveTop(self.mainWindow.geometry().top())
    self.move(geo.topLeft())
    super().show()

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = PyNetworkTimer()
    window.show()
    app.exec()