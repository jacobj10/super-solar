import os
import requests
import pymatlab
import numpy as np
import xlwt
from requests.auth import HTTPBasicAuth
import json
import simplejson
import utm
from pyproj import Proj
from shapely.geometry import shape
import hashlib

m = hashlib.md5()

def getReq(dataPoints):
	search_endpoint_request = {
	  "item_types": ["REOrthoTile"],
	  "filter": getFilter(dataPoints),
	  "_page_size": 1000
	}
	result = \
	  requests.post(
		'https://api.planet.com/data/v1/quick-search',
		auth=HTTPBasicAuth('2074e41ba6b74d27b759d621aefff98b', ''),
		json=search_endpoint_request
		)
	return result

def getFilter(dataPoints):
	# the geo json geometry object we got from geojson.io
	geo_json_geometry = {
	  "type": "Polygon",
	  "coordinates": [dataPoints,]
	}

	# filter for items the overlap with our chosen geometry
	geometry_filter = {
	  "type": "GeometryFilter",
	  "field_name": "geometry",
	  "config": geo_json_geometry
	}

	_filter = {
	  "type": "AndFilter",
	  "config": [geometry_filter,]
	}
	return _filter

def getH(lat, longt):
	x = requests.get('https://eosweb.larc.nasa.gov/cgi-bin/sse/grid.cgi?email=skip%40larc.nasa.gov&step=2&lat={0}&lon={1}&num=186096&p=grid_id&p=ret_tlt0&sitelev=&veg=17&hgt=+100&submit=Submit'.format(lat,longt))
	ind = x.text.index('url=')
	end = x.text.index('<SCRIPT')
	final = x.text[ind+4:end-3]
	y = requests.get(final)
	pls = y.text
	tempList = pls[pls.index('Tilt 0') - 1 : pls.index('OPT')].split('</td></tr>')
	poop = [ float(tempList[i].split('</td><td align="center" nowrap>')[-1]) for i in range(0, len(tempList) - 1) ]
	return str(max(poop))

def write(newJson, latlonglist, h):
	book = xlwt.Workbook(encoding="utf-8")
	sheet1 = book.add_sheet("Sheet 1")
	sheet1.write(0, 0, "Date Acquired")
	sheet1.write(1, 0, "Cloud Cover")
	sheet1.write(2, 0, "Sun Azimuth")
	sheet1.write(3, 0, "Sun Elevation")
	sheet1.write(4, 0, "Lat")
	sheet1.write(5, 0, "Long")
	toReturn = None
	for i in range(1, 6):
		sheet1.write(4, i, latlonglist[i - 1][1])
		sheet1.write(5, i, latlonglist[i - 1][0])
	sheet1.write(6, 0, "H value")
	sheet1.write(6, 1, h)
	for i in range(0, len(newJson['features'])):
		
		tempParse = newJson['features'][i]['properties']['acquired'].split('T') 
		tempParse[1] = tempParse[1].split('.')[0].split('Z')[0]
		tempParse = " ".join(tempParse)
		if i == 0:
			m.update(tempParse)
			toReturn = m.hexdigest()
		matList = [ 
					tempParse,
					newJson['features'][i]['properties']['cloud_cover'],
					newJson['features'][i]['properties']['sun_azimuth'],
					newJson['features'][i]['properties']['sun_elevation'],
				]
		for j in range(0, len(matList)):
			sheet1.write(j, i + 1, matList[j])
	book.save("./spreadsheets/{0}.xls".format(toReturn))
	return toReturn
"""
result = getReq()
newJson = json.loads(result.text)
h = getH(30, 30)
area = getArea(newJson)
write(newJson, area, h)
"""
