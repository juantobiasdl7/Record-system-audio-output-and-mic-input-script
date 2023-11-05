import psutil
import pygetwindow as gw
import subprocess
import time
from datetime import datetime
import pyaudio
import sounddevice as sd
import numpy as np
import wavio
import whisper

def is_meeting_in_progress(window_title):
    """
    Check if the meeting is in progress by looking for specific keywords
    in the window title.
    """
    keywords = ["Microsoft Teams Meeting", "Meet"]  # Add more as needed
    return any(keyword in window_title for keyword in keywords)

def record_audio(filename, mic_device_id=2, stereo_mix_device_id=1, fs=48000, duration=10):
    # Global buffers to store the recordings
    mic_buffer = []
    system_buffer = []

    # Create an interface to PortAudio
    p = pyaudio.PyAudio()

    # Print the available devices
    print("Available devices:\n")
    for i in range(0, p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(str(info["index"]) + ": \t %s \n \t %s \n" % (info["name"], p.get_host_api_info_by_index(info["hostApi"])["name"]))

    # Callback functions for each stream
    def mic_callback(indata, frames, time, status):
        if status:
            print(status)
        # Append indata to mic_buffer
        mic_buffer.extend(indata.copy())

    def system_callback(indata, frames, time, status):
        if status:
            print(status)
        # Append indata to system_buffer
        system_buffer.extend(indata.copy())

    # Start recording from the microphone
    with sd.InputStream(device=mic_device_id, channels=2, callback=mic_callback, samplerate=fs):
        # Start recording from the system audio
        with sd.InputStream(device=stereo_mix_device_id, channels=2, callback=system_callback, samplerate=fs):
            # Sleep while the callbacks are called in the background
            sd.sleep(duration * 1000)

    # Convert the buffers to numpy arrays
    mic_recording = np.array(mic_buffer)
    system_recording = np.array(system_buffer)

    # Ensure the recordings are the same length
    min_len = min(len(mic_recording), len(system_recording))
    mic_recording = mic_recording[:min_len]
    system_recording = system_recording[:min_len]

    # Combine both recordings by stacking them horizontally (side by side)
    combined = np.hstack((mic_recording, system_recording))

    # Save to file
    wavio.write(filename, combined, fs, sampwidth=2)

    print("Recording finished!")

def main_loop():
    global_count = 0

    while True:

        #Begining a new cycle
        print("New cycle in 10 seconds...")
        time.sleep(10) 

        # Flag to indicate if a meeting is in progress
        meeting_in_progress = False

        # Creating the whisper model to transcribe the audio audio file
        model = whisper.load_model("base")

        # Get the current date and time
        now = datetime.now()
        # Format the date and time to a string suitable for a file name
        datetime_str = now.strftime("%Y%m%d_%H%M%S")
        # Create the file name with the date and time
        filename = f"recordings/output_{datetime_str}.wav"

        # If the current time is after 6:00 pm, exit the loop (and the script)
        if now.hour >= 23:
            print("Ending monitoring for today.")
            break
        
        print(global_count)
        print(now)
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
                        meeting_in_progress = True
                        break
                
                if meeting_in_progress:
                    # Script runs because a meeting is detected
                    print("Recording starts: ",datetime.now())
                    record_audio(filename)
                    print("Recording ends: ",datetime.now())
                    #time.sleep(2) # Changes ofr 05/11/2023 start from here, I will add the logic to output a .txt file with the transcription of the audio file.

                    # Transcribe the audio file
                    result = model.transcribe(filename)

                    break  
        if not meeting_in_progress:
            print("No meeting detected, waiting 60 seconds...")
            time.sleep(60)  # Wait 60 seconds before checking again

if __name__ == "__main__":
    main_loop()
