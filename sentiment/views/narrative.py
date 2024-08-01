from django.apps import apps
# from datetime import date, datetime, timedelta, timezone
import json
import math

from utility.helpers.response import generate_response
from utility.pagination import CustomPageNumberPagination

from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from datetime import datetime, timezone, timedelta

from users.middleware.expiring_token_auth import ExpiringTokenAuthentication
from sentiment.serializers.narrative_serializers import NarrativeTrimSerializer

import logging
logger = logging.getLogger("StandardLog")

class narrativeList(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        '''
        returns a list of all a users narratives
        ordered by the time it was last updated
        paginated
        looks for query params start, end, page & topic
        topic:the pk for the topic of the user 
        '''
        try:
            user= request.user
            # data = json.loads(request.body)
        except Exception as e:
            logger.error(f"Error Unauthenticated user: {e}")
            return generate_response(status=400,  data="Could not retrieve user data", custom_message=str(e))
            
        # get start and end 
        try:
            start = request.GET.get("start")
            start =  datetime.fromtimestamp(int(start))
        except Exception as e:
            logger.debug(f"could not process start: {e}")
            start=False
            
        try:
            end= request.GET.get("end")
            end =  datetime.fromtimestamp(int(end))
        except Exception as e:
            logger.debug(f"could not process end: {e}")
            end=False
        
        try:
            topic= request.GET.get("topic")
        except Exception as e:
            logger.debug(f"could not process topic: {e}")
            topic=False
        
        
        try:
            # narratives= user.managed_narratives.order_by("-updated_at")
            narratives= user.managed_narratives.prefetch_related("top_stories").select_related("topic").order_by("-updated_at")
            
            if start:
                narratives = narratives.filter(top_stories__date__gte=start).distinct()
            if end:
                narratives = narratives.filter(top_stories__date__lte=end).distinct()
        except Exception as e:
            logger.error(f"error in GET narrative: {e}")
            return generate_response(status=400,  data="Bad Request: Could not retrieve sentiments", custom_message=str(e))
        
        try:
            if topic:
                narratives = narratives.filter(topic=topic)
        except Exception as e:
            logger.error(f"could not filter by topic: {e}")
        
        try:
            ret = NarrativeTrimSerializer(narratives, many= True).data
            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(ret, request)
            return generate_response(status=200,  data=result, custom_message=None)
        except Exception as e:
            logger.error(f"error in GET Narratives: {e}")
            return generate_response(status=500,  data="Error during serialization and pagination", custom_message=str(e))
        
class narrativeCounts(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        '''
        returns a list of all a users narratives and their article count that occured in a given period
        paginated
        looks for query params start, end, page & topic
        topic:the pk for the topic of the user 
        '''
        try:
            user= request.user
            # user= User.objects.get(email="jordan.meyler+test11@gmail.com")
        except Exception as e:
            logger.error(f"Error Unauthenticated user: {e}")
            return generate_response(status=400,  data="Could not retrieve user data", custom_message=str(e))
            
        # get start and end 
        try:
            start = request.GET.get("start")
            start =  datetime.fromtimestamp(int(start))
        except Exception as e:
            logger.debug(f"could not process start: {e}")
            start=False
            
        try:
            end= request.GET.get("end")
            end =  datetime.fromtimestamp(int(end))
        except Exception as e:
            logger.debug(f"could not process end: {e}")
            end=False
        
        try:
            topic= request.GET.get("topic")
        except Exception as e:
            logger.debug(f"could not process topic: {e}")
            topic=False
        
        
        try:
            narratives= user.managed_narratives.prefetch_related("top_stories").select_related("topic").order_by("-updated_at")
            
            if start:
                narratives = narratives.filter(top_stories__date__gte=start).distinct()
            if end:
                narratives = narratives.filter(top_stories__date__lte=end).distinct()
        except Exception as e:
            logger.error(f"error in GET narrative: {e}")
            return generate_response(status=400,  data="Bad Request: Could not retrieve sentiments", custom_message=str(e))
        
        try:
            if topic:
                narratives = narratives.filter(topic=topic)
        except Exception as e:
            logger.error(f"could not filter by topic: {e}")
        
        try:
            # ret = NarrativeTrimSerializer(narratives, many= True).data
            #update occurances by filter
            ret=[]
            for item in narratives:
                occurence=item.top_stories.all()
                if start:
                    # make lambda
                    # occurence=occurence.filter(date__gte=start)
                    occurence = list(filter(lambda x: (x.date >= start.date()), occurence))
                if end:
                    # occurence = occurence.filter(date__lte=end)
                    occurence = list(filter(lambda x: (x.date <= end.date()), occurence))
                temp={
                    "pk":item.pk,
                    "topic":item.topic.pk,
                    "title":item.title,
                    "occurence":len(occurence)
                }
                ret.append(temp)
            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(ret, request)
            return generate_response(status=200,  data=result, custom_message=None)
        except Exception as e:
            logger.error(f"error in GET Narratives: {e}")
            return generate_response(status=500,  data="Error during serialization and pagination", custom_message=str(e))