import cv2
import numpy as np
import config
from ultralytics import YOLO

class MotionDetector:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(history=1000, varThreshold=24, detectShadows=False)
        self.prediction_output_path = None
        self.objects_detected = []
    
    def detect_motion(self, frame):
            fg_mask = self.background_subtractor.apply(frame)

            _, thresh = cv2.threshold(fg_mask, 0, 255, cv2.THRESH_BINARY)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))

            fg_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            return contours
    
    def is_valid_contour(self, frame, contour):
        is_within_area_bounds = self.is_within_area_bounds(frame, contour, 0.05, 0.9)
        is_in_exclusion_zone = self.is_in_exclusion_zone(contour, config.exclusion_zones)
        return is_within_area_bounds and not is_in_exclusion_zone
    
    def is_within_area_bounds(self, frame, contour, min_ratio, max_ratio):
        object_area = cv2.contourArea(contour)

        # Calculate the area of the frame
        frame_height, frame_width = frame.shape[:2]
        frame_area = frame_width * frame_height

        min_area = frame_area * min_ratio
        max_area = frame_area * max_ratio

        return min_area < object_area < max_area
    
    def is_in_exclusion_zone(self, contour, exclusion_zones):
        x, y, _, _ = cv2.boundingRect(contour)

        for zone in exclusion_zones:
            zone_start_x = min(zone['startX'], zone['endX'])
            zone_end_x = max(zone['startX'], zone['endX'])
            zone_start_y = min(zone['startY'], zone['endY'])
            zone_end_y = max(zone['startY'], zone['endY'])
            if (zone_start_x <= x <= zone_end_x and zone_start_y <= y <= zone_end_y):
                return True
        return False
    
    def detect_objects(self, frame, prediction_output_path):
        self.prediction_output_path = prediction_output_path
        results = self.model.predict(frame)
        for result in results:
            for box in result.boxes:
                class_id = int(box.data[0][-1])
                self.objects_detected.append(str(self.model.names[class_id]))
            result.save(filename= prediction_output_path)

    @staticmethod
    def apply_mask(frame, contour):
        x, y, w, h = cv2.boundingRect(contour)
        frame_height, frame_width = frame.shape[:2]
        mask = np.zeros((frame_height, frame_width), dtype=np.uint8)
        cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)
        masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

        return masked_frame
    
    @staticmethod
    def draw_rectangle(frame, contour, rgb_color, thickness):
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), rgb_color, thickness)