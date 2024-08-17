import os
import cv2
import config
from dotenv import load_dotenv
from config import clips_folder_path
from video_handler import VideoHandler
from generate_frames import generate_frames
from flask import Flask, render_template, request, redirect, jsonify, url_for, Response

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
video_capture = None
camera_url = None

@app.route('/')
def index():
    """
    Render the main index page.
    This checks if the camera has started and passes the motion detection state to the template.
    """
    camera_started = video_capture is not None and video_capture.isOpened()
    return render_template('index.html', camera_started=camera_started, motion_detection_active=config.motion_detection_active)

@app.route('/start_camera', methods=['POST'])
def start_camera():
    """
    Start or switch the camera based on the URL provided by the user.
    If a new camera URL is provided, it closes the existing camera (if any)
    and starts capturing from the new one.
    """
    global video_capture, camera_url
    new_camera_url = request.form['camera_url']

    # Convert to integer if the URL is a digit (for local webcam ID)
    if new_camera_url.isdigit():
        new_camera_url = int(new_camera_url)
    
    # Only switch cameras if a different URL is provided
    if camera_url != new_camera_url:
        # Close the existing camera if it is open
        if video_capture and video_capture.isOpened():
            video_capture.release()
        
        # Update the camera URL and start the new camera
        camera_url = new_camera_url
        video_capture = cv2.VideoCapture(camera_url)
    
    return redirect(url_for('index'))

@app.route('/toggle_motion_detection', methods=['POST'])
def toggle_motion_detection():
    """
    Toggle the motion detection state between active and inactive.
    Returns the new state as JSON.
    """
    if config.motion_detection_active:
        config.motion_detection_active = False
    else:
        config.motion_detection_active = True

    return jsonify({"motion_detection_active": config.motion_detection_active}), 200

@app.route('/set_exclusion_zones', methods=['POST'])
def set_exclusion_zones():
    """
    Set the exclusion zones for motion detection based on the coordinates received.
    """
    config.exclusion_zones = request.json.get('zones')
    return '', 204

@app.route('/clear_exclusion_zones', methods=['POST'])
def clear_exclusion_zones():
    """
    Clear all the exclusion zones for motion detection.
    """
    config.exclusion_zones = []
    return '', 204

@app.route('/video_feed')
def video_feed():
    """
    Provide a video feed from the camera if it is started.
    Streams the frames to the client using a multipart response.
    """
    if video_capture and video_capture.isOpened():
        return Response(generate_frames(video_capture), 
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Camera not started", 400

@app.route('/delete/<clip_name>')
def delete_clip(clip_name):
    """
    Delete a specific video clip by filename.
    Redirects to the clips page after deletion.
    """
    clip_path = os.path.join(app.root_path, clips_folder_path, clip_name)
    
    if os.path.exists(clip_path):
        os.remove(clip_path)
    return redirect(url_for('clips'))

@app.route('/delete_all_clips', methods=['POST'])
def delete_all_clips():
    """
    Delete all video clips in the clips folder.
    Redirects to the clips page after deletion.
    """
    clips_folder = os.path.join(app.root_path, clips_folder_path)
    clips = [f for f in os.listdir(clips_folder) if f.endswith('.mp4')]

    for clip in clips:
        clip_path = os.path.join(clips_folder, clip)
        if os.path.exists(clip_path):
            os.remove(clip_path)

    return redirect(url_for('clips'))

@app.route('/clips')
def clips():
    """
    Display the available video clips on the clips page.
    Clips are sorted by creation time in descending order and shown with the metadata.
    """
    clips_folder = os.path.join(app.root_path, clips_folder_path)
    clips = [f for f in os.listdir(clips_folder) if f.endswith('.mp4')]
    
    # Get the full path for each clip and sort by creation time
    clips_full_path = [os.path.join(clips_folder, f) for f in clips]
    clips_sorted = sorted(clips_full_path, key=os.path.getctime, reverse=True)

    # Extract filenames and metadata for the sorted clips
    formatted_clips = []
    for clip_path in clips_sorted:
        clip_name = os.path.basename(clip_path)
        timestamp = VideoHandler.get_timestamp_from_filename(clip_path)
        comment = VideoHandler.get_video_metadata(clip_path)
        formatted_clips.append((clip_name, timestamp, comment))

    return render_template('clips.html', clips=formatted_clips)

if __name__ == '__main__':
    app.run(debug=True)





