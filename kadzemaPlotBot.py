# Dependencies
import tweepy
import time
import json
import requests as req 
import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt 
import os
import numpy as np
from matplotlib import collections as matcoll


# Twitter API Keys
# kristine keys
consumer_key = "HqmbSQzqMOeQI5U6zaIS42Pja"
consumer_secret = "EfDRnSYxvdBXE4Tj5rwAZyNC5gJXOxg7GL32Vf6QNqb1K45Xaw"
access_token = "35740765-Z8VkREBVuYzEnoKwfKU9NqbJp1FRJEEUZ1VKQ5yNY"
access_token_secret = "N3VeKhoiOgFfrW65uFJflIfAxhDT24MHR2NVkFH5vd0XR"

#create analyzer
analyzer = SentimentIntensityAnalyzer()



# Create a function that tweets
def TweetOut(user, avgSentiment):

    print("in TweetOut")

    # Setup Tweepy API Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

    # tweet out the graph
    graph = user.replace("@","") + ".png"

    try:
        api.update_with_media(graph, user + " - last 100 tweets mean sentiment score: " + str(avgSentiment) )
        print(user + " - last 100 tweets mean sentiment score: " + str(avgSentiment) )
    except:
        print("graph not found")

# create a function that analyzes the target user's last 100 tweets
def AnalyzeSentiment(target_user, requester):

    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    except:
        print("tweepy authorization issue")

    # create a list to hold the values
    sentiments = []

     # loop through 5 times to get 100 tweets
    try:
        for page in range(1,6):
            targetUser_tweets = api.user_timeline(target_user, page= page)

            # Loop through all tweets
            for index, tweet in enumerate(targetUser_tweets):

                # Print the JSON object to view output
                # print(json.dumps(tweet, sort_keys=True, indent=4, separators=(',', ': ')))
                
                # print the tweet text
                # print(str(index) + " " + tweet["text"])
                
                # analyze the tweet text
                compound = analyzer.polarity_scores(tweet["text"])["compound"]         
                
                # add the compound to the sentiment list for plotting
                sentiments.append(compound)
    except:
        print("error in user timeline loop")

    tweetsAgo = np.arange(len(sentiments))

    plt.plot(tweetsAgo, sentiments, label=target_user, marker="o", alpha=0.4, linewidth=0.5)
    plt.ylim(-1,1)

    plt.style.use('bmh')


    plt.gca().invert_xaxis()

    # removed legend - title is sufficient explaination
    # move the legend outside the frame of the plot
    # plt.legend(bbox_to_anchor=(1, 1))
    # plt.legend(loc='top left', bbox_to_anchor=(1, 0.5), title="Tweets")


    # plot a hortizontal line at neutral (0)
    plt.axhline(0, c='k', alpha = .3)

    # get the average
    avgSentiment = round(np.mean(sentiments),2)
    

    plt.ylabel("Tweet Polarity - Vader Sentiment Analyzer")
    plt.xlabel("Number of Tweets Ago")
    plt.title("Tweet Analysis for " + target_user + " requested by: " + requester)

    pltName = target_user.replace("@","") + ".png"

    plt.savefig(pltName, bbox_inches="tight", dpit=300)

    plt.show()

    #tweet out the graph
    TweetOut(target_user, avgSentiment)

                
# create a function that looks for specific mention
def TweetIn():

    # Setup Tweepy API Authentication
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    except:
        print("tweepy authorization issue")

    # look for tweets to me
    q = "@kadzema"
    lastTweet = 0
    public_tweets = api.search(q, count=10, result_type="recent", since_id=lastTweet)

    # print("checking tweets...")

    # Loop through all public_tweets
    for tweet in public_tweets["statuses"]:

        # check the text for the action:
        tweet_text = tweet["text"]
        if ("@kadzema analyze: @" in tweet_text.lower()) and len(tweet_text.split()) == 3:

            # parse out the account to analyze
            tweetSplit = tweet_text.split()
            account = tweetSplit[2]

            tweet_author = "@" + tweet["user"]["screen_name"]
            # print("Requested by " + tweet_author)

            #check that we haven't already analyzed this account
            pltName = account.replace("@","") + ".png"

            if not os.path.isfile(pltName):
                print("Calling AnalyzeSentiment for " + account)
                AnalyzeSentiment(account, tweet_author)
                lastTweet = tweet["id"]
            else:
                fileDate = time.strftime('%m-%d-%Y %I:%M:%S %p', time.localtime(os.path.getmtime(pltName)))
                api.update_status("Sorry " + tweet_author + ", " + account + " was analyzed " + fileDate)
                # print("Sorry " + tweet_author + ", " + account + " was analyzed on " + fileDate)

##############################################################################################################################

# Infinitely loop
while(True):

    # look for last person who tweeted a request to me for an analysis
    TweetIn()

    # # Once tweeted, wait 5 minutes before doing anything else
    time.sleep(300)