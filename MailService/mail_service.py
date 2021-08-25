import os
import smtplib
from email.message import EmailMessage
import imghdr
from log import App_Logger


class MailService:
    def __init__(self, direct, receiver):
        self.direct = direct
        self.receiver = receiver
        self.USER = os.environ.get('E_USER')
        self.PASS = os.environ.get('E_PASS')
        self.logger = App_Logger("extractor_logs.txt")



        msg = EmailMessage()
        msg['Subject'] = 'HEY!!'
        msg['From'] = self.USER
        msg['To'] = receiver
        msg.set_content('Image attached')

        files = os.listdir(direct)
        for file in files:
            with open(os.path.join(direct, file), 'rb') as f:
                f_data = f.read()
                f_type = imghdr.what(f.name)
                f_name = f.name
                # print(f_type)
                # print(f.name)
            msg.add_attachment(f_data, maintype='image', subtype=f_type, filename=f_name)
        # connect to mail server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            #login to gmail server
            smtp.login(self.USER, self.PASS)

            smtp.send_message(msg)
        self.logger.log('info', 'Images has been attached to your email successfully...')






