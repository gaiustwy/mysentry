import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import time

import cv2
import numpy as np
import torch
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

from dotenv import load_dotenv
import os
from collections import Counter

#http://192.q168.86.31:4747/video

# Load the .env file
load_dotenv()

password = os.getenv("PASSWORD")
from_email = os.getenv("EMAIL_ADDRESS")
to_email = os.getenv("EMAIL_ADDRESS")

server = smtplib.SMTP("smtp.gmail.com: 587")
server.starttls()
server.login(from_email, password)

def send_email(to_email, from_email, labels):
	"""Sends an email notification indicating the number of objects detected; defaults to 1 object."""
	message = MIMEMultipart()
	object_counter = Counter()
	
	message["From"] = from_email
	message["To"] = to_email
	message["Subject"] = "Motion Detected"
     
	for label in labels: 
		object_counter[label] += 1
	
	message_body = f"Alert - {len(labels)} objects have been detected: "
	message_body += ", ".join([f"{count} {label}" for label, count in object_counter.items()])

	message.attach(MIMEText(message_body, "plain"))
	server.sendmail(from_email, to_email, message.as_string())
    
class ObjectDetection:
    def __init__(self, capture_index):
        """Initializes an ObjectDetection instance with a given camera index."""
        self.capture_index = capture_index
        self.email_sent = False

        # model information
        self.model = YOLO("yolov8n.pt")

        # visual information
        self.annotator = None
        self.start_time = 0
        self.end_time = 0

        # device information
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

    def predict(self, im0):
        """Run prediction using a YOLO model for the input image `im0`."""
        results = self.model.track(im0, vid_stride = 3)
        return results

    def plot_bboxes(self, results, im0):
        """Plots bounding boxes on an image given detection results; returns annotated image and class IDs."""
        class_ids = []
        labels = []
        self.annotator = Annotator(im0, 3, results[0].names)
        boxes = results[0].boxes.xyxy.cpu()
        clss = results[0].boxes.cls.cpu().tolist()
        names = results[0].names
        print(results[0].boxes)
        for box, cls in zip(boxes, clss):
            class_ids.append(cls)
            label = names[int(cls)] # Get the label of the class
            labels.append(label)
            self.annotator.box_label(box, label=label, color=colors(int(cls), True))
        return im0, class_ids, labels

    def __call__(self):
        """Executes object detection on video frames from a specified camera index, plotting bounding boxes and returning modified frames."""
        cap = cv2.VideoCapture(self.capture_index)
        assert cap.isOpened()
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        while True:
            self.start_time = time()
            ret, im0 = cap.read()
            assert ret
            results = self.predict(im0)
            
            im0, class_ids, labels = self.plot_bboxes(results, im0)
			
            # if len(class_ids) > 0:  # Only send email If not sent before
            #     if not self.email_sent:
            #         send_email(to_email, from_email, labels)
            #         self.email_sent = True
            # else:
            #     self.email_sent = False
            
            cv2.imshow("YOLOv8 Detection", im0)
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()
        server.quit()

detector = ObjectDetection(capture_index="http://192.168.86.31:4747/video")
detector()