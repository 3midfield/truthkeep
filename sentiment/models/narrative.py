from django.db import models

from django.contrib.auth.models import User
from aiModule.scripts.ai_tools.narrative_tools import Narrative_comparison, Narrative_PYD
from aiModule.scripts.pinecone import PineconeWrapper
# from openai import OpenAI
from rest_framework import serializers
from aiModule.scripts.openai_wrapper import OpenAIWrapper
from datetime import datetime, timezone
import os
import json
import instructor
from django.apps import apps
from django.db.models import Sum
# from utility.scripts.ai_tools.narrative_tools import tool_create_narrative
import logging
logger = logging.getLogger("TargetLog")

class Narrative(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="managed_narratives", null=True, blank=True)
    # represents the subject/topic of the narrative
    topic = models.ForeignKey("sentiment.Topic", on_delete=models.CASCADE, related_name="narratives", null=True, blank=True)
    title = models.CharField(max_length=512, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_story_added = models.DateTimeField(blank=True, null=True)
    
    main_points=models.TextField(blank=True, null=True)
    supporting_facts=models.TextField(blank=True, null=True)
    impact_score = models.IntegerField(default=-1)
    

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.pk}): {self.title}, user:{self.user.username if self.user and self.user.username else None}, created_at: {self.created_at}, last_article_added {self.last_story_added}"
    
    def create_narrative_impact_scrore(self):
        '''
        Creates a narrative impact score and saves it to the narrative
        sums the imapcts scores
        updated each time a new article is added to the narrative
        '''
        try:
            impact_score = self.top_stories.aggregate(Sum('impact_score'))
            self.impact_score=int(impact_score["impact_score__sum"])
            self.save()
        except Exception as e:
            logger.error(f"Error summing and saving impact scores: {e}")
    
    @staticmethod
    def analyze_narrative(user, story, topic, texts):
        '''
        This fucntion analyzes a top story and increments or creates a new narrative
        story: TopStory, expecting a top story from the system
        topic: the topic of the narrative
        texts: the text from the article
        
        This function stores narratives in a vdb under the index 'narratives' and using the topic pk as the namespace
        '''
        try:
            logger.debug("starting narrative analysis ------------------------------------------------")
            # create open ai instance
            ai = OpenAIWrapper()
            ai.authorize()

        # use open ai to summarize and create a narrative 
            res, success = ai.send_text_tools_chat(
            message=f"""
            Generate a comprehensive narrative based on the provided information. A narrative represents the main points of an article or set of data and connects them with other relevant information, events, and news. This function synthesizes the central ideas and supporting details into a coherent and engaging story.
            
            A narrative is the core storyline derived from the given information. This narrative should be a concise, clear, and compelling summary that captures the essence of the information and connects it with broader contexts and related events. It should not only present the facts but also provide a cohesive interpretation that highlights the significance and implications of the information.This field is mandatory.
            
            The narrative must pertain to {topic.topic}
        
            here is the article:
            '''
            {texts}
            '''

            """,
            response_model=Narrative_PYD
            )
            try:
                summary = res.summary
                main_points =res.main_points
                supporting_facts = res.supporting_facts
                title= res.title
                
                #TODO add validation to ensure tokenization
                data={
                    "title":title,
                    "summary":summary,
                    "main_points":main_points,
                    "date":str(datetime.now(timezone.utc))
                }
            except Exception as e:
                logger.error("Error processing narrative data")
            
            # create embedding to matcha gainst
            emb = ai.create_embedding(data)
            # connect to vdb
            pc = PineconeWrapper()
            pc.index_create_connect("narratives")
            # query into the vdb for vectors matching the above narrative
            #perform a cosine search
            succ, matching_vectors = pc.query_index_by_vector(vector=emb, top_k=5, include_values=False, include_metadata=True, return_all=False, mdFilter= None, namespace = str(topic.pk))
            # logger.debug(matching_vectors)
            
            if succ:
                matching_vectors=matching_vectors.matches
                updated_narratives=[]
                # validate matches
                if matching_vectors:
                    for match in matching_vectors:
                        #retrieve and augment narrative
                        try:
                            narrative_pk = match.id
                            score= match.score
                            v_narrative=match.metadata["narrative"]
                            
                            if score > 0.97:
                                    #check if stories are relevant
                                ai = OpenAIWrapper()
                                ai.authorize()
                                # TODO system instructions 
                                res, success = ai.send_text_tools_chat(
                                    message=f"""
                                    A narrative is the core storyline derived from the given information. This narrative should captures the essence of the information and connects it with related events.
                                    Please compare the following two narratives and determine if they are related. Please return a boolean representing if the two narratives are related.
                                    Both narratives should pertain to {topic.topic}
                                    Two narratives are related if they share main_points/summary that are directly related to eachother.
                                    Narratives are more commonly not related, for narratives to be a match they should be extremley similar.
                                    The majority of comparisons should come back False.
                                    
                                    
                                    here is narrative 1:
                                    '''
                                    {data}
                                    '''
                                    
                                    Here is narrative 2:
                                    '''
                                    {v_narrative}
                                    '''
                                    """,
                                    response_model=Narrative_comparison
                                    )
                                logger.debug("]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]][[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]")
                                logger.debug(res)
                                if success and res.match:
                                    # update narrative 1 with narrative 2
                                    # TODO system instructions 
                                    res, success = ai.send_text_tools_chat(
                                        message=f"""
                                        Please update narrative 1 with any additional information present in narrative 2.
                                        The two narratives are related please refer to the date for chronological order.
                                        
                                        A narrative is the core storyline derived from the given information. This narrative should be a concise, clear, and compelling summary that captures the essence of the information and connects it with broader contexts and related events. It should not only present the facts but also provide a cohesive interpretation that highlights the significance and implications of the information.This field is mandatory.
                                    
                                        The narrative must pertain to {topic.topic}
                                    
                                        here is narrative 1:
                                        '''
                                        {v_narrative}
                                        '''
                                        
                                        Here is narrative 2:
                                        '''
                                        {data}
                                        '''
                                        """,
                                        response_model=Narrative_PYD
                                        )
                                    
                                    if success:
                                        # retrieve object and update 
                                        try:
                                            logger.debug("updating narrative")
                                            try:
                                                narrative=apps.get_model("sentiment.Narrative").objects.get(pk=narrative_pk)
                                                narrative.summary = res.summary
                                                narrative.title = res.title 
                                                narrative.main_points= res.main_points
                                                narrative.supporting_fact=res.supporting_facts
                                                narrative.last_story_added=datetime.now(timezone.utc)
                                                # narrative.updated_at=datetime.now(timezone.utc)
                                                narrative.save()
                                            except Exception as e:
                                                logger.debug("Could not retrieve and update narrative: {e}")
                                                if not apps.get_model("sentiment.Narrative").objects.filter(pk=narrative_pk).exists():
                                                    logger.debug("creating new narrative due to error --------------------------------------")
                                                    narrative = apps.get_model("sentiment.Narrative").objects.create(
                                                        user = user,
                                                        topic = topic,
                                                        title = res.title,
                                                        summary = res.summary,
                                                        last_story_added = datetime.now(timezone.utc),
                                                        main_points=res.main_points,
                                                        supporting_facts=res.supporting_facts
                                                    )
                                                    # remove old vector 
                                                    try:
                                                        pc.delete_vectors(ids=[narrative_pk], namespace=str(topic.pk))
                                                    except Exception as e:
                                                        logger.error(f"Could not remove vector with missing narrative: {e}")
                                                
                                            logger.debug(narrative)
                                            try:
                                                story.narrative.add(narrative)
                                                narrative.create_narrative_impact_scrore()
                                                # story.save()
                                            except Exception as e:
                                                logger.error(f"--------------------could not update article: {e}")
                                                
                                            #embed vector
                                            data={
                                                "title":narrative.title,
                                                "summary":narrative.summary,
                                                "main_points": narrative.main_points,
                                                "date":str(datetime.now(timezone.utc))
                                            }
                                            emb = ai.create_embedding(data)
                                            metadata = {
                                                "title":title,
                                                "user":str(user.pk),
                                                "topic":str(topic.pk),
                                                #switch to serialized narrative
                                                "narrative":json.dumps(NarrativeCrawlerSerializer(narrative).data)
                                            }
                                            pc.insert_vectors(emb, metadata=metadata, namespace=str(topic.pk), id=str(narrative.pk))
                                            
                                            updated_narratives.append(narrative)
                                        except Exception as e:
                                            logger.error(f"----------------------Error updating narrative: {e}")
                        except Exception as e:
                            logger.error(f"Error processing vector match for narrative: {e}")
                            continue
                   
                    if updated_narratives:
                        return updated_narratives
                    
                #make a new narrative
                logger.debug("creating new narrative")
                narrative = apps.get_model("sentiment.Narrative").objects.create(
                    user = user,
                    topic = topic,
                    title = title,
                    summary = summary,
                    last_story_added = datetime.now(timezone.utc),
                    main_points=main_points,
                    supporting_facts=supporting_facts
                )
                try:
                    story.narrative.add(narrative)
                    narrative.create_narrative_impact_scrore()
                    # story.save()
                except Exception as e:
                    logger.error("could not update article")
                
                # embed new narrative object
                metadata = {
                    "title":title,
                    "user":str(user.pk),
                    "topic":str(topic.pk),
                    #switch to serialized narrative
                    "narrative":json.dumps(NarrativeCrawlerSerializer(narrative).data)
                }

                pc.insert_vectors(emb, metadata=metadata, namespace=str(topic.pk), id=str(narrative.pk))
                
                #return serialized object here
                return [narrative]
            
            return []
        except Exception as e:
            logger.error(f"Error in analyze_narrative:{e}")
            return False
        
        
class NarrativeCrawlerSerializer(serializers.ModelSerializer):
    '''
    used with static function for Narrative
    '''
    user     = serializers.PrimaryKeyRelatedField( many=False, required=False, allow_null=True, default=None, read_only=True)
    topic      = serializers.PrimaryKeyRelatedField( many=False, required=False, allow_null=True, default=None, read_only=True)
    class Meta:
        model = Narrative
        fields = ["pk","user", "topic", "title", "summary", "main_points","updated_at","supporting_facts", "last_story_added"]
        