"""This common utility file is to provide basic functionality to the entire project.
Here we are emphasising on the re-usability principle of software engineering. Most of the parameters are made optional
so that it can be used with most of the methods."""

import configparser
import requests
import json
import datetime
import time


def prepare_payload(conf_parent=None, fetch_type=None):
    """This method is designed to create the payload to hit the API. This is common method that can be used to hit
    almost any Twitter api"""

    url = get_configs(conf_parent, fetch_type)
    query_params = json.loads(get_configs(conf_parent, 'query_params_'+fetch_type))
    end_time, start_time = get_dates()
    query_params['start_time'] = start_time
    query_params['end_time'] = end_time
    return url, query_params

def get_configs(conf_parent, conf_type):
    """This method will read the configuration properties config.ini file. This method is designed to replicate the
    functionality of the key-vault"""

    config = configparser.ConfigParser(interpolation=None)
    """interpolation property is used to ignore the % sign in the property that is being read"""

    config.read('config.ini')
    return config[conf_parent][conf_type]

def set_headers():
    headers = {"Authorization": "Bearer {}".format(get_configs('twitter', 'bearer'))}
    return headers

def get_dates():
    today = datetime.datetime.today()
    end_time = today.strftime('%Y-%m-%dT00:00:00Z')
    start_time = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%dT00:00:00Z')
    return end_time, start_time

def fetch_data(url=None, params=None):
    res = requests.request("GET", url, headers=set_headers(), params=params)
    return res


if __name__ == "__main__":
    response = fetch_data('tweets')
    print(response)
    print(response.json())
    print(json.dumps(response.json(), indent=4, sort_keys=True))
