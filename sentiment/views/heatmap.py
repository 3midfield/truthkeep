from django.apps import apps
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User

from datetime import datetime, timezone, timedelta
from utility.helpers.response import generate_response


from sentiment.serializers.sentiment import SentimentWArticleDateSerializer
from users.middleware.expiring_token_auth import ExpiringTokenAuthentication

import calendar
import json
import math

import logging
logger = logging.getLogger("StandardLog")


class allSentimentsByArticleDate(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        '''
        returns a list of all user sentiments ordered by article date
        has a query param for topic
        '''
        try:
            user= request.user
            # data = json.loads(request.body)
        except Exception as e:
            logger.error(f"Error Unauthenticated user: {e}")
            return generate_response(status=400,  data="Could not retrieve user data", custom_message=str(e))
            
        try:
            sentiments= user.user_in_sentiment.order_by('-top_story__date')
            print(sentiments)
        except Exception as e:
            logger.error(f"error in allSentimentsByArticleDate: {e}")
            return generate_response(status=400,  data="Could not retrieve user sentiments", custom_message=str(e))
        
        try:
            topic = request.GET.get("topic")
            if topic:
                sentiments= sentiments.filter(topic=topic)
        except Exception as e:
            logger.error(f"Could not retrieve topic: {e}")
            return generate_response(status=400,  data="Could not retrieve user data", custom_message=str(e))
        
        try:
            ret = SentimentWArticleDateSerializer(sentiments, many= True).data
            return generate_response(status=200,  data=ret, custom_message=None)
        except Exception as e:
            logger.error(f"error in allSentimentsByArticleDate: {e}")
            return generate_response(status=500,  data="Error retrieving sentiments", custom_message=str(e))
        
class HeatMap(APIView):
    authentication_classes = [ExpiringTokenAuthentication] 
    permission_classes = [IsAuthenticated]
    
    def get(self, request, start, end):
        '''
        This returns an array of month objects which contain day objects these approximations are intended for use with the heatmap
        Recieves: 
        
        start_date => the start date to collect data from
        end_date => the end date to stop collecting data
        
        recieves topic as a query variable
        
        returns:
        interface day {
        positive_narratives: number;
        neutral_narratives: number;
        negative_narratives: number;
        calender_day: number;
        }
        interface month {
            year: number;
            month: number;
            days: day[]
        } 
        
        '''
        try:
            try:
                user= request.user 
                # user = User.objects.get(pk=8)

                # data = json.loads(request.body)
            except Exception as e:
                logger.error(f"Error Unauthenticated user: {e}")
                # return generate_response(status=400,  data="Can not retrieve user", custom_message=str(e))
                error = {
                    "statusCode": 400,
                    "error": True,
                    "data": "",
                    "message": "Bad Request",
                    "errors": e.args[0],
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                if start:
                    start =  datetime.fromtimestamp(start)
                if end:
                    end = datetime.fromtimestamp(end)
            except Exception as e:
                logger.error(f"Error in heatmap: {e}")
                # return generate_response(status=400,  data="Could not parse dates", custom_message=str(e))
                error = {
                    "statusCode": 400,
                    "error": True,
                    "data": "",
                    "message": "Bad Request",
                    "errors": e.args[0],
                }
                
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            sentiments = user.user_in_sentiment.select_related("topic","top_story").all()
            
            try:
                topic = request.GET.get("topic")
            except Exception as e:
                logger.debug(f"No topic found : {e} \nRetrieving data for all topics")
                topic = None
            
            if topic:
                # sentiments=sentiments.filter(topic=topic)
                sentiments = list(filter(lambda x: (x.topic.pk==int(topic)), sentiments))
            
            
            if start:
                # sentiments= sentiments.filter( top_story__date__gte=start)
                sentiments = list(filter(lambda x: (x.top_story.date >= start.date()), sentiments))
            else:
                start= sentiments.first().top_story.date 
            
            if end:
                # sentiments= sentiments.filter(top_story__date__lt=end)
                sentiments = list(filter(lambda x: (x.top_story.date < end.date()), sentiments))
            else:
                end= sentiments.last().top_story.date 
                
            # sentiments=sentiments.order_by('top_story__date')
            sentiments.sort(key=lambda x: x.top_story.date)
            
            
            
            # sentiments= user.user_in_sentiment.all()
            # logger.debug(len(sentiments))
            # for s in sentiments:
            #     logger.debug(s.top_story.date)
            #     logger.debug(s.sentiment_analysis)
                
            sDay = start.day
            sMonth= start.month
            sYear= start.year
            
            
            eDay = end.day
            eMonth= end.month
            eYear= end.year
            
            deltaYears= eYear - sYear
            
            months= 0
            if deltaYears:
                months = (12 - sMonth) + 12*(deltaYears-1) + (eMonth)
            else:
                months = eMonth - sMonth
                
            ret = []
            for x in range( months+1):

                # calculate values for the month 
                temp_year = sYear + math.floor((sMonth + x)/(12.1))
                temp_month = (sMonth + x) % 12
                if temp_month== 0:
                    temp_month= 12
                    
                # logger.debug(x)
                # logger.debug(temp_year)
                # logger.debug(temp_month)
                
                # create day array 
                if temp_month == 2 and calendar.isleap(temp_year):
                    days_in_month= DAYS_IN_MONTH_LEAP[str(temp_month)]
                else:
                    days_in_month= DAYS_IN_MONTH[str(temp_month)]
                
                # create array for each day in month
                start_rg= 1
                if x == 0:
                    start_rg = sDay
                    
                end_rg = days_in_month + 1
                if x == months:
                    end_rg =eDay +1
                

                days=[None] * days_in_month
                    
                # logger.debug(days)
                # for s in sentiments:
                #     logger.debug(s.top_story.date)

                for y in range(start_rg, end_rg):
                    # temp_date = datetime(year=temp_year, month=temp_month, day=x)
                    # logger.debug(temp_date)
                    ey=(datetime(year=temp_year, month=temp_month, day=y, hour= 0, minute = 0, tzinfo=timezone.utc) + timedelta(days=1)) 
                    sy=datetime(year=temp_year, month=temp_month, day=y, hour= 0, minute = 0, tzinfo=timezone.utc)
                    # temp_sentiments = sentiments.filter(top_story__date__lt=ey , top_story__date__gte=sy)a
                    temp_sentiments = list(filter(lambda x: (x.top_story.date < ey.date()) and (x.top_story.date >= sy.date()), sentiments))
                    

                    # if temp_sentiments.count():
                    if len(temp_sentiments):
                        day = {
                            # "positive_narratives": temp_sentiments.filter(sentiment_analysis="positive").count(),
                            "positive_narratives": len(list(filter(lambda x: (x.sentiment_analysis == "positive"), temp_sentiments))),
                            # "neutral_narratives": temp_sentiments.filter(sentiment_analysis="neutral").count(),
                            "neutral_narratives": len(list(filter(lambda x: (x.sentiment_analysis == "neutral"), temp_sentiments))),
                            # "negative_narratives": temp_sentiments.filter(sentiment_analysis="negative").count(),
                            "negative_narratives": len(list(filter(lambda x: (x.sentiment_analysis == "negative"), temp_sentiments))),
                            "calender_day": y
                        }
                    else:
                        day = {
                            "positive_narratives": 0,
                            "neutral_narratives": 0,
                            "negative_narratives": 0,
                            "calender_day": y
                        }
                    
                    days[y-1] = day
                    
                
                
                temp = {
                    "year": temp_year,
                    "month": temp_month,
                    "days": days
                }
                ret.append(temp)

                
                
            
            
            return Response(ret, status=status.HTTP_200_OK)
            # return generate_response(status=200,  data=ret, custom_message=None)
        
        except Exception as e:
            logger.error(f"Error in heatmap: {e}")
            error = {
                "statusCode": 400,
                "error": True,
                "data": "",
                "message": "Bad Request",
                "errors": e.args[0],
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        # return generate_response(status=500,  data="Error processing heatmap.", custom_message=str(e))

class NarrativeHeatMap(APIView):
    authentication_classes = [ExpiringTokenAuthentication] 
    permission_classes = [IsAuthenticated]
    
    def get(self, request, start, end):
        '''
        This is the narrative version of the function
        This returns an array of month objects which contain day objects these approximations are intended for use with the heatmap
        Recieves: 
        
        start_date => the start date to collect data from
        end_date => the end date to stop collecting data
        
        recieves topic as a query variable
        
        returns:
        interface day {
        positive_narratives: number;
        neutral_narratives: number;
        negative_narratives: number;
        calender_day: number;
        }
        interface month {
            year: number;
            month: number;
            days: day[]
        } 
        
        '''
        try:
            try:
                user= request.user 
                # user = User.objects.get(pk=8)

                # data = json.loads(request.body)
            except Exception as e:
                logger.error(f"Error Unauthenticated user: {e}")
                # return generate_response(status=400,  data="Can not retrieve user", custom_message=str(e))
                error = {
                    "statusCode": 400,
                    "error": True,
                    "data": "",
                    "message": "Bad Request",
                    "errors": e.args[0],
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                narrative = request.GET.get("narrative")
            except Exception as e:
                logger.error(f"could not process narrative query param: {e}")            
                
            try:
                if start:
                    start =  datetime.fromtimestamp(start)
                if end:
                    end = datetime.fromtimestamp(end)
            except Exception as e:
                logger.error(f"Error in heatmap: {e}")
                # return generate_response(status=400,  data="Could not parse dates", custom_message=str(e))
                error = {
                    "statusCode": 400,
                    "error": True,
                    "data": "",
                    "message": "Bad Request",
                    "errors": e.args[0],
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            sentiments = user.user_in_sentiment.select_related("topic").prefetch_related("top_story__narrative").all()
            # print(len(sentiments))
            try:
                if narrative:
                    sentiments=sentiments.filter(top_story__narrative__pk=narrative)
                    # sentiments = list(filter(lambda x: (x.top_story.narrative.pk==int(narrative)), sentiments))
            except Exception as e:
                logger.error(f"could not filter by narrative query param: {e}")
                
                
            try:
                topic = request.GET.get("topic")
            except Exception as e:
                logger.debug(f"No topic found : {e} \nRetrieving data for all topics")
                topic = None
            
            if topic:
                sentiments=sentiments.filter(topic=topic)
                # sentiments = list(filter(lambda x: (x.topic.pk==int(topic)), sentiments))
            
            if start:
                # sentiments= sentiments.filter( top_story__date__gte=start)
                sentiments = list(filter(lambda x: (x.top_story.date >= start.date()), sentiments))
            else:
                start= sentiments.first().top_story.date 
            
            if end:
                # sentiments= sentiments.filter(top_story__date__lt=end)
                sentiments = list(filter(lambda x: (x.top_story.date < end.date()), sentiments))
            else:
                end= sentiments.last().top_story.date 
                
            # sentiments=sentiments.order_by('top_story__date')
            sentiments.sort(key=lambda x: x.top_story.date)
            
            
            
            # sentiments= user.user_in_sentiment.all()
            # logger.debug(len(sentiments))
            # for s in sentiments:
            #     logger.debug(s.top_story.date)
            #     logger.debug(s.sentiment_analysis)
                
            sDay = start.day
            sMonth= start.month
            sYear= start.year
            
            
            eDay = end.day
            eMonth= end.month
            eYear= end.year
            
            deltaYears= eYear - sYear
            
            months= 0
            if deltaYears:
                months = (12 - sMonth) + 12*(deltaYears-1) + (eMonth)
            else:
                months = eMonth - sMonth
                
            ret = []
            for x in range( months+1):

                # calculate values for the month 
                temp_year = sYear + math.floor((sMonth + x)/(12.1))
                temp_month = (sMonth + x) % 12
                if temp_month== 0:
                    temp_month= 12
                    
                # logger.debug(x)
                # logger.debug(temp_year)
                # logger.debug(temp_month)
                
                # create day array 
                if temp_month == 2 and calendar.isleap(temp_year):
                    days_in_month= DAYS_IN_MONTH_LEAP[str(temp_month)]
                else:
                    days_in_month= DAYS_IN_MONTH[str(temp_month)]
                
                # create array for each day in month
                start_rg= 1
                if x == 0:
                    start_rg = sDay
                    
                end_rg = days_in_month + 1
                if x == months:
                    end_rg =eDay +1
                

                days=[None] * days_in_month
                    
                # logger.debug(days)
                # for s in sentiments:
                #     logger.debug(s.top_story.date)

                for y in range(start_rg, end_rg):
                    # temp_date = datetime(year=temp_year, month=temp_month, day=x)
                    # logger.debug(temp_date)
                    ey=(datetime(year=temp_year, month=temp_month, day=y, hour= 0, minute = 0, tzinfo=timezone.utc) + timedelta(days=1)) 
                    sy=datetime(year=temp_year, month=temp_month, day=y, hour= 0, minute = 0, tzinfo=timezone.utc)
                    # temp_sentiments = sentiments.filter(top_story__date__lt=ey , top_story__date__gte=sy)a
                    temp_sentiments = list(filter(lambda x: (x.top_story.date < ey.date()) and (x.top_story.date >= sy.date()), sentiments))
                    

                    # if temp_sentiments.count():
                    if len(temp_sentiments):
                        day = {
                            # "positive_narratives": temp_sentiments.filter(sentiment_analysis="positive").count(),
                            "positive_narratives": len(list(filter(lambda x: (x.sentiment_analysis == "positive"), temp_sentiments))),
                            # "neutral_narratives": temp_sentiments.filter(sentiment_analysis="neutral").count(),
                            "neutral_narratives": len(list(filter(lambda x: (x.sentiment_analysis == "neutral"), temp_sentiments))),
                            # "negative_narratives": temp_sentiments.filter(sentiment_analysis="negative").count(),
                            "negative_narratives": len(list(filter(lambda x: (x.sentiment_analysis == "negative"), temp_sentiments))),
                            "calender_day": y
                        }
                    else:
                        day = {
                            "positive_narratives": 0,
                            "neutral_narratives": 0,
                            "negative_narratives": 0,
                            "calender_day": y
                        }
                    
                    days[y-1] = day
                    
                
                
                temp = {
                    "year": temp_year,
                    "month": temp_month,
                    "days": days
                }
                ret.append(temp)

                
                
            
            
            return Response(ret, status=status.HTTP_200_OK)
            # return generate_response(status=200,  data=ret, custom_message=None)
        
        except Exception as e:
            logger.error(f"Error in heatmap: {e}")
            error = {
                "statusCode": 400,
                "error": True,
                "data": "",
                "message": "Bad Request",
                "errors": e.args[0],
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            
DAYS_IN_MONTH= {
    "1":31,
    "2":28,
    "3":31,
    "4":30,
    "5":31,
    "6":30,
    "7":31,
    "8":31,
    "9":30,
    "10":31,
    "11":30,
    "12":31,
}

DAYS_IN_MONTH_LEAP = {
    "1":31,
    "2":29,
    "3":31,
    "4":30,
    "5":31,
    "6":30,
    "7":31,
    "8":31,
    "9":30,
    "10":31,
    "11":30,
    "12":31,
}