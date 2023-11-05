import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import whisper

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, model):
        self.model = model

    def on_created(self, event):
        # This function is called when a new file is created
        if not event.is_directory:
            file_path = event.src_path
            file_name, file_extension = os.path.splitext(file_path)
            if file_extension.lower() in ['.wav', '.mp3']:
                print(f"New audio file detected: {file_path}")
                # Transcribe the audio file
                result = self.model.transcribe(file_path)
                # Save the transcription to a .txt file
                with open(f"{file_name}.txt", "w", encoding="utf-8") as file:
                    file.write(result["text"])
                print(f"Transcription for {file_path} completed.")

def load_model_and_watch_directory(directory):
    print("Loading Whisper model...")
    model = whisper.load_model("base")

    event_handler = NewFileHandler(model)
    observer = Observer()
    observer.schedule(event_handler, path=directory, recursive=False)

    print(f"Starting to monitor {directory} for new audio files...")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    recordings_directory = "recordings"  # Set to your recordings directory
    load_model_and_watch_directory(recordings_directory)
