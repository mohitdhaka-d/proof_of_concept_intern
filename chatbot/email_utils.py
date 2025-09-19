import smtplib
from email.message import EmailMessage

def send_email(to_email: str, subject: str, body: str):
    """
    Sends an email using the SMTP protocol.
    
    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body content of the email.
    """
    # Replace with your email credentials and SMTP server details
    # For security, use environment variables to store credentials
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # TLS port
    sender_email = "dhakad.mohit300@gmail.com"
    password = "jjfahhvpyynedxnm"  # Use an app-specific password for security

    try:
        # print("Email me enter hua h code")
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.send_message(msg)
        
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Failed to send email: {e}")