# utils.py
import requests
import config
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from db import db

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def get_grok_response(message):
    try:
        headers = {
            "Authorization": f"Bearer {config.GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "grok-3",  # Use grok-3 as per initial instructions
            "messages": [
                {"role": "system", "content": "You are a PhD-level mathematician."},
                {"role": "user", "content": message}
            ]
        }
        response = requests.post(config.GROK_API_URL, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        # Assuming xAI API response follows a similar structure to OpenAI
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"xAI API error: {e}")
        return "Error connecting to AI service."

def get_trending_news(country="us", category="general"):
    try:
        params = {"country": country, "category": category, "apiKey": config.NEWS_API_KEY}
        response = requests.get(config.NEWS_API_URL, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        if not articles:
            return "No trending news available."
        news_list = [f"{i+1}. {article['title']} - {article['source']['name']}\n{article['url']}" for i, article in enumerate(articles[:5])]
        return "\n\n".join(news_list)
    except Exception as e:
        logger.error(f"News API error: {e}")
        return "Error fetching news."

def generate_image(prompt):
    try:
        headers = {"Authorization": f"Bearer {config.IMAGE_API_KEY}"}
        data = {"prompt": prompt}
        response = requests.post(config.IMAGE_API_URL, json=data, headers=headers)
        response.raise_for_status()
        return response.json().get("image_url", "Image generation failed.")
    except Exception as e:
        logger.error(f"Image API error: {e}")
        return "Error generating image."

def is_admin(user_id):
    user = db.get_user(user_id)
    return user and user.get("is_admin", False)

def is_banned(user_id):
    user = db.get_user(user_id)
    return user and user.get("is_banned", False)

async def check_subscription(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    if update.effective_chat.type == "private" or is_admin(user_id):
        return True
    try:
        member = await context.bot.get_chat_member(config.FORCE_SUB_CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        else:
            keyboard = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{config.FORCE_SUB_CHANNEL[1:]}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Please join {config.FORCE_SUB_CHANNEL} to use this bot.",
                reply_markup=reply_markup
            )
            return False
    except Exception as e:
        logger.error(f"Error checking subscription for user {user_id}: {e}")
        return False

async def broadcast_message(context, message):
    users = db.get_all_users()
    success_count = 0
    for user in users:
        user_id = user["user_id"]
        if not user.get("is_banned", False):
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
                success_count += 1
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
    return success_count
