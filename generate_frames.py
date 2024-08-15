import cv2
import config
from config import temp_folder_path
from email_alert import EmailAlert
from video_handler import VideoHandler
from motion_detection import MotionDetector

email_alert = EmailAlert()
motion_detector = MotionDetector()
video_handler = VideoHandler()
video_handler_masked = VideoHandler()

def generate_frames(video_capture):
    frame_count = 0
    recording = False
    no_motion_frame_count = 0  # Counter for consecutive frames without motion
    no_motion_threshold = 60  # Threshold before stopping the recording in frames
    motion_detected_frames = []

    while video_capture.isOpened():
        # Read a frame from the video
        success, frame = video_capture.read()

        if not success:
            break

        if config.motion_detection_active:
            contours = motion_detector.detect_motion(frame)
            motion_detected = False

            for contour in contours:
                if motion_detector.is_valid_contour(frame, contour):
                    print("Motion detected")
                    MotionDetector.draw_rectangle(frame, contour, (0, 255, 0), 2)
                    motion_detected = True
                    # Reset the counter whenever motion is detected
                    no_motion_frame_count = 0 

                    if not recording:
                        print("Recording started")
                        recording = True
                        video_handler.initialize_recording(frame)
                        video_handler_masked.initialize_recording(frame, f"{temp_folder_path}/masked_video.mp4")
                        
            if recording:
                video_handler.write_frame(frame)
                masked_frame = MotionDetector.apply_mask(frame, contour)
                video_handler_masked.write_frame(masked_frame)
                frame_count += 1
                
                if not motion_detected:
                    no_motion_frame_count += 1
                else:
                    motion_detected_frames.append(frame_count)
                    no_motion_frame_count = 0

                if no_motion_frame_count >= no_motion_threshold or frame_count >= video_handler.maximum_fps:
                    print("Stopped recording")
                    recording = False
                    video_handler.stop_recording()
                    video_handler_masked.stop_recording()
                    frame_count = 0

                    video_handler.save_preview(motion_detected_frames)
                    video_handler_masked.save_preview(motion_detected_frames, f"{temp_folder_path}/masked_preview.jpg")
                    motion_detector.detect_objects(video_handler_masked.preview_path, f"{temp_folder_path}/prediction_image.jpg")
                    video_handler.add_metadata_to_video(motion_detector.objects_detected)

                    # email_alert.send_motion_detected_email(motion_detector.objects_detected, video_handler.start_time.strftime("%I:%M:%S %p %d %B %Y"), 
                    #                                        video_handler.preview_path, motion_detector.prediction_output_path)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    video_capture.release()