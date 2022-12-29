from django.shortcuts import render
from django.http import *
from ominer.forms import *
from django.shortcuts import render, get_object_or_404

from ominer.models import TweetQuery, Tweets

from django.contrib.auth.models import User

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

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

import networkx as nx
from networkx.readwrite import json_graph

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
                parsed_tweet['followers_count'] = tweet['author']['public_metrics']['followers_count']
                parsed_tweet['id'] = tweet['id']
                
                if tweet['author'].get('location') is not None:
                    parsed_tweet['location'] = tweet['author']['location']
                else:
                    parsed_tweet['location'] = ''
                
                #convert to string
                if tweet.get('context_annotations') is None:
                   parsed_tweet['context_annotation'] = ''
                else:
                    contextannotation = json.dumps(tweet['context_annotations'])
                    parsed_tweet['context_annotation'] = contextannotation
                
                if tweet.get('entities') is None:
                    parsed_tweet['hashtags'] = ''
                else:
                    if tweet['entities'].get('hashtags') is None:
                        parsed_tweet['hashtags'] = ''
                    else:
                        hashtags = json.dumps(tweet['entities']['hashtags'])
                        parsed_tweet['hashtags'] = hashtags

                if tweet.get('entities') is None:
                    parsed_tweet['annotations'] = ''
                else:
                    if tweet['entities'].get('annotations') is None:
                        parsed_tweet['annotations'] = ''
                    else:
                        annotations = json.dumps(tweet['entities']['annotations'])
                        parsed_tweet['annotations'] = annotations

              
                tweets.append(parsed_tweet)

            return tweets
            
        except tweepy.errors.TweepyException as e:
            print("Error : " + str(e))


# Form page that takes the query and number of tweets

#in order to use below function you need to be authenticated
@login_required(login_url='/login/')
def show(request):
    form = TwitterForm()
    return render(request,'index.html',{'ff':form})


# Query page that shows the queries that has been done previously
@login_required(login_url='/login/')
def queries(request):
    querydata = TweetQuery.objects.filter(owner=request.user).order_by('-date')
    
    query = {
        "queries": querydata,
    }
        
    return render(request,'queries.html', query)

# Detail page that shows the details of the query in a dashboard
@login_required(login_url='/login/')
def query_detail(request, pk):
    query = get_object_or_404(TweetQuery, pk=pk)

    tweetdata = Tweets.objects.filter(query=pk)

    userFollowerData = Tweets.objects.order_by('-followers_count').filter(query=pk)[:10]

    tweetLikedData = tweetdata.order_by('-like_count')[:10]

    querytext = TweetQuery.objects.get(pk=pk)

    # Weighted Hashtag List Creation 
    Hashtaglist = []
    for tweet in tweetdata:
        if tweet.hashtags != '':
            jsonHash = json.loads(tweet.hashtags)
            for hashtag in jsonHash:
                Hashtaglist.append(hashtag.get('tag').lower())
    
    WeightedHashtag = hashtag_list(Hashtaglist)
    WeightedHashtag = sorted(WeightedHashtag, key=lambda x: x[1], reverse=True)[:10]

    # Weighted Entity List Creation
    Entitylist = []
    for tweet in tweetdata:
        if tweet.annotations != '':
            jsonEnt = json.loads(tweet.annotations)
            for entity in jsonEnt:
                if entity.get('normalized_text') != querytext.query:
                    if entity.get('normalized_text') != querytext.query.lower():
                        Entitylist.append(entity.get('normalized_text').lower())
                    else: 
                        continue
    
    WeightedEntity = hashtag_list(Entitylist)
    WeightedEntity = sorted(WeightedEntity, key=lambda x: x[1], reverse=True)[:10]
        
    


    stop_words = get_stop_words('en')
    additionalstop_words = nltk.word_tokenize(querytext.query)

    nltk_stop_words = nltk.corpus.stopwords.words('english')
    
    for word in additionalstop_words:
        stop_words.append(word.lower())
    for word in nltk_stop_words:
        stop_words.append(word.lower())

    # get cleaned_tweets from database and create a wordcloud
    pos_tweets = Tweets.objects.filter(query=pk, sentiment='positive')
    neg_tweets = Tweets.objects.filter(query=pk, sentiment='negative')
    neut_tweets = Tweets.objects.filter(query=pk, sentiment='neutral')


    posdomains = []

    for annotation in pos_tweets:
        if annotation.annotations != '':
            jsonEnt = json.loads(annotation.annotations)
            for domain in jsonEnt:
                posdomains.append(domain.get('type').lower())

    negdomains = []

    for annotation in neg_tweets:
        if annotation.annotations != '':
            jsonEnt = json.loads(annotation.annotations)
            for domain in jsonEnt:
                negdomains.append(domain.get('type').lower())
    
    neutdomains = []

    for annotation in neut_tweets:
        if annotation.annotations != '':
            jsonEnt = json.loads(annotation.annotations)
            for domain in jsonEnt:
                neutdomains.append(domain.get('type').lower())

    
    pp = posdomains.count("product")
    po = posdomains.count("organization")
    pe = posdomains.count("person")
    ppe = posdomains.count("place")
    pot = posdomains.count("other")
    np = negdomains.count("product")
    no = negdomains.count("organization")
    ne = negdomains.count("person")
    npe = negdomains.count("place")
    nt = negdomains.count("other")
    nup = neutdomains.count("product")
    nuo = neutdomains.count("organization")
    nue = neutdomains.count("person")
    nupe = neutdomains.count("place")
    nut = neutdomains.count("other")


    positived = [pp, po, pe, ppe, pot]  
    negatived = [np, no, ne, npe, nt]
    neutrald = [nup, nuo, nue, nupe, nut]


    

                   

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
    return render(request, 'queryreport.html', {'values':mylist,
                                                'query': query, 
                                                'tweetdata': tweetdata, 
                                                'wordcloudpos': wordcloudpos, 
                                                'wordcloudneg': wordcloudneg, 
                                                'userFollowerData': userFollowerData, 
                                                'tweetLikedData': tweetLikedData, 
                                                'WeightedHashtag': WeightedHashtag,
                                                'WeightedEntity': WeightedEntity,
                                                'positived': positived,
                                                'negatived': negatived,
                                                'neutrald': neutrald,
                                                })

