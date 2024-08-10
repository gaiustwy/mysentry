import cv2
import torch
from ultralytics import YOLO
from datetime import datetime
import numpy as np

import os
import subprocess

from email_alert import *
from app import *
import config

# Initialize the email server
server, email_address = initialize_email_server()

model = YOLO("yolov8n.pt")
device = "cuda:0" if torch.cuda.is_available() else "cpu"

background_subtractor = cv2.createBackgroundSubtractorMOG2(history=1000, varThreshold=24, detectShadows=False)

# video_capture = cv2.VideoCapture("http://192.168.86.31:4747/video")

fourcc = cv2.VideoWriter_fourcc(*"avc1") # *"avc1"
recording = False
video_writer = None
filename = None

def get_frame_from_clip(video_path, frame_number):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    _, frame = cap.read()
    cap.release()

    return frame

def detect_objects_in_frame(frame):
    objects_detected = []

    results = model.predict(frame)
    for result in results:
        for box in result.boxes:
            class_id = int(box.data[0][-1])
            objects_detected.append(str(model.names[class_id]))
        result.save(filename="static/prediction_image.jpg")

    return objects_detected

def add_metadata_to_video(file_path, metadata):
    # Input and output must be different so temporary file is created
    # Extract the filename and extension
    filename = os.path.basename(file_path)
    # Create the temporary filename
    temp_filename = f"static/temp_{filename}"

    comment = format_object_detected(metadata)
    cmd = [
        "ffmpeg",
        "-i", file_path,
        "-metadata", f"comment={comment}",
        "-codec", "copy",
        temp_filename
    ]
    subprocess.run(cmd)
    # Replace the original file with the new one
    os.replace(temp_filename, file_path)

def is_in_exclusion_zone(contour_x, contour_y, exclusion_zones):
    for zone in exclusion_zones:
        # Normalize the coordinates
        zone_start_x = min(zone['startX'], zone['endX'])
        zone_end_x = max(zone['startX'], zone['endX'])
        zone_start_y = min(zone['startY'], zone['endY'])
        zone_end_y = max(zone['startY'], zone['endY'])

        if (zone_start_x <= contour_x <= zone_end_x and zone_start_y <= contour_y <= zone_end_y):
            return True
    return False
    
def generate_frames(video_capture):
    global recording, video_writer, filename

    frame_count = 0
    recording = False
    max_recording_duration = 20 # seconds
    recording_start_time = None
    fps = 24.0
    no_motion_frame_count = 0  # Counter for consecutive frames without motion
    no_motion_threshold = 60  # Threshold for stopping the recording (e.g., 30 frames)
    motion_detected_frames = []

    while video_capture.isOpened():
        # Read a frame from the video
        success, frame = video_capture.read()

        if not success:
            break

        # Calculate the area of the frame
        frame_height, frame_width = frame.shape[:2]
        frame_area = frame_width * frame_height

        min_area = frame_area * 0.05
        max_area = frame_area * 0.9

        if config.motion_detection_active:
            fg_mask = background_subtractor.apply(frame)

            _, thresh = cv2.threshold(fg_mask, 0, 255, cv2.THRESH_BINARY)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))

            fg_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            motion_detected = False

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                object_area = cv2.contourArea(contour)

                if min_area < object_area < max_area and not is_in_exclusion_zone(x, y, config.exclusion_zones):
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    print("Motion detected")
                    motion_detected = True
                    # Reset the counter whenever motion is detected
                    no_motion_frame_count = 0 

                    if not recording:
                        recording = True
                        recording_start_time = datetime.now()
                        filename = f"static/{recording_start_time.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
                        video_writer = cv2.VideoWriter(filename, fourcc, fps, (frame.shape[1], frame.shape[0]))
                        video_writer_temp = cv2.VideoWriter("static/temp_video.mp4", fourcc, fps, (frame.shape[1], frame.shape[0]))
                        print("Recording started")

            if recording:
                video_writer.write(frame)

                motion_mask = np.zeros_like(fg_mask)
                cv2.rectangle(motion_mask, (x, y), (x + w, y + h), (255, 255, 255), -1)
                masked_frame = cv2.bitwise_and(frame, frame, mask=motion_mask)
                video_writer_temp.write(masked_frame)
                frame_count += 1
                
                if not motion_detected:
                    no_motion_frame_count += 1
                else:
                    no_motion_frame_count = 0
                    motion_detected_frames.append(frame_count)

                if no_motion_frame_count >= no_motion_threshold or frame_count >= (fps * max_recording_duration):
                    recording = False
                    video_writer.release()
                    video_writer_temp.release()
                    frame_count = 0
                    print("Stopped recording")

                    index = len(motion_detected_frames) // 2
                    middle_frame_number = motion_detected_frames[index]

                    frame = get_frame_from_clip(filename, middle_frame_number)
                    cv2.imwrite("static/preview.jpg", frame)

                    masked_frame = get_frame_from_clip("static/temp_video.mp4", middle_frame_number)
                    cv2.imwrite("static/preview_masked.jpg", masked_frame) # DELETE THIS LINE

                    objects_detected = detect_objects_in_frame(masked_frame)
                    add_metadata_to_video(filename, objects_detected)

                    # # Send second email alert
                    # send_second_email_alert(server, email_address, objects_detected,
                    #                         recording_start_time.strftime("%I:%M:%S %p %d %B %Y"), "static/preview.jpg", "static/prediction_image.jpg")

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    video_capture.release()
    if video_writer is not None:
        video_writer.release()