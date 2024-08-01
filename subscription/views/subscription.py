
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User
import stripe
from django.contrib.admin import site
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from subscription.serializers import CreateCheckoutSessionSerializer
from subscription.scripts.stripe_customer import create_customer
from subscription.models.subscription import Subscription
from subscription.forms import EliteSubscriptionForm
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail.mail import Mail

from users.middleware.expiring_token_auth import ExpiringTokenAuthentication

import os
import logging
logger = logging.getLogger("StandardLog")
# Create your views here.
#TODO sendgrid email stuff **

class CreateCheckoutSession(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        Creates a checkout session for stripe
        '''
        user = request.user
        if not user.profile.customer:
            customer = create_customer(
                email=user.email,
                metadata={"user_id": user.id},
            )
            user.profile.customer = customer.stripe_id
            user.profile.save()
        customer = user.profile.customer
        serializer = CreateCheckoutSessionSerializer(
            data=request.query_params, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", False)
        plan = serializer.validated_data.get("plan")
        if plan == "Starter Plan":
            price_item = [
                {
                    "price": os.getenv("STARTER_SUBSCRIPTION_PRICING", False),
                    "quantity": 1,
                },
            ]
        elif plan == "Starter Plan Annual":
            price_item = [
                {
                    "price": os.getenv("STARTER_SUBSCRIPTION_ANNUAL_PRICING", False),
                    "quantity": 1,
                },
            ]
            

        elif plan == "Advantage Plan":
            price_item = [
                {
                    "price": os.getenv("ADVANTAGE_SUBSCRIPTION_PRICING", False),
                    "quantity": 1,
                },
            ]

        elif plan == "Advantage Plan Annual":
            price_item = [
                {
                    "price": os.getenv("ADVANTAGE_SUBSCRIPTION_ANNUAL_PRICING", False),
                    "quantity": 1,
                },
            ]
        else:
            price_item = os.getenv("STARTER_SUBSCRIPTION_PRICING", False)
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=user.id,
                success_url=os.getenv("STRIPE_SUCCESS_URL", False),
                cancel_url=os.getenv("STRIPE_CANCEL_URL", False),
                payment_method_types=["card"],
                mode="subscription",
                customer=customer,
                line_items=price_item,
                billing_address_collection="required",
                metadata={
                    "action": "Subscription",
                    "user_id": request.user.id,
                    "plan": plan,
                },
            )
            return Response(
                {"session_id": checkout_session["id"]}, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(
                "Stripe error during Create Checkout Session for subscription------------"
                + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                + "-------"
                + str(e)
            )
            return Response(
                {
                    "statusCode": 400,
                    "error": True,
                    "message": "Something went wrong. Please try again later!",
                    "data": {
                        "message": "Something went wrong. Please try again later!"
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class IsSubscribedView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    
    def get(request):
        user = request.user
        subscription = Subscription.objects.filter(user=user).first()
        if subscription:
            data = {
                "is_subscribed": True,
                "status": subscription.status,
                "failed_reason": subscription.failed_reason,
                "trial_start_date": user.profile.trial_start_date,
                "trial_status": user.profile.trial_status
            }
        else:
            data = {
                "is_subscribed": False,
                "status": "not subscribed",
                "failed_reason": "",
                "trial_start_date": user.profile.trial_start_date,
                "trial_status": user.profile.trial_status
            }
        response = {
            "statusCode": 200,
            "error": False,
            "message": "Subscription status",
            "data": data,
        }
        return Response(response, status=status.HTTP_200_OK)


#TODO chenge to APIView not in use?*****
# def create_elite_subscription(request):
#     if request.method == "POST":
#         form = EliteSubscriptionForm(request.POST, request.FILES)
#         form.is_valid()
#         user = form.cleaned_data["user_choice"]
#         user = User.objects.get(pk=user)
#         amount = form.cleaned_data["amount"]
#         if not Subscription.objects.filter(user_id=user.id).exists():

#             stripe.api_key = os.getenv("STRIPE_SECRET_KEY", False)
#             plan = "Elite Plan"
#             # price_item = settings.Elite_SUBSCRIPTION_PRICING
#             try:

#                 pricing = stripe.Price.create(
#                     currency="usd",
#                     unit_amount=amount * 100,
#                     product="prod_PwvB2VKEdnqoza",
#                     recurring={"interval": "month"},
#                     # product_data={"name": plan},
#                 )
#                 checkout_session = stripe.checkout.Session.create(
#                     client_reference_id=user.id,
#                     success_url=os.getenv("STRIPE_SUCCESS_URL", False),
#                     cancel_url=os.getenv("STRIPE_CANCEL_URL", False),
#                     payment_method_types=["card"],
#                     mode="subscription",
#                     customer=user.customer,
#                     line_items=[{
#                         'price': pricing.id,
#                         'quantity': 1,
#                     }],
#                     billing_address_collection="required",
#                     metadata={
#                         "action": "Subscription",
#                         "user_id": user.id,
#                         "plan": plan,
#                     },
#                 )

#                 try:
#                     message = Mail(from_email=settings.DEFAULT_FROM_EMAIL, to_emails=user.email)
#                     logger.debug("user email", user.email)
#                     message.dynamic_template_data = {
#                         "full_name": f"{user.first_name} {user.last_name}",
#                         "amount": amount,
#                         "subscription_link": checkout_session.url,
#                     }
#                     message.template_id = os.getenv("PAYMENT_TEMPLATE_ID", False)
#                     # sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY", False))
#                     sg.send(message)
#                 except Exception as e:
#                     messages.error(request, "There is the error sending your email. Please try again later! Payment Link for this user is {}".format(checkout_session.url))
#                     return redirect("admin:index")
#                 messages.success(request, "Payment Link has been sent to the customer.")
#                 return redirect("admin:index")
#             except Exception as e:
#                 logger.error(
#                     "Stripe error during Create Checkout Session for subscription Of Elite Plan------------"
#                     + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
#                     + "-------"
#                     + str(e)
#                 )
#                 messages.error(request, "There is Some Error With Stripe!")
#                 return redirect("admin:index")
#         messages.error(request, "Already subscribed")
#         return redirect("admin:index")
#     else:
#         form = EliteSubscriptionForm()
#         # Get the list of available apps from the admin site
#         available_apps = site.get_app_list(request)
#         return render(
#             request,
#             "admin/elite_plan.html",
#             {"request": request, "form": form, "available_apps": available_apps},
#         )