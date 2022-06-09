import imaplib
import smtplib
import email
from email import encoders
from email.header import decode_header
import os
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

from settings import settings

DOWNLOADS_PATH = settings.PYTALOS_GENERAL['download_path']


class Mail:
    imap = None
    attach_part = None

    def __init__(self, username, password, smtp_server, server_port=587):
        self.username = username
        self.password = password
        self.smtp_server = smtp_server
        self.server_port = server_port
        self.to = None

    @staticmethod
    def _clean(text):
        return "".join(c if c.isalnum() else "_" for c in text)

    def get_mail(self, mails_num: int = 3):
        list_mail = []
        mail_info = {}
        self.imap = imaplib.IMAP4_SSL(self.smtp_server)
        self.imap.login(self.username, self.password)
        status, messages = self.imap.select("INBOX")
        messages = int(messages[0])
        for i in range(messages, messages - mails_num, -1):
            # fetch the email message by ID
            res, msg = self.imap.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)
                    # decode email sender
                    m_from, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(m_from, bytes):
                        m_from = m_from.decode(encoding)
                    mail_info['Subject'] = subject
                    mail_info['From'] = m_from
                    body = ""
                    content_type = ""
                    # if the email message is multipart
                    if msg.is_multipart():
                        # iterate over email parts
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = part.get_payload(decode=True).decode()
                            except Exception as ex:
                                pass
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                # print text/plain emails and skip attachments
                                mail_info['Body'] = body
                            elif "attachment" in content_disposition:
                                # download attachment
                                filename = part.get_filename()
                                if filename:
                                    self._generate_dir_if_not_exist(DOWNLOADS_PATH)
                                    folder_name = self._clean(subject)
                                    final_path = DOWNLOADS_PATH + folder_name
                                    self._generate_dir_if_not_exist(final_path)
                                    filepath = os.path.join(final_path, filename)
                                    # download attachment and save it
                                    open(filepath, "wb").write(part.get_payload(decode=True))
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        if content_type == "text/plain":
                            # print only text email part
                            mail_info['Body'] = body
                    if content_type == "text/html":
                        # if it's HTML, create a new HTML file and open it in browser
                        self._generate_dir_if_not_exist(DOWNLOADS_PATH)
                        folder_name = self._clean(subject)
                        final_path = DOWNLOADS_PATH + folder_name
                        self._generate_dir_if_not_exist(final_path)
                        filename = "index.html"
                        filepath = os.path.join(final_path, filename)
                        open(filepath, "w").write(body)
            list_mail.append(mail_info)

        return list_mail

    def _add_attachment(self, files_to_send, msg):
        # self.attach_part = None
        for file in files_to_send:
            # open the file as read in bytes
            with open(file, "rb") as f:
                # read the file content
                data = f.read()
                # create the attachment
                self.attach_part = MIMEBase("application", "octet-stream")
                self.attach_part.set_payload(data)
            # encode the data to base 64
            encoders.encode_base64(self.attach_part)
            # add the header
            attachment = file.split("/")[-1]
            self.attach_part.add_header("Content-Disposition", f"attachment; filename= {attachment}")
            msg.attach(self.attach_part)

    def send_mail(self, email_to, subject, body, files_to_send=None):
        msg = MIMEMultipart("alternative")
        msg["From"] = self.username
        msg["To"] = email_to
        msg["Subject"] = subject
        # make the text version of the HTML
        text = BeautifulSoup(body, "html.parser").text
        text_part = MIMEText(text, "plain")
        html_part = MIMEText(body, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        if files_to_send:
            self._add_attachment(files_to_send, msg)
        # initialize the SMTP server
        server = smtplib.SMTP(self.smtp_server, self.server_port)
        # connect to the SMTP server as TLS mode (secure) and send EHLO
        server.starttls()
        # login to the account using the credentials
        server.login(self.username, self.password)
        # send the email
        server.sendmail(self.username, email_to, msg.as_string())
        # terminate the SMTP session
        server.quit()

    def delete_email(self, search, folder='INBOX', return_mail_deleted=False):
        # create an IMAP4 class with SSL
        imap = imaplib.IMAP4_SSL(self.smtp_server)
        # authenticate
        imap.login(self.username, self.password)
        imap.select(folder)
        # search for specific mails by sender
        status, messages = imap.search(None, search)
        messages = messages[0].split(b' ')
        try:
            deleted_mails = []
            for mail in messages:
                _, msg = imap.fetch(mail, "(RFC822)")
                if return_mail_deleted is True:
                    for response in msg:
                        if isinstance(response, tuple):
                            msg = email.message_from_bytes(response[1])
                            # decode the email subject
                            subject = decode_header(msg["Subject"])[0][0]
                            if isinstance(subject, bytes):
                                # if it's a bytes type, decode to str
                                subject = subject.decode()
                            deleted_mails.append(subject)
                # mark the mail as deleted
                imap.store(mail, "+FLAGS", "\\Deleted")
            # permanently remove mails that are marked as deleted
            # from the selected mailbox (in this case, INBOX)
            imap.expunge()
            return deleted_mails
        except Exception as ex:
            print(f'No mail to delete: {ex}')

    def logout(self):
        try:
            self.imap.close()
            self.imap.logout()
        except AttributeError:
            pass

    @staticmethod
    def _generate_dir_if_not_exist(dir_path):
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
