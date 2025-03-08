from django.db import models

# Create your models here.
class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, db_index=True,
                             verbose_name='email address', blank=True, null=True)
    phone = models.CharField(max_length=11, db_index=True,
                        blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.email}: sent a message'

    class Meta:
        db_table = 'Contact Us'
        verbose_name_plural = 'Contact Us'
