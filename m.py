import smtplib
from email.message import EmailMessage
from datetime import datetime
date = datetime.now().strftime("%B %d, %Y")
print(date)
test_email = 'test2562006@gmail.com'
my_password = 'wkbbbeojniqtdmbi'
my_email = 'ahmed2562006abd@gmail.com'
msg = EmailMessage()

def contact():

    msg['Subject'] = f'New contact to your website from  '
    msg['From'] = test_email
    msg['To'] = my_email
    body = f'''
                Name: kjjssf
                Email: kdflsjd
                phone: 0000
                To: {my_email}
                Message:
                HELLO'''
    msg.set_content(body)
    with smtplib.SMTP('smtp.gmail.com', 587) as connect:
        connect.starttls()
        connect.login(test_email, my_password)
        connect.send_message(msg)
        print('done')

contact()