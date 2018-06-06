#!/usr/bin/env python
# encoding: utf-8

"""
	User basic information:
		print ("Basic information for", user.name)
		print ("Screen Name:", user.screen_name)
		print ("Name: ", user.name)
		print ("Twitter Unique ID: ", user.id)
		print ("Account created at: ", user.created_at)

	Tweepy tweets attribute:
	    print ("ID:", tweet.id)
        print ("User ID:", tweet.user.id)
        print ("Text:", tweet.text)
        print ("Created:", tweet.created_at)
        print ("Geo:", tweet.geo)
        print ("Contributors:", tweet.contributors)
        print ("Coordinates:", tweet.coordinates) 
        print ("Favorited:", tweet.favorited)
        print ("In reply to screen name:", tweet.in_reply_to_screen_name)
        print ("In reply to status ID:", tweet.in_reply_to_status_id)
        print ("In reply to status ID str:", tweet.in_reply_to_status_id_str)
        print ("In reply to user ID:", tweet.in_reply_to_user_id)
        print ("In reply to user ID str:", tweet.in_reply_to_user_id_str)
        print ("Place:", tweet.place)
        print ("Retweeted:", tweet.retweeted)
        print ("Retweet count:", tweet.retweet_count)
        print ("Source:", tweet.source)
        print ("Truncated:", tweet.truncated)
"""
import tweepy #https://github.com/tweepy/tweepy
import csv
import time
import os
import errno
import re
import collections
from collections import Counter
import JSdistance_EN_wiki as cs
import random
#Twitter API credentials
consumer_key = "hNpaR5AUz78qnt4XurQ2QtySg"
consumer_secret = "JJb6lrTJtk0euoFv2bKps3j9Lu4GmYgSpVZIgAHgMI08lWZai6"
access_key = "49872827-OBzuLDnA51nGjhsEslUkoqrJaMhXlDtvMn3nGLbVj"
access_secret = "zbPJzx37cYF2ZV5zJu49ZVyJ1oGiUFChxUwleqTsmahYf"

#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

def get_latest_tweets(screen_name):
	count=0
	latest_tweets=[]
	data=pd.read_csv("%s_tweets.csv"%(screen_name))
	since_Id=data['tweet_id'].loc[0]
	#print since_Id
	#try:
	#	tweet=api.get_status(since_Id).text
	#except tweepy.error.TweepError:
	#	print "No tweet found on id %s.\nCode Terminated\n"%(since_id)
	#	exit()
	try:
		new_tweets=api.user_timeline(screen_name=screen_name,since_id=since_Id,count=200)
		old = new_tweets[-1].id - 1
	except IndexError:
		print "No new tweets"
		exit()
	count=len(new_tweets)
	print "%s tweets downloaded so far"%(count)
	latest_tweets.extend(new_tweets)
	print latest_tweets[0].id
	while len(new_tweets) <= 200:
		#print "getting latest tweets\n"
		new_tweets=api.user_timeline(screen_name=screen_name,max_id=old,since_id=since_Id,count=200)
		count = count + len(new_tweets)
		print "in loop %s tweets downloaded so far"%(len(new_tweets))
		#print new_tweets[0].id
		latest_tweets.extend(new_tweets)
		old=latest_tweets[-1].id - 1
		#print old,since_Id,len(new_tweets)
        print count
	new_data=[[obj.user.screen_name,obj.user.name,obj.user.id_str,obj.user.description.encode("utf8"),obj.created_at.year,obj.created_at.month,obj.created_at.day,"%s.%s"%(obj.created_at.hour,obj.created_at.minute),obj.id_str,obj.text.encode("utf8")] for obj in latest_tweets ]
	dataframe=pd.DataFrame(new_data,columns=['screen_name','name','twitter_id','description','year','month','date','time','tweet_id','tweet'])
	dataframe=[dataframe,data]
	dataframe=pd.concat(dataframe)
	dataframe.to_csv("%s_tweets.csv"%(screen_name),index=False)

