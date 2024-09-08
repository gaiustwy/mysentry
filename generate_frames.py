import cv2
import config
from config import temp_folder_path
from email_alert import EmailAlert
from video_handler import VideoHandler
from motion_detector import MotionDetector

# Initialize necessary classes
email_alert = EmailAlert()
motion_detector = MotionDetector()
video_handler = VideoHandler()
video_handler_masked = VideoHandler()

def generate_frames(video_capture):
    """
    Generates frames from the video capture and processes them for motion detection.

    Args:
        video_capture (cv2.VideoCapture): Video capture object.

    Yields:
        bytes: Encoded video frames to be streamed to the client.
    """
    frame_count = 0 # Counter for the number of frames processed
    recording = False # Flag to indicate if recording is in progres
    no_motion_frame_count = 0  # Counter for consecutive frames without motion
    no_motion_threshold = 60  # Threshold before stopping the recording in frames
    motion_detected_frames = [] # List to track frames where motion was detected
    motion_detected = False # Flag to indicate if motion is detected in frame

    while video_capture.isOpened():
        # Read a frame from the video
        success, frame = video_capture.read()

        if not success:
            break

        if config.motion_detection_active:
            # Detect motion by analyzing the current frame
            contours = motion_detector.detect_motion(frame)
            motion_detected = False

            for contour in contours:
                # Check if the detected contour is valid (not too small/big or in an exclusion zone)
                if motion_detector.is_valid_contour(frame, contour):
                    print("Motion detected")
                    motion_detected = True

                    # Draw a rectangle around the detected motion
                    MotionDetector.draw_rectangle(frame, contour, (0, 255, 0), 2)
                    
                    # Reset the counter whenever motion is detected
                    no_motion_frame_count = 0

                    if not recording:
                        print("Recording started")
                        recording = True

                        # Initialize the video recording for both regular and masked videos
                        video_handler.initialize_recording(frame)
                        video_handler_masked.initialize_recording(frame, f"{temp_folder_path}/masked_video.mp4")
                        
            if recording:
                # Write the current frame to the video file
                video_handler.write_frame(frame)

                # Count the number of frames while recording
                frame_count += 1
                
                if not motion_detected:
                    no_motion_frame_count += 1
                else:
                    # Apply the motion mask to the frame and write to the masked video file
                    masked_frame = motion_detector.apply_mask(frame, contour)
                    video_handler_masked.write_frame(masked_frame)

                    # Track the frame where motion is detected
                    motion_detected_frames.append(frame_count)

                    # Reset the no-motion counter when motion is detected
                    no_motion_frame_count = 0

                # Stop recording if no motion is detected for a certain number of frames or the video exceeds the maximum length
                if no_motion_frame_count >= no_motion_threshold or frame_count >= video_handler.maximum_fps:
                    print("Stopped recording")
                    recording = False

                    # Stop the video recordings
                    video_handler.stop_recording()
                    video_handler_masked.stop_recording()
                    
                    # Save a preview image from the video and masked video
                    video_handler.save_preview(motion_detected_frames)
                    video_handler_masked.save_preview(motion_detected_frames, f"{temp_folder_path}/masked_preview.jpg")

                    # Detect objects in the saved masked preview image and save the prediction results
                    motion_detector.detect_objects(video_handler_masked.preview_path, f"{temp_folder_path}/prediction_image.jpg")

                    # Add detected objects metadata to the video file
                    video_handler.add_metadata_to_video(motion_detector.objects_detected)

                    # Send an email alert with the motion detection results
                    email_alert.send_motion_detected_email(
                        motion_detector.objects_detected, 
                        video_handler.start_time.strftime("%I:%M:%S %p %d %B %Y"), 
                        video_handler.preview_path, 
                        motion_detector.prediction_output_path
                    )

                    # Clear the both list for the next motion detection event
                    motion_detector.objects_detected.clear()
                    motion_detected_frames.clear()

                    # Reset the frame counter
                    frame_count = 0

        # Encode the frame as JPEG to stream it to the client
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the encoded frame in a format suitable for HTTP streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    video_capture.release()