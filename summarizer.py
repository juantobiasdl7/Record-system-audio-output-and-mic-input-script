import sounddevice as sd
import numpy as np
import wavio
import pyaudio

# Global buffers to store the recordings
mic_buffer = []
system_buffer = []

# Create an interface to PortAudio
p = pyaudio.PyAudio()

# Print the available devices
print("New Available devices:\n")
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

# Device IDs found using `sd.query_devices()`
mic_device_id = 1  # Replace with your microphone device ID
stereo_mix_device_id = 2  # Replace with your system's stereo mix device ID

# Sample rate and duration
fs = 48000
duration = 10  # seconds

# Start recording from the microphone
with sd.InputStream(device=mic_device_id, channels=2, callback=mic_callback, samplerate=fs):
    # Start recording from the system audio
    with sd.InputStream(device=stereo_mix_device_id, channels=1, callback=system_callback, samplerate=fs):
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
wavio.write("output.wav", combined, fs, sampwidth=2)

print("Recording finished!")