import email
from email import message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re
from Classes.mailer import Mailer
from db import BotDB


def send_email_reply(sender_email, recipient_email, subject, body):
    server = "smtp.yandex.ru"
    smtp_port = 465
    smtp_username = "Link3Q@yandex.kz"
    smtp_password = "jglsfpmqofrsaess"

    # Формирование письма
    reply_message = MIMEMultipart()
    reply_message["From"] = smtp_username
    reply_message["To"] = recipient_email
    reply_message["Subject"] = subject
    reply_message.attach(MIMEText(body, "plain"))

    # Подключение к серверу SMTP и отправка письма
    with smtplib.SMTP_SSL(server, smtp_port) as server:
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, recipient_email, reply_message.as_string())


def mailer_resend():
    db = BotDB(host='192.168.0.104', user='bot', port='3306', password='bot', database='bot')

    results = db.get_all_filter_data()

    for row in results:

        mail_connect = Mailer(server='imap.mail.ru', user_email='smyshiyaev@mail.ru', password='dncYy9DE5EGYEEw2DEBm')

        result, data = mail_connect.mail.search(None, 'ALL')
        email_ids = data[0].split()

        latest_email_id = email_ids[-1]
        result, email_data = mail_connect.mail.fetch(latest_email_id, '(RFC822)')

        raw_email = email_data[0][1]
        msg = email.message_from_bytes(raw_email)
        from_address = msg['From']

        match = re.search(r'<([^>]+)>', from_address)

        mail_connect.mail.store(latest_email_id, '-FLAGS', '(\\Seen)')

        if match:
            email_address = match.group(1)

            if email_address == row['email']:
                sender_email = f'{row["email"]}'
                main_email = 'smyshiyaev@mail.ru'
                result, data = mail_connect.mail.search(None, '(HEADER FROM "{}")'.format(sender_email))

                if data[0]:
                    email_ids = data[0].split()
                    for email_id in email_ids:
                        mail_connect.mail.copy(email_id, f'{row['parent_folder']}/{row['client_folder']}')
                        mail_connect.mail.store(email_id, '+FLAGS', '(\\Deleted)')
                        mail_connect.mail.expunge()

                        reply_subject = "Re: от кого надо"
                        reply_body = "Ваше письмо пришло и поставлено, можешь расслабить булки дальше наша работа"
                        send_email_reply('Link3Q@yandex.kz', sender_email, reply_subject, reply_body)

                    print(f"Письма от {sender_email} перемещены в папку, письмо тоже отправлено")

        else:
            print("Пока не чего нету.")

        mail_connect.mail.close()
        mail_connect.mail.logout()


while True:
    mailer_resend()
    time.sleep(5)
