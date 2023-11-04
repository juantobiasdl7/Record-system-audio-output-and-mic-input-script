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
    global_count = 0

    while True:
        # Get the current time
        current_time = datetime.now()
        # If the current time is after 6:00 pm, exit the loop (and the script)
        if current_time.hour >= 18:
            print("Ending monitoring for today.")
            break
        
        print(global_count)
        print(current_time)
        # Your existing logic to check for meetings and run the script
        for process in psutil.process_iter(['pid', 'name']):
            print(process.info['pid'], process.info['name'])
            # Check if Teams or Google Meet is running
            if process.info['name'] in ("Teams.exe", "chrome.exe"):

                print("Found Teams or Google Meet-------------")
                # Loop through all windows titles to find a meeting in progress
                all_windows = gw.getWindowsWithTitle('')

                print("All windows: ", all_windows)

                for window in all_windows:
                    print("ONE windows: ----> ", window.title)
                    if is_meeting_in_progress(window.title):
                        # Run your script and exit loops if a meeting is detected
                        subprocess.Popen(['dist/summarizer.exe'])
                        return

        time.sleep(60)  # Wait 60 seconds before checking again

if __name__ == "__main__":
    main_loop()
