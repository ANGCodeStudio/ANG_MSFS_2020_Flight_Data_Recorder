# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 15:21:28 2024

@author: ANG
"""
import os
import pickle 
from pandas import DataFrame 

def test_check_data_dirs(): 
    os.makedirs('data_csv', exist_ok=True)
    os.makedirs('data_csv/flight_data', exist_ok=True)
    os.makedirs('data_csv/flight_headers', exist_ok=True)
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

def load_header(flight_num): 
    data = load_data(f"./data/{flight_num}/{flight_num}_Flight_Header.pkl")
    return data

def load_flight_data(flight_num): 
    data = load_data(f"./data/{flight_num}/{flight_num}.pkl")
    return data

def data_to_dataframe(data_dictionary):
    try: 
        df = DataFrame(data_dictionary)
    except ValueError: 
        df = DataFrame(data_dictionary, index=[0]).T
    return df

def show_all_flights_and_headers_pkl():
    # Header for the table
    print(f'{"Flights in ./data:":<30} {"Headers in ./data:"}')
    for root, dirs, files in os.walk('./data'):  # iterates through all flight directories in ./data
        if len(files) < 2:
            continue
        else:
            print(f'{files[0]:<30} {files[1]}')
    return

def get_csv_flight_nums(): 
    '''
    Function returns a list of string flight numbers that currently exist in 
    ./data_csv/flight_data

    Returns
    -------
    current_csv_flight_nums : List
        List of string flight nums i.e. ['f1','f2','f3',...].
    '''
    current_csv_flight_nums = []
    for i in os.walk('./data_csv/flight_data'): 
        for i2 in i[2]:
            current_csv_flight_nums.append(i2.split('.')[0])
    return current_csv_flight_nums

def get_csv_flight_headers(): 
    '''
    Function returns a list of string flight headers that currently exist in 
    ./data_csv/flight_data

    Returns
    -------
    current_csv_flight_nums : List
        List of string flight nums i.e. ['f1','f2','f3',...].
    '''
    current_csv_flight_headers = []
    for i in os.walk('./data_csv/flight_headers'): 
        for i2 in i[2]:
            current_csv_flight_headers.append(i2.split('_')[0])
    return current_csv_flight_headers

def get_all_headers_pkl(): 
    '''
    Gets all recorded headers in ./data

    Returns
    -------
    headers_lst : List
        List of string flight header nums i.e. ['f1','f2','f3',...].
    '''
    headers_lst = []
    for root, dirs, files in os.walk('./data'):  # iterates through all flight directories in ./data
        if len(files) == 2:
            headers_lst.append(files[1].split('_')[0])
    return headers_lst

def get_all_flight_pkl(): 
    '''
    Gets all recorded flights in ./data

    Returns
    -------
    flights_lst : List
        List of string flight nums i.e. ['f1','f2','f3',...].
    '''
    flights_lst = []
    for root, dirs, files in os.walk('./data'):  # iterates through all flight directories in ./data
        if len(files) == 2:  
            flights_lst.append(files[0].split('.')[0])
    return flights_lst

def check_convert_headers_to_csv(): 
    '''
    Function checks for all header numbers recorded in ./data that are not 
    yet converted to .csv in ./data_csv/flight_headers

    Returns
    -------
    diff_lst : List
        List of string flight nums i.e. ['f1','f2','f3',...].
    '''
    current_csv_flight_headers_lst = get_csv_flight_headers()
    current_pkl_headers_lst = get_all_headers_pkl()
    diff_lst = [i for i in current_pkl_headers_lst if i not in current_csv_flight_headers_lst]
    return diff_lst

def check_convert_flights_to_csv(): 
    '''
    Fucntion checks for all flight data numbers recorded in ./data that are not 
    yet converted to .csv in ./data_csv/flight_data

    Returns
    -------
    diff_lst : List
        List of string flight nums i.e. ['f1','f2','f3',...].
    '''
    current_csv_flights_lst = get_csv_flight_nums()
    current_pkl_flights_lst = get_all_flight_pkl()
    diff_lst = [i for i in current_pkl_flights_lst if i not in current_csv_flights_lst]
    return diff_lst

def show_all_flights_and_headers_not_converted():
    print('\n\n---------------------------------')
    print('All flights and headers in ./data not converted to .csv')
    print(f'{"Flights:":<30} {"Headers:"}')
    flights_not_converted = check_convert_flights_to_csv()
    headers_not_converted = check_convert_headers_to_csv()
    if len(flights_not_converted) == 0: 
        flights_not_converted = ['None to convert']
    if len(headers_not_converted) == 0: 
        headers_not_converted = ['None to convert']
    max_len = max(len(flights_not_converted), len(headers_not_converted))
    flights_not_converted += [''] * (max_len - len(flights_not_converted))
    headers_not_converted += [''] * (max_len - len(headers_not_converted))

    for flight, header in zip(flights_not_converted, headers_not_converted):
        print(f'{flight:<30} {header}')
    print('---------------------------------')
    return

def convert_single_flight_to_csv(flight_num_str): 
    if flight_num_str in check_convert_flights_to_csv():
        print(f'Converting flight {flight_num_str} to csv...')
        data_to_dataframe(load_flight_data(flight_num_str)).to_csv(f'./data_csv/flight_data/{flight_num_str}.csv', index=False)
    else: 
        print(f"Flight {flight_num_str} already converted or does not exist. ")
    return 

def convert_single_header_to_csv(flight_num_str): 
    if flight_num_str in check_convert_headers_to_csv():
        print(f'Converting flight header {flight_num_str} to csv...')
        data_to_dataframe(load_header(flight_num_str)).to_csv(f'./data_csv/flight_headers/{flight_num_str}_Flight_Header.csv')
    else: 
        print(f"Flight header {flight_num_str} already converted or does not exist. ")
    return 

def export_all_flights_to_csv(): 
    '''
    Function converts and exports all flight data from .pkl in ./data 
    to .csv in data_csv directory if it does not 
    already exist in ./flight_data 

    Returns
    -------
    None.
    '''
    # All flight nums in ./data_csv 
    test_check_data_dirs()
    check_convert_flights_lst = check_convert_flights_to_csv()
    for i in check_convert_flights_lst:
        convert_single_flight_to_csv(i)
    return 

def export_all_headers_to_csv(): 
    '''
    Function converts and exports all flight header data from .pkl in ./data 
    to .csv in data_csv directory if it does not 
    already exist in ./flight_headers 

    Returns
    -------
    None.
    '''
    test_check_data_dirs()
    check_convert_headers_lst = check_convert_headers_to_csv()
    for i in check_convert_headers_lst:
        convert_single_header_to_csv(i)
    return 

