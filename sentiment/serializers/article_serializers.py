from sentiment.models.articles import TopStories
from rest_framework import serializers

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopStories
        fields = [
            "id",
            "title",
            "link",
            "source",
            "date_posted",
            "thumbnail",
            "created_at",
            "date",
            "publisher_level",
            "impact_score"
        ]