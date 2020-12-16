import json
import random
from kafka import KafkaProducer
from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')


def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())

def commit_record(name,weapon,rarity):
    dbdir = "/w205/project-3-haoyuzhang89/"
    conn = sqlite3.connect(os.path.join(dbdir,'player_status.db'))
    cursor = conn.cursor()
    query = "insert Into player_status(player_name, Weapon_type, Rarity) VALUES('" + name +"', '" + weapon +"', "+ str(rarity) + ")"
    results = cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    
def commit_guild_record(g_name,p_name):
    dbdir = "/w205/project-3-haoyuzhang89/"
    conn = sqlite3.connect(os.path.join(dbdir,'player_status.db'))
    cursor = conn.cursor()
    query = "insert Into guild(guild_name,player_name) VALUES('" + g_name +"', '" + p_name +"')"
    results = cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    
def if_in_guild(guild_name, player_name):
    dbdir = "/w205/project-3-haoyuzhang89/"
    conn = sqlite3.connect(os.path.join(dbdir,'player_status.db'))
    cursor = conn.cursor()
    g_name= '"' + guild_name + '"'
    p_name = '"' + player_name + '"'
    query = "select * from guild where guild_name =" + \
         g_name + " and player_name = " + p_name
    
    results = cursor.execute(query).fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    if len(results) > 0:
        return True
    else:
        return False
    

def fetch_player_best_weapon(player_name):
    p_name = '"' + player_name + '"'
    dbdir = "/w205/project-3-haoyuzhang89/"
    conn = sqlite3.connect(os.path.join(dbdir,'player_status.db'))

    cursor = conn.cursor()

    query = "select player_name, max(Rarity) from player_status where player_name=" + \
        p_name + " group by player_name"

    results = cursor.execute(query).fetchall()

    conn.commit()
    cursor.close()
    conn.close()
    
    return results    
    
    

@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('events', default_event)
    return "This is the default response!\n"


@app.route("/purchase_a_sword/<player_name>")
def purchase_a_sword(player_name):
    rarity= random.choice([1,2,3,4,5,6])
    commit_record(str(player_name), 'sword',rarity)
    purchase_sword_event = {'event_type': 'purchase_sword','rarity':rarity,'player_name':player_name}
    log_to_kafka('events', purchase_sword_event)
    return "Sword Purchased! You now have a sword with rarity " + str(rarity) + " \n"

@app.route("/purchase_a_shield/<player_name>")
def purchase_a_shield(player_name):
    rarity= random.choice([1,2,3,4,5,6])
    commit_record(str(player_name), 'shield',rarity )
    #rarity= np.random.choice([1,2,3,4,5,6], p=[0.25, 0.25, 0.15, 0.15, 0.15, 0.05])
    purchase_shield_event = {'event_type': 'purchase_shield','rarity':rarity, 'player_name':player_name}
    log_to_kafka('events', purchase_shield_event)
    return "Shield Purchased! You now have a shield with rarity " + str(rarity) + " \n"


@app.route("/join_a_guild/<guild_name>/<player_name>")
def join_a_guild(guild_name,player_name):
    if if_in_guild(guild_name, player_name):
        return "You are already in this guild ! \n"
    elif len(fetch_player_best_weapon(player_name)) ==0:
        return "You need at least a weapon to join guild\n"
    else:
        best_weapon = fetch_player_best_weapon(player_name)
        commit_guild_record(guild_name,player_name)
        guild_record = {'event_type': 'join_a_guild', 'guild_name':guild_name, 'rarity': best_weapon[0][1], 'player_name':player_name}
        log_to_kafka('events', guild_record)
        return "Congratulation on join this guild\n"
    
        
