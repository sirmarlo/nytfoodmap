#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup 
import os
import json
import urllib
import requests

HUNGRY_CITY_URL='http://www.nytimes.com/svc/collections/v1/publish/www.nytimes.com/column/hungry-city'
RESTAURANT_REVIEW_URL='http://www.nytimes.com/svc/collections/v1/publish/www.nytimes.com/column/restaurant-review'
HTML_DIR = 'review_html'

def get_review_urls(source_url, pages=10):
    ret = []

    for page in range(0, pages):
        url = source_url + '?page=' + str(page)
        r = requests.get(url)

        if r.status_code == 200:
            data = r.json()
            for item in data['members']['items']:
                ret.append((item['url'], item['summary'], item['headline']))

    return ret

def get_review_data(review_url):
    # get filename off full URL
    fields = review_url.split('/')
    filename = HTML_DIR + '/' + fields[-1]
    text = ''

    # check if we have flat file already
    if os.path.isfile(filename) and (os.path.getsize(filename) > 0):
        #print "Found file(%s)" % filename
        with open(filename, 'r') as fo:
            text = fo.read()
    else:   # don't have data, get it on web
        r = requests.get(review_url)

        if r.status_code == 200:
            text = r.text
            with open(filename, 'w') as fo:
                fo.write(text.encode('utf-8'))
        else:
            return None

    # we have our text now, let's extract and build our return object
    soup = BeautifulSoup(text)

    try:
        map_data = soup.find("script", { "id": "review-map-data" }).contents[0]
        data = json.loads(map_data)
        ret = data['GoogleMapOptions'][0]
        ret['name'] = soup.find("meta", { "itemprop": "itemreviewed" })['content']
        return ret
    except:
        return None


def main():
    masterData = { 'hungry': [], 'pete': [] }

    # get list of review urls
    pages = 1
    hungryCityUrls = get_review_urls(HUNGRY_CITY_URL, pages)
    restReviewUrls = get_review_urls(RESTAURANT_REVIEW_URL, pages)


    # get individual review data
    # Hungry City
    for item in hungryCityUrls:
        url = item[0]
        data = get_review_data(url)
        if data is None:
            continue

        data['url'] = url
        data['summary'] = item[1]
        data['headline'] = item[2]
        masterData['hungry'].append(data)

    # Restaurant Review
    for item in restReviewUrls:
        url = item[0]
        data = get_review_data(url)
        if data is None:
            continue

        data['url'] = url
        data['summary'] = item[1]
        data['headline'] = item[2]
        masterData['pete'].append(data)        

    with open('masterData.json', 'w') as fo:
        fo.write(json.dumps(masterData, sort_keys=True, indent=4))

# Let's get the party started

main()
