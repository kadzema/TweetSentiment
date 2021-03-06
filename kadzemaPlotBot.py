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
import matplotlib.patches as mpatches
import html


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
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser(), wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

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

    tweetreply = requester + " Analysis of " + user + "\nMean score: " + str(avgSentiment) + " " + avgDescription
    print("length of tweet: " + str(len(tweetreply)))
    if len(tweetreply) > 140:
         tweetreply = requester + " Analysis of " + user + " you requested!"

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
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser(), wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
    except:
        print("tweepy authorization issue")

    # create a list to hold the values
    sentiments = []
    # remove previous values
    del sentiments[:]

    # get the highest and lowest scored tweets
    negTweetScore = 0.0
    negTweetText = ""
    negTweetIndex = 0
    posTweetScore = 0.0
    posTweetText = ""
    posTweetIndex = 0

     # loop through 25 times to get 500 tweets
    try:
        for page in range(1,26):
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

                if negTweetScore == 0.0 or compound < negTweetScore:
                    negTweetScore = compound
                    negTweetText = html.unescape(tweet["text"])
                    negTweetIndex = len(sentiments) - 1

                if posTweetScore == 0.0 or compound > posTweetScore:
                    posTweetScore = compound
                    posTweetText = html.unescape(tweet["text"])
                    posTweetIndex = len(sentiments) - 1 

    except:
        print("error in user timeline loop")

    tweetsAgo = np.arange(len(sentiments))

    # make sure there were tweets
    if len(sentiments) > 0:

        # get the average
        avgSentiment = round(np.mean(sentiments),2)

        if avgSentiment > 0:
            avgColor = "green"
        elif avgSentiment < 0:
            avgColor = "red"
        else:
            avgColor = "blue"

        # set the style before plotting
        plt.style.use('ggplot')

        # removed legend - title is sufficient explaination
        # move the legend outside the frame of the plot
        # plt.legend(bbox_to_anchor=(1, 1))
        # plt.legend(loc='top left', bbox_to_anchor=(1, 0.5), title="Tweets")
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)

        # handles, labels = ax.get_legend_handles_labels()
        # avgPatch = mpatches.Patch(color=avgColor, label="Mean Score", alpha = .4)
        # neutralPatch = mpatches.Patch(color="k", label="Neutral Score", alpha = .4)
        # posTweetPatch = mpatches.Patch(color="green", label="Most Positive Tweet: " + posTweetText, alpha=.4)
        # negTweetPatch = mpatches.Patch(color="red", label="Most Negative Tweet: " + negTweetText, alpha = .4)

        # plt.legend(handles=[posTweetPatch, negTweetPatch], frameon=True, bbox_to_anchor=(0, 0), loc="center",)

        ax.plot(tweetsAgo, sentiments, label=target_user, marker="o", alpha=0.4, linewidth=0.5, color="b")

        print("Pos: " + posTweetText)
        print("Neg: " + negTweetText)

        # plot the most positive and most negative tweets
        ax.plot(posTweetIndex, posTweetScore, label=posTweetText, marker="o", alpha=.6, color = "green")
        ax.plot(negTweetIndex, negTweetScore, label=negTweetText, marker="o", alpha=.6, color="red")

        plt.ylim(-1,1)

        # invert the x axis so we see oldest tweets first
        plt.gca().invert_xaxis()

        # plot a hortizontal line at neutral (0)
        plt.axhline(0, c='k', alpha = .4)

        # plot a horizontal line at the average - no one liked this!
        # plt.axhline(avgSentiment, c=avgColor, alpha = .4)

        # figtext allows you to put text anywhere on the figure
        plt.figtext(0, -.1, "Most Positive Tweet Sentiment: " + posTweetText, wrap=True, fontsize=8, bbox={'pad':2, 'facecolor':'green', 'alpha':.6})
        plt.figtext(0, -.2, "Most Negative Tweet Sentiment: " + negTweetText, wrap=True, fontsize=8, bbox={'pad':2, 'facecolor':'red', 'alpha':.6})
        #  - Vader Sentiment Analyzer

        plt.ylabel("Tweet Polarity")
        plt.xlabel("Number of Tweets Ago")
        plt.title("Tweet Analysis for " + target_user)

        pltName = target_user.replace("@","") + ".png"

        plt.savefig(pltName, bbox_inches="tight", dpi=300)

        plt.show()
        # close the plot
        plt.close()
        # clear the axis so inverting wil not re-invert!
        plt.cla()
        # clear the figure
        plt.clf()

        #tweet out the graph
        TweetOut(target_user, requester, replyID, avgSentiment)
    
    else:
        try:
            print("Sorry " + requester + ", " + target_user + " doesn't seem to have any tweets")
            api.update_status("Sorry " + requester + ", " + target_user + " doesn't seem to have any tweets", in_reply_to_status_id =replyID)
        except:
            print("no tweet status message error")

                
# create a function that looks for specific mention
def TweetIn(sinceID):

    # Setup Tweepy API Authentication
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser(), wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
    except:
        print("tweepy authorization issue")

    # look for tweets to me
    q = "@kadzema"
    
    public_tweets = api.search(q, count=100, result_type="recent", since_id = sinceID)

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
                try:
                    fileDate = time.strftime('%m-%d-%Y %I:%M:%S %p', time.localtime(os.path.getmtime(pltName)))
                    api.update_status("Sorry " + tweet_author + ", " + account + " was analyzed " + fileDate, in_reply_to_status_id =replyID)
                except:
                    print("already analyzed " + account)

    print(replyIDs)
    print(requesters)

    if len(replyIDs) == 0:
        print("no new requests")
        return sinceID
    else:
        return max(replyIDs)     

##############################################################################################################################

lastTweet = 911001032448204801
# 910672009939611649

# lastTweet = 0

# Infinitely loop
while(True):

    # look for last person who tweeted a request to me for an analysis
    # capture the lastTweet number in the main code so it is retained
    
    # print("lastTweet before call: " + str(lastTweet))

    lastTweet = TweetIn(lastTweet)

    # print("lastTweet after call: " + str(lastTweet))

    # # Once tweeted, wait 5 minutes before doing anything else
    time.sleep(300)
    print("another 5 minutes has passed")