def get_all_tweets(screen_name):
	#Twitter only allows access to a users most recent 3240 tweets with this method
	
	
	#initialize a list to hold all the tweepy Tweets
	alltweets = []	
	
	#make initial request for most recent tweets (200 is the maximum allowed count)
	new_tweets = api.user_timeline(screen_name = screen_name,count=200)
	
	#save most recent tweets
	alltweets.extend(new_tweets)
	
	#save the id of the oldest tweet less one
	# oldest = alltweets[-1].id - 1
	
	# #to allow access 3240 tweets : keep grabbing tweets until there are no tweets left to grab
	# while len(new_tweets) > 0:
	# 	print "getting tweets before %s" % (oldest)
		
	# 	#all subsiquent requests use the max_id param to prevent duplicates
	# 	new_tweets = api.user_timeline(screen_name = screen_name,count=100,max_id=oldest)
		
	# 	#save most recent tweets
	# 	alltweets.extend(new_tweets)
		
	# 	#update the id of the oldest tweet less one
	# 	oldest = alltweets[-1].id - 1
		
	# 	print "...%s tweets downloaded so far" % (len(alltweets))
	
	#transform the tweepy tweets into a 2D array that will populate the csv	
	outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8"), tweet.retweeted, tweet.favorited, tweet.retweet_count] for tweet in alltweets]
	
	return outtweets
	#write the csv	
	# with open('%s_tweets.csv' % screen_name, 'wb') as f:
	# 	writer = csv.writer(f)
	# 	# writer.writerow(["id","created_at","text"])
	# 	writer.writerows(outtweets)
	
	# pass

def get_text_tweets(screen_name):
	#Twitter only allows access to a users most recent 3240 tweets with this method
	
	
	#initialize a list to hold all the tweepy Tweets
	alltweets = []	
	
	#make initial request for most recent tweets (200 is the maximum allowed count)
	new_tweets = api.user_timeline(screen_name = screen_name,count=100)
	
	#save most recent tweets
	alltweets.extend(new_tweets)
	
	outtweets = [tweet.text.encode("utf8") for tweet in alltweets]
	return outtweets

def handle_tweepy_error(cursor):
	while True:
		try:
			yield cursor.next()
		except tweepy.TweepError:
			time.sleep(60*15)

def getFollowers(screen_name):
	# target_user = []
	for user in tweepy.Cursor(api.followers, screen_name=screen_name, count = 200).items():
		#to avoid tweepy.TweepError: when The particular user had protected tweets
		try:
			# write the csv	
			print user.screen_name
			with open(str(screen_name) +'_followers.csv', 'a') as f:
				f.write(str(user.screen_name) + '\n')
				f.close()
			print "continuing.please wait..."

			# print user.screen_name
			# all_tweets = get_all_tweets(user.screen_name)
			# if all_tweets:
			# 	preprocessed_tweet = cs.slangCleanser(all_tweets)
			# 	preprocessed_tweet = cs.lemmatizingText(preprocessed_tweet)
			# 	# print preprocessed_tweet
			# 	# break

			# 	cInterest = cs.cInterest(preprocessed_tweet,ldaScoreA)
			# 	print user.screen_name, ' : ', cInterest
				# if jsd_score*100 <= 60:
				# 	target_user.append(user.screen_name)

		except tweepy.TweepError:
			print("Failed to run the command on that user, Skipping...")
			time.sleep(60 * 15)
			# continue
			pass
		except StopIteration:
			break

def getUserAttributes(name):
	# target_user = []
	for user in tweepy.Cursor(api.friends, screen_name=name, count = 2).items():
		#to avoid tweepy.TweepError: when The particular user had protected tweets
		try:
			# write the csv	

			print user

			# if user.verified and count_foll.followers_count:
			# 	with open('IDenceFinder_datasets/'+str(name)+'/'+str(name) +'_friends.csv', 'a') as f:
			# 		f.write(str(user.screen_name) + '\n')
			# 		f.close()
			# 	print "continuing.please wait..."

			# print user.screen_name
			# all_tweets = get_all_tweets(user.screen_name)
			# if all_tweets:
			# 	preprocessed_tweet = cs.slangCleanser(all_tweets)
			# 	preprocessed_tweet = cs.lemmatizingText(preprocessed_tweet)
			# 	# print preprocessed_tweet
			# 	# break

			# 	cInterest = cs.cInterest(preprocessed_tweet,ldaScoreA)
			# 	print user.screen_name, ' : ', cInterest
				# if jsd_score*100 <= 60:
				# 	target_user.append(user.screen_name)
		except tweepy.TweepError:
			print("Failed to run the command on that user, Skipping...")
			time.sleep(60 * 15)
			# continue
			pass
		except StopIteration:
			break
		break

