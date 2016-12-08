#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
import csv
import time
import nltk
from datetime import date
from nltk.stem import WordNetLemmatizer
from auth_key import *

# Twitter API credentials
# consumer_key
# consumer_secret
# access_key
# access_secret

today = date.today()
election_day = date(2016, 11, 8)
date_from = election_day - (today - election_day)

wordnet_lemmatizer = WordNetLemmatizer()

id_dict = {}
target_words = ['intimidation', 'sexual', 'discrimination', 'hate', 'racial', 'ethnicity', 'crime', 'assault', 'attack', 'abuse', 'arrest', 'caution', 'emergency', 'fight', 'harassment', 'harm', 'improper', 'investigate', 'threat', 'offender', 'misdemeanor', 'offense', 'perpetrator', 'rape', 'violate', 'violation', 'violence', 'suspect', 'suspected', 'victim']

total_num = 0

def pos_converter(upenn_pos):
	if upenn_pos =='MD' or upenn_pos =='VB' or upenn_pos =='VBD' or upenn_pos =='VBG' or upenn_pos =='VBN' or upenn_pos =='VBP' or upenn_pos =='VBZ':
		return 'v'
	elif upenn_pos =='JJ' or upenn_pos =='JJR' or upenn_pos =='JJS':
		return 'a'
	elif upenn_pos == 'RB' or upenn_pos =='RBR' or upenn_pos =='RBS':
		return 'r'
	else:
		return 'n'

def get_2000_univ():
	twitter_list_file = open('twitteraccount_list.txt', 'r')
	indicator = 0
	global total_num
	id_list = []
	for row in twitter_list_file:
		if indicator == 1:
			id_list.append(row)
			indicator = 0
			total_num += 1
		if row.startswith(" Follow"):
			indicator = 1

	for item in id_list:
		try:
			name, account = item.split(' @')
			id_dict[name[1:]] = account[:-1]
		except:
			continue

def get_all_tweets(screen_name):
	#authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth, wait_on_rate_limit=True)
	
	loopCond = True
	#initialize a list to hold all the tweepy Tweets
	alltweets = []	
	
	#make initial request for most recent tweets (200 is the maximum allowed count)
	try:
		new_tweets = api.user_timeline(screen_name = screen_name,count=200)
		if len(new_tweets)>0 and new_tweets[-1].created_at.date() < date_from:
			for tweet in new_tweets:
				if tweet.created_at.date() < date_from:
					new_tweets.remove(tweet)
			loopCond = False
		
	except:
		new_tweets = []
		print(screen_name, "is in trouble.")

	#save most recent tweets
	alltweets.extend(new_tweets)
	
	#save the id of the oldest tweet less one
	if len(alltweets)>0:
		oldest = alltweets[-1].id - 1
	
	#keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0 and loopCond:
		#print "getting tweets before "+ (oldest)
		
		#all subsiquent requests use the max_id param to prevent duplicates
		try:
			new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
			if len(new_tweets)>0 and new_tweets[-1].created_at.date() < date_from:
				for tweet in new_tweets:
					if tweet.created_at.date() < date_from:
						new_tweets.remove(tweet)
				alltweets.extend(new_tweets)
				loopCond = False
				break
			
		except:
			new_tweets = []
			print(screen_name, "is in trouble.")

		#save most recent tweets
		alltweets.extend(new_tweets)
		
		#update the id of the oldest tweet less one
		if len(alltweets)>0:
			oldest = alltweets[-1].id - 1
	print(len(alltweets) ,"tweets appended")
	return alltweets
		

def write_count(inputfile, outputfile):
	count_dic = {}
	input_file = csv.reader(open(inputfile, newline=''), delimiter=',', quotechar='"')

	for row in input_file:
		if row[0]=='id':
			continue
		if row[0] not in count_dic:
			count_dic[row[0]] = 1
		else:
			count_dic[row[0]] += 1

	new_out = list(count_dic.items())

	with open(outputfile, 'w', newline='') as f:
		writer = csv.writer(f, delimiter=',', quotechar='"')
		writer.writerow(["id"]+["count"])
		writer.writerows(new_out)
	pass

def tweet_match(all_writer, before_writer, after_writer, before_target_writer, after_target_writer):
	pos_list = nltk.pos_tag(target_words)
	target_words_lemma = [wordnet_lemmatizer.lemmatize(words[0], pos_converter(words[1])) for words in pos_list]
	
	for key in id_dict:
		print("Retrieving all tweets from", key, "(", counter , "of", total_num, ")")
		all_items = get_all_tweets(id_dict[key])
		all_out = []
		before_out = [[tweet.user.screen_name, tweet.created_at, tweet.text.encode("utf-8")] for tweet in all_items if (tweet.created_at.date()<election_day and tweet.created_at.date() >= date_from)]
		after_out = [[tweet.user.screen_name, tweet.created_at, tweet.text.encode("utf-8")] for tweet in all_items if (tweet.created_at.date()>=election_day)]
		all_out.extend(after_out)
		all_out.extend(before_out)

		print("Writing files...")
		before_writer.writerows(before_out)
		after_writer.writerows(after_out)
		all_writer.writerows(all_out)

		print("Matching target words...")
		before_lem, after_lem = [], []
		for row in before_out:
			text_list = nltk.pos_tag(nltk.word_tokenize(str(row[2]).lower()))
			before_lem.append([row[0], row[1], row[2], [wordnet_lemmatizer.lemmatize(words[0], pos_converter(words[1])) for words in text_list] ])
		for row in after_out:
			text_list = nltk.pos_tag(nltk.word_tokenize(str(row[2]).lower()))
			after_lem.append([row[0], row[1], row[2], [wordnet_lemmatizer.lemmatize(words[0], pos_converter(words[1])) for words in text_list] ])

		before_lem_out, after_lem_out = [], []
		for row in before_lem:
			for word in target_words_lemma:
				if word in row[3]:
					before_lem_out.append([row[0], row[1], row[2]])

		for row in after_lem:
			for word in target_words_lemma:
				if word in row[3]:
					after_lem_out.append([row[0], row[1], row[2]])

		print("Writing",len(before_lem_out),"and",len(after_lem_out),"filtered results...")
		before_target_writer.writerows(before_lem_out)
		after_target_writer.writerows(after_lem_out)

		counter += 1
		pass

def call_writer(filename):
	f = open(filename, 'w', newline='')
	fw = csv.writer(f, delimiter=',', quotechar='"')
	fw.writerow(["id"]+["created_at"]+["text"])
	return fw

def main():
	counter = 1
	print("Today is", today, "and the election day was", election_day)
	print("Therefore, we retrieved data from", date_from)

	get_2000_univ()

	all_writer = call_writer('alltweets.csv')
	before_writer = call_writer('before_refine.csv')
	after_writer = call_writer('after_refine.csv')
	before_target_writer = call_writer('before_refine_target.csv')
	after_target_writer = call_writer('after_refine_target.csv')

	tweet_match(all_writer, before_writer, after_writer, before_target_writer, after_target_writer)

	write_count('before_refine.csv', 'before_counter.csv')
	write_count('after_refine.csv', 'after_counter.csv')
	write_count('before_refine_target.csv', 'before_counter_target.csv')
	write_count('after_refine_target.csv', 'after_counter_target.csv')

	print("Done")

if __name__ == '__main__':
	main()