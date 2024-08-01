from django.contrib.auth.models import User
from rest_framework import serializers
from users.models.Profile import Profile
from sentiment.models.topic import Topic


import re
import json
import logging
logger = logging.getLogger("StandardLog")


class TopicCreationSearializer(serializers.ModelSerializer):
    '''
    User Serializer used for registration of a user. Includes validation
    function to cxreate a token
    
    '''
    
    user = serializers.PrimaryKeyRelatedField( many=False, queryset=User.objects.all(), required=False, allow_null=True, default=None)
    
    class Meta:
        model = Topic
        fields = ["user","topic","tag"]
        
    def validate(self,data):
        """
        validate topic
        """
        error_dict = {}
        
        if "user" not in data:
            error_dict["user"] = "User is required"
            
        if "topic" in data and "user" in data:
            try:
                if Topic.objects.filter(user=data["user"], topic=data["topic"]).exists():
                    error_dict["topic"] = "This user already has a topic with the same name"
            except Exception as e:
                error_dict["topic"] = "Error validating topic"
                
        

        if error_dict != {}:
            raise serializers.ValidationError(error_dict)

        return data


class TopicSerializer(serializers.ModelSerializer):
    '''
    User Serializer used for registration of a user. Includes validation
    function to cxreate a token
    
    '''
    
    user = serializers.PrimaryKeyRelatedField( many=False, required=False, allow_null=True, default=None, read_only=True)
    
    class Meta:
        model = Topic
        fields = ["pk","user","topic","tag"]

