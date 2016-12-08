#!/usr/bin/env python
# encoding: utf-8

import csv
import plotly.plotly as py
from plotly.graph_objs import *
from auth_key import *

#Twitter API credentials
#mapbox_access_token = 'pk.eyJ1IjoieW91bmdnbnMiLCJhIjoiY2l3ZWs0aHBvMDRmcDJvbm0xNjQxdHpidiJ9.XBODA-Loo6VFADOkWT78Zg'
all_file = csv.reader(open('latlong_all.csv', newline=''), delimiter=',', quotechar='"')
all_dic = {}
for row in all_file:
	if row[0]=='id':
		continue
	else:
		all_dic[row[0]] = [row[1], row[2], row[3]]

def target_retrieve(filename):
	lat, lon, name = [], [], []
	input_file = csv.reader(open(filename, newline=''), delimiter=',', quotechar='"')
	for row in input_file:
		if row[0]=='id':
			continue
		else:
			if row[0] in all_dic:
				name.append(all_dic[row[0]][0])
				lat.append(all_dic[row[0]][1])
				lon.append(all_dic[row[0]][2])
	return lat, lon, name

def draw_map(lat1, lon1, name1, lat2, lon2, name2, mapname):
	data = Data([
		Scattermapbox(
	        lat=lat2,
	        lon=lon2,
	        mode='markers',
	        marker=Marker(
	            size=9,
	            color='rgb(255, 29, 29)',
	            opacity=0.8
	        ),
	        text=name2,
	    ),
	    Scattermapbox(
	        lat=lat1,
	        lon=lon1,
	        mode='markers',
	        marker=Marker(
	            size=9,
	            color='rgb(86, 86, 86)',
	            opacity=0.6
	        ),
	        text=name1,
	        hoverinfo='text'
	    )
	])

	layout = Layout(
		title=mapname,
	    autosize=True,
	    hovermode='closest',
	    mapbox=dict(
	        accesstoken=mapbox_access_token,
	        bearing=0,
	        center=dict(
	            lat=38,
	            lon=-94
	        ),
	        pitch=0,
	        zoom=3,
	        style='light'
	    ),
	)

	fig = dict(data=data, layout=layout)
	py.plot(fig, filename=mapname)


def main():
	#lat_b, lon_b, name_b = target_retrieve('before_counter.csv')
	lat_a, lon_a, name_a = target_retrieve('after_counter.csv')
	lat_bt, lon_bt, name_bt = target_retrieve('before_counter_target.csv')
	lat_at, lon_at, name_at = target_retrieve('after_counter_target.csv')
	
	#draw_map(lat_b, lon_b, name_b, lat_bt, lon_bt, name_bt, 'Before Map')
	draw_map(lat_a, lon_a, name_a, lat_at, lon_at, name_at, 'All versus Target (After election)')
	draw_map(lat_bt, lon_bt, name_bt, lat_at, lon_at, name_at, 'Before versus After (Target tweets)')
	
if __name__ == '__main__':
	main()
