from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests
import feedparser
import spacy
from collections import Counter
import tweepy
from dotenv import load_dotenv
import os

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

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
    Fetch trending posts from multiple subreddits on Reddit.
    """
    subreddits = ["popular", "worldnews", "technology", "sports", "entertainment"]
    trends = []

    headers = {"User-Agent": "TrendingApp"}
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]  # Common image extensions
    
    for subreddit in subreddits:
        url = f"https://www.reddit.com/r/{subreddit}.json?limit=100"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            for post in data['data']['children']:
                title = post['data'].get('title', "")
                main_idea = extract_main_idea(title)

                # Get external URL or fallback to Reddit permalink
                external_url = post['data'].get('url', "")
                permalink = f"https://www.reddit.com{post['data'].get('permalink', '')}"
                is_self_post = post['data'].get('is_self', False)

                # Check if the URL is an image
                if any(external_url.endswith(ext) for ext in image_extensions) or is_self_post:
                    full_url = permalink  # Use Reddit post URL
                else:
                    full_url = external_url  # Use external URL

                trends.append({
                    "idea": main_idea,
                    "title": title,
                    "url": full_url,
                    "source": f"Reddit - r/{subreddit}"
                })

            print(f"Fetched {len(data['data']['children'])} posts from r/{subreddit}.")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from r/{subreddit}: {e}")
            continue

    print(f"Total fetched posts from Reddit: {len(trends)}")
    return trends




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

def fetch_twitter_trends():
    """
    Fetch trending tweets using Twitter v2 API Recent Search, limiting to 20 requests.
    """
    # Twitter API Bearer Token
    BEARER_TOKEN = TWITTER_BEARER_TOKEN

    # Initialize Tweepy Client
    client = tweepy.Client(bearer_token=BEARER_TOKEN)

    # Keywords for fetching popular tweets
    topics = ["world news"]
    trends = []
    max_requests = 20  # Limit total requests
    request_count = 0  # Track requests made

    for topic in topics:
        if request_count >= max_requests:  # Stop if max requests reached
            break

        try:
            # Fetch recent tweets for the topic
            response = client.search_recent_tweets(
                query=topic,
                max_results=20,  # Limit to 20 tweets per request
                tweet_fields=["created_at", "text", "public_metrics"]
            )
            request_count += 1  # Increment request count

            if response.data:
                for tweet in response.data:
                    trends.append({
                        "idea": extract_main_idea(tweet.text),  # Extract main idea from tweet
                        "title": tweet.text,
                        "url": f"https://twitter.com/i/web/status/{tweet.id}",
                        "source": "Twitter"
                    })

        except tweepy.errors.TweepyException as e:
            print(f"Error fetching tweets for topic '{topic}': {e}")
            continue

    print(f"Fetched {len(trends)} trends from Twitter after {request_count} requests.")
    return trends


def fetch_newsapi_trends():
    """
    Fetch news articles from multiple categories using NewsAPI.
    """
    url = "https://newsapi.org/v2/top-headlines"
    categories = ["general","science", "business", "technology", "entertainment", "sports", "health"]
    trends = []

    for category in categories:
        params = {
            "language": "en",        # Fetch English articles
            "category": category,    # Use category parameter for filtering
            "pageSize": 35,          # Limit to 35 articles per category
            "apiKey": NEWSAPI_KEY    # Your NewsAPI key from .env
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()

            for article in data.get("articles", []):
                trends.append({
                    "idea": extract_main_idea(article["title"]),
                    "title": article["title"],
                    "url": article["url"],
                    "source": f"NewsAPI - {category.capitalize()}"
                })

            print(f"Fetched {len(data.get('articles', []))} articles from NewsAPI ({category}).")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from NewsAPI ({category}): {e}")
            continue

    print(f"Total fetched articles from NewsAPI: {len(trends)}")
    return trends



def fetch_combined_trends():
    """
    Combine trends from Reddit, Google News, Twitter, and NewsAPI, aggregate counts, and save to MongoDB.
    """
    reddit_trends = fetch_reddit_trends()
    google_news_trends = fetch_google_news()
    twitter_trends = fetch_twitter_trends()
    newsapi_trends = fetch_newsapi_trends()

    print(f"Fetched {len(reddit_trends)} total posts from Reddit")
    print(f"Fetched {len(google_news_trends)} total posts from Google News")
    print(f"Fetched {len(twitter_trends)} trends from Twitter")
    print(f"Fetched {len(newsapi_trends)} articles from NewsAPI")

    aggregated_data = {}

    def aggregate_trends(trends):
        for trend in trends:
            idea = trend["idea"]
            if idea not in aggregated_data:
                aggregated_data[idea] = {"count": 0, "titles": []}

            is_duplicate = any(
                t["title"] == trend["title"] and t["url"] == trend["url"]
                for t in aggregated_data[idea]["titles"]
            )
            if not is_duplicate:
                aggregated_data[idea]["count"] += 1
                aggregated_data[idea]["titles"].append({
                    "title": trend["title"],
                    "url": trend["url"],
                    "source": trend["source"]
                })

    aggregate_trends(reddit_trends)
    aggregate_trends(google_news_trends)
    aggregate_trends(twitter_trends)
    aggregate_trends(newsapi_trends)

    total_posts = len(reddit_trends) + len(google_news_trends) + len(twitter_trends) + len(newsapi_trends)
    print(f"Fetched {total_posts} combined total posts")

    combined_trends = [
        {"idea": idea, "count": data["count"], "titles": data["titles"]}
        for idea, data in aggregated_data.items()
    ]

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
    Retrieve all trends from MongoDB, excluding those with a count of 1, sorted by count in descending order.
    """
    trends = list(
        trends_collection.find(
            {"count": {"$gt": 1}},  # Filter out ideas with count <= 1
            {"_id": 0}             # Exclude MongoDB's internal `_id` field
        ).sort("count", -1)         # Sort by count in descending order
    )
    return jsonify(trends)

if __name__ == "__main__":
    fetch_combined_trends()  # Fetch and combine trends at startup
    app.run(debug=True)
