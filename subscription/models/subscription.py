from django.contrib.auth import get_user_model
from django.db.models import OneToOneField, CASCADE, IntegerField, CharField, DateTimeField, TextField
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

PLAN = (
    ("Starter Plan", "Starter Plan"),
    ("Starter Plan Annual", "Starter Plan Annual"),
    ("Advantage Plan", "Advantage Plan"),
    ("Advantage Plan Annual", "Advantage Plan Annual"),
    ("Elite Plan", "Elite Plan"),
)

# Create your models here.
class Subscription(models.Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name='user_in_subscription')
    amount = IntegerField(default=0)
    subscription_id = CharField(max_length=100, null=True, blank=True)
    plan = CharField(max_length=25, choices=PLAN, default="Starter Plan")
    start = DateTimeField(null=True, blank=True)
    end = DateTimeField(null=True, blank=True)
    status = CharField(max_length=100, null=True, blank=True)
    cancel_at = DateTimeField(null=True, blank=True)
    last_payment = DateTimeField(null=True, blank=True)
    charge_id = CharField(max_length=255, null=True, blank=True)
    failed_reason = TextField(null=True, blank=True)

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")
