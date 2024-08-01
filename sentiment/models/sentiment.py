from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class SentimentAnalysis(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_in_sentiment",
        null=True,
        blank=True,
    )
    top_story = models.ForeignKey(
        "sentiment.TopStories",
        on_delete=models.CASCADE,
        related_name="top_story_in_sentiment",
        null=True,
        blank=True,
    )
    reasoning = models.TextField(null=True, blank=True, default="Reasoning not provided.")
    topic = models.ForeignKey("sentiment.Topic",blank=True, null=True, on_delete=models.CASCADE, related_name="sentiments")
    score = models.IntegerField(default=-1)
    sentiment_analysis = models.CharField(max_length=250, null=True, blank=True)
    positive_score = models.CharField(max_length=250, null=True, blank=True)
    positive_percentage = models.CharField(max_length=250, null=True, blank=True)
    negative_score = models.CharField(max_length=250, null=True, blank=True)
    negative_percentage = models.CharField(max_length=250, null=True, blank=True)
    neutral_score = models.CharField(max_length=250, null=True, blank=True)
    neutral_percentage = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.__class__.__name__}(id:{self.id}) score:{self.score}, topic: {self.topic.topic if self.topic and self.topic.topic else None}, top story: {self.top_story if self.top_story else None}"


# class ContactUs(models.Model):
#     email = models.EmailField(_("email address"), null=True, blank=True)
#     first_name = models.CharField(max_length=250, null=True, blank=True)
#     last_name = models.CharField(max_length=250, null=True, blank=True)
#     subject = models.CharField(max_length=250, null=True, blank=True)
#     message = models.CharField(max_length=250, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.__class__.__name__}(id={self.id})"


# class Subscribe(models.Model):
#     email = models.EmailField(_("email address"), null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.__class__.__name__}(id={self.id})"


# class Flagged(models.Model):
#     ''' redundant we should remove'''
#     top_story = models.ForeignKey(
#         TopStories,
#         on_delete=models.CASCADE,
#         related_name="top_story_in_flagged",
#         null=True,
#         blank=True,
#     )
#     percentage = models.CharField(max_length=250, null=True, blank=True)
#     value = models.CharField(max_length=1000, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class Waitlist(models.Model):
#     first_name = models.CharField(max_length=50, null=True, blank=True)
#     last_name = models.CharField(max_length=50, null=True, blank=True)
#     email = models.EmailField(_("email address"), null=True, blank=True, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.__class__.__name__}(id={self.id})"
