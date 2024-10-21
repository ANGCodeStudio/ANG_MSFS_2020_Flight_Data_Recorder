# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 11:52:44 2024

@author: ANG
"""
# IMPORTS
import math 
import os 
import glob
import pickle 
import pytz
import timezonefinder 
import shutil 
from datetime import datetime
from SimConnect import SimConnect, AircraftEvents, AircraftRequests

def connect_sm():
    # Create SimConnect link
    _SM = SimConnect()
    return _SM

def connect_aq(_SM):
    # Note the default _time is 2000 to be refreshed every 2 seconds
    _AQ = AircraftRequests(_SM, _time=2000)
    return _AQ

def connect_ae(_SM): 
    _AE = AircraftEvents(_SM)
    return _AE

def connect_tf(): 
    _TF = timezonefinder.TimezoneFinder()
    return _TF

'''
_SM = connect_sm()
_AQ = connect_aq(_SM)
_AE = connect_ae(_SM)
_TF = connect_tf() 
'''

def check_test_data_dir(): 
    print('Check data dir exist...')
    os.makedirs('data', exist_ok=True)
    return 

def check_test_csv_data_dirs():
    print('Check data csv dirs exist...')
    os.makedirs('data_csv', exist_ok=True)
    os.makedirs('data_csv/flight_data', exist_ok=True)
    os.makedirs('data_csv/flight_headers', exist_ok=True)
    return 

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
    degrees = rads * 180/math.pi
    return degrees

def get_last_flight_num(): 
    '''
    Function gets next flight num for the ./data/ directory. 

    Returns
    -------
    latest_file : String.
        Gets last flight number from ./data/.

    '''
    list_of_files = glob.glob('./data/*') # * means all if need specific format then *.csv
    latest_file = None
    if len(list_of_files) == 0:
        # latest_file = '000000'
        latest_file = 'f0'
    else: 
        latest_file = max(list_of_files, key=os.path.getctime).split('\\')[-1]
    return latest_file

def check_flight_number(str_flight_num):
    list_of_files = glob.glob('./data/*') # * means all if need specific format then *.csv
    curr_flight_nums_in_dir = []
    for i in list_of_files: 
        curr_flight_nums_in_dir.append(i.split('\\')[-1])
    if str_flight_num in curr_flight_nums_in_dir: 
        is_in_dir = True
    else: 
        is_in_dir = False 
    return is_in_dir

def get_local_time_stamp(_AQ, _TF): 
    '''
    Function gets local time stamp depending where the current flights lat and 
    lon. 

    Returns
    -------
    timestamp: String
        String timestamp.

    '''
    long = _AQ.get("PLANE_LONGITUDE")
    lat = _AQ.get("PLANE_LATITUDE")
    try: 
        if type(lat) != float: 
            lat = _AQ.get("PLANE_LONGITUDE")
            
        if type(long) != float: 
            long = _AQ.get("PLANE_LATITUDE")
            
        timezone_str = _TF.certain_timezone_at(lat=round(lat,10), 
                                               lng=round(long,10)) 
        timezone = pytz.timezone(timezone_str)
        dt = datetime.utcnow()
        timestamp = dt + timezone.utcoffset(dt)
    except:
        print("Retry time stamp time stamp.")
        timestamp = get_local_time_stamp(_AQ,_TF)
        
    return timestamp

def get_start_flight_data(_AQ, _TF, fnum): 
    '''
    Data here is used to build a header data for the flight. 

    Returns
    -------
    None.

    '''
    header_dict = {"LOCAL_TIME":get_local_time_stamp(_AQ, _TF),
                   "ANG_FLIGHT_NUMBER":fnum,
                   "ATC_FLIGHT_NUMBER":_AQ.get("ATC_FLIGHT_NUMBER"),
                   "ATC_TYPE":_AQ.get("ATC_TYPE"),
                   "ATC_MODEL":_AQ.get("ATC_MODEL"),
                   "TOTAL_WEIGHT":_AQ.get("TOTAL_WEIGHT"), # In Pounds 
                   "ENGINE_TYPE":_AQ.get("ENGINE_TYPE"),
                   "NUMBER_OF_ENGINES":_AQ.get("NUMBER_OF_ENGINES"),
                   "PLANE_LATITUDE":_AQ.get("PLANE_LATITUDE"),
                   "PLANE_LONGITUDE":_AQ.get("PLANE_LONGITUDE"),
                   "PLANE_ALTITUDE":_AQ.get("PLANE_ALTITUDE"),
                   "PLANE_ALT_ABOVE_GROUND":_AQ.get("PLANE_ALT_ABOVE_GROUND"), # Feet from ground
                   "DESTINATION_LAT":_AQ.get("GPS_WP_NEXT_LAT"),
                   "DESTINATION_LON":_AQ.get("GPS_WP_NEXT_LON"),
                   "DESTINATION_ALT":_AQ.get("GPS_WP_NEXT_ALT"), 
                   "FUEL_TOTAL_QUANTITY":_AQ.get("FUEL_TOTAL_QUANTITY") # In Gallons
                   } 
    return header_dict

def get_flight_data(flight_dict, _AQ, _TF):
    '''
    Data here is monitored throughout the flight and stored 
    in a dictionary. 
    
    Returns
    -------
    None.

    '''
    flight_dict["LOCAL_TIME"].append(get_local_time_stamp(_AQ, _TF))
    flight_dict["AIRSPEED_TRUE"].append(_AQ.get("AIRSPEED_TRUE")) # In Knots
    flight_dict["GROUND_VELOCITY"].append(_AQ.get("GROUND_VELOCITY")) # In Knots
    flight_dict["PLANE_LATITUDE"].append(_AQ.get("PLANE_LATITUDE")) # In Degrees; North is positive, South negative
    flight_dict["PLANE_LONGITUDE"].append(_AQ.get("PLANE_LONGITUDE")) # In Degrees;  East is positive, West negative
    flight_dict["PLANE_ALTITUDE"].append(_AQ.get("PLANE_ALTITUDE")) # Feet from sea level 
    flight_dict["PLANE_ALT_ABOVE_GROUND"].append(_AQ.get("PLANE_ALT_ABOVE_GROUND")) # Feet from ground
    flight_dict["AMBIENT_WIND_VELOCITY"].append(_AQ.get("AMBIENT_WIND_VELOCITY")) # In knots
    flight_dict["AMBIENT_WIND_DIRECTION"].append(_AQ.get("AMBIENT_WIND_DIRECTION")) # In degrees
    flight_dict["AMBIENT_WIND_X"].append(_AQ.get("AMBIENT_WIND_X")) # Wind component in East/West direction. Meters per sec.
    flight_dict["AMBIENT_WIND_Y"].append(_AQ.get("AMBIENT_WIND_Y")) # Wind component in vertical direction. Meters per sec.
    flight_dict["AMBIENT_WIND_Z"].append(_AQ.get("AMBIENT_WIND_Z")) # Wind component in North/South direction. Meters per sec. 
    flight_dict["AIRCRAFT_WIND_X"].append(_AQ.get("AIRCRAFT_WIND_X")) # Wind component in aircraft lateral axis
    flight_dict["AIRCRAFT_WIND_Y"].append(_AQ.get("AIRCRAFT_WIND_Y")) # Wind component in aircraft vertical axis
    flight_dict["AIRCRAFT_WIND_Z"].append(_AQ.get("AIRCRAFT_WIND_Z")) # Wind component in aircraft longitudinal axis
    flight_dict["AMBIENT_VISIBILITY"].append(_AQ.get("AMBIENT_VISIBILITY")) # In Meters 
    flight_dict["AMBIENT_TEMPERATURE"].append(_AQ.get("AMBIENT_TEMPERATURE")) # Celsius
    flight_dict["BAROMETER_PRESSURE"].append(_AQ.get("BAROMETER_PRESSURE")) # Determines air density, which impacts lift and engine performance
    flight_dict["AILERON_LEFT_DEFLECTION"].append(_AQ.get("AILERON_LEFT_DEFLECTION")) # In Radians 
    flight_dict["AILERON_RIGHT_DEFLECTION"].append(_AQ.get("AILERON_RIGHT_DEFLECTION")) # In Radians 
    flight_dict["ANGLE_OF_ATTACK_INDICATOR"].append(_AQ.get("ANGLE_OF_ATTACK_INDICATOR")) # In Radians 
    flight_dict["GPS_WP_TRUE_BEARING"].append(_AQ.get("GPS_WP_TRUE_BEARING")) # In Radians 
    flight_dict["GPS_WP_DISTANCE"].append(_AQ.get("GPS_WP_DISTANCE")) # In Meters
    flight_dict["ELEVATOR_TRIM_POSITION"].append(_AQ.get("ELEVATOR_TRIM_POSITION")) # In Radians
    flight_dict["FLAPS_HANDLE_PERCENT"].append(_AQ.get("FLAPS_HANDLE_PERCENT")) # Percent Over 100
    flight_dict["HEADING_INDICATOR"].append(_AQ.get("HEADING_INDICATOR")) # In Radians
    flight_dict["PLANE_PITCH_DEGREES"].append(_AQ.get("PLANE_PITCH_DEGREES")) # In Radians; mentions degrees in err
    flight_dict["PLANE_BANK_DEGREES"].append(_AQ.get("PLANE_BANK_DEGREES")) # In Radians; mentions degrees in err
    flight_dict["RUDDER_POSITION"].append(_AQ.get("RUDDER_POSITION")) # Percent rudder input deflection
    flight_dict["VERTICAL_SPEED"].append(_AQ.get("VERTICAL_SPEED")) # In feet/minute
    flight_dict["G_FORCE"].append(_AQ.get("G_FORCE")) 
    flight_dict["FUEL_TOTAL_QUANTITY"].append(_AQ.get("FUEL_TOTAL_QUANTITY")) # In Gallons 
    flight_dict["GENERAL_ENG_THROTTLE_LEVER_POSITION:1"].append(_AQ.get("GENERAL_ENG_THROTTLE_LEVER_POSITION:1")) # Percent of max throttle position
    flight_dict["GENERAL_ENG_THROTTLE_LEVER_POSITION:2"].append(_AQ.get("GENERAL_ENG_THROTTLE_LEVER_POSITION:2")) 
    flight_dict["GENERAL_ENG_THROTTLE_LEVER_POSITION:3"].append(_AQ.get("GENERAL_ENG_THROTTLE_LEVER_POSITION:3")) 
    flight_dict["GENERAL_ENG_THROTTLE_LEVER_POSITION:4"].append(_AQ.get("GENERAL_ENG_THROTTLE_LEVER_POSITION:4")) 
    flight_dict["PROP_THRUST:1"].append(_AQ.get("PROP_THRUST:1")) # In Pounds 
    flight_dict["PROP_THRUST:2"].append(_AQ.get("PROP_THRUST:2"))
    flight_dict["PROP_THRUST:3"].append(_AQ.get("PROP_THRUST:3"))
    flight_dict["PROP_THRUST:4"].append(_AQ.get("PROP_THRUST:4"))
    flight_dict["GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:1"].append(_AQ.get("GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:1")) # In Rankine
    flight_dict["GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:2"].append(_AQ.get("GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:2"))
    flight_dict["GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:3"].append(_AQ.get("GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:3"))
    flight_dict["GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:4"].append(_AQ.get("GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:4"))
    flight_dict["GENERAL_ENG_FUEL_PRESSURE:1"].append(_AQ.get("GENERAL_ENG_FUEL_PRESSURE:1")) # In Psi
    flight_dict["GENERAL_ENG_FUEL_PRESSURE:2"].append(_AQ.get("GENERAL_ENG_FUEL_PRESSURE:2"))
    flight_dict["GENERAL_ENG_FUEL_PRESSURE:3"].append(_AQ.get("GENERAL_ENG_FUEL_PRESSURE:3"))
    flight_dict["GENERAL_ENG_FUEL_PRESSURE:4"].append(_AQ.get("GENERAL_ENG_FUEL_PRESSURE:4"))
    flight_dict["ENG_FUEL_FLOW_GPH:1"].append(_AQ.get("ENG_FUEL_FLOW_GPH:1")) # In Gallons Per Hour 
    flight_dict["ENG_FUEL_FLOW_GPH:2"].append(_AQ.get("ENG_FUEL_FLOW_GPH:2"))
    flight_dict["ENG_FUEL_FLOW_GPH:3"].append(_AQ.get("ENG_FUEL_FLOW_GPH:3"))
    flight_dict["ENG_FUEL_FLOW_GPH:4"].append(_AQ.get("ENG_FUEL_FLOW_GPH:4"))
    flight_dict["TURB_ENG_VIBRATION:1"].append(_AQ.get("TURB_ENG_VIBRATION:1")) # Number/Float
    flight_dict["TURB_ENG_VIBRATION:2"].append(_AQ.get("TURB_ENG_VIBRATION:2"))
    flight_dict["TURB_ENG_VIBRATION:3"].append(_AQ.get("TURB_ENG_VIBRATION:3"))
    flight_dict["TURB_ENG_VIBRATION:4"].append(_AQ.get("TURB_ENG_VIBRATION:4"))
    flight_dict["GENERAL_ENG_OIL_PRESSURE:1"].append(_AQ.get("GENERAL_ENG_OIL_PRESSURE:1")) # In Psf 
    flight_dict["GENERAL_ENG_OIL_PRESSURE:2"].append(_AQ.get("GENERAL_ENG_OIL_PRESSURE:2"))
    flight_dict["GENERAL_ENG_OIL_PRESSURE:3"].append(_AQ.get("GENERAL_ENG_OIL_PRESSURE:3"))
    flight_dict["GENERAL_ENG_OIL_PRESSURE:4"].append(_AQ.get("GENERAL_ENG_OIL_PRESSURE:4"))
    flight_dict["GENERAL_ENG_RPM:1"].append(_AQ.get("GENERAL_ENG_RPM:1")) 
    flight_dict["GENERAL_ENG_RPM:2"].append(_AQ.get("GENERAL_ENG_RPM:2"))
    flight_dict["GENERAL_ENG_RPM:3"].append(_AQ.get("GENERAL_ENG_RPM:3"))
    flight_dict["GENERAL_ENG_RPM:4"].append(_AQ.get("GENERAL_ENG_RPM:4"))
    flight_dict["FUEL_TANK_RIGHT_MAIN_QUANTITY"].append(_AQ.get("FUEL_TANK_RIGHT_MAIN_QUANTITY")) # In Gallons
    flight_dict["FUEL_TANK_LEFT_MAIN_QUANTITY"].append(_AQ.get("FUEL_TANK_LEFT_MAIN_QUANTITY")) # In Gallons
    flight_dict["FUEL_TOTAL_QUANTITY_WEIGHT"].append(_AQ.get("FUEL_TOTAL_QUANTITY_WEIGHT")) # In Pounds 
    flight_dict["STALL_WARNING"].append(_AQ.get("STALL_WARNING"))
    flight_dict["OVERSPEED_WARNING"].append(_AQ.get("OVERSPEED_WARNING"))
    # flight_dict[""].append(_AQ.get(""))
    return flight_dict

def get_flight_dictionary(): 
    '''
    Function creates a flight data dictionary. 

    Returns
    -------
    flight_dict : Dictionary
        A flight dictionary containing all key fields of recorded flight data.

    '''
    flight_dict = {"LOCAL_TIME":[],
                   "PLANE_LATITUDE":[],
                   "PLANE_LONGITUDE":[],
                   "PLANE_ALTITUDE":[],
                   "PLANE_ALT_ABOVE_GROUND":[],
                   "AMBIENT_WIND_VELOCITY":[],
                   "AMBIENT_WIND_DIRECTION":[],
                   "AMBIENT_WIND_X":[],
                   "AMBIENT_WIND_Y":[],
                   "AMBIENT_WIND_Z":[],
                   "AIRCRAFT_WIND_X":[],
                   "AIRCRAFT_WIND_Y":[],
                   "AIRCRAFT_WIND_Z":[],
                   "AMBIENT_VISIBILITY":[],
                   "AMBIENT_TEMPERATURE":[],
                   "BAROMETER_PRESSURE":[],
                   "AILERON_LEFT_DEFLECTION":[],
                   "AILERON_RIGHT_DEFLECTION":[],
                   "ANGLE_OF_ATTACK_INDICATOR":[],
                   "AIRSPEED_TRUE":[],
                   "GROUND_VELOCITY":[],
                   "GPS_WP_TRUE_BEARING":[],
                   "GPS_WP_DISTANCE":[],
                   "ELEVATOR_TRIM_POSITION":[],
                   "FLAPS_HANDLE_PERCENT":[],
                   "HEADING_INDICATOR":[],
                   "PLANE_PITCH_DEGREES":[],
                   "PLANE_BANK_DEGREES":[],
                   "RUDDER_POSITION":[],
                   "VERTICAL_SPEED":[],
                   "G_FORCE":[],
                   "FUEL_TOTAL_QUANTITY":[],
                   "GENERAL_ENG_THROTTLE_LEVER_POSITION:1":[],
                   "GENERAL_ENG_THROTTLE_LEVER_POSITION:2":[],
                   "GENERAL_ENG_THROTTLE_LEVER_POSITION:3":[],
                   "GENERAL_ENG_THROTTLE_LEVER_POSITION:4":[],
                   "PROP_THRUST:1":[], 
                   "PROP_THRUST:2":[], 
                   "PROP_THRUST:3":[], 
                   "PROP_THRUST:4":[], 
                   "GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:1":[],
                   "GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:2":[],
                   "GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:3":[],
                   "GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:4":[],
                   "GENERAL_ENG_FUEL_PRESSURE:1":[],
                   "GENERAL_ENG_FUEL_PRESSURE:2":[],
                   "GENERAL_ENG_FUEL_PRESSURE:3":[],
                   "GENERAL_ENG_FUEL_PRESSURE:4":[],
                   "ENG_FUEL_FLOW_GPH:1":[],
                   "ENG_FUEL_FLOW_GPH:2":[],
                   "ENG_FUEL_FLOW_GPH:3":[],
                   "ENG_FUEL_FLOW_GPH:4":[],
                   "TURB_ENG_VIBRATION:1":[],
                   "TURB_ENG_VIBRATION:2":[],
                   "TURB_ENG_VIBRATION:3":[],
                   "TURB_ENG_VIBRATION:4":[],
                   "GENERAL_ENG_OIL_PRESSURE:1":[],
                   "GENERAL_ENG_OIL_PRESSURE:2":[],
                   "GENERAL_ENG_OIL_PRESSURE:3":[],
                   "GENERAL_ENG_OIL_PRESSURE:4":[],
                   "GENERAL_ENG_RPM:1":[],
                   "GENERAL_ENG_RPM:2":[],
                   "GENERAL_ENG_RPM:3":[],
                   "GENERAL_ENG_RPM:4":[],
                   "FUEL_TANK_RIGHT_MAIN_QUANTITY":[],
                   "FUEL_TANK_LEFT_MAIN_QUANTITY":[],
                   "FUEL_TOTAL_QUANTITY_WEIGHT":[],
                   "STALL_WARNING":[],
                   "OVERSPEED_WARNING":[],
                   # "":[],
                   }
    return flight_dict

def update_flight_dict(flight_dict, _AQ, _TF): 
    '''
    Function updates the flight data dict. 

    Parameters
    ----------
    flight_dict : Dictionary.
        Flight data dictionary.

    Returns
    -------
    updated_dict : Dictionary. 
        Updated Flight data dictionary.

    '''
    updated_dict = get_flight_data(flight_dict, _AQ, _TF) 
    return updated_dict

def save_data(SomeData, str_dir, str_file_name):
    '''
    Function saves given data to given directory and filename. 

    Parameters
    ----------
    SomeData : *
        Data to be pickled.
    str_dir : String
        String directory.
    str_file_name : String
        String file name w/o .pkl.

    Returns
    -------
    None.

    '''
    with open(f'./data/{str_dir}/{str_file_name}.pkl', 'wb') as fp:
        pickle.dump(SomeData, fp)
    return 

def load_data(some_pickle_file_path_str):
    '''
    Function loads pickled data given a string filepath. 

    Parameters
    ----------
    some_pickle_file_path_str : String
        String path to pickle file.

    Returns
    -------
    the_data : *
        The given pickled data.

    '''
    with open(some_pickle_file_path_str, 'rb') as fp:
        the_data = pickle.load(fp)
    return the_data

def get_atc_flight_number(_AQ): 
    '''
    Function retrieves the flight number of an active flight. If there is no 
    active flight method iterates until active flight number is assinged. 

    Parameters
    ----------
    _AQ : SimConnect Aircraft Requests object.
        Used to connect to MSFS.

    Returns
    -------
    flight_num_str : String
        ATC Flight number.

    '''
    flight_num_str = None
    while flight_num_str == None:
        flight_num_str = _AQ.get("ATC_FLIGHT_NUMBER")
        if type(flight_num_str) == type(None):
            continue
        else:
            flight_num_str = flight_num_str.decode()
    return flight_num_str

def get_flight_num():
    '''
    Function sets next flight number. 

    Returns
    -------
    None.

    ''' 
    flight_num = get_last_flight_num()
    # flight_num = flight_num + 1
    # _AQ.set("ATC_FLIGHT_NUMBER", str.encode(flight_num))
    return flight_num

def clear_flight_num(_AQ):
    '''
    Function sets next flight number. 

    Returns
    -------
    None.

    ''' 
    _AQ.set("ATC_FLIGHT_NUMBER", str.encode('STANDBY_FOR_FLIGHT_NUMBER'))
    return 

def make_flight_data_dir(_AQ):
    '''
    Makes a new directory to record flight data with a custom flight num. 

    Returns
    -------
    None.

    '''
    flight_number = int(get_last_flight_num()[1:])+1
    flight_number_f = f'f{flight_number}'
    os.mkdir(f'./data/{flight_number_f}')
    return 

def make_flight_header(_AQ, _TF): 
    '''
    Function sets the flight number, creates directory for the flight, and saves 
    the flight header.  

    Parameters
    ----------
    _AQ : Sim connect Aircraft Requests Object.
        
    _TF : Timezone Finder Object.
        

    Returns
    -------
    start_flight_data : TYPE
        DESCRIPTION.

    '''
    # Set the flight num and make dir 
    print("Making flight data directory...")
    make_flight_data_dir(_AQ)
    print("Setting flight number...")
    flight_num = get_last_flight_num() # GETS LAST FLIGHT NUMBER IN DATA DIRECTORY IN ABOVE LINE
    start_flight_data = get_start_flight_data(_AQ, _TF, flight_num)
    save_data(start_flight_data, flight_num, f'{flight_num}_Flight_Header') # SAVES THE HEADER .pkl
    return  start_flight_data

def check_set_last_dir(): 
    last_flight_dir = get_last_flight_num()
    file_path = f"./data/{last_flight_dir}/{last_flight_dir}.pkl"

    if os.path.exists(file_path):
        print("File exists")
    else:
        print(f'Flight data {file_path} does not exist. Removing...')
        shutil.rmtree(f"./data/{last_flight_dir}", ignore_errors=True)
    return 

def active_record(flight_dictionary, _AQ, _TF, flight_num): 
    '''
    Function gets an active flight number, if there is an active flight, iterates 
    checking flight number is still active, updates the flight data in 
    flight_dictionary, saves data to directory flight number.

    Parameters
    ----------
    flight_dictionary : Dictionary
        Flight data dictionary appends every iteration.
    flight_num : String
        Flight number string.

    Returns
    -------
    updated_dict : Dictionary
        Flight data dictionary with appended data per iteration.

    '''
    flight_num = get_last_flight_num()
    flight_dictionary = update_flight_dict(flight_dictionary, _AQ, _TF) 
    save_data(flight_dictionary, flight_num, flight_num)
    return flight_dictionary
