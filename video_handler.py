import os
import cv2
import subprocess
from datetime import datetime
from utilities import format_object_detected
from config import temp_folder_path, clips_folder_path

class VideoHandler:
    """
    A class to handle video recording, processing, and metadata management.
    """

    def __init__(self):
        """
        Initializes the VideoHandler with default settings.
        """
        self.fourcc = cv2.VideoWriter_fourcc(*"avc1") # Codec for encoding video
        self.fps = 24.0 # Frames per second for the output video
        self.video_writer = None # Video writer object
        self.start_time = None # Start time of the recording
        self.filename = None # File path for the output video
        self.preview_path = None # Path for the preview image
        self.maximum_duration = 20 # Maximum duration for video recording in seconds

    def initialize_recording(self, frame, filename=None):
        """
        Initializes video recording.

        Args:
            frame (numpy.ndarray): The first frame of the video, used to determine frame size.
            filename (str, optional): The name of the video file. Defaults to a timestamped filename.
        """
        self.start_time = datetime.now() # Record the start time of the video

        # Generate a filename if not provided
        if filename is None:
            self.filename = f"{clips_folder_path}/{self.start_time.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
        else:
            self.filename = filename

        # Initialize the VideoWriter object with the frame size, codec, and fps
        self.video_writer = cv2.VideoWriter(self.filename, self.fourcc, self.fps, (frame.shape[1], frame.shape[0]))
    
    def write_frame(self, frame):
        """
        Writes a single frame to the video file.

        Args:
            frame (numpy.ndarray): The frame to write to the video.
        """
        self.video_writer.write(frame)

    def stop_recording(self):
        """
        Stops the video recording and releases the VideoWriter object.
        """
        self.video_writer.release()
    
    def save_preview(self, total_frames, preview_path=None):
        """
        Saves a preview image extracted from the middle of the video.

        Args:
            total_frames (list): A list of frame indices for the video.
            preview_path (str, optional): The path to save the preview image. Defaults to a temp folder.
        """
        # Calculate the middle frame index and extract the corresponding frame
        index = len(total_frames) // 2
        middle_frame_number = total_frames[index]
        frame = self.get_frame_from_clip(middle_frame_number)

        # Generate the preview path if not provided
        if preview_path is None:
            self.preview_path = f"{temp_folder_path}/preview.jpg"
        else:
            self.preview_path = preview_path
        
        # Save the extracted frame as the preview image
        cv2.imwrite(self.preview_path, frame)
    
    def get_frame_from_clip(self, frame_number):
        """
        Retrieves a specific frame from the video file.

        Args:
            frame_number (int): The index of the frame to retrieve.

        Returns:
            numpy.ndarray: The requested frame.
        """
        # Open the video file and set the frame position
        cap = cv2.VideoCapture(self.filename)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read the frame from the video
        _, frame = cap.read()
        cap.release()

        return frame
    
    def add_metadata_to_video(self, metadata):
        """
        Adds metadata (e.g., detected objects) to the video file.

        Args:
            metadata (list): List of detected objects to be added as metadata.
        """
        # Input and output must be different so temporary file is created
        # Extract the filename and extension and create a temporary filename
        filename = os.path.basename(self.filename)
        temp_filename = f"{temp_folder_path}/temp_{filename}"

        # Format the metadata comment using the utility function
        comment = format_object_detected(metadata)

        # FFmpeg command to add metadata to the video
        cmd = [
            "ffmpeg",
            "-i", self.filename, # Input video file
            "-metadata", f"comment={comment}", # Add metadata as a comment
            "-codec", "copy", # Copy the original codec (no re-encoding)
            temp_filename # Output to a temporary file
        ]
        
        # Execute the command to add metadata
        subprocess.run(cmd)

        # Replace the original video with the new one containing metadata
        os.replace(temp_filename, self.filename)
        
    @property
    def maximum_fps(self):
        """
        Calculates the maximum number of frames based on the FPS and maximum duration.

        Returns:
            float: The maximum number of frames allowed for the recording.
        """
        return self.fps * self.maximum_duration
    
    @staticmethod
    def get_timestamp_from_filename(filename):
        """
        Extracts and formats the timestamp from the video filename.

        Args:
            filename (str): The video filename.

        Returns:
            str: Formatted timestamp (e.g., "12:34:56PM 15 August 2024").
        """
        # Extract the filename and remove the extension to get the timestamp string
        filename = os.path.basename(filename)
        timestamp_str = filename.split('.')[0]  

        # Parse the timestamp string into a datetime object
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

        # Format the datetime object into the string new format
        formatted_timestamp = timestamp.strftime("%I:%M:%S%p %d %B %Y")
        
        return formatted_timestamp
    
    @staticmethod
    def get_video_metadata(file_path):
        """
        Retrieves metadata from a video file.

        Args:
            file_path (str): Path to the video file.

        Returns:
            str: The comment metadata from the video, if available.
        """
        # FFmpeg command to extract metadata from the video file
        cmd = [
            "ffmpeg",
            "-i", file_path, # Input video file
            "-f", "ffmetadata", # Output format to ffmetadata
            "-"
        ]

        # Execute the command and capture the output
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Parse the output to extract key-value pairs
        metadata = {}
        for line in result.stdout.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                metadata[key.strip()] = value.strip()
        
        # Return the comment metadata if available
        return metadata.get("comment", "")
