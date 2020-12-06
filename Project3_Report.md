# Project 3: Understanding User Behavior
### Team 4
### Team Member: Hao Wu, Haolun Zhang, Haoyu Zhang

## **Report Struture**:
    1. Project Description
    2. Tools
    3. Project Overview - Database, Pipeline, Analysis
    4. Commands & Example Outputs
    5. Example Sanity Check
    6. Simple Data Analysis (Presto)

## 1. Project Description

-  Our project is intended to mimic a real world gaming system to include simple gaming ideas such as purchases, inventory, guild joining mechanics. We utilized the below tools to realize features like: 
    1. live time player status check
    2. Inventory tracking
    3. Purchase randomization in terms of weapon rarity
    4. Simple analysis using Hive and Presto utilizing the live data stream build using flask API and Kafka.


    
- **Our project focused more on API building and game event logics rather than the analysis part in Presto. The analysis in presto is intended to show idea demonstration the game owner can potentially perform rather than an actual full length data analysis with real world data.**
    


- Most of our examples shown in this report are ran our teammate's, **Haoyu Zhang's**, system, so you might observer certain system path call that is different from the owner in Github.

- The MD file and the jupyter notebook files serve as our main report for the project to demonstrate the pipeline workflow, simple analysis. In case the format of MD is not ideal due to plateform supporting and various code examples, please refer to ou jupyter file for your reference.

## 2. Tools

For this project, we used the following tools:
1. Docker Images: 
  - cloudera 
  - kafka                        
  - mids (terminal system image)
  - spark
  - zookeeper
  - Presto
2. SQLite Database
3. Kafka
4. Hive
5. Flask API
6. Presto
7. Google Cloud Virtual Machine 
8. Jupyter Notebook

## 3. Project Overview - Database, Pipeline, Analysis

#### SQLite Database setup
- To keep live referrence with each API call the player enters in their record and satisfy certain join guild conditions. We implemented SQLite database techinques including:
    1. Creating tables: player_status (weapon inventory), and guild (guild name and the player in it)
    2. Building connections within API calls so for certain event criteria, the API can interact with the live status of the SQLite database created and identify if the player satisfy the criterias or not and return the appropriate response.


#### API Functionality
Event Types:
   1. Purchase a sword
   2. Purchase a shield
   3. Join a guild
   
#### Event action details:
   - For `Purchase a sword` and `Purchase a shield` events, when getting called for each user, the API function will generate a rarity number that is assigned randomly along with the weapon type for the user.
   
   - For `Join a guild` event, the player will specify the guild name they want to join along with their player name into the API call, the function will check whether they qualify for the conditions for them to join the guild. **Conditions include: 1. this player has not joined the same guild before. 2. the player has at least a sword or a shield** Our API function will check for these two conditions before letting the player join the guild and return the according responses to the user in API call.
   
#### Information passed through Kafka
   - For `Purchase a sword` and `Purchase a shield` events, th API will pass the player name, weapon type and weapon rarity information along with Host info and other system info into the created Kafka pipelines.
   - For `Join a guild` events, the API will pass the player name, guild name, the 
   
#### Stream Filtering and Hive Table Creation

- For designing the pipeline, we decided to use a single topic in kafka, and separate script for filtering events and creating hive tables for querying purpose for the 3 event types listed in the above section.

- We created the filters by identifying the event type in each json record passed through kafka and created 3 tables in hive using hive sql querying and matched these tables to the parquet files stored in the corresponding locations. 

- The 3 tables we created and matched to the parquet files are:
    1.shield_purchases
    2.sword_purchases
    3.guild_joins

#### Presto Querying for simple analysis

- After the streaming is setup and the Hive tables created, we inputed sudo user data and performed simple analysis for each table to test the notion of some user behavior and player status.


## 4. Commands & Example Outputs
### a. Set up Database


```python
import sqlite3
```


