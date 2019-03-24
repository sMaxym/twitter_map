from flask import Flask, render_template, request
from folium import Map, FeatureGroup, CircleMarker
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import urllib.request, urllib.parse, urllib.error
import twurl
import json
import ssl


def init_map(path, data):
    """
    str, list -> folium map
    Creates a folium map .html file in the direction path.
    """
    map = Map()
    data_group = FeatureGroup(name='Data Layer')
    geolocator = Nominatim(user_agent='shumakov')
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.01)
    for row in data:
        if not row[0] or not row[1]:
            continue
        pos = geolocator.geocode(row[1])
        data_group.add_child(CircleMarker(location=[pos.latitude, pos.longitude],
                                          radius=7,
                                          popup=row[0],
                                          fill_color='red',
                                          color='white',
                                          fill_opacity=0.5))
    map.add_child(data_group)
    map.save(path)
    return map


def get_data(name):
    """
    str -> list(tuple)
    Return the list of friends and their locations in a
    form of list of tuples by the twitter account name.
    """
    info = list()
    TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    url = twurl.augment(TWITTER_URL,
                            {'screen_name': name, 'count': '5'})
    connection = urllib.request.urlopen(url, context=ctx)
    data = connection.read().decode()
    js = json.loads(data)
    users = js['users']
    for user in users:
        print((user['name'], user['location']))
        info.append((user['name'], user['location']))
    return info


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/Map', methods=['POST'])
def map():
    name = request.form.get('input_name')
    data = get_data(name)
    init_map('templates/map.html', data)
    return render_template('map.html')
