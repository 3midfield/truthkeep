from django.db import models
from django.apps import apps
from django.contrib.auth.models import User
# from utility.scripts.ai_tools.narrative_tools import tool_create_narrative

import logging
logger = logging.getLogger("StandardLog")


class Topic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="managed_topics", null=True, blank=True)
    topic = models.CharField(max_length=512, null=True, blank=True)
    tag = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.__class__.__name__}(id={self.pk}): {self.topic}, user: {self.user.username if self.user and self.user.username else None}, created_at:{self.created_at}, updated_at: {self.updated_at}"
    