# My django imports
from django.conf import settings #to gain access to variables from the settings
from django.template.loader import get_template #used for getting html template
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# My App imports
from FleetOne_info.models import CompanyInfo
from Mail.utils import AppTokenGenerator, Mailer

class ReVerifyEmail:
    """Handles sending emails re-verification to investors."""

    template_name = 'email/email_reverification_mail.html'

    def __init__(self, request=None):
        self.request = request
        self.mailer = Mailer()
        self.token_generator = AppTokenGenerator()
        info = CompanyInfo.objects.first()
        self.app_name = info.name if info and info.name else settings.APP_NAME
        self.domain_name = info.domain if info and info.domain else settings.DOMAIN_NAME
        self.http = getattr(settings, "HTTP", 'https://')

    def send(self, user):
        """Send welcome email message"""

        # Safely build dashboard URL
        domain = get_current_site(self.request).domain if self.request else f"{self.domain_name}"

        # Generate secure token and encoded user ID
        token = self.token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))

        # Build email verification URL
        verification_path = reverse('account:verify_email', kwargs={'uidb64':uidb64, 'token':token})
        verification_url = f"{self.http}{domain}{verification_path}"

        # Render HMTL content
        context = {
            'app_name': self.app_name,
            'user': user,
            'verification_url': verification_url
        }

        # Send Email
        email_subject = f'Verify Your {self.app_name} Email address to Activate Your Account'
        email_body = get_template(self.template_name).render(context)

        self.mailer.send_mail_directly(
            email_subject,
            email_body,
            [user.email]
        )
