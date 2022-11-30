from django.contrib import admin


# Register your models here.

from .models import TweetQuery, Tweets

admin.site.register(TweetQuery)
admin.site.register(Tweets)

