from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings

# Create your models here.

class TweetQuery(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.TextField(max_length=255)

    def __str__(self):
         return self.query

class Tweets(models.Model):
    
    query = models.ForeignKey(TweetQuery,default=None, on_delete=models.CASCADE)
    tweet = models.TextField(max_length=280)

    def __str__(self):
         return self.tweet