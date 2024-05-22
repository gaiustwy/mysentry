import cv2
import numpy as np
import torch
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

from dotenv import load_dotenv
import os
import smtplib

from email_alert import send_email_alert

# Load the .env
load_dotenv()

password = os.getenv("PASSWORD")
from_email = os.getenv("EMAIL_ADDRESS")
to_email = os.getenv("EMAIL_ADDRESS")

server = smtplib.SMTP("smtp.gmail.com: 587")
server.starttls()
server.login(from_email, password)

model = YOLO("yolov8n.pt")
device = "cuda:0" if torch.cuda.is_available() else "cpu"

background_subtractor = cv2.createBackgroundSubtractorMOG2(history = 1000, detectShadows=False)

video_capture = cv2.VideoCapture("http://192.168.86.31:4747/video")

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

# class ObjectDetection:
    # def __init__(self, capture_index):
    #     """Initializes an ObjectDetection instance with a given camera index."""
    #     self.capture_index = capture_index
    #     self.email_sent = False

    #     # model information
    #     self.model = YOLO("yolov8n.pt")

    #     # visual information
    #     self.annotator = None

    #     # device information
    #     self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

    # def predict(self, im0):
    #     """Run prediction using a YOLO model for the input image `im0`."""
    #     results = self.model.track(im0, vid_stride = 3)
    #     return results

    # def plot_bboxes(self, results, im0):
    #     """Plots bounding boxes on an image given detection results; returns annotated image and class IDs."""
    #     class_ids = []
    #     labels = []
    #     self.annotator = Annotator(im0, 3, results[0].names)
    #     boxes = results[0].boxes.xyxy.cpu()
    #     clss = results[0].boxes.cls.cpu().tolist()
    #     names = results[0].names
    #     print(results[0].boxes)
    #     for box, cls in zip(boxes, clss):
    #         class_ids.append(cls)
    #         label = names[int(cls)] # Get the label of the class
    #         labels.append(label)
    #         self.annotator.box_label(box, label=label, color=colors(int(cls), True))
    #     return im0, class_ids, labels

    # def __call__(self):
    #     """Executes object detection on video frames from a specified camera index, plotting bounding boxes and returning modified frames."""
    #     cap = cv2.VideoCapture(self.capture_index)
    #     assert cap.isOpened()
    #     # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    #     # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    #     while True:
    #         ret, im0 = cap.read()
    #         assert ret
    #         results = self.predict(im0)
            
    #         im0, class_ids, labels = self.plot_bboxes(results, im0)
            
    #         if len(class_ids) > 0:  # Only send email If not sent before
    #             if not self.email_sent:
    #                 send_email_alert(server, to_email, from_email, labels)
    #                 self.email_sent = True
    #         else:
    #             self.email_sent = False
            
    #         cv2.imshow("YOLOv8 Detection", im0)
            
    #         if cv2.waitKey(1) & 0xFF == ord("q"):
    #             break
    #     cap.release()
    #     cv2.destroyAllWindows()
    #     server.quit()

# detector = ObjectDetection(capture_index="http://192.168.86.31:4747/video")
# detector()