```python
conn = sqlite3.connect('player_status.db')

cursor = conn.cursor()

command_create = """Create TABLE IF NOT EXISTS 
player_status(player_name TEXT, Weapon_type Text, Rarity INTEGER)"""

cursor.execute(command_create)

cursor.execute("insert Into player_status VALUES('Hao','Sword', 5)")
cursor.execute("insert Into player_status VALUES('Dan','Sword', 2)")

conn.commit()
conn.close()
```


```python
conn = sqlite3.connect('player_status.db')

cursor = conn.cursor()

command_create = """Create TABLE IF NOT EXISTS 
guild(guild_name TEXT, player_name)"""

cursor.execute(command_create)

cursor.execute("insert Into guild VALUES('Avengers', 'Hao')")
cursor.execute("insert Into guild VALUES('Justice_League', 'Dan')")
cursor.execute("insert Into guild VALUES('SpongeBob', 'Alan')")

conn.commit()
conn.close()
```

### b. Set up Docker

```
docker-compoes up -d

```

```
docker-compose ps

```

```

Name                             Command               State                               Ports                            
-------------------------------------------------------------------------------------------------------------------------------------------
project-3-haoyuzhang89_cloudera_1    /usr/bin/docker-entrypoint ...   Up      10000/tcp, 50070/tcp, 8020/tcp, 0.0.0.0:8888->8888/tcp,      
                                                                              9083/tcp                                                     
project-3-haoyuzhang89_kafka_1       /etc/confluent/docker/run        Up      29092/tcp, 9092/tcp                                          
project-3-haoyuzhang89_mids_1        /bin/bash                        Up      0.0.0.0:5000->5000/tcp, 8888/tcp                             
project-3-haoyuzhang89_presto_1      /usr/bin/docker-entrypoint ...   Up      8080/tcp                                                     
project-3-haoyuzhang89_spark_1       docker-entrypoint.sh bash        Up      8888/tcp                                                     
project-3-haoyuzhang89_zookeeper_1   /etc/confluent/docker/run        Up      2181/tcp, 2888/tcp, 32181/tcp, 3888/tcp   

```

```
docker-compose exec kafka \
  kafka-topics \
    --create \
    --topic events \
    --partitions 1 \
    --replication-factor 1 \
    --if-not-exists \
    --zookeeper zookeeper:32181
```

### c. Build API 
**Calling game API from local environment**

```
docker-compose exec mids \
env FLASK_APP=/w205/project-3-haoyuzhang89/game_api.py \
flask run --host 0.0.0.0
```

 ```
 * Serving Flask app "game_api"
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 ```

**Keep Kafka pipeline open for streaming and visualization**

```
docker-compose exec mids \
kafkacat -C -b kafka:29092 -t events -o beginning
```    

### d. Set up Filtering & Streaming for Kafka Data Input

```
docker-compose exec spark \
spark-submit \
/w205/project-3-haoyuzhang89/write_swords_stream.py
```

```
docker-compose exec spark \
spark-submit \
/w205/project-3-haoyuzhang89/write_shields_stream.py
```

```
docker-compose exec spark \
spark-submit \
/w205/project-3-haoyuzhang89/write_guild_stream.py
```

### e. Hive table Creation

```
docker-compose exec cloudera hive
```

```
create external table if not exists default.sword_purchases (
    raw_event string,
    timestamp string,
    Accept string,
    Host string,
    User_Agent string,
    event_type string,
    rarity string,
    player_name string
  )
  stored as parquet
  location '/tmp/sword_purchases'
  tblproperties ("parquet.compress"="SNAPPY");
```

```
OK
Time taken: 5.794 seconds
```

### f. Call Events

#### Single Event Call

```
docker-compose exec mids curl http://localhost:5000/purchase_a_sword/Haoyu
        
docker-compose exec mids curl http://localhost:5000/purchase_a_shield/Hao

docker-compose exec mids curl http://localhost:5000/join_a_guild/SpongeBob/Alan
```

#### Batch Event Call

