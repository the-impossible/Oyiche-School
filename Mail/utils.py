# My django imports
import threading #for enhancing page functionality
from django.core.mail import send_mail #for sending mails
from django.conf import settings #to gain access to variables from the settings
from django.views import View
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from django.utils.html import strip_tags

# My App imports

class EmailThread(threading.Thread):
    def __init__(self, email_subject, email_body, receiver):
        self.email_subject = email_subject
        self.email_body = email_body
        self.sender = 'info@fleetone.ng'
        self.receiver = receiver
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.email_subject,
            self.email_body,
            self.sender,
            self.receiver,
            html_message=self.email_body,
            fail_silently=False
        )

class AppTokenGenerator(PasswordResetTokenGenerator):
    def __make_hash_value(self, user, timestamp):
        return (text_type(user.is_active) + text_type(user.id)+text_type(timestamp))

class Mailer(View):

    def send_mail_directly(self, subject, body, recipient_list):
        print(f"subject: {subject}, {recipient_list}")
        send_mail(
            subject,
            strip_tags(body),  # Plain text fallback body (can be left empty if using HTML only)
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            html_message=body,
            fail_silently=False
        )

