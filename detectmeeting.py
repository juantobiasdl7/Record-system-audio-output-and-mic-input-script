import psutil
import pygetwindow as gw
import subprocess
import time
from datetime import datetime

def is_meeting_in_progress(window_title):
    """
    Check if the meeting is in progress by looking for specific keywords
    in the window title.
    """
    keywords = ["Microsoft Teams Meeting", "Meet"]  # Add more as needed
    return any(keyword in window_title for keyword in keywords)

def main_loop():
    while True:
        # Get the current time
        current_time = datetime.now()
        # If the current time is after 6:00 pm, exit the loop (and the script)
        if current_time.hour >= 18:
            print("Ending monitoring for today.")
            break

        # Your existing logic to check for meetings and run the script
        for process in psutil.process_iter(['pid', 'name']):
            # Check if Teams or Google Meet is running
            if process.info['name'] in ("Teams.exe", "GoogleMeet.exe"):
                # Loop through all windows titles to find a meeting in progress
                for window in gw.getWindowsWithTitle(''):
                    if is_meeting_in_progress(window.title):
                        # Run your script and exit loops if a meeting is detected
                        subprocess.Popen(['path_to_your_script.exe'])
                        return

        time.sleep(60)  # Wait 60 seconds before checking again

if __name__ == "__main__":
    main_loop()
