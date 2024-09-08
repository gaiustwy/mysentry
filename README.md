# MySentry

**MySentry** is an AI-driven video analytics surveillance system designed to offer affordable and privacy-focused security. Built with Flask, this application leverages OpenCV for motion detection and the YOLOv8 model for object recognition. MySentry processes live video feeds, detects motion, identifies objects, and sends email alerts with detailed information and images. By using open-source tools and local storage, MySentry ensures that user data remains secure and private, with no need for buying additional hardware.

## Features

- **Motion Detection**: Detects motion in real-time using OpenCV's background subtraction method.
- **Object Recognition**: Identifies objects in the motion detection events using the YOLOv8 model.
- **Email Alerts**: Sends email notifications with detected object details and attached images.
- **Exclusion Zones**: Configurable zones where motion detection is ignored.
- **Web Dashboard**: A user-friendly interface for monitoring video feeds, managing clips, configuring settings, and playback motion detection clips.

## Installation

Follow these steps to set up the application:

1. **Install FFmpeg** 
	- Install FFmpeg according to your operating system by visiting the [FFmpeg website](https://ffmpeg.org/download.html).

2. **Create an App Password** 
	- Create an app password for email notifications within the application using your email provider’s settings. For Gmail, click [here](https://support.google.com/accounts/answer/185833?hl=en&sjid=16925965526713193581-AP).

3. **Download or Clone the Repository**.
	```powershell
	git clone https://github.com/gaiustwy/fp_app.git
	```

4. **Set Up Environment Variables**
	- In the root directory of the project, create a .env file with your credentials:
	```powershell
	EMAIL_ADDRESS=your-email@gmail.com
	PASSWORD=your-app-password
	```

5. **Run the Application**
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
   - To set up your phone as a camera input, download the [DroidCam](https://play.google.com/store/apps/details?id=com.dev47apps.droidcam&hl=en) mobile application.

3. **Configure Exclusion Zones**:
   - Define areas on the video feed to ignore motion detection by drawing exclusion zones.

4. **Start Motion Detection**:
   - Activate motion detection to begin monitoring.

5. **Review Alerts and Clips**:
   - Check your email for alerts and access recorded clips of motion detection as needed.


