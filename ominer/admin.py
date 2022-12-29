from django.contrib import admin


# Register your models here.

from .models import TweetQuery, Tweets

class AdminTweetQuery(admin.ModelAdmin):
    model= TweetQuery
    list_display = ('owner','query','date')
    list_filter = ('owner',)

admin.site.register(TweetQuery, AdminTweetQuery)


class AdminTweets(admin.ModelAdmin):
    model= Tweets
    list_display = ('user','query','tweet','cleaned_tweet','sentiment','location','queryowner','like_count','retweet_count','date','followers_count','context_annotations','hashtags', 'annotations')
    list_filter = ('query','sentiment')

admin.site.register(Tweets, AdminTweets)

