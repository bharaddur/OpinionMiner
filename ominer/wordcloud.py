from django.shortcuts import render
from django.http import *
from ominer.forms import *

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
from wordcloud import WordCloud


#write a class that analyze text and return a wordcloud

class wordcloud():
    def __init__(self):
        pass
    def wordcloud(self, text):
        # Create and generate a word cloud image:
        wordcloud = WordCloud().generate(text)

        # Diplay the generated image:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()


