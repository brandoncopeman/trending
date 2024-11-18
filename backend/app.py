from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests
import feedparser
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
    """
    Fetch trending posts from Reddit.
    """
    url = "https://www.reddit.com/r/popular.json?limit=100"
    headers = {"User-Agent": "TrendingApp"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        trends = []
        for post in data['data']['children']:
            title = post['data'].get('title', "")
            main_idea = extract_main_idea(title)
            permalink = post['data'].get('permalink', "")
            full_url = f"https://www.reddit.com{permalink}" if permalink else ""

            trends.append({
                "idea": main_idea,
                "title": title,
                "url": full_url,
                "source": "Reddit"
            })

        return trends

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Reddit: {e}")
        return []

def fetch_google_news():
    """
    Fetch news articles from multiple Google News RSS feeds.
    """
    # Define RSS feeds with categories
    feeds = {
        "Top Stories": "https://news.google.com/rss",
        "World": "https://news.google.com/rss/headlines/section/topic/WORLD",
        "Technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY",
        "Entertainment": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT",
        "Sports": "https://news.google.com/rss/headlines/section/topic/SPORTS"
    }

    trends = []

    # Fetch and parse each feed
    for category, url in feeds.items():
        feed = feedparser.parse(url)
        print(f"Fetched {len(feed.entries)} posts from {category} category.")  # Log the count

        for entry in feed.entries:
            trends.append({
                "idea": extract_main_idea(entry.title),
                "title": entry.title,
                "url": entry.link,
                "source": f"Google News - {category}"
            })

    return trends



def fetch_combined_trends():
    """
    Combine trends from Reddit and Google News, aggregate counts, and save to MongoDB.
    """
    # Fetch data from both sources
    reddit_trends = fetch_reddit_trends()
    google_news_trends = fetch_google_news()

    # Centralized dictionary for aggregation
    aggregated_data = {}

    def aggregate_trends(trends):
        for trend in trends:
            idea = trend["idea"]
            if idea not in aggregated_data:
                aggregated_data[idea] = {"count": 0, "titles": []}

            # Increment the count and add the title + URL
            aggregated_data[idea]["count"] += 1
            aggregated_data[idea]["titles"].append({
                "title": trend["title"],
                "url": trend["url"],
                "source": trend["source"]
            })

    # Aggregate trends from both sources
    aggregate_trends(reddit_trends)
    aggregate_trends(google_news_trends)

    # Convert aggregated data to a list for MongoDB
    combined_trends = [
        {"idea": idea, "count": data["count"], "titles": data["titles"]}
        for idea, data in aggregated_data.items()
    ]

    # Clear MongoDB collection and insert combined trends
    trends_collection.delete_many({})
    trends_collection.insert_many(combined_trends)

    return combined_trends

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['trending_db']
trends_collection = db['trends']

@app.route('/trends', methods=['GET'])
def get_trends():
    """
    Retrieve all trends from MongoDB, sorted by count in descending order.
    """
    trends = list(trends_collection.find({}, {"_id": 0}).sort("count", -1))
    return jsonify(trends)

if __name__ == "__main__":
    fetch_combined_trends()  # Fetch and combine trends at startup
    app.run(debug=True)
