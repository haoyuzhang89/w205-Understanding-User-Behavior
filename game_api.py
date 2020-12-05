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
    curs = conn.cursor()
    query = "insert Into player_status(player_name, Weapon_type, Rarity) VALUES('" + name +"', '" + weapon +"', "+ str(rarity) + ")"
    results = curs.execute(query)
    conn.commit()
    curs.close()
    conn.close()


@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('events', default_event)
    return "This is the default response!\n"


@app.route("/purchase_a_sword/<player_name>")
def purchase_a_sword(player_name):
    rarity= random.choice([1,2,3,4,5,6])
    commit_record(str(player_name), 'sword',rarity )
    purchase_sword_event = {'event_type': 'purchase_sword','rarity':rarity}
    log_to_kafka('events', purchase_sword_event)
    return "Sword Purchased! You now have a sword with rarity " + str(rarity) + " \n"

@app.route("/purchase_a_shield/<player_name>")
def purchase_a_shield(player_name):
    rarity= random.choice([1,2,3,4,5,6])
    commit_record(str(player_name), 'shield',rarity )
    #rarity= np.random.choice([1,2,3,4,5,6], p=[0.25, 0.25, 0.15, 0.15, 0.15, 0.05])
    purchase_shield_event = {'event_type': 'purchase_shield','rarity':rarity}
    log_to_kafka('events', purchase_shield_event)
    return "Shield Purchased! You now have a shield with rarity " + str(rarity) + " \n"


# @app.route("/purchase_a_shield")
# def purchase_a_shield():
#     rarity= random.choice([1,2,3,4,5,6])
#     commit_record(str(player_name), 'shield',rarity )
#     #rarity= np.random.choice([1,2,3,4,5,6], p=[0.25, 0.25, 0.15, 0.15, 0.15, 0.05])
#     purchase_shield_event = {'event_type': 'purchase_shield','rarity':rarity}
#     log_to_kafka('events', purchase_shield_event)
#     return "Shield Purchased! You now have a shield with rarity " + str(rarity) + " \n"