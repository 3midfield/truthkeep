# Generated by Django 5.0.3 on 2024-07-09 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sentiment', '0009_topstories_impact_score_topstories_publisher_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='narrative',
            name='impact_score',
            field=models.IntegerField(default=-1),
        ),
    ]
