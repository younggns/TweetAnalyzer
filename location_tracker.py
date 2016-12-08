#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
import csv
from geopy.geocoders import Nominatim
from auth_key import *

# Twitter API credentials
# Twitter API credentials
# consumer_key
# consumer_secret
# access_key
# access_secret

auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_key,access_secret)

geolocator = Nominatim()

def read_location(filename):
	lat, lon, name, account = [], [], [], []
	csv_reader = csv.reader(open(filename, newline=''), delimiter=',', quotechar='"')

	api = tweepy.API(auth, wait_on_rate_limit=True)
	counter = 0
	for row in csv_reader:
		counter += 1
		if row[0]=='id':
			continue
		try:
			user = api.get_user(row[0]).name
			screen_name = api.get_user(row[0]).screen_name
			location = geolocator.geocode(api.get_user(row[0]).location)
			if location:
				lat.append(location.latitude)
				lon.append(location.longitude)
				name.append(user)
				account.append(screen_name)
				print(user, "appended")
			else:
				continue
		except:
			print("passed")
	return lat, lon, name, account

def main():
	lat, lon, name, account = read_location('after_counter.csv')
	r_list = []
	for i in range(len(lat)):
		r_list.append([account[i], name[i], lat[i], lon[i]])

	with open('latlong_all.csv', 'w', newline='') as f:
		writer = csv.writer(f, delimiter=',', quotechar='"')
		writer.writerow(["id"]+["name"]+["lat"]+["long"])
		writer.writerows(r_list)
	pass
	
if __name__ == '__main__':
	main()
