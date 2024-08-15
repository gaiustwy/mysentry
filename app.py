import os
import cv2
import config
from config import clips_folder_path
from flask import Flask, render_template, request, redirect, jsonify, url_for, Response
from generate_frames import generate_frames
from video_handler import VideoHandler

app = Flask(__name__)
video_capture = None
camera_url = None

@app.route('/')
def index():
    camera_started = video_capture is not None and video_capture.isOpened()
    return render_template('index.html', camera_started=camera_started, motion_detection_active=config.motion_detection_active)

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global video_capture, camera_url
    new_camera_url = request.form['camera_url']

    if new_camera_url.isdigit():
        new_camera_url = int(new_camera_url)
    
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
    if config.motion_detection_active:
        config.motion_detection_active = False
    else:
        config.motion_detection_active = True

    return jsonify({"motion_detection_active": config.motion_detection_active}), 200

@app.route('/set_exclusion_zones', methods=['POST'])
def set_exclusion_zones():
    config.exclusion_zones = request.json.get('zones')
    return '', 204

@app.route('/clear_exclusion_zones', methods=['POST'])
def clear_exclusion_zones():
    config.exclusion_zones = []
    return '', 204

@app.route('/video_feed')
def video_feed():
    if video_capture and video_capture.isOpened():
        return Response(generate_frames(video_capture), 
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Camera not started", 400

@app.route('/delete/<clip_name>')
def delete_clip(clip_name):
    clip_path = os.path.join(app.root_path, clips_folder_path, clip_name)
    
    if os.path.exists(clip_path):
        os.remove(clip_path)
    return redirect(url_for('clips'))

@app.route('/delete_all_clips', methods=['POST'])
def delete_all_clips():
    clips_folder = os.path.join(app.root_path, clips_folder_path)
    clips = [f for f in os.listdir(clips_folder) if f.endswith('.mp4') and f != 'masked_video.mp4']

    for clip in clips:
        clip_path = os.path.join(clips_folder, clip)
        if os.path.exists(clip_path):
            os.remove(clip_path)

    return redirect(url_for('clips'))

@app.route('/clips')
def clips():
    clips_folder = os.path.join(app.root_path, clips_folder_path)
    clips = [f for f in os.listdir(clips_folder) if f.endswith('.mp4') and f != 'masked_video.mp4']
    
    # Get the full path for each clip
    clips_full_path = [os.path.join(clips_folder, f) for f in clips]

    # Sort the clips by their creation time in descending order
    clips_sorted = sorted(clips_full_path, key=os.path.getctime, reverse=True)

    # Extract the filenames from the sorted full paths and format the creation time
    formatted_clips = []
    for clip_path in clips_sorted:
        clip_name = os.path.basename(clip_path)
        timestamp = VideoHandler.get_timestamp_from_filename(clip_path)
        comment = VideoHandler.get_video_metadata(clip_path)
        formatted_clips.append((clip_name, timestamp, comment))

    return render_template('clips.html', clips=formatted_clips)

if __name__ == '__main__':
    app.run(debug=True)





