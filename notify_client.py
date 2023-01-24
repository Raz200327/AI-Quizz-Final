import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def notify_user(receiving_email, link, name):
    my_email = "infoquizzai@gmail.com"
    message = Mail(
        from_email=my_email,
        to_emails=receiving_email,
        subject="Your Quiz is Ready!",
        html_content=f"<h1>Your Quiz is Ready!</h1><h3>Hey {name},</h3><br><p>Your Quiz has Generated! "
                     f"Head to the link we sent you to download it now! Let us know if you need any adjustments or if you're having trouble downloading it."
                     f"Happy quizzing!</p>"
                     f"<br><a href='http://127.0.0.1:5050{link}' style='btn btn-lg btn-primary background-color: #EB6440'>Start Quiz</a>"
    )

    sg = SendGridAPIClient(os.environ.get("EMAILAPIKEY"))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
