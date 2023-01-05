import smtplib

def reset_user_password(receiving_email, link):
    my_email = "infoquizzai@gmail.com"
    password = "pouclufpqtmucvrv"
    with smtplib.SMTP('smtp.gmail.com') as connection:
        connection.starttls()
        connection.login(my_email, password)
        connection.sendmail(from_addr=my_email, to_addrs=receiving_email,
                            msg=f"Subject:Reset Quizz Password\n\n"
                                f"Hi, use this link to reset your Quizz password: https://quizz.com.au{link}")
        print("Sent Email")


