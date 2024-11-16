from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests


def fetch_reddit_trends():
    url = "https://www.reddit.com/r/popular.json"
    headers = {"User-Agent": "TrendingApp"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ensure the request was successful
        data = response.json()
        
        # Extract only titles from posts
        trends = [{"title": post['data']['title']} for post in data['data']['children'] if 'title' in post['data']]
        # Clear the collection
        trends_collection.delete_many({})  
        #return trends
        trends_collection.insert_many(trends)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Reddit: {e}")
        return []
    


app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['trending_db']
trends_collection = db['trends']

@app.route('/trends', methods=['GET'])
def get_trends():
        # Retrieve all trends from MongoDB
    trends = list(trends_collection.find({}, {"_id": 0}))
    return jsonify(trends)

if __name__ == "__main__":
    trends = fetch_reddit_trends()
    app.run(debug=True)
