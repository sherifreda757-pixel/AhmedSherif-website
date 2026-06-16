import smtplib
from email.message import EmailMessage
import os

test_email = 'test2562006@gmail.com'
my_password = 'brbebhtdhbpqcqxo'
my_email = 'ahmed2562006abd@gmail.com'


def send_me_an_email(name, email, phone, message):
    print(name)
    print(email)
    print(phone)
    msg = EmailMessage()
    msg['Subject'] = f'New contact to your website from {name} '
    msg['From'] = test_email
    msg['To'] = my_email
    body = f'''
                Name: {name}
                Email: {email}
                phone: {phone}
                To: {my_email}
                Message:
                {message}'''
    msg.set_content(body)
    with smtplib.SMTP('smtp.gmail.com', 587) as connect:
        connect.starttls()
        connect.login(test_email, my_password)
        connect.send_message(msg)
            
        print('done')