# My Django Imports
from django.contrib import admin

# My App Imports
from oyiche_payment.models import *

# Register your models here.
admin.site.register(ProductCost)
admin.site.register(SchoolUnit)
admin.site.register(SchoolPaymentHistory)
admin.site.register(UnitUsedByTerm)
