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
import logging
import requests
from twarc.client2 import Twarc2
from twarc.expansions import ensure_flattened

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
        bearer_tokenenv = env('BEARER_TOKEN')  
        
        try:
            self.auth = OAuthHandler(API_key, 
                                     API_secret)
            self.auth.set_access_token(access_token,
                                       access_token_secret)
            self.api = tweepy.API(self.auth)

            self.client = tweepy.Client(bearer_tokenenv, 
                       API_key, 
                       API_secret, 
                       access_token, 
                       access_token_secret)

            self.twarc = Twarc2(bearer_token=bearer_tokenenv)

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

        try:
            filtered = qu +" lang:en -is:retweet"
            
            if int(count)<=100:
                max = int(count)
                limit = 1
            else:
                limit = int(count)/100
                max = 100

            search_results = self.twarc.search_recent(query=filtered, max_results=max)

            i = 0
            for page in search_results:
                i += 1
                # Do something with the whole page of results.
                for tweet in ensure_flattened(page):
                    # Do something with the tweet
                    fetched_tweets.append(tweet)
                if i == limit:
                # Stop iteration prematurely, to only get 1 page of results.
                    break

            for tweet in fetched_tweets:

                parsed_tweet = {}
                parsed_tweet['author_id'] = tweet['author_id']
                parsed_tweet['username'] = tweet['author']['username']
                parsed_tweet['text'] = tweet['text']
                parsed_tweet['cleaned_text'] = TextBlob(self.cleaning_process(tweet['text']))
                parsed_tweet['sentiment'] = self.get_sentiment(tweet['text'])
                parsed_tweet['like_count'] = tweet['public_metrics']['like_count']
                parsed_tweet['retweet_count'] = tweet['public_metrics']['retweet_count']
                parsed_tweet['date'] = tweet['created_at']
                parsed_tweet['entities'] = 'entity'
                parsed_tweet['id'] = tweet['id']
                if tweet['author'].get('location') is not None:
                    parsed_tweet['location'] = tweet['author']['location']
                else:
                    parsed_tweet['location'] = 'None'
                
                #convert to string
                if tweet.get('context_annotations') is None:
                   parsed_tweet['context_annotation'] = 'None'
                else:
                    contextannotation = json.dumps(tweet['context_annotations'])
                    parsed_tweet['context_annotation'] = contextannotation
           

              
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
                user=i['username'],
                author_id = i['author_id'],
                location = i['location'],
                cleaned_tweet = i['cleaned_text'],
                like_count = i['like_count'],
                retweet_count = i['retweet_count'],
                date = i['date'],
                entities = i['entities'],
                context_annotations = i['context_annotation'],

                
            )
            tweet_data.save()
        
        return render(request, 'collectedpage.html', {'tweets': tweets1})




