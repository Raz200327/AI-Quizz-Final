import smtplib
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def reset_user_password(receiving_email, link):
    my_email = "infoquizzai@gmail.com"
    message = Mail(
        from_email=my_email,
        to_emails=receiving_email,
        subject="Reset Quizz Password",
        html_content=f'<h2>Hi there,</h1><p>Click this link to change your password</p><br><h2><a href="https://quizz.com.au{link}">Reset Password</a></h2>'
    )

    sg = SendGridAPIClient(os.environ.get("EMAILAPIKEY"))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)

