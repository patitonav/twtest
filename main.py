# -*- coding: utf-8 -*-

import tweepy, time, sys

argfile = str(sys.argv[1])

#enter the corresponding information from your Twitter application:
CONSUMER_KEY = 'DeCNY09i3R5qTLfz65BlpA'	#keep the quotes, replace this with your consumer key
CONSUMER_SECRET = 'hWwSjUa1iQXDRGAVzuaa1gXsTtiTY9S3y0JXtxPwYSQ'	#keep the quotes, replace this with your consumer secret key
ACCESS_KEY = '1926951986-2ZogpaXC8FM4h8tBtx8784xeozA4GqNbAwjmysu'	#keep the quotes, replace this with your access token
ACCESS_SECRET = 'NepKUpPCNl35fUqTwPWWSSIf5Zagvu6vItfqBlsMw'	#keep the quotes, replace this with your access token secret
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

filename=open(argfile,'r')
f=filename.readlines()
filename.close()

for line in f:
    api.update_status(line)
    time.sleep(900)#Tweet every 15 minutes
