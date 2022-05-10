"""This is the common mysql utility file. This file manages the connection variable.
All the sql queries will be executed from here, which makes the code cleaner in other scripts.
Currently, database name is hardcoded here, as generally the is one database for one module. However, there is enough
flexibility in this script to work with different databases dynamically"""

import mysql.connector
import common_utilites as cu
import logging

def create_connection():
    user = cu.get_configs('mysql', 'user')
    passwrd = cu.get_configs('mysql', 'pass')
    conn = mysql.connector.connect(host='localhost', database='test1', user=user, password=passwrd)
    return conn

def execute_query(query=None, data=None):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        if data:
            cursor.executemany(query, data)
        else:
            cursor.execute(query)

        total_count = cursor.rowcount
        res = cursor.fetchall()
        conn.commit()
        cursor.close()
        return 0, total_count, res
    except Exception as e:
        print(e.__str__())
        logging.exception(datetime.datetime.now().strftime("%Y-%m-%d %H-%m-%S"))
        return 1, e

def update_exec_stats(current_count=None, sec=None):
    """This method is designed to update the stats in execution stats table.
    query1 and query2 are used to fetch data to update number of tweets collected in every batch.
    query3 and query4 are used compare the counts of tweets present in the Twitter and tweets fetched
    further it updates the status of entire job execution"""

    query1 = "select exec_id,tweets_collected from execution_stats where exec_id =" \
             " (select max(exec_id) from execution_stats)"
    query2 = "update execution_stats set tweets_collected = {} where exec_id = {}"
    query3 = "select tweets_at_source, tweets_collected,exec_id from execution_stats where exec_id = (" \
             "select max(exec_id) from execution_stats)"
    query4 = "update execution_stats set status = '{}' where exec_id = {}"

    if sec == 'status':
        print(query3)
        q3_res = execute_query(query=query3)
        tweets_at_source = q3_res[2][0][0]
        tweets_collected = q3_res[2][0][1]
        job_status = 'success'
        if tweets_collected != tweets_at_source:
            job_status = 'failed'
        print(job_status)
        execute_query(query=query4.format(job_status, q3_res[2][0][2]))

    else:
        q1_res = execute_query(query=query1)
        if q1_res[2][0][1]:
            current_count = q1_res[2][0][1] + current_count
        execute_query(query=query2.format(current_count, q1_res[2][0][0]))
    return 0


if __name__ == "__main__":
    ee = update_exec_stats(sec='status')
