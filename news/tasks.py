import os
import requests
import random
import google.generativeai as genai  # Google Gemini AI
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from .models import NewsArticle

# Load API keys from .env file (safer than hardcoding)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")


# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Trusted news sources
TRUSTED_SOURCES = [
    "bbc-news", "cnn", "techcrunch", "the-verge", "ndtv", "reuters"
]

def generate_summary(title, description):
    """Generate a professional and neutral summary using Google Gemini AI."""
    if not GEMINI_API_KEY:
        return "Summary unavailable (API key missing)."

    prompt = f"""
    Summarize this news article in 2-3 sentences for public awareness.
    Please ensure the summary is professional, neutral, and fact-based.

    Title: {title}
    Description: {description}

    Summary:
    """
    
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        
        if hasattr(response, "candidates") and response.candidates:
            for candidate in response.candidates:
                if candidate.finish_reason == 3:
                    print("⚠ Gemini blocked this content due to moderation rules.")
                    return "Summary unavailable due to content moderation."
        
        return response.text.strip() if response.text else "No summary available."
    except Exception as e:
        print(f"⚠ ERROR generating summary: {e}")
        return "No summary available."

def get_image(query):
    """Fetch a random image from Unsplash based on the query."""
    if not UNSPLASH_ACCESS_KEY:
        return "https://via.placeholder.com/600x400"
    
    url = f"https://api.unsplash.com/search/photos?query={query}&client_id={UNSPLASH_ACCESS_KEY}"
    try:
        response = requests.get(url).json()
        if response.get("results"):
            return random.choice(response["results"])['urls']['regular']
    except Exception as e:
        print(f"⚠ ERROR fetching image: {e}")
    
    return "https://via.placeholder.com/600x400"

def fetch_trending_news():
    """Fetch general trending news from trusted sources and save the latest articles."""
    if not NEWS_API_KEY:
        print("⚠ ERROR: NewsAPI Key is missing!")
        return
    
    url = f"https://newsapi.org/v2/top-headlines?sources={','.join(TRUSTED_SOURCES)}&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url).json()
        
        if "articles" in response:
            for article in response["articles"][:10]:  # Get top 10 general news articles
                title = article.get("title", "No Title Available")
                description = article.get("description", "No Description Available")
                news_url = article.get("url", "#")
                image_url = article.get("urlToImage") or get_image(title)
                
                # Generate AI summary using Gemini AI
                summary = generate_summary(title, description)
                
                # Ensure uniqueness: Save only new articles
                if not NewsArticle.objects.filter(title=title).exists():
                    NewsArticle.objects.create(
                        title=title,
                        description=summary,
                        url=news_url,
                        image_url=image_url
                    )
        
        # Keep only the latest 50 articles, delete older ones
        latest_articles = NewsArticle.objects.order_by('-published_at')[:50]
        NewsArticle.objects.exclude(id__in=[article.id for article in latest_articles]).delete()
        
        print("✅ General News Updated Successfully!")
    except Exception as e:
        print(f"⚠ ERROR fetching news: {e}")