```
docker-compose exec mids \
ab \
-n 10 \
-H "Host: user1.comcast.com" \
http://localhost:5000/purchase_a_sword/Haoyu
```

```
127.0.0.1 - - [05/Dec/2020 01:12:48] "GET /purchase_a_sword/Haoyu HTTP/1.0" 200 -
127.0.0.1 - - [05/Dec/2020 01:12:48] "GET /purchase_a_sword/Haoyu HTTP/1.0" 200 -
127.0.0.1 - - [05/Dec/2020 01:12:48] "GET /purchase_a_sword/Haoyu HTTP/1.0" 200 -
127.0.0.1 - - [05/Dec/2020 01:12:48] "GET /purchase_a_sword/Haoyu HTTP/1.0" 200 -
127.0.0.1 - - [05/Dec/2020 01:12:49] "GET /purchase_a_sword/Haoyu HTTP/1.0" 200 -
127.0.0.1 - - [05/Dec/2020 01:12:49] "GET /purchase_a_sword/Haoyu HTTP/1.0" 200 -
127.0.0.1 - - [05/Dec/2020 01:12:49] "GET /purchase_a_sword/Haoyu HTTP/1.0" 200 -
127.0.0.1 - - [05/Dec/2020 01:12:49] "GET /purchase_a_sword/Haoyu HTTP/1.0" 200 -
127.0.0.1 - - [05/Dec/2020 01:12:49] "GET /purchase_a_sword/Haoyu HTTP/1.0" 200 -
127.0.0.1 - - [05/Dec/2020 01:12:49] "GET /purchase_a_sword/Haoyu HTTP/1.0" 200 -
```

```
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 5}
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 5}
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 1}
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 6}
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 2}
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 4}
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 5}
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 4}
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 5}
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 4}
```

#### Real-time Event Call

```
while true; do
docker-compose exec mids \
ab -n 10 -H "Host: user1.comcast.com" \
http://localhost:5000/purchase_a_sword/Haoyu 
sleep 10
done
```

```
while true; do
docker-compose exec mids \
ab -n 10 -H "Host: user2.att.com" \
http://localhost:5000/purchase_a_shield/Haolun
sleep 15
done
```

```
while true; do
docker-compose exec mids \
ab -n 10 -H "Host: user3.apple.com" \
http://localhost:5000/purchase_a_sword/Hao
sleep 10
done
```

### g. Presto Querying for Analysis

```
docker-compose exec presto presto --server presto:8080 --catalog hive --schema default
```

```
presto:default> select count(*) from sword_purchases;
```

``` 
 _col0 
-------
   280 
(1 row)

Query 20201205_031806_00002_6wv7i, FINISHED, 1 node
Splits: 35 total, 31 done (88.57%)
0:11 [250 rows, 64.7KB] [22 rows/s, 5.9KB/s]
```

## 5. Example Sanity Check

#### Check if API is deployed successfully

```
* Serving Flask app "game_api"
* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

#### Check if API call is successful

```
127.0.0.1 - - [05/Dec/2020 01:17:56] "GET /purchase_a_shield/Hao HTTP/1.0" 200 -
```

#### Check if API call generate the expected output for the user

```
jupyter@w205-1:~/w205/project-3-haoyuzhang89$ docker-compose exec mids curl http://localhost:5000/join_a_guild/Ferrari/Haoyu 
Congratulation on join this guild

jupyter@w205-1:~/w205/project-3-haoyuzhang89$ docker-compose exec mids curl http://localhost:5000/join_a_guild/Ferrari/Haoyu 
You are already in this guild ! 

