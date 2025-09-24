import imaplib
import email
from db import collection  # MongoDB collection for emails
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

# Your email credentials
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = "imap.gmail.com"

def check_replies_function():
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(SENDER_EMAIL, PASSWORD)
        mail.select("inbox")  # select inbox

        # Search for unseen emails
        status, messages = mail.search(None, '(UNSEEN)')
        if status != "OK":
            print("No new emails found.")
            return

        for num in messages[0].split():
            status, data = mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(data[0][1])
            in_reply_to = msg.get("In-Reply-To")

            # If this is a reply to a sent email
            if in_reply_to:
                original_email = collection.find_one({"message_id": in_reply_to})
                if original_email:
                    # Update original email status
                    collection.update_one(
                        {"_id": original_email["_id"]},
                        {"$set": {"status": "replied"}}
                    )

                    # Store the reply
                    reply_doc = {
                        "thread_id": original_email["thread_id"],
                        "message_id": msg.get("Message-ID"),
                        "in_reply_to": in_reply_to,
                        "from_email": msg.get("From"),
                        "to_email": msg.get("To"),
                        "subject": msg.get("Subject"),
                        "body": get_email_body(msg),
                        "status": "replied",
                        "timestamp": datetime.now()
                    }
                    collection.insert_one(reply_doc)

                    # Print in terminal
                    print(f"📩 Reply received from {msg.get('From')} for thread {original_email['thread_id']}")

        mail.logout()
    except Exception as e:
        print(f"❌ Error checking replies: {e}")


def get_email_body(msg):
    """
    Extract the plain text body from an email message.
    """
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""
