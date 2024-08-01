from datetime import datetime

import stripe
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

# from accounts.utils import CrawlerThread
from subscription.models.subscription import Subscription
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
import os

import logging
logger = logging.getLogger("StandardLog")
# old setup 
# @csrf_exempt
# def stripe_webhook(request):

class Stripe_webhook(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        '''
        stripe webhook
        '''
        try:
            stripe.api_key = os.getenv("STRIPE_SECRET_KEY", False)
            endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET", False)
            payload = request.body
            sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            # Handle the checkout.session.completed event
            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]
                si_item = ""
                # Fetch all the required data from session
                client_reference_id = session.get("client_reference_id")
                customer = session["customer"]

            if event["type"] == "invoice.paid":
                session = event["data"]["object"]
                invoice_status = session["status"]

                billing_reason = session["billing_reason"]
                amount_paid = session["amount_paid"]
                charge_id = session["charge"]
                customer = session["customer"]
                paid = session["paid"]
                subscription = session["subscription"]
                current_time = datetime.now()
                user = User.objects.filter(customer=customer).first()
                if user:
                    if paid and invoice_status == "paid":
                        if billing_reason == "subscription_create":
                            subscription = stripe.Subscription.retrieve(session.subscription)
                            if subscription.plan.id == os.getenv("STARTER_SUBSCRIPTION_PRICING", False):
                                amount_paid = 99
                                plan = "Starter Plan"
                            elif subscription.plan.id == os.getenv("STARTER_SUBSCRIPTION_ANNUAL_PRICING", False):
                                amount_paid = 799
                                plan = "Starter Plan Annual"
                            elif subscription.plan.id == os.getenv("ADVANTAGE_SUBSCRIPTION_PRICING", False):
                                amount_paid = 249
                                plan = "Advantage Plan"
                            elif subscription.plan.id == os.getenv("ADVANTAGE_SUBSCRIPTION_ANNUAL_PRICING", False):
                                amount_paid = 1999
                                plan = "Advantage Plan Annual"
                            else:
                                plan = "Elite Plan"
                                amount_paid = amount_paid/100
                            if subscription.plan.interval == "month":
                                end = current_time + relativedelta(months=1)
                            else:
                                end = current_time + relativedelta(years=1)
                            subscription_obj = Subscription.objects.filter(
                                user=user
                            )
                            if subscription_obj:
                                subscription_obj = subscription_obj.update(
                                    subscription_id=subscription.id,
                                    amount=amount_paid,
                                    plan=plan,
                                    start=current_time,
                                    end=end,
                                    status="active",
                                    charge_id=charge_id
                                )
                            else:
                                subscription_obj = Subscription.objects.create(
                                    user=user,
                                    subscription_id=subscription.id,
                                    amount=amount_paid,
                                    plan=plan,
                                    start=current_time,
                                    end=end,
                                    status="active",
                                    charge_id=charge_id
                                )
                                # crawler_thread = CrawlerThread(user, user.fullname)
                                # crawler_thread.start()
                            # subscription_obj_stipe = stripe.Subscription.retrieve(subscription)
                            latest_invoice = subscription.latest_invoice
                            invoice_payment_time = stripe.Invoice.retrieve(latest_invoice)
                            if invoice_payment_time.status_transitions.paid_at:
                                subscription_obj.last_payment = datetime.fromtimestamp(
                                    invoice_payment_time.status_transitions.paid_at
                                )
                            subscription_obj.save()

                            cards = stripe.PaymentMethod.list(
                                customer=customer,
                                type="card",
                            )

                            stripe.Customer.modify(
                                customer,
                                invoice_settings={
                                    "default_payment_method": cards["data"][0]["id"]
                                },
                            )

                        elif billing_reason == "subscription_cycle":
                            if paid and invoice_status == "paid":
                                subscription_obj_stipe = stripe.Subscription.retrieve(
                                    subscription
                                )
                                subscription_obj = Subscription.objects.filter(
                                    user=user
                                ).first()
                                start_date = subscription_obj_stipe.current_period_start
                                end_date = subscription_obj_stipe.current_period_end
                                subscription_obj.start = datetime.fromtimestamp(start_date)
                                subscription_obj.end = datetime.fromtimestamp(end_date)
                                latest_invoice = subscription_obj_stipe.latest_invoice
                                invoice_payment_time = stripe.Invoice.retrieve(latest_invoice)
                                if invoice_payment_time.status_transitions.paid_at:
                                    subscription_obj.last_payment = datetime.fromtimestamp(
                                        invoice_payment_time.status_transitions.paid_at
                                    )
                                subscription_obj.charge_id = charge_id
                                subscription_obj.status = "active"
                                subscription_obj.failed_reason = ""

                                subscription_obj.save()

            if event["type"] == "invoice.payment_failed":
                session = event["data"]["object"]
                customer = session["customer"]
                invoice_status = session["status"]
                paid = session["paid"]
                charge_id = session["charge"]
                user = User.objects.filter(customer=customer).first()
                if charge_id:
                    if user:
                        if not paid and invoice_status == "open":
                            charge = stripe.Charge.retrieve(charge_id)
                            reason = charge["failure_message"]
                            if session["attempt_count"] >= 2:
                                subscription_obj = Subscription.objects.filter(
                                    user=user
                                ).first()
                                subscription_obj.failed_reason = reason
                                subscription_obj.status = "inactive"
                                subscription_obj.charge_id = session["charge"]
                                subscription_obj.save()

            return HttpResponse(status=200)
        except Exception as e:
            logger.debug("webhooke error: {e}")