import smtplib
import uuid
from email.message import EmailMessage
import smtplib
from datetime import datetime
from db import collection
from email.utils import make_msgid
import os
from dotenv import load_dotenv
load_dotenv()


def send_email(to_email: str, subject: str, body: str,thread_id=None):
    """
    Sends an email using the SMTP protocol and logs it into MongoDB.
    
    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body content of the email.
    """
    # Replace with your email credentials and SMTP server details
    # For security, use environment variables to store credentials

    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # TLS port
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    status = "sent"



    if thread_id is None:
        thread_id = str(uuid.uuid4())


    

    try:
        # print("Email me enter hua h code")
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email
        msg.set_content(body)

        msg_id = make_msgid()  # generate unique ID
        msg["Message-ID"] = msg_id

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.send_message(msg)
        
        print("Email sent successfully!")
        
    except Exception as e:
        status = f"failed: {str(e)}"
        print(f"Failed to send email: {e}")

     # Store email details in MongoDB
    
    if collection is not None:
        email_doc = {
            "thread_id":thread_id,
            "message_id": msg_id,
            "in_reply_to": None,  # original email
            "to_email": to_email,
            "from_email": sender_email,
            "subject": subject,
            "body": body,
            "status": status,
            "timestamp": datetime.now()
        }
        collection.insert_one(email_doc)
        print("📩 Email logged in MongoDB!")