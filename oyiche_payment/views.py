# My Django app imports
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import *
from decouple import config
import requests
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from requests.exceptions import ConnectionError
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.db import transaction
import uuid

# My App imports
from oyiche_payment.models import *
from oyiche_payment.forms import *
from oyiche_schMGT.views import get_school

def generate_transaction_reference():
    # Generate a random UUID
    unique_id = uuid.uuid4()

    return str(unique_id)


# Create your views here.
class PaymentDashboard(TemplateView):
    template_name = "backend/payment/payment_dashboard.html"
    form_class = BuyUnitsForm

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()

        return context

    def create_payment(self, amount_paid, reference, unit_purchased):

        school = self.school

        try:

            academic_session = AcademicSession.objects.get(is_current=True, school_info=school)
            academic_term = AcademicTerm.objects.get(is_current=True, school_info=school)

            SchoolPaymentHistory.objects.create(
                academic_session=academic_session,
                academic_term=academic_term,
                purchased_by=self.request.user,
                reference=reference,
                school=school,
                amount_paid=amount_paid,
                unit_purchased=unit_purchased,
            )

            return True

        except AcademicSession.DoesNotExist:
            messages.error(self.request, "Failed to log history, current academic session not set!!")

        except AcademicTerm.DoesNotExist:
            messages.error(self.request, "Failed to log history, current academic term not set!!")

        return False

    def initialize_paystack_transaction(self, email, amount, reference):

        url = "https://api.paystack.co/transaction/initialize"

        headers = {
            "Authorization": f"Bearer {config('PAYSTACK_TEST_SECRET_KEY')}",
            "Content-Type": "application/json"
        }

        current_site = get_current_site(self.request).domain

        data = {
            "email": email,
            "amount": amount,
            "channels": ["card", "bank_transfer", "bank"],
            "reference": reference,
            "callback_url": f"{settings.HTTP}{current_site}/payment/verify_payment/",
        }

        try:

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:

                response_data = response.json()

                if response_data.get("status") is True:
                    authorization_url = response_data["data"]["authorization_url"]
                    return redirect(authorization_url)
                else:
                    messages.error(self.request, f"Paystack returned an error: {response_data.get('message')}")
                    return

            else:
                messages.error(self.request, f"Failed to connect to Paystack: {response.text}")
                return

        except ConnectionError:
            messages.error(self.request, "Unable to connect to Paystack. Please try again later.")
            return

    def post(self, request, *args, **kwargs):
        # Handle the form submission
        form = self.form_class(request.POST)
        self.school = get_school(self.request)

        if form.is_valid():

            units = form.cleaned_data['units']
            amount = form.cleaned_data['amount']

            product_cost_exist =   ProductCost.objects.all()
            reference = generate_transaction_reference()

            if product_cost_exist.exists():
                amount_per_unit = product_cost_exist.first().company_incentive  # Securely hardcoded on server
                amount_to_be_paid = int(units) * amount_per_unit

                amount_in_kobo = int(units) * amount_per_unit * 100  # Final Kobo

                if int(amount) != int(amount_to_be_paid):
                    messages.error(request, "Amount is not correct")
                    return render(request, self.template_name, {'form': form})

                email = request.user.email

                # Initialize the Paystack transaction
                response = self.initialize_paystack_transaction(email=email, amount=f"{amount_in_kobo}", reference=reference)

                # If it's a redirect, just return it
                if isinstance(response, HttpResponseRedirect):

                    # Create Payment
                    self.create_payment(amount_paid=amount_to_be_paid, reference=reference, unit_purchased=units)

                    return response

            else:
                messages.error(request, 'Product cost not set, contact management!')

        else:
            messages.error(request, f"{form.errors.as_text()}")

        return render(request, self.template_name, {'form': form})

class VerifyPayment(View):
    template_name = "backend/payment/payment_dashboard.html"
    form_class = BuyUnitsForm
    school = None

    def update_payment(self, reference, payment_status):

        school = self.school

        try:
            # Update the payment record
            updated = SchoolPaymentHistory.objects.filter(
                reference=reference,
                school=school
            ).update(
                payment_status=payment_status,
                date_paid=timezone.now()
            )

            if updated:
                return True
            else:
                messages.error(self.request, "No matching payment record found to update.")
                return False

        except Exception as e:
            # Catch any unexpected errors (e.g., DB issues)
            messages.error(self.request, f"Error updating payment: {str(e)}")
        return False

    def update_school_unit(self, unit):

        school = self.school

        obj, _ = SchoolUnit.objects.get_or_create(school=school)

        obj.increase_unit(unit)
        obj.save()

    def get(self, request, *args, **kwargs):

        reference = request.GET.get("reference")
        self.school = get_school(self.request)

        if not reference:
            messages.error(request, "No transaction reference provided.")
            return redirect("payment:payment_dashboard")

        headers = {
            "Authorization": f"Bearer {config('PAYSTACK_TEST_SECRET_KEY')}"
        }

        url = f"https://api.paystack.co/transaction/verify/{reference}"

        try:
            response = requests.get(url, headers=headers)
            response_data = response.json()

            print(f'Response Data: {response_data}')

            if response_data.get("status") is True:
                payment_data = response_data["data"]
                status = payment_data["status"]

                if status == "success":

                    product_cost_exist =   ProductCost.objects.all()

                    if product_cost_exist.exists():

                        amount_kobo = int(payment_data["amount"])
                        amount_naira = amount_kobo // 100
                        units = amount_naira // product_cost_exist.first().company_incentive  # Since 1 unit = ₦400

                        # Update Payment
                        self.update_payment(reference=reference, payment_status=status)

                        # Update School Unit
                        self.update_school_unit(unit=units)

                        messages.success(request, f"Payment successful! {units} units added.")

                    else:
                        messages.error(request, f"Product cost not set, contact management!!.")

                elif status in ["failed", "reversed"]:

                    # Update Payment
                    self.update_payment(reference=reference, payment_status='failed')
                    messages.error(request, f"Transaction failed. Status: {status}")

                elif status in ["processing", "pending", "abandoned", "ongoing", "queued"]:

                    # Update Payment
                    self.update_payment(reference=reference, payment_status='pending')

                    messages.warning(request, f"Transaction is still pending or incomplete. Status: {status}")

                else:

                    messages.error(request, f"Unhandled transaction status: {status}")

            else:
                messages.error(request, f"Verification failed: {response_data.get('message')}")

        except requests.ConnectionError:

            messages.error(request, "Connection error. Please try again.")

        return redirect("payment:payment_dashboard")
