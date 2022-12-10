from django.shortcuts import render
from django.http import *
from ominer.forms import *
from django.shortcuts import render, get_object_or_404

from ominer.models import TweetQuery, Tweets

from django.contrib.auth.models import User

import json
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

from . import wordcloud

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
        if type(tweet) == np.float:
            return ""
            
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"
                               , " ", tweet.lower()).split())
 
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
        fetched_tweets = []
        limit = int(count)
        i = 0 
        try:
            #filter the query to remove retweets
            filtered = qu + "-filter:retweets"

            for t in tweepy.Cursor(self.api.search_tweets,
                                    q=filtered,
                                    lang='en',
                                    count = count,
                                    tweet_mode='extended').items():
                
                fetched_tweets.append(t)
                i += 1
                if i>= limit:
                    break
                else:
                    pass

            for tweet in fetched_tweets:
                parsed_tweet = {}
                parsed_tweet['user'] = tweet.user.screen_name
                parsed_tweet['text'] = tweet.full_text
                parsed_tweet['cleaned_text'] = TextBlob(self.cleaning_process(tweet.full_text))
                parsed_tweet['sentiment'] = self.get_sentiment(tweet.full_text)
                parsed_tweet['location'] = tweet.user.location
                parsed_tweet['like_count'] = tweet.favorite_count
                parsed_tweet['retweet_count'] = tweet.retweet_count
                parsed_tweet['date'] = tweet.created_at
                parsed_tweet['entities']= tweet.entities
                parsed_tweet['context_annotations'] = tweet.context_annotations
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


def queries(request):
    querydata = TweetQuery.objects.filter(owner=request.user).order_by('-date')
    
    query = {
        "queries": querydata,
    }
        
    return render(request,'queries.html', query)


def query_detail(request, pk):
    query = get_object_or_404(TweetQuery, pk=pk)

    tweetdata = Tweets.objects.all().filter(query=pk)

            # get cleaned_tweets from database and create a wordcloud
    pos_tweets = Tweets.objects.filter(query=pk, sentiment='positive')
    neg_tweets = Tweets.objects.filter(query=pk, sentiment='negative')
    neut_tweets = Tweets.objects.filter(query=pk, sentiment='neutral')

        # adding the percentages to the prediction array to be shown in the html page.  

    values = []
    positive = round(100*len(pos_tweets)/len(tweetdata),2)
    negative = round(100*len(neg_tweets)/len(tweetdata),2)
    neutral = round(100*len(neut_tweets)/len(tweetdata),2)


    values.append(positive)
    values.append(negative)
    values.append(neutral)

    mylist = json.dumps(values)
    return render(request, 'queryreport.html', {'values':mylist,'query': query, 'tweetdata': tweetdata})


def collect(request):

    if request.method == 'POST' :
        api = TwitterSentClass()
        t = request.POST['Keyword']
        c = request.POST['Count']
        tweets1 = api.get_tweets(qu = t, count = c)

        ######### current query almayı öğren

        query_data = TweetQuery(
            owner= request.user,
            query = t,
            count = len(tweets1)
        )
        query_data.save()

        for i in tweets1:
            tweet_data = Tweets(
                queryowner=request.user,
                tweet=i['text'],
                query=TweetQuery.objects.filter(owner=request.user, query=t).last(),
                sentiment=i['sentiment'],
                user=i['user'],
                location = i['location'],
                cleaned_tweet = i['cleaned_text'],
                like_count = i['like_count'],
                retweet_count = i['retweet_count'],
                date = i['date'],
                entities = i['entities'],
                context_annotations = i['context_annotations'],

                
            )
            tweet_data.save()
        
        return render(request, 'collectedpage.html', {'tweets': tweets1})



