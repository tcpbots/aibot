# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Credentials
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "17760082"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "c3fc3cd44886967cf3c0e8585b5cad1c")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7213949258:AAEY9mFQlooQpAy9ZsA4JLchiR82DrfMJ8E")

# Force Subscription Settings
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "@tcp_bots")
FORCE_SUB_CHANNEL_ID = int(os.getenv("FORCE_SUB_CHANNEL_ID", "-1002398821254"))

# Admin and Developer Settings
DEVELOPER_USERNAME = os.getenv("DEVELOPER_USERNAME", "@mr_provider")
OWNER_ID = int(os.getenv("OWNER_ID", "6116993643"))
ADMIN_IDS = {6116993643, 1809710185}  # Owner and other admin

# Hypothetical Grok AI API (replace with actual free AI API endpoint and key)
GROK_API_URL = os.getenv("GROK_API_URL", "https://api.x.ai/grok")
GROK_API_KEY = os.getenv("GROK_API_KEY", "xai-lMFHXsUhlvwmfyAGvXc2imtoMqOEGIwpstb1qv1go0KNcYAOZxdoJS0IICAigOZaPYsDxA5vsY8coqNO")

# News API for trending news (free tier available at newsapi.org)
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "6e44fac15a2b4ba9918494f94fd8f255")

# Image Generation API (placeholder; replace with free API like Stable Diffusion if available)
IMAGE_API_URL = os.getenv("IMAGE_API_URL", "https://api.stablediffusion.example/generate")
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY", "55DZTnjpITuBhOHNKraeOoIMQkqdk3aI878T6laJNeIGBl0oPKL5eJPBetm7")

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://shivay:86WGXrEf@jnEf3z@cluster0.flsrmr2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
MONGO_DB_NAME = "telegram_bot"
