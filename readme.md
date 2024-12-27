# TfL Bus Time Display

A Raspberry Pi application that displays real-time London bus arrival times on an LCD screen. The application shows upcoming arrivals for both northbound and southbound buses at specified stops.

## Features

- Real-time bus arrival information from TfL API
- Displays next two buses for each direction (north/south)
- Shows bus line numbers, expected arrival times, and minutes until arrival
- 30-second refresh rate
- Error handling and automatic recovery
- Clean display formatting for 16x2 LCD screens

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- 16x2 LCD display compatible with `rpi_lcd` library
- Appropriate wiring between Raspberry Pi and LCD

## Software Requirements

- Python 3.6+
- Required Python packages:
  - `requests`
  - `rpi_lcd`
  - `datetime`

## Installation

1. Clone this repository to your Raspberry Pi
2. Install required packages:
   ```bash
   pip install requests rpi_lcd
   ```
3. Ensure your LCD is properly connected to the Raspberry Pi's GPIO pins

## Configuration

The application is configured to monitor two TfL bus stops:
- Northbound: <STOPID>
- Southbound: <STOPID>

To monitor your chosen bus stops, modify the `NORTH_URL` and `SOUTH_URL` variables at the top of the script. Stop ID's can be found through the (https://api.tfl.gov.uk/)[TFL's API documentation.]

## Display Format

The LCD displays four lines of information in the following format:
```
N: Bus 76  17:15 9m
N: Bus 141 17:16 10m
S: Bus 76  17:20 14m
S: Bus 141 17:22 16m
```

Where:
- N/S indicates direction (North/South)
- Bus number
- Expected arrival time (24-hour format)
- Minutes until arrival

## Running the Application

To start the application:
```bash
python bus_display.py
```

The program will continuously update the display every 30 seconds until interrupted with Ctrl+C.

## Error Handling

The application includes robust error handling for:
- LCD initialization failures
- API connection issues
- Data parsing problems
- Display update errors

In case of errors, the application will attempt to recover automatically and continue running.

## Termination

The application can be safely terminated using Ctrl+C. The LCD screen will be cleared upon exit.
