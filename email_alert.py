from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from collections import Counter
from datetime import datetime
import os
import smtplib

def format_object_detected(labels):
    """
    Counts the frequency of each label and formats it as a comma-separated string.
    Example: "2 persons, 1 toilet, 1 vase"
    """
    if len(labels) == 0:
        return "Unidentifiable object"
    
    object_counter = Counter(labels)
    objects_detected = ", ".join([f"{count} {label}" for label, count in object_counter.items()])
    return objects_detected

def initialize_email_server():
    password = os.getenv("PASSWORD")
    email_address = os.getenv("EMAIL_ADDRESS")

    server = smtplib.SMTP("smtp.gmail.com: 587")
    server.starttls()
    server.login(email_address, password)

    return server, email_address

    # This is an automated alert to inform you that motion has been detected.

    # You will receive another email with the further details of the objects detected once the clip is processed. 


def send_first_email_alert(server, email_address):
    """Sends an email notification indicating that motion has been detected."""
    message = MIMEMultipart()
    
    message["From"] = email_address
    message["To"] = email_address
    message["Subject"] = "Motion Detected" 
    
    message_body = """
    Hello Sir/Mdm,

    1 person has been detected in the video feed.

    Please visit the dashboard to view the recorded clip.

    Thank you,
    MySentry
    """

    message.attach(MIMEText(message_body, "plain"))
    server.sendmail(email_address, email_address, message.as_string())

def send_second_email_alert(server, email_address, labels, current_time):
    """Sends an email notification indicating the number of objects detected; defaults to 1 object."""
    message = MIMEMultipart()
    
    message["From"] = email_address
    message["To"] = email_address

    # Get the current date and time
    # current_time = datetime.now().strftime("%I:%M:%S %p %d %B %Y")
    message["Subject"] = f"Motion Detected - {current_time}" 
    
    # Get the formatted object details
    object_details = format_object_detected(labels)

    message_body = f"""
    Hello,

    This is an automated alert to inform you that motion has been detected.

    Objects detected at {current_time}:
    {object_details}

    Please visit the dashboard to view the recorded clip.

    Thank you,
    MySentry
    """

    message.attach(MIMEText(message_body, "plain"))
    server.sendmail(email_address, email_address, message.as_string())
    print("Sent email alert")
