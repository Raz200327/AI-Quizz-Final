import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def notify_user(receiving_email, link, name, quiz_name):
    my_email = "infoquizzai@gmail.com"
    message = Mail(
        from_email=my_email,
        to_emails=receiving_email,
        subject="Your Quiz is Ready!",
        html_content=f"<h1>Your Quiz about {quiz_name} is Ready!</h1><h3>Hey {name},</h3><p>"
                     f"Click to the link we sent you to go to your dashboard!</p><p>Let us know if you need any adjustments or if you're having trouble downloading it.</p>"
                     f"<p>Happy quizzing!</p>"
                     f"<br><h2><a href='http://127.0.0.1:5050{link}' style='text-decoration: none;'>Start Quiz</a></h2>"
    )

    sg = SendGridAPIClient(os.environ.get("EMAILAPIKEY"))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)


