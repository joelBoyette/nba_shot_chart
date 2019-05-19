from flask import Flask, render_template, redirect,jsonify
from flask_pymongo import PyMongo
import pandas as pd
import json
from bson import json_util
from bson.json_util import dumps
import pymongo

# create instance of Flask app
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/nba_shots"

mongo = PyMongo(app)

db = mongo.db
collection = db.shot_data

#create route that renders index.html.
@app.route("/")
def home():
    
    cursor = list(collection.find())

    # return template 
    return render_template("index.html",game_shots=cursor)

@app.route("/shots")
def game_shots():

    #connect to mongo db
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)

    #set db variable to nba_shots db
    db = client.nba_shots

    #set collection variable to shot_data collection
    collection = db.shot_data
    
    #convert collection into a dictionary for the json dumps function
    shot_dict = list(collection.find())

    #return json data when the route is called
    return json.dumps(shot_dict, default=json_util.default)
    

if __name__ == "__main__":
    app.run(debug=True)