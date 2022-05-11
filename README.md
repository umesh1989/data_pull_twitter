This is the brief description of how this entire modules is working.
This writeup will contain, what functionalities have been developed, reason for making current decisions and enhancement 
that can be done.


**Flow of the module:**\
Driver_file.py is the entering point for this module. It will start with initiation the logger. Post that it calls the 
get_count method, which gets the count of the tweets for given keyword for a given time range. Once counts are extracted 
it will be stored in the execution stats table along with the other execution attributes, like:
execution date(date on which execution is taking place), job start datetime and job end datetime,
tweets at the source. Once all of these attributes are updated, method to fetch tweets will start. Fetched tweets will be 
stored in the tweets table. 

Currently, following attributes are stored in table:
1. tweet id
2. tweet text
3. retweet count
4. reply count
5. likes count
6. quotes count
7. created at
8. author id
9. emojis/emoticons

Along with the above-mentioned attributes many more are also being fetched, but they are not being stored in tables yet.

**Brief summary of attributes that are being fetched:**
1. Media in the tweet
2. User info like:
   1. username
   2. user id
   3. location
   4. profile pic
   5. followers count
   6. following count
3. Other tweet info like:
   1. mentions
   2. info of mentioned users

Details list of attributes that are fetched now:

**"expansions":** "author_id,attachments.media_keys,in_reply_to_user_id,entities.mentions.username,geo.place_id",

**"tweet.fields":** "id,text,created_at,author_id,geo,in_reply_to_user_id,attachments,public_metrics,reply_settings,conversation_id,entities,referenced_tweets,source",


**"user.fields":** "id,name,username,created_at,description,profile_image_url,location,public_metrics,url",

**"place.fields":** "full_name,id,country,country_code,geo,name,place_type",

**"media.fields":** "media_key,type,url"

Above-mentioned additional info can help us in figuring out the reach and engagement of any positive or negative tweet. Moreover, it 
can give us insight about the user and help us understand user better.

**Database and Tables:**\
For now mysql is being used as the backend.\
**Reason:**\
When I hit the tweets count api for the ikea keyword, which is very common, in that there were maximum 2-3k tweets per 
day and without any language filter it was around 6-7k. Now, even if we consider 10k tweets per day, this makes 360k tweets
a year, which doesn't look like a huge number. Mysql can easily handle this much data, and the query will be faster too
 as compared to Hive, or any other data storing tool.

**Exec_stats_table:**

    create table execution_stats(exec_id int not null auto_increment, execution_date date, starttime datetime, endtime datetime, tweets_at_source int, tweets_collected int, status varchar(8), primary key (exec_id));

**Tweets table**

    create table tweets1 (id bigint, msg text, retweets int, reply int, likes int, quotes int, created_at datetime, author_id bigint,emoji text, primary key(id));


Currently, we are using two data table:
1. Execution status: this will store the info and status of the data fetch job.
2. Tweets table: This table will store the properties mentioned above in this writeup. Since this table already has author id which we can use to join with user table and **user table** can be joined with **media table**.

**Logging:**\
Python default logger has been used here. A log file will get created in the log folder with date and time. Couple of 
logs and failure traceback will be captured in these logs.

**Exception handling**\
Currently Exception handling is at a very broad level in this. Which can be detailed if it comes to develop this at prod 
level.

**Current Test Case**

For now as part of test cases, I am comparing the number of tweets at source and tweets collected, if, the count matches
the job execution status is updated with success else with failure.

**Future Enhancements**
1. More detailed level exception handling can be done where retry option can also be implemented.
2. New tables User and media can be introduced to store additional information that is being fetched.
3. Instead of using the config.ini file a key vault service can be used.
4. Dumping the raw data in the file system, where that data can be used if someone wanted to use the data which is not being inserted in the table.
5. Currently, this is an on prem implementation, it can be migrated to cloud.
6. If data grows overtime, However, my sql can easily deal with 6-7 years of data, but we can choose to move to a nosql db or postgre sql.



