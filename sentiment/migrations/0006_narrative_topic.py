# Generated by Django 5.0.3 on 2024-06-20 04:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sentiment', '0005_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='narrative',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='narratives', to='sentiment.topic'),
        ),
    ]