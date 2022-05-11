"""This is the main driver file which will trigger the execution. It will first hit the count api to get the count for a
date range. After that hit the search api to get data. This script updates the execution date, job start and end time,
tweets at source and tweets collected."""
import datetime

import common_utilites as cu
import json
import time
import re
import emoji
import mysql_utility as mu
import logging
import datetime


def get_count():
    url, query_params = cu.prepare_payload(conf_parent='twitter', fetch_type='counts')
    response = cu.fetch_data(url=url, params=query_params)
    logging.info(response.json())
    tweets_at_source = response.json()['meta']['total_tweet_count']
    insert_query = cu.get_configs('mysql', 'exec_stats_insert_query')
    start_time = re.sub('[TZ]', ' ', query_params['start_time']).strip()
    end_time = re.sub('[TZ]', ' ', query_params['end_time']).strip()
    """in above two lines Timezone characters are striped from the datetime, so that it can be inserted in msql"""

    vals = "'"+query_params['end_time'].split('T')[0]+"','"+start_time+"','"+end_time+"',"+str(tweets_at_source)
    insert_query = insert_query.format(str(vals))
    mu.execute_query(query=insert_query)

    return 0

def get_tweets():
    url, query_params = cu.prepare_payload(conf_parent='twitter', fetch_type='tweets')
    while True:
        data_list = []
        response = cu.fetch_data(url=url, params=query_params)
        logging.info(response.json())
        data = response.json()['data']
        for tweet in data:
            tid = tweet['id']
            tt = tweet['text']
            retweets = tweet['public_metrics']['retweet_count']
            reply = tweet['public_metrics']['reply_count']
            like_count = tweet['public_metrics']['like_count']
            quote = tweet['public_metrics']['quote_count']
            auth_id = tweet['author_id']
            created_at = re.sub('[TZ]', ' ', tweet['created_at']).strip()
            emoticon = '  '.join(c for c in tt if c in emoji.UNICODE_EMOJI['en'])
            encoded_content = emoticon.encode('unicode-escape').decode('ASCII')
            # decoded_content = encoded_content.encode('ASCII').decode('unicode-escape')
            """above line is commented because, this line decodes the ASCII value of emoji to display 
            it in the graphic manner"""

            data_list.append((tid, tt, retweets, reply, like_count, quote, created_at, auth_id, encoded_content))
        query = cu.get_configs('mysql', 'tweets_insert')
        query_result = mu.execute_query(query=query, data=data_list)
        logging.info('inserted tweets '+str(query_result[1]))
        mu.update_exec_stats(current_count=query_result[1])
        logging.info('updated tweets stats with new tweets '+str(query_result[1]))
        if 'next_token' in response.json()['meta']:
            query_params['next_token'] = response.json()['meta']['next_token']
            time.sleep(2)
        else:
            break

    return 0


if __name__ == "__main__":
    logging.basicConfig(filename='logs/exec_logs_' + datetime.datetime.now().strftime("%Y-%m-%d %H-%m-%S") + '.log',
                        level=logging.INFO)
    try:
        tweet_counts = get_count()
        tweets_res = get_tweets()
        update_stat = mu.update_exec_stats(sec='status')
    except Exception as e:
        logging.exception(datetime.datetime.now().strftime("%Y-%m-%d %H-%m-%S"))
