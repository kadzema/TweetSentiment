# Dependencies
import tweepy
import time
import json
import requests as req 
import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib
matplotlib.use('Agg')
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
def TweetOut(user, requester, replyID, avgSentiment):

    print("in TweetOut")

    # Setup Tweepy API Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

    # tweet out the graph
    graph = user.replace("@","") + ".png"

    if avgSentiment < -.5:
        avgDescription = "Yikes! Pretty negative"
    elif avgSentiment < 0:
        avgDescription = "Neutral, leans negative."
    elif avgSentiment == 0:
        avgDescription = "Completely neutral!"
    elif avgSentiment < .35:
        avgDescription = "Neutral, leans positive."
    elif avgSentiment < .5:
        avgDescription = "Fairly positive!"
    else:
        avgDescription = "Awesome! That's positive!"

    tweetreply = requester + "Here's that analysis of " + user + " you requested! \n Mean score: " + str(avgSentiment) + " " + avgDescription
    print("length of tweet: " + str(len(tweetreply)))

    try:
        api.update_with_media(graph, tweetreply, in_reply_to_status_id =replyID )
        print(tweetreply)
    except:
        print("update with media error")

# create a function that analyzes the target user's last 100 tweets
def AnalyzeSentiment(target_user, requester, replyID):

    print("Analyzing " + target_user + " for " + requester)

    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    except:
        print("tweepy authorization issue")

    # create a list to hold the values
    sentiments = []
    # remove previous values
    del sentiments[:]

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

    # set the style before plotting
    plt.style.use('bmh')

    plt.plot(tweetsAgo, sentiments, label=target_user, marker="o", alpha=0.4, linewidth=0.5)
    plt.ylim(-1,1)



    # invert the x axis so we see oldest tweets first
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
    plt.title("Tweet Analysis (last 100) for " + target_user)

    pltName = target_user.replace("@","") + ".png"

    plt.savefig(pltName, bbox_inches="tight", dpit=300)

    # plt.show()
    # close the plot
    plt.close()
    # clear the axis so inverting wil not re-invert!
    plt.cla()
    # clear the figure
    plt.clf()

    #tweet out the graph
    TweetOut(target_user, requester, replyID, avgSentiment)

                
# create a function that looks for specific mention
def TweetIn(sinceID):

    # Setup Tweepy API Authentication
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    except:
        print("tweepy authorization issue")

    # look for tweets to me
    q = "@kadzema"
    
    public_tweets = api.search(q, count=10, result_type="recent", since_id = sinceID)

    print("checking tweets since " + str(lastTweet) + "...")
    
    # create lists to see whats going on
    replyIDs = []
    requesters = []

    # Loop through all public_tweets
    for tweet in public_tweets["statuses"]:

        # check the text for the action:
        tweet_text = tweet["text"]
        print(tweet["text"])
        if ("@kadzema analyze: @" in tweet_text.lower()) and len(tweet_text.split()) == 3:
            replyID = tweet["id"]

            replyIDs.append(tweet["id"])

            print("Tweet ID requesting analysis: " + str(replyID))

            # parse out the account to analyze
            tweetSplit = tweet_text.split()
            account = tweetSplit[2]

            tweet_author = "@" + tweet["user"]["screen_name"]
            requesters.append(tweet_author)
            # print("Requested by " + tweet_author)

            #check that we haven't already analyzed this account by looking for the file
            pltName = account.replace("@","") + ".png"

            if not os.path.isfile(pltName):
                print("Calling AnalyzeSentiment for " + account)
                AnalyzeSentiment(account, tweet_author, replyID)
                # lastTweet = tweet["id"]
            else:
                # try:
                #     fileDate = time.strftime('%m-%d-%Y %I:%M:%S %p', time.localtime(os.path.getmtime(pltName)))
                #     api.update_status("Sorry " + tweet_author + ", " + account + " was analyzed " + fileDate)
                # except:
                print("already analyzed " + account)

    # return lastTweet
    print(replyIDs)
    print(requesters)

    if len(replyIDs) == 0:
        print("no new requests")
        return sinceID
    else:
        return max(replyIDs)     

##############################################################################################################################

lastTweet = 0

# Infinitely loop
while(True):

    # look for last person who tweeted a request to me for an analysis
    # capture the lastTweet number in the main code so it is retained
    
    print("lastTweet before call: " + str(lastTweet))

    lastTweet = TweetIn(lastTweet)
    # TweetIn()

    print("lastTweet after call: " + str(lastTweet))

    # # Once tweeted, wait 5 minutes before doing anything else
    time.sleep(300)
    print("another 5 minutes has passed")
