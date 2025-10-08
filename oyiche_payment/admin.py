# My Django Imports
from django.contrib import admin

# My App Imports
from oyiche_payment.models import *

# Register your models here.
@admin.register(ProductCost)
class ProductCostAdmin(admin.ModelAdmin):
    list_display = ['product_cost_id', 'product_cost', 'company_incentive', 'school_incentive']
    list_editable = ['product_cost', 'company_incentive', 'school_incentive',]
    list_display_links = ['product_cost_id']
    list_per_page = 10

@admin.register(SchoolPaymentHistory)
class SchoolPaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ['sch_payment_history_id', 'school', 'academic_session', 'academic_term', 'purchased_by__username', 'reference', 'payment_status', 'amount_paid', 'unit_purchased', 'date_paid', 'created_at']
    list_editable = ['payment_status']
    list_display_links = ['sch_payment_history_id']
    list_per_page = 100
    list_select_related = ['school', 'academic_session', 'academic_term']
    list_filter = ['payment_status', 'created_at', 'date_paid']

@admin.register(SchoolUnit)
class SchoolUnitAdmin(admin.ModelAdmin):
    list_display = ['sch_unit_id', 'school', 'available_unit', 'total_unit']
    list_editable = ['available_unit', 'total_unit']
    list_per_page = 100
    list_select_related = ['school']

@admin.register(UnitUsedByTerm)
class UnitUsedByTermAdmin(admin.ModelAdmin):
    list_display = ['unit_used_id', 'school', 'academic_session', 'academic_term', 'unit_used']
    list_editable = ['unit_used']
    list_per_page = 100
    list_select_related = ['school', 'academic_session', 'academic_term']

