from email.message import EmailMessage
import ssl
import smtplib

EMAIL_SENDER = "konzol.world.2023@gmail.com"
EMAIL_PASSWORD = "wwhorzzrvcrhrwol55555"

SUBJECT = ""
BODY = f""""""


def send_email(email_receiver):
    email_message = EmailMessage()
    email_message["From"] = EMAIL_SENDER
    email_message["To"] = email_receiver
    email_message["Subject"] = SUBJECT
    email_message.set_content(BODY)

    def_context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=def_context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_SENDER, email_receiver, email_message.as_string())


if __name__ == '__main__':
    send_email(email_receiver="")
