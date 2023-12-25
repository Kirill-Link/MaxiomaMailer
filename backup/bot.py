import imaplib
import email
from email.header import decode_header
import mysql.connector
import re

mydb = mysql.connector.connect(
    host="192.168.0.103",
    port="3306",
    user="bot",
    password="bot",
    database="bot"
)

cursor = mydb.cursor(dictionary=True)

cursor.execute("SELECT * FROM bottable")

results = cursor.fetchall()

cursor.close()
mydb.close()


while True:
    for row in results:
        mail = imaplib.IMAP4_SSL('imap.mail.ru')
        mail.login('smyshiyaev@mail.ru', 'dncYy9DE5EGYEEw2DEBm')

        mail.select('inbox')


        result, data = mail.search(None, 'ALL')
        email_ids = data[0].split()

        latest_email_id = email_ids[-1]
        result, email_data = mail.fetch(latest_email_id, '(RFC822)')

        raw_email = email_data[0][1]
        msg = email.message_from_bytes(raw_email)
        from_address = msg['From']

        match = re.search(r'<([^>]+)>', from_address)

        if match:
            email_address = match.group(1)

            if email_address == row['email']:
                sender_email = f'{row["email"]}'
                result, data = mail.search(None, '(HEADER FROM "{}")'.format(sender_email))
                
                if data[0]:
                    email_ids = data[0].split()
                    for email_id in email_ids:
                        mail.copy(email_id, f'inbox/{row["folder"]}')
                        mail.store(email_id, '+FLAGS', '(\Deleted)')
                        mail.expunge() 
                    print(f"Письма от {sender_email} перемещены в папку.")

        else:
            print("Email нету.")

        mail.create('mailbox/mailbox')

        mail.close()
        mail.logout()


def mailer(email :str, folder :str) -> None:
    
