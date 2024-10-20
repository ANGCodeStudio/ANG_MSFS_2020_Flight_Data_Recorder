# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 16:59:50 2024

@author: ANG
"""
import ang_data_reader_utils as angdru
import time 

def main():
    help_str = "\nWelcome to ANG Flight Data Converter!\n"\
                       "0. Show all Flights not converted to .csv\n"\
                       "1. Convert flight to .csv\n"\
                       "2. Convert flight header to .csv\n"\
                       "3. Convert all flights to .csv\n"\
                       "4. Convert all headers to .csv\n"\
                       "5. Convert all flights and all headers not converted to .csv\n"\
                       "6. Exit\n\n"
    print(help_str)
    while True:
        user_input = input("Enter your choice: ")
        if user_input == "0":
            angdru.show_all_flights_and_headers_not_converted()
        elif user_input == "1":
            user_in_flight_num = input("Enter flight number to convert to .csv i.e. f1: ")
            angdru.convert_single_flight_to_csv(user_in_flight_num)
        elif user_input == "2": 
            user_in_flight_num = input("Enter flight header number to convert to .csv i.e. f1: ")
            angdru.convert_single_header_to_csv(user_in_flight_num)
        elif user_input == "3": 
            angdru.show_all_flights_and_headers_not_converted()
            user_cont_0 = input('The flights from the above table will be converted to .csv. Continue [y n]:')
            if user_cont_0 == 'n': 
                print('Not converting... continue...')
                continue 
            elif user_cont_0 == 'y': 
                angdru.export_all_flights_to_csv()
        elif user_input == "4": 
            angdru.show_all_flights_and_headers_not_converted()
            user_cont_0 = input('The flight headers from the above table will be converted to .csv. Continue [y n]:')
            if user_cont_0 == 'n': 
                continue 
            elif user_cont_0 == 'y': 
                angdru.export_all_headers_to_csv()
            else: 
                continue
        elif user_input == "5": 
            angdru.show_all_flights_and_headers_not_converted()
            user_cont_0 = input('The flights and headers from the table above will be converted to .csv. Continue [y n]:')
            if user_cont_0 == 'n': 
                print('Not converting... continue...')
                continue 
            elif user_cont_0 == 'y': 
                angdru.export_all_headers_to_csv()
                angdru.export_all_flights_to_csv()
            else: 
                continue
        elif user_input == "6":
            print("Exiting the application. Goodbye!")
            time.sleep(4)
            break
        else:
            # Handle invalid input
            print(help_str)
            print("Please enter a valid input [0 1 2 3 4 5 6]")
            

if __name__ == "__main__":
    main()

