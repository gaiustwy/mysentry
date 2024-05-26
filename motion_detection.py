import cv2
import torch
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from datetime import datetime
import time

from dotenv import load_dotenv
import os
import subprocess

from email_alert import *

# Load the .env
# load_dotenv()

# Initialize the email server
server, email_address = initialize_email_server()

model = YOLO("yolov8n.pt")
device = "cuda:0" if torch.cuda.is_available() else "cpu"

background_subtractor = cv2.createBackgroundSubtractorMOG2(history = 1000, detectShadows=False)

video_capture = cv2.VideoCapture("http://192.168.86.31:4747/video")

fourcc = cv2.VideoWriter_fourcc(*"avc1")
recording = False
video_writer = None
filename = None

def add_metadata_to_video(file_path, metadata):
    # Input and output must be different so temporary file is created
    # Extract the filename and extension
    filename = os.path.basename(file_path)
    # Create the temporary filename
    temp_filename = f"static/temp_{filename}"

    comment = format_object_detected(metadata["comment"])
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
    

while video_capture.isOpened():
    # Read a frame from the video
    success, frame = video_capture.read()

    if not success:
        break

    results = model(frame, device = device, stream = True)

    labels = []

    for result in results:
        annotator = Annotator(frame, 3, result.names)
        boxes = result.boxes.xyxy.cpu().tolist()
        clss = result.boxes.cls.cpu().tolist()
        names = result.names

        person_detected = False

        for box, cls in zip(boxes, clss):
            cls_index = int(cls)
            # Get the label of the class
            label = names[cls_index] 
            labels.append(label) # List of labels e.g. ["person", "cat"]
            annotator.box_label(box, label=label, color=colors(cls_index, True))
       
            # If person is detected
            if (cls_index == 0):
                person_detected = True
        
        if person_detected and not recording:
            recording = True
            # Send first email alert
            send_first_email_alert(server, email_address)
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # "%d %B %Y %I:%M:%S %p"
            filename = f"static/{now}.mp4"
            video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
            print("Recording started")
            

        elif not person_detected and recording:
            recording = False
            video_writer.release()
            video_writer = None
            print(labels)



            # Add comment about object detected to metadata of the video
            # add_metadata_to_video(filename, {"comment": labels})

            # Send second email alert
            # send_second_email_alert(server, email_address, email_address, labels)
            print("Recording stopped")

        if recording:
            video_writer.write(frame)
        
    cv2.imshow("Press \"q\" to quit", frame)

    

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

if video_writer:
    video_writer.release()
video_capture.release()
cv2.destroyAllWindows()
server.quit()




# while video_capture.isOpened():
#     # Read a frame from the video
#     success, frame = video_capture.read()

#     if success:

#         fg_mask = background_subtractor.apply(frame)

#         _, thresh = cv2.threshold(fg_mask, 0, 255, cv2.THRESH_BINARY)

#         kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))

#         fg_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

#         fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

#         contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         for contour in contours:
#             x, y, w, h = cv2.boundingRect(contour)

#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
#         cv2.imshow("Press \"q\" to quit", frame)

#         # results = model(frame, device = device, stream = True)
        
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break

#     else:
#         # Break the loop if the end of the video is reached
#         break