import subprocess
import os

def add_metadata_to_video(file_path, metadata):
    # Input and output must be different so temporary file is created
    # Extract the filename and extension
    filename = os.path.basename(file_path)
    # Create the temporary filename
    temp_filename = f"static/temp_{filename}"
    cmd = [
        "ffmpeg.exe",
        "-i", file_path,
        "-metadata", f"comment={metadata['comment']}",
        "-codec", "copy",
        temp_filename
    ]
    subprocess.run(cmd)
    print(file_path)
    print(temp_filename)
    # Replace the original file with the new one
    os.replace(temp_filename, file_path)
    
add_metadata_to_video("static/2024-05-25_00-15-21.mp4", {"comment": "This is a test comment"})