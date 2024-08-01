from django.urls import path
from subscription.views.subscription import (
    CreateCheckoutSession,
    IsSubscribedView,
)
from subscription.views.webhook import Stripe_webhook


urlpatterns = [
    path("subscription/create_checkout_session", CreateCheckoutSession.as_view(), name="create_checkout_session"),
    path("api/subscription/stripe_webhook", Stripe_webhook.as_view(), name="stripe_webhook"),
    path("subscription/is_subscribed",IsSubscribedView.as_view(),name="is_subscribed"),
    # path("subscription/elite_plan/", create_elite_subscription, name="elite_plan"),
]
