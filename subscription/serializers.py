from rest_framework import serializers
from .models.subscription import Subscription

PLAN = (
    ("Starter Plan", "Starter Plan"),
    ("Starter Plan Annual", "Starter Plan Annual"),
    ("Advantage Plan", "Advantage Plan"),
    ("Advantage Plan Annual", "Advantage Plan Annual"),
    ("Elite Plan", "Elite Plan"),
)

class SubscriptionSerializer(serializers.ModelSerializer):
    '''
    General outgoing Serializer
    used to serialize in conjunction with user serializers
    '''

    user     = serializers.PrimaryKeyRelatedField( many=False, required=False, allow_null=True, default=None, read_only=True)
    # course      = serializers.PrimaryKeyRelatedField( many=False, required=False, allow_null=True, default=None, read_only=True)
    class Meta:
        model = Subscription
        fields = ["pk","user", "amount", "plan", "start", "end","status"]
    


# old stuff pk team
class CreateCheckoutSessionSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=PLAN, default="Starter Plan")

    def validate(self, attrs):
        if Subscription.objects.filter(user=self.context["request"].user).exists():
            raise serializers.ValidationError({"message": "Already Subscribed!"})
        return attrs


