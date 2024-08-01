from sentiment.models.sentiment import SentimentAnalysis
from rest_framework import serializers
import logging
logger = logging.getLogger("StandardLog")

class SentimentSerializer(serializers.ModelSerializer):
    link = serializers.CharField(source="top_story.link", read_only=True)
    title = serializers.CharField(source="top_story.title", read_only=True)

    class Meta:
        model = SentimentAnalysis
        fields = [
            "id",
            "title",
            "link",
            "score",
        ]
        
class SentimentWArticleDateSerializer(serializers.ModelSerializer):
    link = serializers.CharField(source="top_story.link", read_only=True)
    title = serializers.CharField(source="top_story.title", read_only=True)

    class Meta:
        model = SentimentAnalysis
        fields = [
            "id",
            "title",
            "link",
            "score",
            "reasoning",
        ]
        
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        try:
            ret["article_date"] = instance.top_story.date
            
        except Exception as e:
            logger.debug(f"Error updating Sentiment with article data {e}")        
        
        try:
            ret["link"] = instance.top_story.link
            
        except Exception as e:
            logger.debug(f"Error updating Sentiment with link{e}")   
                
        try:
            ret["source"] = instance.top_story.source
            
        except Exception as e:
            logger.debug(f"Error updating Sentiment with source {e}")
            
        try:
            ret["thumbnail"] = instance.top_story.thumbnail
            
        except Exception as e:
            logger.debug(f"Error updating Sentiment with source {e}")
            
        try:
            ret["impact_score"] = instance.top_story.impact_score
            
        except Exception as e:
            logger.debug(f"Error updating Sentiment with impact score {e}")
            
        try:
            ret["article_pk"] = instance.top_story.pk
            
        except Exception as e:
            logger.debug(f"Error updating Sentiment with article pk: {e}")
            
        return ret
    
    
