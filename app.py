from flask import Flask, render_template, request
import pandas as pd
import re
from urllib.parse import urlparse
import joblib

# Load RandomForest model and label map
model = joblib.load("URL_Flask/randomforest.pkl")
label_map = joblib.load("URL_Flask/label_map.pkl")

app = Flask(__name__)

# Feature extraction function
def extract_features(url):
    parsed = urlparse(url)
    hostname = parsed.hostname if parsed.hostname else ""
    return {
        'url_length': len(url),
        'hostname_length': len(hostname),
        'count_dots': url.count('.'),
        'count_hyphens': url.count('-'),
        'count_at': url.count('@'),
        'count_question': url.count('?'),
        'count_percent': url.count('%'),
        'count_equals': url.count('='),
        'count_http': url.count('http'),
        'count_https': url.count('https'),
        'has_ip': 1 if re.match(r'^\d{1,3}(\.\d{1,3}){3}', hostname) else 0,
        'is_https': 1 if parsed.scheme == 'https' else 0
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/check", methods=["POST"])
def check_url():
    url = request.form.get("url")
    if url.isdigit():
        return render_template("index.html", result="Invalid Input")

    whitelist = [
        "google.com", "bing.com", "yahoo.com", "duckduckgo.com",
        "microsoft.com", "apple.com", "amazon.com", "ibm.com", "oracle.com",
        "openai.com", "chat.openai.com", "slack.com", "zoom.us", "notion.so",
        "dropbox.com", "adobe.com",
        "facebook.com", "twitter.com", "x.com", "linkedin.com",
        "instagram.com", "tiktok.com", "snapchat.com", "pinterest.com",
        "reddit.com", "discord.com",
        "youtube.com", "netflix.com", "twitch.tv", "spotify.com",
        "hulu.com", "disneyplus.com", "primevideo.com",
        "wikipedia.org", "stackoverflow.com", "khanacademy.org",
        "coursera.org", "edx.org",
        "github.com", "gitlab.com", "bitbucket.org", "heroku.com",
        "vercel.com", "netlify.app",
        "paypal.com", "stripe.com", "visa.com", "mastercard.com",
        "bbc.com", "cnn.com", "nytimes.com", "theguardian.com", "forbes.com",
        "ebay.com", "etsy.com", "aliexpress.com", "walmart.com", "target.com"
    ]

    if any(domain in url for domain in whitelist):
        result = "benign"
    else:
        feat = pd.DataFrame([extract_features(url)])
        pred = model.predict(feat)[0]
        result = label_map[pred]
        
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)

