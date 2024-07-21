import cv2
import torch
from ultralytics import YOLO
from datetime import datetime, timedelta

import os
import subprocess

from email_alert import *
from app import *

# Initialize the email server
server, email_address = initialize_email_server()

model = YOLO("yolov8n.pt")
device = "cuda:0" if torch.cuda.is_available() else "cpu"

background_subtractor = cv2.createBackgroundSubtractorMOG2(history=5000, varThreshold=24, detectShadows=False)

# video_capture = cv2.VideoCapture("http://192.168.86.31:4747/video")

fourcc = cv2.VideoWriter_fourcc(*"avc1") # *"avc1"
recording = False
video_writer = None
filename = None


def get_frame_from_clip(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    middle_frame_number = total_frames // 2

    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_number)
    _, frame = cap.read()
    cap.release()

    return frame

def detect_objects_in_frame(frame):
    objects_detected = []
    results = model.predict(frame, save=True, )
    for result in results:
        for box in result.boxes:
            class_id = int(box.data[0][-1])
            objects_detected.append(str(model.names[class_id]))

    print(objects_detected)
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
    
def generate_frames(video_capture, motion_detection_active):
    global recording, video_writer, filename

    frame_count = 0
    warm_up_frames = 240
    recording = False
    max_recording_duration = 20 # seconds
    recording_start_time = None
    frame_count_start = None
    fps = 20.0
    
    no_motion_frames = 0
    max_no_motion_frames = fps * 2 # Stop recording if no motion for 2 seconds

    while video_capture.isOpened():
        # Read a frame from the video
        success, frame = video_capture.read()

        if not success:
            break
        
        frame_count += 1

        # Prevents instant motion detection when the camera is first turned on
        if motion_detection_active and frame_count > warm_up_frames:
            fg_mask = background_subtractor.apply(frame)

            _, thresh = cv2.threshold(fg_mask, 0, 255, cv2.THRESH_BINARY)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))

            fg_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            motion_detected = False

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)

                if area > 30000:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    print("Motion detected")
                    motion_detected = True
                    no_motion_frames = 0

                    if not recording:
                        recording = True
                        frame_count_start = frame_count
                        recording_start_time = datetime.now()
                        filename = f"static/{recording_start_time.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
                        video_writer = cv2.VideoWriter(filename, fourcc, fps, (frame.shape[1], frame.shape[0]))
                        print("Recording started")
            
            # if not motion_detected:
            #     no_motion_frames += 1

            if recording:
                video_writer.write(frame)
                if motion_detected == False or (frame_count - frame_count_start) >= (fps * max_recording_duration):
                    recording = False
                    video_writer.release()
                    print("Stopped recording")

                    # Perform object detection on the middle frame
                    frame = get_frame_from_clip(filename)
                    frame_path = f"static/preview.jpg"
                    cv2.imwrite(frame_path, frame)
                    objects_detected = detect_objects_in_frame(frame)
                    add_metadata_to_video(filename, objects_detected)

                    # Send second email alert
                    # send_second_email_alert(server, email_address, objects_detected,
                    #                         recording_start_time.strftime("%I:%M:%S %p %d %B %Y"), frame_path)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    video_capture.release()
    if video_writer is not None:
        video_writer.release()





    #     results = model(frame, device = device, stream = True)

    #     labels = []

    #     for result in results:
    #         annotator = Annotator(frame, 3, result.names)
    #         boxes = result.boxes.xyxy.cpu().tolist()
    #         clss = result.boxes.cls.cpu().tolist()
    #         names = result.names

    #         person_detected = False

    #         for box, cls in zip(boxes, clss):
    #             cls_index = int(cls)
    #             # Get the label of the class
    #             label = names[cls_index] 
    #             labels.append(label) # List of labels e.g. ["person", "cat"]
    #             annotator.box_label(box, label=label, color=colors(cls_index, True))
        
    #             # If person is detected
    #             if (cls_index == 0):
    #                 person_detected = True
            
    #         if person_detected and not recording:
    #             recording = True
    #             # Send first email alert
    #             send_first_email_alert(server, email_address)
    #             now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # "%d %B %Y %I:%M:%S %p"
    #             filename = f"static/{now}.mp4"
    #             video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
    #             print("Recording started")
                

    #         elif not person_detected and recording:
    #             recording = False
    #             video_writer.release()
    #             video_writer = None
    #             print(labels)



    #             # Add comment about object detected to metadata of the video
    #             # add_metadata_to_video(filename, {"comment": labels})

    #             # # Send second email alert
    #             # send_second_email_alert(server, email_address, email_address, labels)
    #             print("Recording stopped")

    #         if recording:
    #             video_writer.write(frame)
            
    #     _, buffer = cv2.imencode('.jpg', frame)
    #     frame = buffer.tobytes()
    #     yield (b'--frame\r\n'
    #            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # if video_writer:
    #     video_writer.release()
    # video_capture.release()
    # cv2.destroyAllWindows()
    # server.quit()




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