@login_required(login_url='/login/')
def gnetwork_detail_tweet(request, pk):
    query = get_object_or_404(TweetQuery, pk=pk)

    tweetdata = Tweets.objects.filter(query=pk)


    g = nx.Graph()
    node_counts = {}
    edge_counts = {}

    p = 0.7

    for tweet in tweetdata:
        annotations = tweet.annotations.lower()
        if annotations != '':
            json_string = json.loads(annotations)
            for i in json_string:
                # Increment the count for the node
                if i.get('normalized_text') not in node_counts and i.get('probability') > p:
                    node_counts[i.get('normalized_text')] = 0
                if i.get('probability') > p:
                    node_counts[i.get('normalized_text')] += 1

                for j in json_string:
                    if i.get('normalized_text') != j.get('normalized_text') and i.get('probability') > p and j.get('probability') > p:
                        # Increment the count for the edge
                        if not g.has_edge(i.get('normalized_text'), j.get('normalized_text')) and not g.has_edge(j.get('normalized_text'), i.get('normalized_text')):
                            edge_counts[(i.get('normalized_text'), j.get('normalized_text'))] = 0
                        edge_counts[(i.get('normalized_text'), j.get('normalized_text'))] += 1

    # Add the nodes to the graph and set the weight based on the count
    for node, count in node_counts.items():
        g.add_node(node, weight=count, size=count)

    # Add the edges to the graph and set the weight based on the count
    for edge, count in edge_counts.items():
        u, v = edge
        g.add_edge(u, v, weight=count, size=count)



    # Get the list of nodes with less than 5 edges
    nodes_to_remove = [node for node in g.nodes() if g.degree(node) < 10]

    # Remove the nodes from the graph
    for node in nodes_to_remove:
        g.remove_node(node)

        

    graph_json = json_graph.node_link_data(g)

    for i, node in enumerate(graph_json['nodes']):
        graph_json['nodes'][i]['id'] = node['id']
        graph_json['nodes'][i]['label'] = node['id']
        graph_json['nodes'][i]['font'] = {'size': 9, 'color': 'black'}
    
    for i, link in enumerate(graph_json['links']):
        graph_json['links'][i]['from'] = link['source']
        graph_json['links'][i]['to'] = link['target']
        graph_json['links'][i]['font'] = {'size': 9, 'color': 'black'}

    graph_json['edges'] = graph_json.pop("links")
    

    graph_json = json.dumps(graph_json)

    ## Graph With Simplified Annotations

    return render(request, 'gnetwork.html', {'query': query, 'tweetdata': tweetdata,'graph_json': graph_json})

