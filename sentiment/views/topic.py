from django.apps import apps
# from datetime import date, datetime, timedelta, timezone
import json
import math

from utility.helpers.response import generate_response,error_list_object
from utility.pagination import CustomPageNumberPagination

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from datetime import datetime, timezone, timedelta

from users.middleware.expiring_token_auth import ExpiringTokenAuthentication
from sentiment.serializers.topic_serializers import TopicCreationSearializer, TopicSerializer
from utility.helpers.crawler.crawlerThread import CrawlerThread


import logging
logger = logging.getLogger("StandardLog")
        
class TopicAPIView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        '''
        returns a list of all user topics 
        '''
        try:
            user= request.user
            topics= user.managed_topics
            # data = json.loads(request.body)
        except Exception as e:
            logger.error(f"Error Unauthenticated user: {e}")
            return generate_response(status=400,  data="Could not retrieve user data and topics", custom_message=str(e))
        
        try:
            ret = TopicSerializer(topics, many= True).data

            return generate_response(status=200,  data=ret, custom_message=None)
        except Exception as e:
            logger.error(f"error in TopicAPIView GET: {e}")
            return generate_response(status=500,  data="Error during serialization for TopicAPIView GET", custom_message=str(e))
        
        
    def post(self, request):
        '''
        create a topic for a user
        
        topic: the name of the topic
        tag: the tag for the topic
        '''
        try:
            try:
                user= request.user
                data = json.loads(request.body)
                data["user"] = user.pk
            except Exception as e:
                logger.error(f"Error Unauthenticated user: {e}")
                return generate_response(status=400,  data="Could not data", custom_message=str(e))
            
            try:
                serializer = TopicCreationSearializer(data=data)
                # check if valid create objects
                if serializer.is_valid():
                    topic = serializer.save()
                    
                    try:
                        crawler_thread = CrawlerThread(user, topic)
                        crawler_thread.start()
                    except Exception as e:
                        logger.error(f"Error threading scraper for user: {e}")   
                               
                    
                    return generate_response(status=201,  data=serializer.data, custom_message=None)
                else:
                    ret =[]
                    for error in serializer.errors:
                        # print(error.error)
                        title=str(error)
                        ret.append(error_list_object(str(error), str(serializer.errors[title][0])))
                        
                    return generate_response(status=422,  data=ret, custom_message="Could not create topic")
            except Exception as e:
                logger.debug(f"Error creating top: {e}")
                return generate_response(status=400,  data="create topic", custom_message=str(e))
        except Exception as e:
            logger.error(f"Error creating topic: {e}")
            return generate_response(status=500,  data="Error during creation of a topic in TopicAPIView Post", custom_message=str(e))
        
    def delete(self, request):
        '''
        deletes a topic for a user
        
        topic: the name of the topic
        '''
        try:
            try:
                user= request.user
                data = json.loads(request.body)
            except Exception as e:
                logger.error(f"Error Unauthenticated user: {e}")
                return generate_response(status=400,  data="Could not retrieve data", custom_message=str(e))
            
            try:
                topic = user.managed_topics.get(pk=data["topic"])
                topic.delete()
                return generate_response(status=200,  data=None, custom_message="Topic Deleted")
            except Exception as e:
                logger.debug(f"Could not delete topic: {e}")
                return generate_response(status=400,  data="Could not delete Topic.", custom_message=str(e))
        except Exception as e:
            logger.error(f"Error delteting topic: {e}")
            return generate_response(status=500,  data="Error deleting topic", custom_message=str(e))
            