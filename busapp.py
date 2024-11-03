import requests
from datetime import datetime, timezone
import time
import json
from pathlib import Path
from rpi_lcd import LCD

# TfL API endpoints
SOUTH_URL = "https://api.tfl.gov.uk/StopPoint/490006169N1/arrivals"
NORTH_URL = "https://api.tfl.gov.uk/StopPoint/490015109W/arrivals"
CACHE_FILE = "bus_cache.json"

class BusTimeDisplay:
    def __init__(self):
        self.cache = {'south': [], 'north': []}
        try:
            self.lcd = LCD()
            self.lcd.clear()
        except Exception as e:
            print(f"Error initializing LCD: {e}")
            raise
        
    def get_bus_arrivals(self, url):
        """Get bus arrivals with error handling and fallback to cache"""
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
        return arrivals[:2]  # Ensure we never return more than 2

    def format_line(self, direction, bus):
        """Format line to exactly 20 characters"""
        # Format: "South: 242 14:33 3m "
        return f"{direction}: {bus['line']} {bus['arrival_time']} {bus['minutes']}m".ljust(20)

    def update_display(self, lines):
        """Update LCD display with the given lines"""
        try:
            for i, line in enumerate(lines, start=1):
                self.lcd.text(line, i)
        except Exception as e:
            print(f"Error updating LCD: {e}")
            # Try to reinitialize LCD
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
        # Try one last time to clear the display
        try:
            LCD().clear()
        except:
            pass