from flask import Flask, render_template, redirect, url_for, Response
import os
from datetime import datetime
from motion_detection import generate_frames
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
	static_folder = os.path.join(app.root_path, 'static')
	clips = [f for f in os.listdir(static_folder) if f.endswith('.mp4')]
	return render_template('index.html', clips = clips)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/delete/<clip_name>')
def delete_clip(clip_name):
    clip_path = os.path.join(app.root_path, 'static', clip_name)
    if os.path.exists(clip_path):
        os.remove(clip_path)
    return redirect(url_for('clips'))

@app.route('/clips')
def clips():
    static_folder = os.path.join(app.root_path, 'static')
    clips = [f for f in os.listdir(static_folder) if f.endswith('.mp4')]

    # Get the full path for each clip
    clips_full_path = [os.path.join(static_folder, f) for f in clips]
    
    # Sort the clips by their creation time in descending order
    clips_sorted = sorted(clips_full_path, key=os.path.getctime, reverse=True)

    # Extract the filenames from the sorted full paths and format the creation time
    formatted_clips = []
    for clip_path in clips_sorted:
        clip_name = os.path.basename(clip_path)
        timestamp = get_timestamp_from_filename(clip_path)
        comment = get_video_metadata(clip_path)
        formatted_clips.append((clip_name, timestamp, comment))

    return render_template('clips.html', clips=formatted_clips)

if __name__ == '__main__':
    app.run(debug=True)

def get_timestamp_from_filename(filepath):
    # Extract the filename from the path
    filename = os.path.basename(filepath)

    # Extract the timestamp string from the filename by removing the file extension
    timestamp_str = filename.split('.')[0]  

    # Parse the timestamp string into a datetime object
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

    # Format the datetime object into the string new format
    formatted_timestamp = timestamp.strftime("%I:%M:%S %p %d %B %Y")
    
    return formatted_timestamp

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

