import requests

url = "https://www.reddit.com/r/popular.json"
headers = {"User-Agent": "TrendingApp"}

response = requests.get(url, headers=headers)
print(response.status_code)
print(response.json())