for t in tweepy.Cursor(self.api.search_tweets,
                                    q=filtered,
                                    tweet_fields = 'context_annotations',
                                    lang='en',
                                    count = count,
                                    tweet_mode='extended').items():
                
                fetched_tweets.append(t)
                i += 1
                if i>= limit:
                    break
                else:
                    pass