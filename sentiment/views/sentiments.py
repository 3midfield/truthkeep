from django.apps import apps
from django.db.models import Q
# from datetime import date, datetime, timedelta, timezone
import json
import math

from django.contrib.auth.models import User
from utility.helpers.response import generate_response
from utility.pagination import CustomPageNumberPagination

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from datetime import datetime, timezone, timedelta

from users.middleware.expiring_token_auth import ExpiringTokenAuthentication
from sentiment.serializers.sentiment import SentimentWArticleDateSerializer


import logging
logger = logging.getLogger("StandardLog")
        
class sentimentsByScore(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        '''
        returns a list of all user sentiments filtereed by a score range
        
        applies filter based on what is provided
        '''
        try:
            user= request.user
        except Exception as e:
            logger.error(f"Error Unauthenticated user: {e}")
            return generate_response(status=400,  data="Could not retrieve user data", custom_message=str(e))
            
        # get min and max 
        try:
            min= request.GET.get("min")
        except Exception as e:
            logger.debug("could not process min: {e}")
            min=False
            
        try:
            max= request.GET.get("max")
        except Exception as e:
            logger.debug("could not process max: {e}")
            max=False
            
        try:
            topic= request.GET.get("topic")
        except Exception as e:
            logger.debug(f"could not process topic: {e}")
            topic=False
            
        try:
            narrative= request.GET.get("narrative")
        except Exception as e:
            logger.debug(f"could not process topic: {e}")
            narratvive=False
            
        try:
            search= request.GET.get("search")
        except Exception as e:
            logger.debug(f"could not process topic: {e}")
            search=False
        
            
        try:
            # sentiments= user.user_in_sentiment.order_by("-top_story__date")
            sentiments= user.user_in_sentiment.prefetch_related("top_story__narrative").order_by("-top_story__date")
            if min:
                sentiments = sentiments.filter(score__gte=min)
            if max:
                sentiments = sentiments.filter(score__lte=max)
        except Exception as e:
            logger.error(f"error in allSentimentsByArticleDate: {e}")
            return generate_response(status=400,  data="Bad Request: Could not retrieve sentiments", custom_message=str(e))
        
        try:
            if topic:
                sentiments = sentiments.filter(topic=topic)
        except Exception as e:
            logger.error(f"could not filter by topic: {e}")
            
        try:
            if narrative:
                sentiments = sentiments.filter(top_story__narrative=narrative)
        except Exception as e:
            logger.error(f"could not filter by narrative: {e}")
            
        try:
            if search:
                    sentiments = sentiments.filter(Q(top_story__title__icontains = search) | Q(reasoning__icontains = search))
        except Exception as e:
            logger.error(f"could not filter by search: {e}")
        
        try:
            ret = SentimentWArticleDateSerializer(sentiments, many= True).data
            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(ret, request)
            result={
                "count":sentiments.count(),
                "results":result
            }
            # result["count"]= sentiments.count()
            return generate_response(status=200,  data=result, custom_message=None)
        except Exception as e:
            logger.error(f"error in allSentimentsByArticleDate: {e}")
            return generate_response(status=500,  data="Error during serialization and pagination", custom_message=str(e))