def getFriends(name):
	# target_user = []
	for user in tweepy.Cursor(api.friends, screen_name=name, count = 200).items():
		#to avoid tweepy.TweepError: when The particular user had protected tweets
		try:
			# write the csv	

			print user.screen_name, user.verified, user.followers_count

			# if user.verified and count_foll.followers_count:
			# 	with open('IDenceFinder_datasets/'+str(name)+'/'+str(name) +'_friends.csv', 'a') as f:
			# 		f.write(str(user.screen_name) + '\n')
			# 		f.close()
			# 	print "continuing.please wait..."

			# print user.screen_name
			# all_tweets = get_all_tweets(user.screen_name)
			# if all_tweets:
			# 	preprocessed_tweet = cs.slangCleanser(all_tweets)
			# 	preprocessed_tweet = cs.lemmatizingText(preprocessed_tweet)
			# 	# print preprocessed_tweet
			# 	# break

			# 	cInterest = cs.cInterest(preprocessed_tweet,ldaScoreA)
			# 	print user.screen_name, ' : ', cInterest
				# if jsd_score*100 <= 60:
				# 	target_user.append(user.screen_name)

		except tweepy.TweepError:
			print("Failed to run the command on that user, Skipping...")
			time.sleep(60 * 15)
			# continue
			pass
		except StopIteration:
			break


def countHashtags(screen_name,user):
	with open(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'_hashtags.txt') as f:
		hashtags = f.read().replace('\n', ' ')
		return Counter(hashtags.lower().split()).most_common(3)

def searchHashtags(q,screen_name,user, limit):
	counter = 0
	for item in handle_tweepy_error(tweepy.Cursor(api.search, q='#'+str(q), lang='en').items(limit=limit)):
		if counter >= limit:
			break
		with open(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'_hashtags_tweets.txt', 'a') as f:

			f.write(str(item.text.encode('utf-8'))+'\n')
			f.close()
			counter += 1

	print 'finishing up all tweets of hashtags #',user,q

def searchMentions(screen_name, user, limit):
	counter = 0
	for item in handle_tweepy_error(tweepy.Cursor(api.search, q='@'+str(user), lang='en').items(limit=limit)):
		if counter >= limit:
			break
		with open(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'_mentioned_tweets.txt', 'a') as f:

			f.write(str(item.text.encode('utf-8'))+'\n')
			f.close()
			counter += 1

	print 'finishing up crawling all mention tweets',user

def hashtagGenerator(screen_name):
	with open(str(screen_name)+'_datasets/'+str(screen_name)+'_followers.txt') as f:
		followers = f.read().splitlines()

	for user in followers:
		try:
			if os.path.exists(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'_hashtags.txt'):
				if os.path.exists(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'_hashtags_tweets.txt'):
					silentremove(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'_hashtags_tweets.txt')

				hashtags_list = countHashtags(screen_name, user)
				limit = 50
				for q in hashtags_list:
					searchHashtags(q[0],screen_name,user,limit)
					limit -= 10
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise

def mentionGenerator(screen_name):
	with open(str(screen_name)+'_datasets/'+str(screen_name)+'_followers.txt') as f:
		followers = f.read().splitlines()

	for user in followers:
		try:
			if os.path.exists(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'_hashtags.txt'):
				silentremove(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'_mentioned_tweets.txt')
				hashtags_list = countHashtags(screen_name, user)
				searchMentions(screen_name,user,50)
				
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured

def silentMakedir(dirname):
	try:
		os.makedirs(dirname)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

