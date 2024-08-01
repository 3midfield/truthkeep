from django.contrib import admin
from sentiment.models.articles import TopStories
from .models.narrative import Narrative
from .models.topic import Topic
from .models.sentiment import SentimentAnalysis


# Register your models here.
# class TopStoriesAdmin(admin.ModelAdmin):
#     readonly_fields = ("created_at",)


admin.site.register(TopStories)
admin.site.register(SentimentAnalysis)
# admin.site.register(ContactUs)
# admin.site.register(Subscribe)
# admin.site.register(Flagged)
# admin.site.register(Waitlist)
admin.site.register(Narrative)
admin.site.register(Topic)