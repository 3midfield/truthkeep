# Generated by Django 5.0.3 on 2024-06-20 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sentiment', '0006_narrative_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='topstories',
            name='narrative',
            field=models.ManyToManyField(blank=True, related_name='top_stories', to='sentiment.narrative'),
        ),
    ]
