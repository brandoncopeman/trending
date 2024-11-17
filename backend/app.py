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
    Extract the main idea (single phrase) from a title using spaCy.
    """
    doc = nlp(title)

    # Collect proper noun phrases first (e.g., "Jake Paul")
    proper_noun_phrases = []
    for ent in doc.ents:
        if ent.label_ in {"PERSON", "ORG", "GPE"}:  # Focus on people, organizations, places
            proper_noun_phrases.append(ent.text)

    if proper_noun_phrases:
        return proper_noun_phrases[0]  # Use the first proper noun phrase

    # Use significant noun chunks, excluding small/unimportant phrases
    noun_chunks = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1]
    if noun_chunks:
        return noun_chunks[0]

    # Fallback: Return the first noun or the title itself
    for token in doc:
        if token.pos_ == "NOUN":
            return token.text

    return title


def fetch_reddit_trends():
    url = "https://www.reddit.com/r/popular.json?limit=100"
    headers = {"User-Agent": "TrendingApp"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Count occurrences and group titles for each main idea
        trends_data = {}
        for post in data['data']['children']:
            title = post['data'].get('title', "")
            main_idea = extract_main_idea(title)
            permalink = post['data'].get('permalink', "")
            full_url = f"https://www.reddit.com{permalink}" if permalink else ""

            # Initialize the main idea in trends_data if it doesn't exist
            if main_idea not in trends_data:
                trends_data[main_idea] = {"count": 0, "titles": []}
            
            # Increment the count and append the title with its URL
            trends_data[main_idea]["count"] += 1
            trends_data[main_idea]["titles"].append({"title": title, "url": full_url})

        # Prepare ranked trends with associated titles
        ranked_trends = [
            {"idea": idea, "count": data["count"], "titles": data["titles"]}
            for idea, data in trends_data.items()
        ]

        # Clear the collection and insert ranked trends
        trends_collection.delete_many({})
        trends_collection.insert_many(ranked_trends)

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
    trends = list(trends_collection.find({}, {"_id": 0}).sort("count", -1))
    return jsonify(trends)

if __name__ == "__main__":
    trends = fetch_reddit_trends()
    app.run(debug=True)
