import requests
from datetime import datetime, timezone
import time
from rpi_lcd import LCD

# TfL API endpoints
SOUTH_URL = "https://api.tfl.gov.uk/StopPoint/490006169N1/arrivals"
NORTH_URL = "https://api.tfl.gov.uk/StopPoint/490015109W/arrivals"

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
            
            sorted_arrivals = sorted(data, key=lambda x: x['expectedArrival'])
            arrivals = []
            now = datetime.now(timezone.utc)
            
            for arrival in sorted_arrivals[:2]:
                expected_time = datetime.fromisoformat(arrival['expectedArrival'].replace('Z', '+00:00'))
                minutes_until = int((expected_time - now).total_seconds() / 60)
                arrival_time = expected_time.astimezone().strftime('%H:%M')
                
                if minutes_until >= 0:
                    arrivals.append({
                        'line': arrival['lineName'],
                        'minutes': minutes_until,
                        'arrival_time': arrival_time
                    })
            
            return self.pad_arrivals(arrivals)
            
        except requests.RequestException:
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
        Format: "South: 242 14:33 3m "
                "South: 12  14:33 3m "
                "North: 242 14:33 3m "
                "North: 12  14:33 3m "
        """
        # Direction (6 chars) + ': ' (2 chars) = 8 chars total
        direction_part = f"{direction}: "
        
        # Bus line number (3 chars, right-padded with spaces)
        bus_part = f"{bus['line']}".ljust(3)
        
        # One space separator
        space = " "
        
        # Time (5 chars) + space + minutes (2 chars) + 'm' = 9 chars
        time_part = f"{bus['arrival_time']} {bus['minutes']}m"
        
        return f"{direction_part}{bus_part}{space}{time_part}"

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
                south_arrivals = self.get_bus_arrivals(SOUTH_URL)
                north_arrivals = self.get_bus_arrivals(NORTH_URL)
                
                # Format all 4 lines
                lines = []
                for bus in south_arrivals:
                    lines.append(self.format_line('South', bus))
                for bus in north_arrivals:
                    lines.append(self.format_line('North', bus))
                
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