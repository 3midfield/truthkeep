from django.contrib.auth.models import User
from django.apps import apps
from utility.helpers.crawler.fetchArticles import get_and_parse_articles 
from users.middleware.expiring_token_auth import ExpiringTokenAuthentication
from utility.pagination import CustomPageNumberPagination
from sentiment.serializers.article_serializers import ArticleSerializer
from utility.helpers.email.crawler_emails import crawler_summary_email
from users.middleware.expiring_token_auth import ExpiringTokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from sentiment.serializers.sentiment import SentimentWArticleDateSerializer

from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import base64
import os
import json


import logging
logger = logging.getLogger("StandardLog")


class fetchArticles(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request,pk):
        try:
            #TODO update to check groups instaed of sueper user status && add filter options for users
            req_user = request.user
            if not req_user.is_superuser:
                logger.debug(f"non super user attempted to access this method: {req_user}")
            if pk:
                users= User.objects.filter(pk=pk)
            else:
                users = User.objects.all().exclude(is_superuser=True)
            
            for user in users:
                # get users subsciprtion status
                try:
                    subscription = user.user_in_subscription.filter(status="active").all()
                except:
                    subscription= None

                if user.profile.trial_status != True and not subscription:
                    logger.debug(f"User does not have a valid trial or subscription: {user.pk}")
                    continue
                
                #fetch articles
                for topic in user.managed_topics.all():
                    tmp = get_and_parse_articles(user, topic)
                    if not tmp:
                        logger.error(f"Error User was not processed skipping....")
                        continue
            
                # email
                crawler_summary_email(user)
                
            return Response("done", status=status.HTTP_200_OK)
                    
        except Exception as e:
            logger.error(f"Critical Error While scraping: {e}")
            error = {
                    "statusCode": 500,
                    "error": True,
                    "data": "",
                    "message": "Bad Request",
                    "errors": str(e),
                }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class TrendingArticles(APIView):
    
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        '''
        Returns trending top stories
        query params:
        narrative: the narrative to filter by
        topic: the topic to filter by
        search: the term to serach titles or reasoning by
        
        '''
        try:
            user= request.user
            # user= User.objects.get(email="jordan.meyler+test11@gmail.com")
            top_stories_with_sentiments = user.user_in_top_story.prefetch_related("top_story_in_sentiment__narrative").select_related("topic").order_by("-date")
            try:
                narrative_pk = request.GET.get("narrative")
                if narrative_pk:
                    top_stories_with_sentiments = top_stories_with_sentiments.filter(narrative__pk = narrative_pk)
            except Exception as e:
                logger.error(f"Error filtering by narrative: {e}")
                
            try:
                topic = request.GET.get("topic")
                if topic:
                    top_stories_with_sentiments = top_stories_with_sentiments.filter(topic = topic)
            except Exception as e:
                logger.error(f"Error filtering by topic: {e}")
                
            try:
                search = request.GET.get("search")
                if search:
                    top_stories_with_sentiments = top_stories_with_sentiments.filter(Q(title__icontains = search) | Q(top_story_in_sentiment__reasoning__icontains = search))
            except Exception as e:
                logger.error(f"Error filtering by narrative: {e}")
                
            # order by date when finished
            top_stories_with_sentiments = top_stories_with_sentiments.order_by("-date")
            #convert top stories to sentiments
            sentiments= apps.get_model("sentiment.SentimentAnalysis").objects.select_related("top_story").filter(top_story__in=top_stories_with_sentiments).order_by("-created_at")
            
            # Paginate the combined data
            paginator = CustomPageNumberPagination()
            result_page = paginator.paginate_queryset(
                sentiments, request
            )

            # Serialize the paginated data
            serializer = SentimentWArticleDateSerializer(result_page, many=True)
            
            
            # # Paginate the combined data old method using articles changed to normalize responses
            # paginator = CustomPageNumberPagination()
            # result_page = paginator.paginate_queryset(
            #     top_stories_with_sentiments, request
            # )

            # # Serialize the paginated data
            # serializer = ArticleSerializer(result_page, many=True)

            # Return paginated response
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            error = {
                "statusCode": 400,
                "error": True,
                "data": "",
                "message": "Bad Request, Please check request",
                "errors": e.args[0],
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)