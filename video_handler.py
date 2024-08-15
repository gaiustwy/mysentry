import os
import cv2
import subprocess
from datetime import datetime
from utilities import format_object_detected
from config import temp_folder_path, clips_folder_path

class VideoHandler:
    def __init__(self):
        self.fourcc = cv2.VideoWriter_fourcc(*"avc1")
        self.fps = 24.0
        self.video_writer = None
        self.start_time = None
        self.filename = None
        self.preview_path = None
        self.maximum_duration = 20

    def initialize_recording(self, frame, filename=None):
        self.start_time = datetime.now()
        if filename is None:
            self.filename = f"{clips_folder_path}/{self.start_time.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
        else:
            self.filename = filename
        self.video_writer = cv2.VideoWriter(self.filename, self.fourcc, self.fps, (frame.shape[1], frame.shape[0]))
    
    def write_frame(self, frame):
            self.video_writer.write(frame)

    def stop_recording(self):
            self.video_writer.release()
    
    def save_preview(self, total_frames, preview_path=None):
        index = len(total_frames) // 2
        middle_frame_number = total_frames[index]
        frame = self.get_frame_from_clip(middle_frame_number)

        if preview_path is None:
            self.preview_path = f"{temp_folder_path}/preview.jpg"
        else:
            self.preview_path = preview_path
        cv2.imwrite(self.preview_path, frame)
    
    def get_frame_from_clip(self, frame_number):
        cap = cv2.VideoCapture(self.filename)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        _, frame = cap.read()
        cap.release()

        return frame
    
    def add_metadata_to_video(self, metadata):
        # Input and output must be different so temporary file is created
        # Extract the filename and extension
        filename = os.path.basename(self.filename)
        # Create the temporary filename
        temp_filename = f"{temp_folder_path}/temp_{filename}"

        comment = format_object_detected(metadata)

        cmd = [
            "ffmpeg",
            "-i", self.filename,
            "-metadata", f"comment={comment}",
            "-codec", "copy",
            temp_filename
        ]
        
        subprocess.run(cmd)
        # Replace the original file with the new one
        os.replace(temp_filename, self.filename)
        
    @property
    def maximum_fps(self):
        return self.fps * self.maximum_duration
    
    @staticmethod
    def get_timestamp_from_filename(filename):
        # Extract the filename from the path
        filename = os.path.basename(filename)

        # Extract the timestamp string from the filename by removing the file extension
        timestamp_str = filename.split('.')[0]  

        # Parse the timestamp string into a datetime object
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

        # Format the datetime object into the string new format
        formatted_timestamp = timestamp.strftime("%I:%M:%S %p %d %B %Y")
        
        return formatted_timestamp
    
    @staticmethod
    def get_video_metadata(file_path):
        cmd = [
            "ffmpeg",
            "-i", file_path,
            "-f", "ffmetadata",
            "-"
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        metadata = {}
        for line in result.stdout.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                metadata[key.strip()] = value.strip()
        
        return metadata.get("comment", "")
