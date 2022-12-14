from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings

# Create your models here.

class TweetQuery(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.TextField(max_length=255)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    count = models.IntegerField(default=0)

    def __str__(self):
         return self.query

class Tweets(models.Model):
    
    queryowner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.ForeignKey(TweetQuery,default=None, on_delete=models.CASCADE)
    tweet = models.TextField(max_length=280)
    cleaned_tweet = models.TextField(max_length=280, blank='True', null='True')
    sentiment = models.TextField(max_length=15)
    user = models.TextField(max_length=100)
    location = models.TextField(max_length=100,null=True, blank=True)
    like_count = models.IntegerField(default=0)
    retweet_count = models.IntegerField(default=0)
    date = models.DateTimeField(blank=True, null=True)
    followers_count = models.IntegerField(default=0)
    context_annotations = models.TextField(max_length=1000, blank=True, null=True)
    author_id = models.TextField(max_length=280, blank=True, null=True)
    hashtags = models.TextField(max_length=1000, blank=True, null=True)
    annotations = models.TextField(max_length=1000, blank=True, null=True)

    def __str__(self):
         return self.tweet