@login_required(login_url='/login/')
def gnetwork_detail_domain(request, pk):

    query = get_object_or_404(TweetQuery, pk=pk)

    tweetdata = Tweets.objects.filter(query=pk)
      # Initialize a dictionary to store the counts of the nodes and edges
    node_counts = {}
    edge_counts = {}

    sg = nx.Graph()

    for tweet in tweetdata:
        annotations = tweet.annotations.lower()
        if annotations != '':
            jsonA = json.loads(annotations)
            for i in jsonA:
                # Increment the count for the node
                if i.get('normalized_text') not in node_counts:
                    node_counts[i.get('normalized_text')] = 0
                node_counts[i.get('normalized_text')] += 1
                if i.get('type') not in node_counts:
                    node_counts[i.get('type')] = 0
                node_counts[i.get('type')] += 1

                # Add the count as the size attribute to the node
                sg.add_node(i.get('normalized_text'), size=node_counts[i.get('normalized_text')])
                sg.add_node(i.get('type'), color='red', shadow=True, size=node_counts[i.get('type')])
                # Increment the count for the edge
                if not sg.has_edge(i.get('type'),i.get('normalized_text')) and not sg.has_edge(i.get('normalized_text'), i.get('type')):
                    edge_counts[(i.get('type'),i.get('normalized_text'))] = 0
                edge_counts[(i.get('type'),i.get('normalized_text'))] += 1
                # Add the count as the weight attribute to the edge
                sg.add_edge(i.get('type'),i.get('normalized_text'), weight=edge_counts[(i.get('type'),i.get('normalized_text'))])

    # Add the nodes to the graph and set the weight based on the count
    for node, count in node_counts.items():
        sg.add_node(node, weight=count, size=count)

    # Add the edges to the graph and set the weight based on the count
    for edge, count in edge_counts.items():
        u, v = edge
        sg.add_edge(u, v, weight=count, size=count)  


    # Get the list of nodes with weight less than 5
    nodes_to_remove = [node for node in sg.nodes(data=True) if node[1]['weight'] < 3]

    # Remove the nodes from the graph
    for node in nodes_to_remove:
        sg.remove_node(node[0])
          
                        

    graph_jsonAnno = json_graph.node_link_data(sg)


    for i, node in enumerate(graph_jsonAnno['nodes']):
        graph_jsonAnno['nodes'][i]['id'] = node['id']
        graph_jsonAnno['nodes'][i]['label'] = node['id']
        graph_jsonAnno['nodes'][i]['font'] = {'size': 14, 'color': 'black'}
    
    for i, link in enumerate(graph_jsonAnno['links']):
        graph_jsonAnno['links'][i]['from'] = link['source']
        graph_jsonAnno['links'][i]['to'] = link['target']
        graph_jsonAnno['links'][i]['font'] = {'size': 14, 'color': 'black'}

    graph_jsonAnno['edges'] = graph_jsonAnno.pop("links")
    

    graph_jsonAnno = json.dumps(graph_jsonAnno)

    return render(request, 'gnetworkdomain.html', {'query': query, 'tweetdata': tweetdata, 'graph_jsonAnno': graph_jsonAnno})

@login_required(login_url='/login/')
def datatable_detail(request, pk):
    query = get_object_or_404(TweetQuery, pk=pk)

    tweetdata = Tweets.objects.filter(query=pk)

    return render(request, 'datatable.html', {'query': query, 'tweetdata': tweetdata})


# Collect function that collects the tweets and stores them in the database
@login_required(login_url='/login/')
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
                followers_count = i['followers_count'],
                context_annotations = i['context_annotation'],
                hashtags = i['hashtags'],
                annotations = i['annotations'],

                
            )
            tweet_data.save()

            query = TweetQuery.objects.filter(owner=request.user, query=t).last()
            
        
        return render(request, 'collectedpage.html', {'query': query})
        

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


# Create a weighted hashtag list
def hashtag_list(list):
    frequency = {}

    # Iterate over the list and update the frequency dictionary
    for item in list:
        if item in frequency:
            frequency[item] += 1
        else:
            frequency[item] = 1

    # Create an empty set to keep track of added items
    added_items = set()

    # Create an empty list to store the weighted items
    weighted_items = []

    # Add items to the list with weights based on their frequency
    for item in list:
        if item not in added_items:
            weight = frequency[item]
            weighted_items.append((item, weight))
            added_items.add(item)

    return weighted_items  