def getUserFriends(screen_name):
	# silentMakedir(str(screen_name)+'_datasets/')
	counter = 0
	for user in handle_tweepy_error(tweepy.Cursor(api.friends, screen_name=screen_name, count = 200).items()):
		# print user.screen_name
		if not user.protected and user.lang == 'en' and user.description != '' and user.statuses_count > 100:
			# print user._json
			# break
			counter +=1
			with open(str(screen_name)+'_datasets/'+str(screen_name)+'_friends.txt', 'a') as f:
				f.write(str(user.screen_name) + '\n')
				f.close()
	print 'friends: ', counter

def getUserFollowers(screen_name):
	silentMakedir(str(screen_name)+'_datasets/')
	counter = 0
	for user in handle_tweepy_error(tweepy.Cursor(api.followers, screen_name=screen_name, count = 200).items()):
		counter +=1
		if not user.protected and user.lang == 'en' and user.description != '' and user.statuses_count > 100:

			silentMakedir(str(screen_name)+'_datasets/' + str(user.screen_name) )
			silentremove(str(screen_name)+'_datasets/'+ str(user.screen_name) +'/'+ str(user.screen_name) +'_desc_followers.txt')
			with open(str(screen_name)+'_datasets/'+ str(user.screen_name) +'/'+ str(user.screen_name) +'_desc_followers.txt', 'w') as f:
				f.write(str(user.description.encode('utf-8')))
				f.close()
			with open(str(screen_name)+'_datasets/'+str(screen_name)+'_followers.txt', 'a') as f:
				f.write(str(user.screen_name) + '\n')
				f.close()
	print 'followers: ', counter

def getFollowersTweets(screen_name):
	with open(str(screen_name)+'_datasets/'+str(screen_name)+'_followers.txt') as f:
		followers = f.read().splitlines()

	for user in followers:
		try:
			if os.path.exists(str(screen_name)+'_datasets/'+str(user)+'/'):
				silentremove(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'_hashtags.txt')
				silentremove(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'.txt')
			else:
				silentMakedir(str(screen_name)+'_datasets/'+ str(user) +'/')

			all_tweets = get_all_tweets(user)
			print 'writing all tweets of user ', user
			for tweet in all_tweets:
				if re.search(r'(?=.*#\b)', tweet[2]):
					print cs.extract_hashtags(tweet[2])
					hashtags = "\n".join(cs.extract_hashtags(tweet[2]))	

					with open(str(screen_name)+'_datasets/'+ str(user) +'/'+ str(user) +'_hashtags.txt', 'a') as f:
						f.write(str(hashtags)+"\n")
						f.close()	

				with open(str(screen_name)+'_datasets/'+ str(user) +'/'+ str(user) +'.txt', 'a') as f:
					f.write(str(tweet[2])+'\n')
					f.close()

		except tweepy.TweepError:
			print("Failed to run the command on that user, Skipping...")
			time.sleep(60)
			pass

def getNumberOfFollowers(screen_name):
	with open(str(screen_name)+'_datasets/'+str(screen_name)+'_followers.txt') as f:
		followers = f.read().splitlines()

	for user in followers:
		try:
			get_follower = api.get_user(user)
		except tweepy.TweepError as e:
			print "Failed to run the command on that user, Skipping...",user, e.message
			time.sleep(60)

		with open(str(screen_name)+'_datasets/'+ str(user) +'/'+ str(user) +'_count_followers.txt', 'w') as f:
			f.write(str(get_follower.followers_count))
			f.close()
		print user, get_follower.followers_count

def getDescOfFollowers(screen_name):
	with open(str(screen_name)+'_datasets/'+str(screen_name)+'_followers.txt') as f:
		followers = f.read().splitlines()
	for user in followers:

		try:
			get_follower = api.get_user(user)
			silentremove(str(screen_name)+'_datasets/'+ str(user) +'/'+ str(user) +'_desc_followers.txt')
			with open(str(screen_name)+'_datasets/'+ str(user) +'/'+ str(user) +'_desc_followers.txt', 'w') as f:
				f.write(str(get_follower.description.encode('utf-8')))
				f.close()
			print get_follower.description.encode('utf-8')

		except tweepy.TweepError:
			print("Failed to run the command on that user, Skipping...")
			time.sleep(60*15)
			pass

