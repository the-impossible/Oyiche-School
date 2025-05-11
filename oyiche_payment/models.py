# My Django app imports
from django.db import models
from django.utils import timezone

# My app imports
from oyiche_schMGT.models import *
from oyiche_auth.models import *

# Create your models here.

class ProductCost(models.Model):
    product_cost = models.DecimalField(max_digits=10, decimal_places=2)
    company_incentive = models.DecimalField(max_digits=10, decimal_places=2)
    school_incentive = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Total Product Cost: {self.product_cost}, Company Incentive: {self.company_incentive}, School Incentive: {self.school_incentive}"

    class Meta:
        db_table = "Product Cost"
        verbose_name = "Product Cost"
        verbose_name_plural = "Product Costs"

class SchoolUnit(models.Model):

    school = models.ForeignKey(to=SchoolInformation, related_name="school_unit_info", on_delete=models.CASCADE)

    available_unit = models.IntegerField(default=0)
    total_unit = models.IntegerField(default=0)

    def __str__(self):
        return f"School: {self.school} - Available_unit:{self.available_unit}"

    def increase_unit(self, unit):
        self.available_unit += unit
        self.total_unit += unit

    def decrease_unit(self, unit):
        self.available_unit -= unit

    class Meta:
        db_table = "School Unit"
        verbose_name = "School Unit"
        verbose_name_plural = "School Units"

class UnitUsedByTerm(models.Model):

    school = models.ForeignKey(to=SchoolInformation, related_name="school_unit_used", on_delete=models.CASCADE)
    academic_session = models.ForeignKey(to=AcademicSession, related_name="school_unit_session", on_delete=models.CASCADE, db_constraint=False)
    academic_term = models.ForeignKey(AcademicTerm, related_name="school_unit_term", on_delete=models.CASCADE, db_constraint=False)

    unit_used = models.IntegerField(default=0)

    def __str__(self):
        return f"School: {self.school} - unit used:{self.unit_used}"

    class Meta:
        db_table = "Term_Unit"
        verbose_name = "Unit Used By Term"
        verbose_name_plural = "Unit Used By Terms"

class SchoolPaymentHistory(models.Model):

    school = models.ForeignKey(to=SchoolInformation, related_name="school_payment_info", on_delete=models.CASCADE)
    academic_session = models.ForeignKey(to=AcademicSession, related_name="payment_session", on_delete=models.CASCADE, db_constraint=False)
    academic_term = models.ForeignKey(AcademicTerm, related_name="payment_academic_term", on_delete=models.CASCADE, db_constraint=False)
    purchased_by = models.ForeignKey(to=User, related_name="purchased_by", on_delete=models.CASCADE)

    reference = models.CharField(max_length=500, null=True, blank=True)

    payment_status = models.CharField(max_length=100, default="pending")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_purchased = models.IntegerField(default=1)

    date_paid = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"School: {self.school} - Status:{self.payment_status} - Units: {self.unit_purchased}"

    class Meta:
        db_table = "payment_history"
        verbose_name = "School Payment History"
        verbose_name_plural = "School Payment History"

