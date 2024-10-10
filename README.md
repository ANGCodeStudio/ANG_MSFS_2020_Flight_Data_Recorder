
# ANG Flight Data Utilities

This repository contains various Python modules designed for interacting with Microsoft Flight Simulator data. The utilities include functions for recording flight data, handling aircraft systems, converting flight data to CSV format, and more. These tools are built using PyQt5 for the GUI and leverage SimConnect for communication with the flight simulator.

## Table of Contents

1. Files Overview
2. Installation
3. Usage
4. Modules Overview
   - ANG_MSFS_2020_Flight_Data_Recorder.py
   - ANG_Flight_Recorder_v_0_5.py
   - ANG_flight_data_converter.py
   - ang_flight_data_reader_utils.py
5. Requirements
6. License

## Files Overview

- **ANG_MSFS_2020_Flight_Data_Recorder.py**: Manages aircraft-related utilities with a PyQt5 GUI for flight recording and aircraft control.
- **ANG_Flight_Recorder_v_0_5.py**: Handles flight data collection, including connecting to SimConnect and recording detailed flight metrics.
- **ANG_flight_data_converter.py**: Converts recorded flight data into CSV format using user-friendly command-line options.
- **ang_flight_data_reader_utils.py**: Provides utility functions for loading and displaying flight data and converting data to pandas DataFrames.

## Installation

To set up the environment and install dependencies:

1. Clone the repository:
   ```
   git clone https://github.com/your-repo-name.git
   cd your-repo-name
   ```

2. Dependencies:
   Python 3.7 or higher
   PyQt5
   pandas
   SimConnect
   timezonefinder
   pytz

3. Ensure you have Microsoft Flight Simulator and SimConnect properly set up on your machine.

## Usage

### Running the Utilities

To use the flight data converter:
```
python ANG_flight_data_converter.py
```

To launch the aircraft utility GUI application:
```
python ANG_MSFS_2020_Flight_Data_Recorder.py
```

## Modules Overview

### ANG_MSFS_2020_Flight_Data_Recorder.py

This module creates a graphical user interface for managing flight recording and aircraft operations using PyQt5. Key features include:

- **Flight Recording**: Automates the recording of flight data while in the simulator.
- **Aircraft System Control**: Start or stop all aircraft systems and trigger specific actions (like fast travel).
- **Dashboard Monitoring**: Displays real-time aircraft data like latitude, longitude, altitude, and more.

Key Classes and Functions:
- `WorkerThread`: Handles background processing for recording flight data in a separate thread.
- `SimUtilsApp`: Main application class for managing the GUI and user interactions.
- `connect_to_sim()`: Ensures connection to Microsoft Flight Simulator before running other operations.

### ANG_Flight_Recorder_v_0_5.py

This module is responsible for recording detailed flight data from Microsoft Flight Simulator. It handles the data collection and management of aircraft metrics.

Key Functions:
- `get_flight_data()`: Collects real-time data such as speed, altitude, wind velocity, and engine parameters.
- `save_data()`: Saves flight data to a `.pkl` file.
- `make_flight_header()`: Creates and stores a header for each new flight.
- `connect_sm()`, `connect_aq()`, `connect_ae()`: Establish connections with SimConnect to interact with the simulator.

### ANG_flight_data_converter.py

A command-line utility to convert recorded flight data and headers from `.pkl` files to CSV format. It provides a menu-driven interface with the following options:

1. Show all flights not yet converted to CSV.
2. Convert individual flights or headers to CSV.
3. Bulk convert all recorded flights and headers to CSV.

Usage Example:
```
Welcome to ANG Flight Data Converter!
0. Show all Flights not converted to .csv
1. Convert flight to .csv
2. Convert flight header to .csv
3. Convert all flights to .csv
4. Convert all headers to .csv
5. Convert all flights and all headers not converted to .csv
6. Exit
```

### ang_flight_data_reader_utils.py

Contains utility functions for loading and displaying flight data. It can convert the data into pandas DataFrames for easier manipulation and analysis.

Key Functions:
- `load_data()`: Loads pickled flight data from a file.
- `data_to_dataframe()`: Converts flight data dictionaries into pandas DataFrames.
- `check_convert_flights_to_csv()`, `check_convert_headers_to_csv()`: Identifies which flights and headers have not yet been converted to CSV format.

## Requirements

- Python 3.7 or higher
- PyQt5
- pandas
- SimConnect
- timezonefinder
- pytz

## License

This project is licensed under the Creative Commons Zero (CC0) License. This means you can copy, modify, distribute, and perform the work, even for commercial purposes, all without asking permission.

This software and its associated files are provided "as is," without any express or implied warranties, including but not limited to the implied warranties of merchantability, fitness for a particular purpose, or non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

Use this software at your own risk. The authors make no guarantees about the correctness, reliability, or functionality of the software, nor do they provide support or assume responsibility for its use in any specific context.

By using this software, you agree to the terms of this disclaimer and accept that the authors are not responsible for any damages or losses that may occur as a result of using, modifying, or distributing this software.