jupyter@w205-1:~/w205/project-3-haoyuzhang89$ docker-compose exec mids curl http://localhost:5000/join_a_guild/Ferrari/Alan
You need at least a weapon to join guild
```

#### Check if the expected info is logged into Kafka pipeline

```
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 5}
{"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 5}
```

#### Check if data is properly stored as parquet files in the right directory

```
Found 2 items
drwxr-xr-x   - root supergroup          0 2020-12-05 03:12 /tmp/sword_purchases/_spark_metadata
-rw-r--r--   1 root supergroup        767 2020-12-05 03:12 /tmp/sword_purchases/part-00000-34fa90f5-9fd8-40f8-bbc8-6dc9077cc235-c000.snappy.parquet
```

#### Check hive table is created

```
create external table if not exists default.guild_joins (
    raw_event string,
    timestamp string,
    Accept string,
    Host string,
    User_Agent string,
    event_type string,
    rarity string,
    player_name string,
    guild_name string
  )
  stored as parquet
  location '/tmp/guild_joins'
  tblproperties ("parquet.compress"="SNAPPY");

```


```
OK
Time taken: 1.842 seconds
hive>
```

#### Check if data exists in Presto queries

```
presto:default> select count(*) from shield_purchases;

```

```
 _col0 
-------
  1150 
(1 row)

Query 20201205_033127_00009_6wv7i, FINISHED, 1 node
Splits: 105 total, 100 done (95.24%)
0:06 [1.14K rows, 103KB] [201 rows/s, 18.1KB/s]
```

```
presto:default> select count(*), rarity  from sword_purchases group by rarity;
```

```
_col0 | rarity 
-------+--------
    80 | 4      
    79 | 6      
    79 | 2      
    86 | 1      
    73 | 5      
    73 | 3      
(6 rows)

Query 20201205_032239_00006_6wv7i, FINISHED, 1 node
Splits: 56 total, 55 done (98.21%)
0:05 [470 rows, 122KB] [93 rows/s, 24.2KB/s]
```

```
presto:default> select count(*) as number, rarity  from shield_purchases group by rarity order by number desc;
```

```
number | rarity 
--------+--------
     99 | 1      
     91 | 2      
     89 | 6      
     85 | 4      
     84 | 3      
     82 | 5      
(6 rows)

Query 20201205_033355_00012_6wv7i, FINISHED, 1 node
Splits: 62 total, 55 done (88.71%)
0:03 [490 rows, 127KB] [157 rows/s, 40.8KB/s]
```

```
presto:default> select * from sword_purchases limit 10;
```

```

raw_event                                                           |        timestamp        | acc
------------------------------------------------------------------------------------------------------------------------------+-------------------------+----
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 4} | 2020-12-05 03:22:07.779 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 6} | 2020-12-05 03:22:07.809 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 2} | 2020-12-05 03:22:07.883 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 3} | 2020-12-05 03:22:07.961 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 1} | 2020-12-05 03:22:07.987 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 4} | 2020-12-05 03:22:08.016 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 6} | 2020-12-05 03:22:08.043 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 5} | 2020-12-05 03:22:08.091 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 1} | 2020-12-05 03:22:08.144 | */*
:...skipping...
                                                          raw_event                                                           |        timestamp        | acc
------------------------------------------------------------------------------------------------------------------------------+-------------------------+----
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 4} | 2020-12-05 03:22:07.779 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 6} | 2020-12-05 03:22:07.809 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 2} | 2020-12-05 03:22:07.883 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 3} | 2020-12-05 03:22:07.961 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 1} | 2020-12-05 03:22:07.987 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 4} | 2020-12-05 03:22:08.016 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 6} | 2020-12-05 03:22:08.043 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 5} | 2020-12-05 03:22:08.091 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 1} | 2020-12-05 03:22:08.144 | */*
 {"Host": "user1.comcast.com", "User-Agent": "ApacheBench/2.3", "event_type": "purchase_sword", "Accept": "*/*", "rarity": 5} | 2020-12-05 03:22:08.176 | */*
(10 rows)
~
~
~

Query 20201205_034620_00019_6wv7i, FINISHED, 1 node
Splits: 61 total, 4 done (6.56%)
2:07 [30 rows, 7.8KB] [0 rows/s, 63B/s]
```

## 6. Simple Data Analysis (Presto)

### Check if the data stream is setup correctly in Presto

```
docker-compose exec presto presto --server presto:8080 --catalog hive --schema default
```

```
presto:default> select count(*) from guild_joins;
```

```
_col0 
-------
     1 
(1 row)

Query 20201206_062711_00003_54dp9, FINISHED, 1 node
Splits: 3 total, 1 done (33.33%)
0:01 [0 rows, 0B] [0 rows/s, 0B/s]
```

### Check if the raw data field are matched correctly based on our created schema in Hive

```
presto:default> select * from guild_joins;
```

```
                                                                              raw_event                 
--------------------------------------------------------------------------------------------------------
 {"player_name": "Alan", "event_type": "join_a_guild", "guild_name": "Ferrari", "Accept": "*/*", "User-A
