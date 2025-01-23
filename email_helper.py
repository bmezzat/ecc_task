import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logger import setup_logger

logger = setup_logger(__name__)

MAIL_SERVER_HOST_NAME='smtp.office365.com'
SMTP_PORT=1025
MAIL_USERNAME = "bassem@outlook.com"
MAIL_PASSWORD = "BaSsEm"
SMTP_SSL_CONTEXT = ssl.create_default_context()


def send_smtp_email(email_data: dict):
    try:
        with smtplib.SMTP(MAIL_SERVER_HOST_NAME, SMTP_PORT, timeout=5) as server:
            server.starttls(context=SMTP_SSL_CONTEXT)
            server.login(MAIL_USERNAME, MAIL_PASSWORD)

            msg = MIMEMultipart()
            msg["From"] = MAIL_USERNAME
            msg["To"] = email_data["recipient"]
            msg["Subject"] = email_data["subject"]
            msg.attach(MIMEText(email_data["content"], "html"))

            server.sendmail(MAIL_USERNAME, email_data["recipient"], msg.as_string())
            logger.info("Mail Sent to predefined Mail Group")
            return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def send_email(subject, mismatch_rows):
    if mismatch_rows.empty:
        email_body = "<p>No mismatch on report</p>"
    else:
        email_body = (
            """
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <thead>
                        <tr>
                            <th>Clearing Member</th>
                            <th>Account</th>
                            <th>Margin Type</th>
                            <th>Margin CC050</th>
                            <th>Margin CI050</th>
                        </tr>
                    </thead>
                    <tbody>
            """
        )

        for _, row in mismatch_rows.iterrows():
            email_body += f"""
                <tr>
                    <td>{row['clearing_member']}</td>
                    <td>{row['account']}</td>
                    <td>{row['margin_type']}</td>
                    <td>{row['margin_cc050']}</td>
                    <td>{row['margin_ci050']}</td>
                </tr>
            """
        email_body += "</tbody></table>"

    logger.info("Report mail sending Attempt.")
    with open("email_template.html", "r") as template_file:
        html_template = template_file.read()
    html_content = html_template.replace("{{ subject }}", subject).replace("{{ email_body }}", email_body)
    email_data = {
        "subject": subject,
        "content": html_content,
        "recipient": "all@gmail.com"
    }

    return send_smtp_email(email_data)
