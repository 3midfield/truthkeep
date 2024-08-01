from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError



def positive_integer_validator(value):
    if value <= 0:
        raise ValidationError("Please enter a positive integer.")


class EliteSubscriptionForm(forms.Form):
    amount = forms.IntegerField(validators=[positive_integer_validator], required=True)
    user_choice = forms.ChoiceField(label='Select User', required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_choice'].choices = self.get_user_choices()

    def get_user_choices(self):
        users = User.objects.all().exclude(is_superuser=True)
        choices = [(user.id, user.email) for user in users]
        return choices