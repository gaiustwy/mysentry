import cv2
import numpy as np
import config
from ultralytics import YOLO

class MotionDetector:
    """
    A class to handle motion detection and object recognition in video frames.
    """

    def __init__(self):
        """
        Initializes the motion detector with a YOLO model and a background subtractor.
        """
        # Load the YOLO model for object detection
        self.model = YOLO("yolov8n.pt")

        # Create a background subtractor for motion detection
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(history=1000, varThreshold=24, detectShadows=False)

        self.prediction_output_path = None 
        self.objects_detected = []  
    
    def detect_motion(self, frame):
        """
        Detects motion in a given video frame by applying background subtraction.

        Args:
            frame (numpy.ndarray): The current video frame.

        Returns:
            contours (list): A list of contours representing the areas with detected motion.
        """
        # Apply the background subtractor to get the foreground mask
        fg_mask = self.background_subtractor.apply(frame)

        # Apply thresholding to convert the mask to a binary image
        _, thresh = cv2.threshold(fg_mask, 0, 255, cv2.THRESH_BINARY)

        # Create a structuring element for morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))

        # Apply morphological operations to clean up the mask
        fg_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

        # Find contours in the mask, representing moving objects
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        return contours
    
    def is_valid_contour(self, frame, contour):
        """
        Checks if a contour is valid based on area bounds and exclusion zones.

        Args:
            frame (numpy.ndarray): The current video frame.
            contour (list): The contour to validate.

        Returns:
            bool: True if the contour is valid, False otherwise.
        """
        # Check if the contour is within the specified area bounds and not in an exclusion zone
        is_within_area_bounds = self.is_within_area_bounds(frame, contour, 0.05, 0.9)
        is_in_exclusion_zone = self.is_in_exclusion_zone(contour, config.exclusion_zones)
        return is_within_area_bounds and not is_in_exclusion_zone
    
    def is_within_area_bounds(self, frame, contour, min_ratio, max_ratio):
        """
        Checks if a contour's area is within the given bounds relative to the frame size.

        Args:
            frame (numpy.ndarray): The current video frame.
            contour (list): The contour to check.
            min_ratio (float): Minimum area ratio relative to the frame.
            max_ratio (float): Maximum area ratio relative to the frame.

        Returns:
            bool: True if the contour's area is within the bounds, False otherwise.
        """
        # Calculate the area of the contour
        object_area = cv2.contourArea(contour)

        # Calculate the area of the frame
        frame_height, frame_width = frame.shape[:2]
        frame_area = frame_width * frame_height

        # Determine the minimum and maximum allowable areas for a valid contour
        min_area = frame_area * min_ratio
        max_area = frame_area * max_ratio

        # Check if the contour's area is within the specified bounds
        return min_area < object_area < max_area
    
    def is_in_exclusion_zone(self, contour, exclusion_zones):
        """
        Checks if a contour is located within any exclusion zones.

        Args:
            contour (list): The contour to check.
            exclusion_zones (list): A list of exclusion zones defined by rectangles.

        Returns:
            bool: True if the contour is in an exclusion zone, False otherwise.
        """
        # Get the bounding rectangle of the contour
        x, y, _, _ = cv2.boundingRect(contour)

        # Check if the contour's bounding box intersects any exclusion zone
        for zone in exclusion_zones:
            zone_start_x = min(zone['startX'], zone['endX'])
            zone_end_x = max(zone['startX'], zone['endX'])
            zone_start_y = min(zone['startY'], zone['endY'])
            zone_end_y = max(zone['startY'], zone['endY'])
            if (zone_start_x <= x <= zone_end_x and zone_start_y <= y <= zone_end_y):
                return True
        return False
    
    def detect_objects(self, frame, prediction_output_path):
        """
        Detects objects in the given frame using the YOLO model and saves the prediction.

        Args:
            frame (numpy.ndarray): The current video frame.
            prediction_output_path (str): The file path to save the prediction image.
        """
        self.prediction_output_path = prediction_output_path

        # Predict objects in the frame using the YOLO model
        results = self.model.predict(frame)

        # Extract detected objects and save the prediction image
        for result in results:
            for box in result.boxes:
                class_id = int(box.data[0][-1])
                self.objects_detected.append(str(self.model.names[class_id]))
            result.save(filename= prediction_output_path)

    @staticmethod
    def apply_mask(frame, contour):
        """
        Applies a mask to the frame, keeping only the area inside the contour visible.

        Args:
            frame (numpy.ndarray): The current video frame.
            contour (list): The contour to apply the mask to.

        Returns:
            masked_frame (numpy.ndarray): The masked video frame.
        """
        # Get the bounding rectangle of the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Create a blank mask with the same dimensions as the frame
        frame_height, frame_width = frame.shape[:2]
        mask = np.zeros((frame_height, frame_width), dtype=np.uint8)

        # Draw a filled rectangle on the mask at the contour's location
        cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)

        # Apply the mask to the frame, keeping only the area inside the contour visible
        masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

        return masked_frame
    
    @staticmethod
    def draw_rectangle(frame, contour, rgb_color, thickness):
        """
        Draws a rectangle around the contour on the frame.

        Args:
            frame (numpy.ndarray): The current video frame.
            contour (list): The contour to draw the rectangle around.
            rgb_color (tuple): The color of the rectangle in RGB format.
            thickness (int): The thickness of the rectangle's border.
        """
        # Get the bounding rectangle of the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Draw the rectangle on the frame with the specified color and thickness
        cv2.rectangle(frame, (x, y), (x + w, y + h), rgb_color, thickness)