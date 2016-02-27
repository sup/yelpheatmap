# -*- coding: utf-8 -*-
"""
Yelp API v2.0 code sample.

This program demonstrates the capability of the Yelp API version 2.0
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.

Please refer to http://www.yelp.com/developers/documentation for the API documentation.

This program requires the Python oauth2 library, which you can install via:
`pip install -r requirements.txt`.

Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
import argparse
import json
import pprint
import sys
import urllib
import urllib2
from secret import *
import oauth2
import time


API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 20
SORT = 1
RADIUS = 40000
FILTER = 'restaurants'
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()
    
    print u'Querying {0} ...'.format(signed_url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def get_all_businesses(term, location):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        tuple (business_id, rating, address_list): Of 1000 businesses
        as limited by the Yelp API.
    """
    offset = 0
    one_star = []
    two_star = []
    three_star = []
    four_star = []
    while offset < 1000: 
        url_params = {
            'term': term.replace(' ', '+'),
            'location': location.replace(' ', '+'),
            'limit': SEARCH_LIMIT,
            'offset': offset,
            'filter': FILTER,
        }
        result = request(API_HOST, SEARCH_PATH, url_params=url_params)
        resulting_businesses = result["businesses"]
        one_star = one_star + [{"address": ", ".join(x["location"]["display_address"])} if len(x["location"]["display_address"]) <= 2 else {"address": ", ".join([x["location"]["display_address"][0]] + x["location"]["display_address"][2:])} for x in resulting_businesses if x["rating"] < 2]
        two_star = two_star + [{"address": ", ".join(x["location"]["display_address"])} if len(x["location"]["display_address"]) <= 2 else {"address": ", ".join([x["location"]["display_address"][0]] + x["location"]["display_address"][2:])} for x in resulting_businesses if x["rating"] < 3 and x["rating"] >= 2.0]
        three_star = three_star + [{"address": ", ".join(x["location"]["display_address"])} if len(x["location"]["display_address"]) <= 2 else {"address": ", ".join([x["location"]["display_address"][0]] + x["location"]["display_address"][2:])} for x in resulting_businesses if x["rating"] < 4 and x["rating"] >= 3.0]
        four_star = four_star + [{"address": ", ".join(x["location"]["display_address"])} if len(x["location"]["display_address"]) <= 2 else {"address": ", ".join([x["location"]["display_address"][0]] + x["location"]["display_address"][2:])} for x in resulting_businesses if x["rating"] <= 5 and x["rating"] >= 4.0]
        offset += 20
    businesses = {
        "one_star": one_star,
        "two_star": two_star,
        "three_star": three_star,
        "four_star": four_star
    }
    return businesses

def compute_lat_lng(businesses, stars):
    final_results = []
    for x in businesses[stars]:
        address = x["address"].replace(" ", "+")
        url="https://maps.googleapis.com/maps/api/geocode/json?address=%s" % address
        response = urllib2.urlopen(url)
        jsongeocode = response.read()
        try:
            final_results.append(json.loads(jsongeocode)["results"][0]["geometry"]["location"])
        except Exception:
            time.sleep(.2)
    return final_results

def main():
    #print "Done computing lat lngs!"
    businesses = get_all_businesses("chinese food", "New York City, NY")
    with open('nyc_businesses.txt', 'w') as nyc_businesses:
        nyc_businesses.write(str(businesses))
    with open('nyc_businesses.txt') as text_file:
        content = text_file.readlines()
    businesses = eval(content[0])
    with open('nyc_lat_lng.txt', 'w') as text_file:
        one_star = str(compute_lat_lng(businesses, "one_star")) + "\n"
        two_star = str(compute_lat_lng(businesses, "two_star")) + "\n"
        three_star = str(compute_lat_lng(businesses, "three_star")) + "\n"
        four_star = str(compute_lat_lng(businesses, "four_star"))
        text_file.write(one_star + two_star + three_star + four_star)

if __name__ == '__main__':
    main()