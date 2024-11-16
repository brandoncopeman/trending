from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests
import spacy
from collections import Counter

# Load spaCy's English NLP model
nlp = spacy.load("en_core_web_sm")

def extract_main_idea(title):
    """
    Extract main ideas (proper nouns and key phrases) from a title.
    """
    doc = nlp(title)
    main_ideas = []

    for token in doc:
        # Proper Nouns (e.g., Mike Tyson, Donald Trump)
        if token.pos_ == "PROPN":
            main_ideas.append(token.text)
        # Combine nouns and adjectives for key ideas (e.g., American Economy)
        elif token.pos_ == "NOUN" or token.pos_ == "ADJ":
            phrase = " ".join([w.text for w in token.subtree if w.pos_ in {"NOUN", "ADJ"}])
            if phrase not in main_ideas:
                main_ideas.append(phrase)

    return main_ideas

def fetch_reddit_trends():
    url = "https://www.reddit.com/r/popular.json"
    headers = {"User-Agent": "TrendingApp"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ensure the request was successful
        data = response.json()
        
        # Extract and process main ideas from titles
        main_idea_counter = Counter()
        for post in data['data']['children']:
            title = post['data'].get('title', "")
            main_ideas = extract_main_idea(title)
            main_idea_counter.update(main_ideas)

        # Store ranked main ideas in MongoDB
        trends_collection.delete_many({})  # Clear the collection
        trends = [{"idea": idea, "count": count} for idea, count in main_idea_counter.most_common()]
        trends_collection.insert_many(trends)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Reddit: {e}")
    


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
