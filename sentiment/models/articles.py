from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from aiModule.scripts.openai_wrapper import OpenAIWrapper
from aiModule.scripts.ai_tools.article_tools import Article_Comparison

import logging
logger = logging.getLogger("TargetLog")
# Create your models here.
class TopStories(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_in_top_story",null=True, blank=True)
    # narrative = models.ForeignKey("sentiment.narrative", on_delete=models.SET_NULL, related_name="top_stories", null=True, blank=True)
    narrative = models.ManyToManyField("sentiment.narrative", related_name="top_stories",  blank=True)
    topic = models.ForeignKey("sentiment.Topic", on_delete=models.CASCADE, related_name="articles", null=True, blank=True)
    title = models.CharField(max_length=1000, null=True, blank=True)
    link = models.CharField(max_length=1000, null=True, blank=True)
    source = models.CharField(max_length=250, null=True, blank=True)
    date_posted = models.CharField(max_length=250, null=True, blank=True)
    thumbnail = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #this is a datetime for the date posted
    date = models.DateField()
    publisher_level = models.IntegerField(default=-1)
    impact_score = models.IntegerField(default=-1)
    

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id})"
    

    def create_article_impact_scrore(self):
        '''
        Creates an article impact_score and saves it to the article
        '''
        #create basemodel to create level score
        try:
            try:
                logger.debug("starting article impact score analysis ------------------------------------------------")
                # create open ai instance
                ai = OpenAIWrapper()
                ai.authorize()
            except:
                logger.error(f"error initializing ai wwrapper: {e}")
                return False
            # call prompt with base model
            res, success = ai.send_text_tools_chat(
            message=f"""
            Assign a level from 1-3 based on the sources reknown. 
            3 is for a highly reputable outlet, 2 for a lesser known source, and 1 for an unknown source. 
            You must assign a level from the options 1,2 and 3 
        
            here is the source:
            '''
            {self.source}
            '''

            """,
            response_model=Article_Comparison
            )
            
            if not success:
                return False
        
            level = int(res.publisher_level)
        except Exception as e:
            logger.error(f"Error processing Article_Comparison: {e}")
            return False
        

        # sort sentiment according to the following
        try:
            score = self.top_story_in_sentiment.first().score
        except Exception as e:
            logger.error(f"Could not retrieve sentiment score: {e} \nSkipping...")
            return False
        
        try:
            impact = 0
            match level:
                case 1:
                    if score <= 20:
                        impact=2
                    elif score > 20 and score <= 40:
                        impact=2
                    elif score > 40 and score <= 60:
                        impact=1
                    elif score > 60 and score <= 80:
                        impact=1
                    elif score > 80:
                        impact=2
                case 2:
                    if score <= 20:
                        impact=3
                    elif score > 20 and score <= 40:
                        impact=2
                    elif score > 40 and score <= 60:
                        impact=1
                    elif score > 60 and score <= 80:
                        impact=2
                    elif score > 80:
                        impact=2
                case 3:
                    if score <= 20:
                        impact=3
                    elif score > 20 and score <= 40:
                        impact=3
                    elif score > 40 and score <= 60:
                        impact=2
                    elif score > 60 and score <= 80:
                        impact=3
                    elif score > 80:
                        impact=3
        except Exception as e:
            logger.error(f"Could not process impact score: {e} \nSkipping...")
            return False
        # create impact score
        try:
            self.publisher_level= level
            self.impact_score = impact
            self.save()
            
        except Exception as e:
            logger.error(f"Error saving impact score: {e} \nSkipping...")
            return False
        