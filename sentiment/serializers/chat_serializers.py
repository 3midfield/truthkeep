from rest_framework import serializers

class ChatBotSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)


def validate_article_links(value):
    if not value:
        raise serializers.ValidationError("article_ids field cannot be empty!")
    return value


class ChatBotWithCertainArticlesSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    article_ids = serializers.ListField(
        child=serializers.CharField(allow_null=False, required=True),
        required=True,
        allow_null=False,
        validators=[validate_article_links],
    )