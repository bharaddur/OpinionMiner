from django.contrib import admin


# Register your models here.

from .models import TweetQuery, Tweets

class AdminTweetQuery(admin.ModelAdmin):
    model= TweetQuery
    list_display = ('owner','query')
    list_filter = ('owner',)

admin.site.register(TweetQuery, AdminTweetQuery)


class AdminTweets(admin.ModelAdmin):
    model= Tweets
    list_display = ('query', 'tweet','sentiment')
    list_filter = ('query','sentiment')

admin.site.register(Tweets, AdminTweets)

