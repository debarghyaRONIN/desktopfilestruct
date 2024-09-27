from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
from time import sleep

import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ! TO BE CONFIGURED
# ? Directory to monitor e.g. Windows: "C:\\Users\\UserName\\Downloads"
watch_directory = ""
sfx_destination = ""
music_destination = ""
video_destination = ""
image_destination = ""
doc_destination = ""
torrent_destination = ""  # New folder for torrent links

# ? Supported image file formats
image_types = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
               ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]
# ? Supported video file formats
video_types = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
               ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]
# ? Supported audio file formats
audio_types = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]
# ? Supported document file formats
document_types = [".doc", ".docx", ".odt",
                  ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]
# ? Supported torrent file formats
torrent_types = [".torrent"]  

# Function to ensure unique filenames
def ensure_unique(dest, filename):
    file_base, file_ext = splitext(filename)
    count = 1
    # * Add a counter to the filename if it already exists
    while exists(f"{dest}/{filename}"):
        filename = f"{file_base}({str(count)}){file_ext}"
        count += 1

    return filename

# Function to move files, ensuring no overwrites
def relocate_file(destination, entry, filename):
    if exists(f"{destination}/{filename}"):
        new_name = ensure_unique(destination, filename)
        current_name = join(destination, filename)
        updated_name = join(destination, new_name)
        rename(current_name, updated_name)
    move(entry, destination)

class FileMoverHandler(FileSystemEventHandler):
    # ? Triggered when the watch directory is modified
    def on_modified(self, event):
        with scandir(watch_directory) as files:
            for file in files:
                file_name = file.name
                self.process_audio_files(file, file_name)
                self.process_video_files(file, file_name)
                self.process_image_files(file, file_name)
                self.process_document_files(file, file_name)
                self.process_torrent_files(file, file_name)  # New function for torrents

    # * Process audio files
    def process_audio_files(self, file, file_name):
        for audio_ext in audio_types:
            if file_name.endswith(audio_ext) or file_name.endswith(audio_ext.upper()):
                if file.stat().st_size < 10_000_000 or "SFX" in file_name:  # ? Files below 10MB or labeled as SFX
                    destination = sfx_destination
                else:
                    destination = music_destination
                relocate_file(destination, file, file_name)
                logging.info(f"Relocated audio file: {file_name}")

    # * Process video files
    def process_video_files(self, file, file_name):
        for video_ext in video_types:
            if file_name.endswith(video_ext) or file_name.endswith(video_ext.upper()):
                relocate_file(video_destination, file, file_name)
                logging.info(f"Relocated video file: {file_name}")

    # * Process image files
    def process_image_files(self, file, file_name):
        for image_ext in image_types:
            if file_name.endswith(image_ext) or file_name.endswith(image_ext.upper()):
                relocate_file(image_destination, file, file_name)
                logging.info(f"Relocated image file: {file_name}")

    # * Process document files
    def process_document_files(self, file, file_name):
        for doc_ext in document_types:
            if file_name.endswith(doc_ext) or file_name.endswith(doc_ext.upper()):
                relocate_file(doc_destination, file, file_name)
                logging.info(f"Relocated document file: {file_name}")

    # * Process torrent files
    def process_torrent_files(self, file, file_name):
        for torrent_ext in torrent_types:
            if file_name.endswith(torrent_ext) or file_name.endswith(torrent_ext.upper()):
                relocate_file(torrent_destination, file, file_name)
                logging.info(f"Relocated torrent file: {file_name}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = watch_directory
    event_handler = FileMoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

