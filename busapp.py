import requests
from datetime import datetime, timezone, timedelta
import time
from rpi_lcd import LCD

# TfL API endpoints
SOUTH_URL = "https://api.tfl.gov.uk/StopPoint/<YOURSTOPIDS>/arrivals"
NORTH_URL = "https://api.tfl.gov.uk/StopPoint/<YOURSTOPIDS>/arrivals"

class BusTimeDisplay:
    def __init__(self):
        try:
            self.lcd = LCD()
            self.lcd.clear()
        except Exception as e:
            print(f"Error initializing LCD: {e}")
            raise

    def get_bus_arrivals(self, url):
        """Get bus arrivals with error handling"""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            arrivals = []
            now = datetime.now(timezone.utc)
            
            # Process all arrivals
            for arrival in data:
                expected_time = datetime.fromisoformat(arrival['expectedArrival'].replace('Z', '+00:00'))
                # Subtract 30 seconds to account for display update frequency
                buffer_time = timedelta(seconds=30)
                adjusted_time = expected_time - buffer_time
                minutes_until = int((adjusted_time - now).total_seconds() / 60)
                
                if minutes_until >= 0:  # Only include future arrivals
                    arrivals.append({
                        'line': arrival['lineName'],
                        'minutes': minutes_until,
                        'arrival_time': adjusted_time.astimezone().strftime('%H:%M')
                    })
            
            # Simply sort by minutes until arrival and take first two
            sorted_arrivals = sorted(arrivals, key=lambda x: x['minutes'])[:2]
            return self.pad_arrivals(sorted_arrivals)
            
        except requests.RequestException as e:
            print(f"API Error: {e}")
            return self.pad_arrivals([])
    
    def pad_arrivals(self, arrivals):
        """Ensure we always have exactly 2 arrivals"""
        while len(arrivals) < 2:
            arrivals.append({
                'line': '--',
                'minutes': 0,
                'arrival_time': '--:--'
            })
        return arrivals[:2]

    def format_line(self, direction, bus):
        """Format line with fixed-width spacing
        Format for LCD display:
        "N: Bus 12  17:15 9m"
        "N: Bus 23 17:16 10m"
        """
        # Direction (2 chars) + ': ' = 4 chars total
        direction_part = f"{direction[0]}: "  # Just take first letter
        
        # "Bus " prefix + bus line number (3 chars, right-padded with spaces)
        bus_part = f"Bus {bus['line']}".ljust(7)
        
        # Time (5 chars) + space + Minutes (2 chars) + 'm'
        minutes_str = str(bus['minutes']).rjust(2)
        time_part = f"{bus['arrival_time']} {minutes_str}m"
        
        return f"{direction_part}{bus_part} {time_part}"

    def update_display(self, lines):
        """Update LCD display with the given lines"""
        try:
            for i, line in enumerate(lines, start=1):
                self.lcd.text(line, i)
        except Exception as e:
            print(f"Error updating LCD: {e}")
            try:
                self.lcd = LCD()
                for i, line in enumerate(lines, start=1):
                    self.lcd.text(line, i)
            except:
                pass

    def run(self):
        try:
            while True:
                # Get arrivals
                north_arrivals = self.get_bus_arrivals(NORTH_URL)
                south_arrivals = self.get_bus_arrivals(SOUTH_URL)
                
                # Format all 4 lines, North first then South
                lines = []
                for bus in north_arrivals:
                    lines.append(self.format_line('North', bus))
                for bus in south_arrivals:
                    lines.append(self.format_line('South', bus))
                
                # Update LCD
                self.update_display(lines)
                
                time.sleep(30)

        except KeyboardInterrupt:
            print("\nProgram terminated by user")
            self.lcd.clear()
        except Exception as e:
            print(f"Error: {e}")
            self.lcd.clear()

    def __del__(self):
        """Cleanup when the object is destroyed"""
        try:
            self.lcd.clear()
        except:
            pass

if __name__ == "__main__":
    try:
        display = BusTimeDisplay()
        display.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        try:
            LCD().clear()
        except:
            pass