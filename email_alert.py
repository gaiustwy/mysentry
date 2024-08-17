import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from utilities import format_object_detected

class EmailAlert:
    """
    A class to handle sending email alerts for motion detection events.
    """

    def __init__(self):
        """
        Initializes the email server and stores the sender's email address.
        """
        self.server, self.email_address = self.initialize_email_server()
    
    def initialize_email_server(self):
        """
        Initializes the SMTP server for sending emails.

        Returns:
            tuple: A tuple containing the SMTP server instance and the email address.
        """
        # Retrieve the email and app password from environment variables
        email_address = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("PASSWORD")
        
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP("smtp.gmail.com: 587")
        server.starttls()   # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.login(email_address, password)   # Log in to the email account using the credentials

        return server, email_address
    
    def send_email(self, subject, body, attachments=[]):
        """
        Sends an email with the specified subject, body, and image attachments.

        Args:
            subject (str): The subject of the email.
            body (str): The body text of the email.
            attachments (list): A list of file paths to attach to the email.
        """
        # Create a multipart email message to include text and attachments
        message = MIMEMultipart()
        message["From"] = self.email_address
        message["To"] = self.email_address
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain")) # Attach the plain text body to the email

        # Attach each image file from the attachments list
        for attachment_path in attachments:
            with open(attachment_path, "rb") as attachment:
                img = MIMEImage(attachment.read())
                img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                message.attach(img) # Attach the image to the email

        # Send the email
        self.server.sendmail(self.email_address, self.email_address, message.as_string())
        print(f"Email sent with subject: {subject}")

    def send_motion_detected_email(self, objects_detected, current_time, preview_image_path, prediction_image_path):
        """
        Sends a motion detected alert email with details about the detected objects.

        Args:
            objects_detected (list): A list of objects detected (e.g., ["person", "dog"]).
            current_time (str): The time when motion was detected.
            preview_image_path (str): The file path of the preview image to attach.
            prediction_image_path (str): The file path of the prediction image to attach.
        """
        # Define the subject line with the current time
        subject = f"Motion Detected - {current_time}"

        # Format the detected objects into a human-readable string
        object_details = format_object_detected(objects_detected)

        # Define the body text of the email
        body = f"""
        Hello,

        This is an automated alert to inform you that motion has been detected.

        Objects detected at {current_time}:
        {object_details}

        See the attached images for more details.

        Please visit the dashboard to view the recorded clip.

        Thank you,
        MySentry
        """

        # Send the email with the subject, body, and attached images
        self.send_email(subject, body, [preview_image_path, prediction_image_path])