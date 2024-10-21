# -*- coding: utf-8 -*-
"""
Created on Mon May  6 11:49:55 2024

@author: ANG
"""
# IMPORTS 
import time 
import sys
import math
import ANG_Flight_Recorder_v_0_5 as angflightrec
from PyQt5.QtWidgets import (
    QApplication, QPushButton, QVBoxLayout, QWidget, QLabel,
    QListWidget, QStackedWidget, QHBoxLayout, QMessageBox, QLineEdit, QTextEdit
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import (QObject, pyqtSignal, QTimer, Qt, QRunnable, 
                          QThreadPool, pyqtSlot)

class WorkerSignals(QObject):
    '''
    Class defines signals available from a running worker thread. Without this 
    the WorkerThread cannot send (emit) data to the main application. 
    
    Signals: 
        message_text : string data to send to main thread via emit(). 
    '''
    message_text = pyqtSignal(str) 

class WorkerThread(QRunnable):
    '''
    Worker thread class. Inherits from QRunnable to handler worker thread setup, 
    signals and wrap-up. 
    
    '''
    def __init__(self, _SM, _AQ, _AE, _TF, *args, **kwargs):
        super(WorkerThread, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.running = True
        self._SM = _SM 
        self._AQ = _AQ
        self._AE = _AE 
        self._TF = _TF
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.is_paused = False
        self.flight_dictionary = None
        self.ang_fnum = None
        
    @pyqtSlot()
    def run(self):
        '''
        Initialise the run function with passed args, kwargs. Iterates about 
        every 1 seconds. 
        ''' 
        # DO HEAVY LIFTING HERE 
        while self.running:
            time.sleep(1.0) 
            # Check if we are in a flight 
            self.in_flight = self.in_current_flight()
            # Get current flight number 
            # self.current_flight_num = angflightrec.get_flight_number(self._AQ)
            # Get last flight number in data directory 
            self.last_flight_num = angflightrec.get_last_flight_num()
            
            if self.is_paused:
                self.message_text = "RECORD PAUSED."
                self.signals.message_text.emit(self.message_text)
                continue  # Skip to the next iteration
                
            if not self.in_flight:
                self.message_text = "WAITING FOR FLIGHT..."
                self.signals.message_text.emit(self.message_text)
                # Reset flight dictionary since flight has ended
                self.flight_dictionary = None
                # Reset flight number since flight has ended
                self.ang_fnum = None
                continue  # Skip to the next iteration
    
            # At this point, we are in flight
            if self.flight_dictionary is None:
                # Start a new flight
                self.wait_loading(30)
                self.start_new_flight()
                self.emmit_header()
            else:
                # Continue recording flight data
                updated_dict = angflightrec.active_record(
                    self.flight_dictionary, self._AQ, self._TF, self.ang_fnum)
                self.emmit_header()

    def stop(self):
        '''
        Function signals for the thread to stop. 

        Returns
        -------
        None.

        '''
        self.running = False
        return 
    
    def wait_loading(self, int_load_time): 
        '''
        Function used to allow time to load. 

        Returns
        -------
        None.

        '''
        for i in range(int_load_time): 
            time.sleep(1)
            t_minus = int_load_time - i
            self.message_text = f"Loading: {t_minus}"
            self.signals.message_text.emit(self.message_text) 
        return
    
    def emmit_header(self):
        '''
        Function emits header to app.

        Returns
        -------
        None.

        '''
        if self.ang_fnum == None: 
            print("NO FLIGHT NUMBER")
        else: 
            try: 
                dir_str = f'./data/{self.ang_fnum}/{self.ang_fnum}_Flight_Header.pkl'
                self.header_data = angflightrec.load_data(dir_str)
                self.header_str = 'RECORDING:\n--FLIGHT HEADER--\n'
                for k,v in self.header_data.items(): 
                    self.header_str += str(k) + " : " + str(v) + "\n"
                self.message_text = self.header_str + f"\nRecording in Directory {dir_str}"
                self.signals.message_text.emit(self.message_text) 
            except FileNotFoundError as e: 
                # If the flight directory is absent the flight has not started yet 
                # or ATC assinged a flight number prematurely
                print('EMMIT HEADER WAITING...')
                # self.start_new_flight()
        return 
    
    def check_master_systems_on(self): 
        '''
        Function checks AVIONICS_MASTER_SWITCH and ELECTRICAL_MASTER_BATTERY. 
        If both on returns True. If both off returns False. Else returns False.

        Returns
        -------
        master_systems_on : Bool
            
        '''
        self.avionics_master_check = self._AQ.get("AVIONICS_MASTER_SWITCH")
        self.electrical_master_bat_check = self._AQ.get("ELECTRICAL_MASTER_BATTERY")
        if self.avionics_master_check == 0.0 and self.electrical_master_bat_check == 0.0:
            master_systems_on = False
        elif self.avionics_master_check == 1.0 and self.electrical_master_bat_check == 1.0:
            master_systems_on = True 
        else: 
            master_systems_on = False
        return master_systems_on
    
    def in_current_flight(self): 
        '''
        Function checks if currently in flight. The main menu default coordinates 
        signify that the flight has ended. 
        

        Returns
        -------
        in_current_flight : Bool
            If in flight True else False.

        '''
        curr_pos_lat = self._AQ.get("PLANE_LATITUDE")
        curr_pos_lon = self._AQ.get("PLANE_LONGITUDE")
        curr_pos_alt = self._AQ.get("PLANE_ALTITUDE")
        
        default_end_pos_lat = round(0.000407442168686809,4)
        default_end_pos_lon = round(0.01397450300629543,4)
        # default_end_pos_alt = round(3.276148519246465,4)
        
        in_current_flight = None 
        if (curr_pos_lat is not None and 
            curr_pos_lon is not None and 
            curr_pos_alt is not None):
            curr_pos_lat = round(curr_pos_lat,4)
            curr_pos_lon = round(curr_pos_lon,4)
            curr_pos_alt = round(curr_pos_alt,4)
        else: 
            self.in_current_flight()
            
        if (curr_pos_lat is not None and 
            curr_pos_lon is not None and 
            curr_pos_alt is not None and 
            curr_pos_lat == default_end_pos_lat and 
            curr_pos_lon == default_end_pos_lon and 
            curr_pos_alt < 50):
               in_current_flight = False
        else: 
            in_current_flight = True
            self.ang_fnum = angflightrec.get_last_flight_num()
        return in_current_flight
    
    def start_new_flight(self): 
        '''
        Starts new flight via creating a new flight directory for header 
        and flight data--in ./data directory. 

        Returns
        -------
        None.

        '''
        angflightrec.check_set_last_dir() 
        self.message_text = "Creating Flight Header..."
        self.signals.message_text.emit(self.message_text) 
        
        self.header_data = angflightrec.make_flight_header(self._AQ, self._TF)
        self.message_text = "Creating Flight Dictionary..."
        self.signals.message_text.emit(self.message_text) 
        self.flight_dictionary = angflightrec.get_flight_dictionary()
        self.current_flight_num = angflightrec.get_last_flight_num() # CURRENT FLIGHT NUMBER FROM DIR
        return 

class SimUtilsApp(QWidget):
    def __init__(self):
        super(SimUtilsApp, self).__init__()
        # SET APP FONT
        self.setFont(QFont('consolas',11))
        # INSTANTIATE THE LIST
        self.leftlist = QListWidget()
        self.leftlist.setMaximumSize(225,1000)
        # ADD ITEMS TO LIST
        self.leftlist.insertItem(0, 'Local Flight Record')
        self.leftlist.insertItem(1, 'Aircraft Shutdown Util')
        self.leftlist.insertItem(2, 'Aircraft Fast Travel')
        self.leftlist.insertItem(3, 'Repair and Refuel')
        self.leftlist.insertItem(4, 'ANG Sim Dashboard')
        self.leftlist.resize(50, 50)
        # INSTANTIATE LAYOUT USER INTERFACES AS WIDGETS
        self.stack0 = QWidget()
        self.stack1 = QWidget()
        self.stack2 = QWidget()
        self.stack3 = QWidget()
        self.stack4 = QWidget()
		# CALL THE STACKS
        self.stack0UI()
        self.stack1UI()
        self.stack2UI()
        self.stack3UI()
        self.stack4UI()
		# ADD STACKS TO MAIN STACK
        self.Stack = QStackedWidget (self)
        self.Stack.addWidget (self.stack0)
        self.Stack.addWidget (self.stack1)
        self.Stack.addWidget (self.stack2)
        self.Stack.addWidget (self.stack3)
        self.Stack.addWidget (self.stack4)
        self.Stack.setMaximumSize(800,800)
		# ADD SUBLAYOUT STACK/STACKS TO MAIN LAYOUT STACK
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.leftlist)
        hbox.addWidget(self.Stack, alignment=Qt.AlignTop)
        # STYLES AND CALL UI
        self.setLayout(hbox)
        self.setMinimumSize(300,200)
        self.leftlist.currentRowChanged.connect(self.display)
        self.switch = 0 # On/Off proper connect to SimConnect
        self.switch_rec = 0
        self.setWindowTitle('ANG MSFS 2020 Flight Data Recorder')
        self.show()
        # Create Threadpool
        self.threadpool = QThreadPool()
        
        def connect_to_sim(self): 
            '''
            Function checks that an instance of Microsoft Flight Simulator is running. 
            If no instance is running closes application with advice. 

            Returns
            -------
            None.

            '''
            try:
                # Create SimConnect link
                self._SM = angflightrec.connect_sm() # SimConnect()
                # Note the default _time is 2000 to be refreshed every 2 seconds
                self._AQ = angflightrec.connect_aq(self._SM) # AircraftRequests(self._SM, _time=2000)
                self._AE = angflightrec.connect_ae(self._SM) # AircraftEvents(self._SM)
                self._TF = angflightrec.connect_tf()
                self.switch = 1 # On/Off proper connect to SimConnect
                angflightrec.check_test_data_dir()
                angflightrec.check_test_csv_data_dirs()
            except ConnectionError:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("MSFS Not Detected...")
                msg.setText("Connection Error. Microsoft Flight Simulator Must Be Running.")
                x = msg.exec_()
                self.close()
                sys.exit(0)
            return 
        connect_to_sim(self)
        
    def stack0UI(self):
        # WRITE THE STACK FOR CONNECTING TO THE MySQL DB HERE
        # INSTATIATE THE UI 0 LAYOUT(S)
        layout = QVBoxLayout() 
        # INSTANTIATE WIDGETS 
        text_input_diag = QTextEdit()
        start_push_button = QPushButton('MYSQL CONNECT') 
        start_record_button = QPushButton('START LOCAL RECORD') 
        pause_record_button = QPushButton("PAUSE LOCAL RECORD")
        resume_record_button = QPushButton("RESUME LOCAL RECORD")
        self.header_switch = 0
        self.text_trigger_switch = 0
        self.worker_true = False
        # WIDGET STYLES
        text_input_diag.setReadOnly(True)
        text_input_diag.setStyleSheet("background-color: black; border: 1px solid green;")
        text_input_diag.setTextColor(QColor("green"))
        start_record_button.setStyleSheet("background-color: #64c851") # GREEN
        pause_record_button.setStyleSheet("background-color: #f42525") # RED
        resume_record_button.setStyleSheet("background-color: #FFFF00") # YELLOW
        # ADD WIDGETS TO LAYOUT
        layout.addWidget(text_input_diag)
        layout.addWidget(start_push_button)
        layout.addWidget(start_record_button)
        layout.addWidget(pause_record_button)
        layout.addWidget(resume_record_button)
        resume_record_button.hide()
        pause_record_button.hide()
        start_push_button.hide()
        # INSTANTIATE METHODS OF THE STACK
        def pause_flight_record(self): 
            '''
            Function pauses the flight recorder. 

            Returns
            -------
            None.

            '''
            pause_record_button.hide()
            resume_record_button.show()
            self.worker.is_paused = True
            text_input_diag.setText("RECORD PAUSE")
            return 
        
        def resume_flight_record(self): 
            '''
            Function resumes flight recorder. 

            Returns
            -------
            None.

            '''
            resume_record_button.hide()
            pause_record_button.show()
            self.worker.is_paused = False
            return
        
        def update_progress(self, str_value):
            '''
            Function is sent str_value from worker thread to display in app. 

            Parameters
            ----------
            str_value : String
                String value emitted from worker thread.

            Returns
            -------
            None.

            '''
            text_input_diag.clear()
            self.message_from_thread = str_value
            if self.message_from_thread.startswith('RECORDING'): 
                t = self.message_from_thread.split("\n")
                for i in t: 
                    text_input_diag.append(i)
            else: 
                text_input_diag.setText(str_value)
            return 
        
        def start_flight_record(self):
            '''
            Function starts flight recorder by instantiating an instance of 
            a worker thread which operates to record the flight.

            Returns
            -------
            None.

            '''
            start_record_button.hide()
            pause_record_button.show()
            self.worker = WorkerThread(self._SM, self._AQ, self._AE, self._TF) 
            self.worker.setAutoDelete(True)
            self.worker.signals.message_text.connect(lambda checked: update_progress(self, self.worker.message_text))
            self.worker_true = True
            self.threadpool.start(self.worker) 
            return
        
        # CONNECT METHODS TO WIDGETS 
        start_record_button.clicked.connect(lambda checked: start_flight_record(self))
        pause_record_button.clicked.connect(lambda checked: pause_flight_record(self)) 
        resume_record_button.clicked.connect(lambda checked: resume_flight_record(self)) 
        # APPLY THE STACK
        self.stack0.setLayout(layout)
		
    def stack1UI(self):
        # INSTATIATE THE UI 1 LAYOUT(S)
        layout = QVBoxLayout() 
        # INSTANTIATE WIDGETS
        start_push_button = QPushButton('Start All Aircraft Systems')
        stop_push_button = QPushButton('Stop All Aircraft Systems') 
        start_push_button.setStyleSheet("background-color: #64c851")
        stop_push_button.setStyleSheet("background-color: #f42525")
        # ADD WIDGETS TO LAYOUT
        layout.addWidget(QLabel('Buttons start/stop all systems include: \n'\
                                'ENGINE_AUTO_START\n'\
                                'TOGGLE_MASTER_BATTERY_ALTERNATOR\n'\
                                'TOGGLE_AVIONICS_MASTER'))
        layout.addWidget(start_push_button)
        layout.addWidget(stop_push_button) 
        
        # INSTANTIATE METHODS OF THE STACK
        def start_all_systems(self): 
            event_to_trigger = self._AE.find("ENGINE_AUTO_START")  
            event_to_trigger()
            toggle_master_batt_alternator = self._AE.find("TOGGLE_MASTER_BATTERY_ALTERNATOR")  
            toggle_master_batt_alternator()
            # TOGGLE_AVIONICS_MASTER
            toggle_avionics_mast = self._AE.find("TOGGLE_AVIONICS_MASTER")  
            toggle_avionics_mast()
            return 
        
        def stop_all_systems(self): 
            event_to_trigger = self._AE.find("ENGINE_AUTO_SHUTDOWN")  
            event_to_trigger()
            toggle_master_batt_alternator = self._AE.find("TOGGLE_MASTER_BATTERY_ALTERNATOR")  
            toggle_master_batt_alternator()
            toggle_avionics_mast = self._AE.find("TOGGLE_AVIONICS_MASTER")  
            toggle_avionics_mast()
            return 
        
        # CONNECT METHODS TO WIDGETS
        start_push_button.clicked.connect(lambda checked: start_all_systems(self))
        stop_push_button.clicked.connect(lambda checked: stop_all_systems(self))
        #APPLY THE STACK
        self.stack1.setLayout(layout)
		
    def stack2UI(self):
        # INSTATIATE THE UI 1 LAYOUT(S)
        layout = QVBoxLayout()
        # INSTANTIATE WIDGETS
        note_str = 'IMPORTANT: When using the fast travel utility:\n'\
                   '- Unstable utility use at your own risk.\n'\
                   '- Aircraft must be in flight.\n'\
                   '- Be mindful of the altitude (sometimes it will place you way too close to the ground.\n'\
                   '- Proper LAT/LON inputs are floats i.e. 43.63100084864455 -79.38926956621822\n'\
                   '- Be mindful that you do not fast travel youself into a building or mountain.\n'\
                   '- Be mindful of your destinations wheather conditions. Do not fast travel into a hurricane.\n'\
                   '- Flight time total will be lost (will not account for time it would have taken to fly).'
        
        text_note_label = QLabel(note_str)
        text_input_lat = QLineEdit() 
        text_input_lon = QLineEdit()
        text_input_alt = QLineEdit()
        start_push_button = QPushButton('GO')
        start_push_button.setStyleSheet("background-color: #FFFF00")
        # ADD WIDGETS TO LAYOUT
        layout.addWidget(text_note_label)
        layout.addWidget(QLabel("LAT:"))
        layout.addWidget(text_input_lat)
        layout.addWidget(QLabel("LON:"))
        layout.addWidget(text_input_lon)
        layout.addWidget(QLabel("ALT (FEET ABOVE GROUND):"))
        layout.addWidget(text_input_alt)
        layout.addWidget(start_push_button)
        # INSTANTIATE METHODS OF THE STACK
        def go_fast_travel(self): 
            fast_lat = text_input_lat.text()
            fast_lon = text_input_lon.text()
            fast_alt = text_input_alt.text()
            if fast_lat != '': 
                self._AQ.set("PLANE_LATITUDE", float(fast_lat))
            if fast_lon != '': 
                self._AQ.set("PLANE_LONGITUDE", float(fast_lon))
            if fast_alt != '': 
                self._AQ.set("PLANE_ALT_ABOVE_GROUND", float(fast_alt))
            return 
        
        # CONNECT METHODS TO WIDGETS
        start_push_button.clicked.connect(lambda checked: go_fast_travel(self))
        # APPLY THE STACK
        self.stack2.setLayout(layout)

    def stack3UI(self):
        # INSTATIATE THE UI 0 LAYOUT(S)
        layout = QVBoxLayout()
        # INSTANTIATE WIDGETS
        start_push_button = QPushButton('REPAIR_AND_REFUEL')
        monitor_label = QLabel('*** Fully repair and refuel current aircraft')
        start_push_button.setStyleSheet("background-color: #64c851") # GREEN
        # ADD WIDGETS TO LAYOUT
        layout.addWidget(monitor_label)
        layout.addWidget(start_push_button)
        # INSTANTIATE METHODS OF THE STACK
        def do_repair_and_refuel(self):
            event_to_trigger = self._AE.find("REPAIR_AND_REFUEL")  
            event_to_trigger() 
            return 
        # CONNECT METHODS TO WIDGETS
        start_push_button.clicked.connect(lambda checked: do_repair_and_refuel(self))
        # APPLY THE STACK
        self.stack3.setLayout(layout)
        
    def stack4UI(self):
        # INSTATIATE THE UI 0 LAYOUT(S) 
        layout = QVBoxLayout() 
        # INSTANTIATE WIDGETS 
        cb = QApplication.clipboard()
        start_push_button = QPushButton('Start ANG Sim Dashboard')
        stop_push_button = QPushButton('Stop ANG Sim Dashboard')
        copy_to_clip_button = QPushButton('Copy Lat/long to Clipboard')
        start_push_button.setStyleSheet("background-color: #64c851")
        stop_push_button.setStyleSheet("background-color: #f42525")
        copy_to_clip_button.setStyleSheet("background-color: #ff0000")
        lat_label = QLabel('...')
        lon_label = QLabel('...')
        alt_label = QLabel('...') 
        dis_to_targ = QLabel('...')
        monitor_label = QLabel('...')
        my_auto_pilot_button = QPushButton('AUTO HOLD')
        # ADD WIDGETS TO LAYOUT 
        layout.addWidget(start_push_button)
        layout.addWidget(stop_push_button)
        layout.addWidget(QLabel('PLANE_LATITUDE:'))
        layout.addWidget(lat_label)
        layout.addWidget(QLabel('PLANE_LONGITUDE:'))
        layout.addWidget(lon_label)
        layout.addWidget(copy_to_clip_button)
        layout.addWidget(QLabel('ALTITUDE (FEET FROM GROUND):'))
        layout.addWidget(alt_label)
        layout.addWidget(QLabel('GPS_WP_DISTANCE (KILOMETERS):'))
        layout.addWidget(dis_to_targ)
        # CHANGE STYLES 
        font_size_ = 40
        lat_label.setFont(QFont('Consolas', font_size_)) 
        lat_label.setStyleSheet("background-color: red; border: 1px solid black;")
        lon_label.setFont(QFont('Consolas', font_size_)) 
        lon_label.setStyleSheet("background-color: red; border: 1px solid black;")
        alt_label.setFont(QFont('Consolas', font_size_)) 
        alt_label.setStyleSheet("background-color: red; border: 1px solid black;")
        dis_to_targ.setFont(QFont('Consolas', font_size_)) 
        dis_to_targ.setStyleSheet("background-color: red; border: 1px solid black;")
        layout.addWidget(QLabel('SIM RATE:'))
        layout.addWidget(monitor_label)
        monitor_label.setFont(QFont('Consolas', font_size_)) 
        monitor_label.setStyleSheet("background-color: red; border: 1px solid black;")
        timer = QTimer()
        stop_push_button.hide()
        
        # INSTANTIATE METHODS OF THE STACK
        def radians_to_degrees(rads): 
            '''
            Function to convert Radians to Degrees. 

            Parameters
            ----------
            rads : Float
                Radians.

            Returns
            -------
            degrees : float
                Degrees.

            '''
            try: 
                degrees = rads * 180/math.pi
            except TypeError:
                degrees = -99999999999999.99
            return degrees
        
        def update_lat(): 
            '''
            Function updates Dashboard display latitude. 

            Returns
            -------
            None.

            '''
            lat = self._AQ.get("PLANE_LATITUDE")
            lat_label.setText(str(lat))
            return 
        
        def update_lon():
            '''
            Function updates Dashboard display longitude. 

            Returns
            -------
            None.

            '''
            lon = self._AQ.get("PLANE_LONGITUDE")
            lon_label.setText(str(lon))
            return 
        
        def update_alt_ground():
            '''
            Function updates Dashboard display altitude from ground. 

            Returns
            -------
            None.

            '''
            alt = self._AQ.get("PLANE_ALT_ABOVE_GROUND")
            alt_label.setText(str(alt))
            return 
        
        def update_dist_to_targ():
            '''
            Function updates Dashboard distance to next waypoint. 

            Returns
            -------
            None.

            '''
            try: 
                dis = self._AQ.get("GPS_WP_DISTANCE")
                dis_in_k = dis / 1000
                dis_to_targ.setText(str(dis_in_k))
            except TypeError:
                dis = -99999999999999.99
            return 
        
        def copy_lat_long_to_clip(self): 
            '''
            Function copies displayed latitude and longitude to clipboard. 

            Returns
            -------
            None.

            '''
            string_to_copy = f'{lat_label.text()}, {lon_label.text()}'
            cb.clear(mode=cb.Clipboard )
            cb.setText(string_to_copy, mode=cb.Clipboard)
            return 
        
        def start_sim_rate_mon(self):
            '''
            Function monitors sim rate and other variables and displays in the 
            app. Refreshes every 2.5 seconds. 

            Returns
            -------
            None.

            '''
            try: 
                if self.switch == 1: # On/Off proper connect to SimConnect
                    timer.start(2500)
                    # print("MONITOR START")
                    start_push_button.hide()
                    stop_push_button.show()
                else:  
                    stop_sim_rate_mon(self)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("MSFS Not Detected...")
                    msg.setText("Connection Error. Microsoft Flight Simulator Must Be Running.")
                    x = msg.exec_()
            except OSError: 
                timer.stop()
                monitor_label.setText('...')
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("MSFS Not Detected...")
                msg.setText("Microsoft Flight Simulator Must Be Running.")
                x = msg.exec_()
            return 
            
        def stop_sim_rate_mon(self): 
            '''
            Function will cease dashboard display and communication with Sim 
            Connect--connected to stop_push_button. 

            Returns
            -------
            None.

            '''
            timer.stop()
            print("MONITOR STOP")
            start_push_button.show()
            stop_push_button.hide()
            monitor_label.setText('...')
            lat_label.setText('...')
            lon_label.setText('...')
            alt_label.setText('...')
            dis_to_targ.setText('...')
            return 
        
        def every_second_while_pressed():
            '''
            Function runs every 2.5 seconds and updates ANG Sim Dashboard--
            connected to start_push_button. 

            Returns
            -------
            None.

            '''
            try:
                monitor_label.setText(str(self._AQ.get("SIMULATION_RATE"))) 
                update_lat()
                update_lon()
                update_alt_ground()
                update_dist_to_targ()
            except OSError: 
                timer.stop()
                monitor_label.setText('...')
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("MSFS Not Detected...")
                msg.setText("Microsoft Flight Simulator Must Be Running.")
                x = msg.exec_()
            return 
        
        # CONNECT METHODS TO WIDGETS
        start_push_button.clicked.connect(lambda checked: start_sim_rate_mon(self))
        stop_push_button.clicked.connect(lambda checked: stop_sim_rate_mon(self))
        copy_to_clip_button.clicked.connect(lambda checked: copy_lat_long_to_clip(self))
        timer.timeout.connect(every_second_while_pressed)
        # APPLY THE STACK 
        self.stack4.setLayout(layout)    
    
    def display(self,i):
       self.Stack.setCurrentIndex(i)
    
    def closeEvent(self, event):
        '''
        Function ensures the worker thread is closed on close of the application. 

        Parameters
        ----------
        event : Close Event.
            Is applied by app on close. 

        Returns
        -------
        None.

        '''
        print("Window closing...")
        # Perform cleanup tasks here
        print("Killing Thread...")
        if self.worker_true:
            self.worker.running = False

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion') 
    ex = SimUtilsApp()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
   main()
