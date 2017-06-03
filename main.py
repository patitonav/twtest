# -*- coding: utf-8 -*-

import tweepy
from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET, TECH_URLS
import feedparser
import time
from subprocess import check_output
import sys
import json
from AdflyApiManager import AdflyManager

db = 'feeds.db'
limit = 12 * 3600 * 1000

#
# function to get the current time
#
current_time_millis = lambda: int(round(time.time() * 1000))
current_timestamp = current_time_millis()

def post_is_in_db(title):
    with open(db, 'r') as database:
        for line in database:
            if title in line:
                return True
    return False
#    
# return true if the title is in the database with a timestamp > limit
#
def post_is_in_db_with_old_timestamp(title):
    with open(db, 'r') as database:
        for line in database:
            if title in line:
                ts_as_string = line.split('|', 1)[1]
                ts = long(ts_as_string)
                if current_timestamp - ts > limit:
                    return True
    return False

#
# figure out which posts to print
#
posts_to_print = []
posts_to_skip = []

url = 'http://feeds.feedburner.com/TechCrunch/'


for ulr in TECH_URLS:
	feed = feedparser.parse(url)
	for post in feed.entries:
	    # if post is already in the database, skip it
	    # TODO check the time
	    title = post.title
	    link = post.link
	    if post_is_in_db_with_old_timestamp(title):
	        posts_to_skip.append(title)
	    else:
	        posts_to_print.append([title,link])



#enter the corresponding information from your Twitter application:
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
apiAdfly = AdflyManager()
#
# add all the posts we're going to print to the database with the current timestamp
# (but only if they're not already in there)
#
f = open(db, 'a')
for title in posts_to_print:
	try:
		json_result = apiAdfly.shorten(title[1].encode('utf8'))
		print(title[0][:90].encode('utf8')+' '+json_result['data'][0]['short_url'])
		api.update_status(title[0][:90].encode('utf8')+' '+json_result['data'][0]['short_url'])
		if not post_is_in_db(title[0]):
				f.write(title + "|" + str(current_timestamp) + "\n")
		time.sleep(900)#Tweet every 15 minutes
	except Exception, e:
		print(str(e))
f.close
