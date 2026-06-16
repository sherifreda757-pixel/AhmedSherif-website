import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv


load_dotenv()
test_email = os.getenv('test_email')
my_password = os.getenv('my_password')
my_email = os.getenv('my_email')


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