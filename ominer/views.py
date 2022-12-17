from django.shortcuts import render
from django.http import *
from ominer.forms import *
from django.shortcuts import render, get_object_or_404

from ominer.models import TweetQuery, Tweets

from django.contrib.auth.models import User

import json
import nltk
from nltk.corpus import stopwords
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

from stop_words import get_stop_words


# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

class TwitterSentClass():

    # class constructor

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


    # function to clean tweet text by removing links, special characters using simple regex statements.
    def cleaning_process(self, tweet):
        if type(tweet) == np.float:
            return ""
            
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"
                               , " ", tweet.lower()).split())
    
    # function to get sentiment of a tweet

    def get_sentiment(self, tweet):
        analysis = TextBlob(self.cleaning_process(tweet))
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    # function to get tweets and store them in a dataframe sentiment function is also called here

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


# Form page that takes the query and number of tweets

def show(request):
    form = TwitterForm()
    return render(request,'index.html',{'ff':form})


# Query page that shows the queries that has been done previously

def queries(request):
    querydata = TweetQuery.objects.filter(owner=request.user).order_by('-date')
    
    query = {
        "queries": querydata,
    }
        
    return render(request,'queries.html', query)

# Detail page that shows the details of the query in a dashboard
def query_detail(request, pk):
    query = get_object_or_404(TweetQuery, pk=pk)

    tweetdata = Tweets.objects.filter(query=pk)


    stop_words = get_stop_words('en')

    querytext = TweetQuery.objects.get(pk=pk)
    additionalstop_words = nltk.word_tokenize(querytext.query)
    
    for word in additionalstop_words:
        stop_words.append(word.lower())

    # get cleaned_tweets from database and create a wordcloud
    pos_tweets = Tweets.objects.filter(query=pk, sentiment='positive')
    neg_tweets = Tweets.objects.filter(query=pk, sentiment='negative')
    neut_tweets = Tweets.objects.filter(query=pk, sentiment='neutral')

    negtext = neg_tweets.values_list('cleaned_tweet', flat=True)
    wordcloudneg = word_cloud_view(negtext, stop_words)


    postext =  pos_tweets.values_list('cleaned_tweet', flat=True)
    wordcloudpos = word_cloud_view(postext, stop_words)  

    # adding the percentages to the prediction array to be shown in the html page.  

    values = []
    positive = round(100*len(pos_tweets)/len(tweetdata),2)
    negative = round(100*len(neg_tweets)/len(tweetdata),2)
    neutral = round(100*len(neut_tweets)/len(tweetdata),2)


    values.append(positive)
    values.append(negative)
    values.append(neutral)

    mylist = json.dumps(values)
    return render(request, 'queryreport.html', {'values':mylist,'query': query, 'tweetdata': tweetdata, 'wordcloudpos': wordcloudpos, 'wordcloudneg': wordcloudneg, 'stop_words': stop_words})


# Collect function that collects the tweets and stores them in the database

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




# Wordcloud function that creates necessary values to send to the html page

def word_cloud_view(sentences, stopwords):
    # Tokenize the sentences and count the frequencies of the words
    word_counts = {}
    for sentence in sentences:
        # Tokenize the sentence and remove stopwords
        tokens = nltk.word_tokenize(sentence)
        tokens = [token for token in tokens if token.lower() not in stopwords and len(token) > 1]

        # Count the frequency of each token
        for token in tokens:
            if token in word_counts:
                word_counts[token] += 1
            else:
                word_counts[token] = 1

    # Sort the word counts in descending order
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    # Limit the number of words to the first 100
    words = sorted_word_counts[:100]

    # Convert the word counts into a 2d array of objects suitable for the wordcloud2.js library
    words = [[w, c] for w, c in words]

    # Render the template and pass the data as context
    return words