(1 row)
(END)
```

### Check weapon rarity distribution

```
presto:default> select count(*), rarity  from sword_purchases group by rarity;
```

```
_col0 | rarity 
-------+--------
    80 | 4      
    79 | 6      
    79 | 2      
    86 | 1      
    73 | 5      
    73 | 3      
(6 rows)

Query 20201205_032239_00006_6wv7i, FINISHED, 1 node
Splits: 56 total, 55 done (98.21%)
0:05 [470 rows, 122KB] [93 rows/s, 24.2KB/s]
```

```
presto:default> select count(*) as number, rarity  from shield_purchases group by rarity order by number desc;
```

``` 
 number | rarity 
--------+--------
     99 | 1      
     91 | 2      
     89 | 6      
     85 | 4      
     84 | 3      
     82 | 5      
(6 rows)

Query 20201205_033355_00012_6wv7i, FINISHED, 1 node
Splits: 62 total, 55 done (88.71%)
0:03 [490 rows, 127KB] [157 rows/s, 40.8KB/s]
```

### See who is in which Guild ( with simple sample output)

```
presto:default> select guild_name, player_name from guild_joins;
```

```
 guild_name | player_name 
------------+-------------
 Benz       | Hao         
(1 row)
```

### See what are the team size for the existing guilds

```
presto:default> select guild_name, count(*) as team_size from guild_joins group by guild_name;
```

``` 
 guild_name | team_size 
------------+-----------
 Benz       |         1 
 Mclaren    |         4 
 Williams   |         3 
 Ferrari    |         4 
(4 rows)

Query 20201206_070412_00008_wa84i, FINISHED, 1 node
Splits: 16 total, 9 done (56.25%)
0:02 [8 rows, 22.9KB] [4 rows/s, 12.8KB/s]
```

### Check who are the members in guild "Williams"

```
presto:default> select player_name, guild_name from guild_joins where guild_name='Williams';
```

```
player_name | guild_name 
-------------+------------
 Joe         | Williams   
 Jon         | Williams   
 Gay         | Williams  

```

### Check who are the players with player name that contains a certain letter and which guilds are they in

```
presto:default> select player_name, guild_name from guild_joins where player_name like '%H%';
```

```
player_name | guild_name 
-------------+------------
 Hao         | Benz       
 Hao         | Ferrari    
(2 rows)

Query 20201206_071257_00017_wa84i, FINISHED, 1 node
Splits: 15 total, 12 done (80.00%)
0:01 [10 rows, 28.6KB] [7 rows/s, 22.9KB/s]
```

```
presto:default> select player_name, guild_name from guild_joins where player_name like '%J%';
```

``` 
 player_name | guild_name 
-------------+------------
 Joe         | Mclaren    
 Joe         | Williams   
 Jon         | Mclaren    
 Jon         | Williams   
 Jon         | Ferrari    
(5 rows)

Query 20201206_071338_00018_wa84i, FINISHED, 1 node
Splits: 15 total, 9 done (60.00%)
0:01 [9 rows, 25.7KB] [9 rows/s, 28.6KB/s]

```


```python

```
