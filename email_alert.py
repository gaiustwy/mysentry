from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from collections import Counter
from datetime import datetime

def send_email_alert(server, to_email, from_email, labels):
	"""Sends an email notification indicating the number of objects detected; defaults to 1 object."""
	message = MIMEMultipart()
	object_counter = Counter()
	
	message["From"] = from_email
	message["To"] = to_email

	# Get the current date and time
	current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	message["Subject"] = f"Motion Detected - {current_time}" 
     
	# Count frequency of each label
	for label in labels: 
		object_counter[label] += 1
	
	object_details = "\n ".join([f"{count} {label}" for label, count in object_counter.items()])
	total_objects = len(labels)

	message_body = f"""
	Hello,

	This is an automated alert to inform you that motion has been detected.

	{total_objects} object(s) detected:
	{object_details}

	Time of detection: {current_time}

	Please check the dashboard for further details.

	Thank you
	"""

	message.attach(MIMEText(message_body, "plain"))
	server.sendmail(from_email, to_email, message.as_string())
    