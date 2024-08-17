# MySentry

**MySentry** is a Flask-based application designed for motion detection and object recognition using OpenCV and the YOLOv8 model. The application captures and processes video streams, detects motion, identifies objects, and sends email alerts with relevant details and images.

## Features

- **Motion Detection**: Detects motion in real-time using OpenCV's background subtraction method.
- **Object Recognition**: Identifies objects in the detected motion using the YOLOv8 model.
- **Email Alerts**: Sends email notifications with detected object details and attached images.
- **Video Recording**: Records video clips of detected motion and saves image previews and metadata.
- **Exclusion Zones**: Configurable zones where motion detection is ignored.
- **Web Dashboard**: A user-friendly interface for monitoring video feeds, managing clips, configuring settings, and viewing motion detection status.

## Installation

Follow these steps to set up the application:

1. **Install FFmpeg** 
	- Install FFmpeg according to your operating system by visiting the [FFmpeg website](https://ffmpeg.org/download.html).

2. **Clone the Repository**.
	```powershell
	git clone https://github.com/gaiustwy/fp_app.git
	```

3. **Create an app password** 
	- Create an app password for email notifications within the application using your email provider’s settings. For Gmail, click [here](https://support.google.com/accounts/answer/185833?hl=en&sjid=16925965526713193581-AP).

4. Set up enviornment variables in the `.env` file with your newly created credientials.
	```powershell
	EMAIL_ADDRESS=your-email@gmail.com
	PASSWORD=your-app-password
	```

5. Run the Application
	```powershell
	flask --app app run  
	```

## Dependencies

	- Refer to the `requirements.txt` file for a full list of Python packages required.

## Usage

1. **Access the Application**:
   - Open your web browser and go to [http://localhost:5000](http://localhost:5000).

2. **Set Up Your Camera**:
   - Enter the URL of your camera feed to start the video stream.

3. **Configure Exclusion Zones**:
   - Define areas on the video feed to ignore motion detection by drawing exclusion zones.

4. **Start Motion Detection**:
   - Activate motion detection to begin monitoring.

5. **Review Alerts and Clips**:
   - Check your email for alerts and access recorded clips of detected motion as needed.


