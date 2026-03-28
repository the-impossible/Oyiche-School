# My django imports
from django.conf import settings #to gain access to variables from the settings
from django.template.loader import get_template #used for getting html template
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# My App imports
from Mail.utils import Mailer
from Mail.utils import AppTokenGenerator

class ResetPassword:
    """Handles sending password reset emails to users."""

    template_name = 'email/reset_password.html'

    def __init__(self, request=None):
        self.request = request
        self.mailer = Mailer()
        self.token_generator = AppTokenGenerator()

        self.app_name = settings.APP_NAME
        self.domain_name = settings.DOMAIN_NAME
        self.http = getattr(settings, "HTTP", 'https://')

    def send(self, user):
        """Send a secure password reset email to the user"""

        email = user.email
        domain = get_current_site(self.request).domain if self.request else f"{self.domain_name}"

        # Generate secure token and encoded user ID
        token = self.token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.user_id))

        # Build password reset URL
        reset_path = reverse('auth:reset-password', kwargs={'uidb64':uidb64, 'token':token})
        reset_password_url = f"{self.http}{domain}{reset_path}"

        # Render HMTL content
        context = {
            'app_name': self.app_name,
            'user': user,
            'reset_password_url': reset_password_url
        }

        # Send Email
        email_subject = f'Reset Your {self.app_name} Password'
        email_body = get_template(self.template_name).render(context)

        self.mailer.send_mail_directly(
            email_subject,
            email_body,
            [email]
        )
