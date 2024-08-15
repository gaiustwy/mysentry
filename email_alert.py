import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from utilities import format_object_detected

class EmailAlert:
    def __init__(self):
        self.server, self.email_address = self.initialize_email_server()
    
    def initialize_email_server(self):
        password = os.getenv("PASSWORD")
        email_address = os.getenv("EMAIL_ADDRESS")

        server = smtplib.SMTP("smtp.gmail.com: 587")
        server.starttls()
        server.login(email_address, password)

        return server, email_address
    
    def send_email(self, subject, body, attachments=[]):
        message = MIMEMultipart()
        message["From"] = self.email_address
        message["To"] = self.email_address
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        for attachment_path in attachments:
            with open(attachment_path, "rb") as attachment:
                img = MIMEImage(attachment.read())
                img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                message.attach(img)
        self.server.sendmail(self.email_address, self.email_address, message.as_string())
        print(f"Email sent with subject: {subject}")

    def send_motion_detected_email(self, objects_detected, current_time, preview_image_path, prediction_image_path):
        subject = f"Motion Detected - {current_time}"
        object_details = format_object_detected(objects_detected)
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
        self.send_email(subject, body, [preview_image_path, prediction_image_path])