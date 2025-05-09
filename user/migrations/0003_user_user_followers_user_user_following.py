# Generated by Django 5.1.1 on 2024-09-20 06:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_user_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="user_followers",
            field=models.ManyToManyField(
                blank=True, related_name="follower_users", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_following",
            field=models.ManyToManyField(
                blank=True, related_name="following_users", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