def getNumberOfRT(screen_name):
	with open(str(screen_name)+'_datasets/'+str(screen_name)+'_followers.txt') as f:
		followers = f.read().splitlines()

	for user in followers:
		try:
			counterR = 0
			counterF = 0
			all_tweets = get_all_tweets(user)

			silentremove(str(screen_name)+'_datasets/'+ str(user) +'/'+ str(user) +'_retweets.txt')
			silentremove(str(screen_name)+'_datasets/'+ str(user) +'/'+ str(user) +'_favorited.txt')

			for tweet in all_tweets:
				if tweet[3] or 'RT @' in tweet[2]:
					counterR += 1
					with open(str(screen_name)+'_datasets/'+ str(user) +'/'+ str(user) +'_retweets.txt', 'a') as f:
						f.write(str(tweet[2]) + "\n")
						f.close()
				elif tweet[4]:
					counterF += 1
					with open(str(screen_name)+'_datasets/'+ str(user) +'/'+ str(user) +'_favorited.txt', 'a') as f:
						f.write(str(tweet[2]) + "\n")
						f.close()
			print 'counter:', counterR, counterF
		except tweepy.TweepError:
			print("Failed to run the command on that user, Skipping...")
			time.sleep(60*15)

def countDatasets(screen_name):
	with open(str(screen_name)+'_datasets/'+str(screen_name)+'_followers.txt') as f:
		followers = f.read().splitlines()
	counter = 0
	users = 0
	for user in followers:
		i = 0
		if os.path.exists(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'.txt'):
			with open(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'.txt') as f:
				length = len(f.read().splitlines())
				counter += length
				if length:
					i += 1
				f.close()

		if os.path.exists(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'_hashtags_tweets.txt'):
			with open(str(screen_name)+'_datasets/'+str(user)+'/'+ str(user) +'_hashtags_tweets.txt') as f:
				length = len(f.read().splitlines())
				counter += length
				if length:
					i += 1
				f.close()
		if i>0:
			users += 1
		print user, counter, users
	return counter

def randomSample(screen_name):
	with open(str(screen_name)+'_datasets/'+str(screen_name)+'_followers.txt') as f:
		followers = f.read().splitlines()
	counter = 0
	print random.sample(followers,200)

def scrapTweets(screen_name):
	#step1 get list of followers and friends. Using function --> getUserFollowers()
	#step2 crawl recent tweets and the 3 most used hashtags of followers and friends. Using function --> getFollowersTweets()
	#step3a crawl tweets of the 3 most used hastags. Using function -->  hashtagGenerator()
	#step3b crawl tweets that is mentioning respective user. Using function -->  mentionGenerator()
	#step4 fetch user profile description. Using function --> getDescOfFollowers()
	#step5 extract all retweet (i.e. auto RT and normal RT) tweets and favorite tweets (if any) for each user. Using function --> getNumberOfRT()
	#optional: count number of followers. Using function --> getNumberOfFollowers()
	getUserFollowers(screen_name)
	getFollowersTweets(screen_name)
	hashtagGenerator(screen_name)
	mentionGenerator(screen_name)
	getDescOfFollowers(screen_name)
	getNumberOfRT(screen_name)
	getNumberOfFollowers(screen_name)


if __name__ == '__main__':

	userdataset2 = ['whussupfoot','valmaidearden','dVbryann','Todd_The_Fox','daniellejade198']
	for user in userdataset2:
		print user
		scrapTweets(user)
	# getUserAttributes("cliefsengkey")
	# randomSample("Europ4Americans")
	# getNumberOfFollowers("Europ4Americans")
	# countDatasets()
	# getNumberOfRT()
	# getDescOfFollowers()
	# getNumberOfFollowers()
	# getFollowersTweets()
	# getUserFollowers()
	# countHashtags()
	# searchHashtags()
	# searchMentions()
	# hashtagGenerator()