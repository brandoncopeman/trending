from celery import Celery
from app import fetch_reddit_trends

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def fetch_trends_task():
    fetch_reddit_trends()
