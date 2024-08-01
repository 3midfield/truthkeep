# Generated by Django 5.0.3 on 2024-06-19 19:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0)),
                ('subscription_id', models.CharField(blank=True, max_length=100, null=True)),
                ('plan', models.CharField(choices=[('Starter Plan', 'Starter Plan'), ('Starter Plan Annual', 'Starter Plan Annual'), ('Advantage Plan', 'Advantage Plan'), ('Advantage Plan Annual', 'Advantage Plan Annual'), ('Elite Plan', 'Elite Plan')], default='Starter Plan', max_length=25)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('cancel_at', models.DateTimeField(blank=True, null=True)),
                ('last_payment', models.DateTimeField(blank=True, null=True)),
                ('charge_id', models.CharField(blank=True, max_length=255, null=True)),
                ('failed_reason', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_in_subscription', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'subscription',
                'verbose_name_plural': 'subscriptions',
            },
        ),
    ]
