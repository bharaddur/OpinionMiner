from django.shortcuts import render
from django.http import *
from ominer.forms import *

from ominer.models import TweetQuery, Tweets

from django.contrib.auth.models import User


import environ
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import tweepy
import os
from tweepy import OAuthHandler
from textblob import TextBlob
# Create your views here.

# Create your views here.
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

class TwitterSentClass():
    def __init__(self):
        API_key = env('API_KEY')
        API_secret = env('API_SECRET')
        access_token = env('ACCESS_TOKEN')
        access_token_secret = env('ACCESS_TOKEN_SECRET')  
        
        try:
            self.auth = OAuthHandler(API_key, 
                                     API_secret)
            self.auth.set_access_token(access_token,
                                       access_token_secret)
            self.api = tweepy.API(self.auth)
            print('Authenticated')
        except:
            print("Sorry! Error in authentication!")
 
    def cleaning_process(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"
                               , " ", tweet).split())
 
    def get_sentiment(self, tweet):
        analysis = TextBlob(self.cleaning_process(tweet))
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

 
    def get_tweets(self, qu, count):
        tweets = []
        try:
            fetched_tweets = self.api.search_tweets(q = qu, count = count)
            for tweet in fetched_tweets:
                parsed_tweet = {}
                parsed_tweet['text'] = tweet.text
                parsed_tweet['sentiment'] =self.get_sentiment(tweet.text)
                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            return tweets
            
        except tweepy.errors.TweepyException as e:
            print("Error : " + str(e))



# Create your views here.

def show(request):
    form = TwitterForm()
    return render(request,'index.html',{'ff':form})

            
def prediction(request):
    arr_pred = []
    arr_pos_txt = []
    arr_neg_txt = []
    if request.method == 'POST' :
        api = TwitterSentClass()
        t = request.POST['Keyword']
        tweets1 = api.get_tweets(qu = t, count = 100)

        pos_tweets = [tweet for tweet in tweets1 if tweet['sentiment'] == 'positive']
        pos = "Positive tweets percentage: {} %".format(100*len(pos_tweets)/len(tweets1))

        neg_tweets = [tweet for tweet in tweets1 if tweet['sentiment'] == 'negative']
        neg="Negative tweets percentage: {}%".format(100*len(neg_tweets)/len(tweets1))                
        # adding the percentages to the prediction array to be shown in the html page.
        arr_pred.append(pos)
        arr_pred.append(neg)
        
        # storing first 5 positive tweets
        arr_pos_txt.append("Positive tweets:")
        for tweet in pos_tweets[:5]:
            arr_pos_txt.append(tweet['text'])

        # storing first 5 negative tweets
        arr_neg_txt.append("Negative tweets:")
        for tweet in neg_tweets[:5]:
            arr_neg_txt.append(tweet['text'])

          

        query_data = TweetQuery(
            owner= request.user,
            query = t
        )
        query_data.save()

        for i in tweets1:
            tweet_data = Tweets(
                tweet=i['text'],
                query=TweetQuery.objects.get(query=t)
            )
            tweet_data.save()

        return render(request,'prediction.html',{'arr_pred':arr_pred,'arr_pos_txt':arr_pos_txt,'arr_neg_txt':arr_neg_txt})



