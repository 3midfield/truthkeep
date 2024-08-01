from sentiment.models.narrative import Narrative
from rest_framework import serializers

import logging
logger = logging.getLogger("StandardLog")
'''
please note the crawler narrative serializer used in the narrative analysis static function is located in the narrative model file
'''

class NarrativeSerializer(serializers.ModelSerializer):
    '''
    General outgoing Serializer
    used to serialize and send Enrollments to the front end
    '''

    user     = serializers.PrimaryKeyRelatedField( many=False, required=False, allow_null=True, default=None, read_only=True)
    topic      = serializers.PrimaryKeyRelatedField( many=False, required=False, allow_null=True, default=None, read_only=True)
    class Meta:
        model = Narrative
        fields = ["pk","user", "topic", "title", "summary", "main_points", "supporting_facts","updated_at", "last_story_added","impact_score"]
        
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        try:
            ret["occurence"]= instance.top_stories.count()
            # ret["occurence"]= 1
        except Exception as e:
            logger.error(f"Error serializing json in NarrativeTrimSerializer: {e}")
            
            
        return ret
    
class NarrativeTrimSerializer(serializers.ModelSerializer):
    '''
    Provides a streamlined representation of the narrative
    used to serialize and send Enrollments to the front end
    '''

    topic      = serializers.PrimaryKeyRelatedField( many=False, required=False, allow_null=True, default=None, read_only=True)
    class Meta:
        model = Narrative
        fields = ["pk", "topic", "title"]
        
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        try:
            ret["occurence"]= instance.top_stories.count()
            # ret["occurence"]= 1
        except Exception as e:
            logger.error(f"Error serializing json in NarrativeTrimSerializer: {e}")
            
            
        return ret