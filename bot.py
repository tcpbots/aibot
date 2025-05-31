# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, ContextTypes
import config
from db import db
import utils
import logging
import os
import sys

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.id in config.ADMIN_IDS)
    if utils.is_banned(user.id):
        await update.message.reply_text("You are banned from using this bot.")
        return
    if not await utils.check_subscription(update, context):
        return
    keyboard = [
        [InlineKeyboardButton("Get News", callback_data='news')],
        [InlineKeyboardButton("Generate Image", callback_data='image')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Welcome, {user.first_name}! I'm an AI-powered bot by {config.DEVELOPER_USERNAME}. "
        f"Use /news for trending news, /image to generate an image, or send a message to chat.",
        reply_markup=reply_markup
    )

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if utils.is_banned(update.effective_user.id):
        await update.message.reply_text("You are banned from using this bot.")
        return
    if not await utils.check_subscription(update, context):
        return
    news = utils.get_trending_news()
    await update.message.reply_text(news)

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if utils.is_banned(update.effective_user.id):
        await update.message.reply_text("You are banned from using this bot.")
        return
    if not await utils.check_subscription(update, context):
        return
    await update.message.reply_text("Please provide a description for the image you want to generate.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not utils.is_admin(update.effective_user.id):
        await update.message.reply_text("Admin access required.")
        return
    if not context.args:
        await update.message.reply_text("Please provide a message to broadcast. Usage: /broadcast <message>")
        return
    message = " ".join(context.args)
    success_count = await utils.broadcast_message(context, message)
    await update.message.reply_text(f"Broadcast sent to {success_count} users.")

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not utils.is_admin(update.effective_user.id):
        await update.message.reply_text("Admin access required.")
        return
    await update.message.reply_text("Restarting bot...")
    # Simulate restart by exiting (hosting platform like Render/Heroku will restart)
    os._exit(0)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not utils.is_admin(update.effective_user.id):
        await update.message.reply_text("Admin access required.")
        return
    user_count = db.get_user_count()
    message_count = db.get_message_count()
    await update.message.reply_text(f"Bot Stats:\nTotal Users: {user_count}\nTotal Messages: {message_count}")

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not utils.is_admin(update.effective_user.id):
        await update.message.reply_text("Admin access required.")
        return
    users = db.get_all_users()
    if not users:
        await update.message.reply_text("No users found.")
        return
    user_list = [f"ID: {user['user_id']}, Username: @{user['username'] or 'N/A'}, Banned: {user.get('is_banned', False)}" for user in users]
    await update.message.reply_text("\n".join(user_list))

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not utils.is_admin(update.effective_user.id):
        await update.message.reply_text("Admin access required.")
        return
    if not context.args:
        await update.message.reply_text("Please provide a user ID to ban. Usage: /ban <user_id>")
        return
    try:
        user_id = int(context.args[0])
        if user_id in config.ADMIN_IDS:
            await update.message.reply_text("Cannot ban an admin.")
            return
        db.ban_user(user_id)
        await update.message.reply_text(f"User {user_id} has been banned.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Usage: /ban <user_id>")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not utils.is_admin(update.effective_user.id):
        await update.message.reply_text("Admin access required.")
        return
    if not context.args:
        await update.message.reply_text("Please provide a user ID to unban. Usage: /unban <user_id>")
        return
    try:
        user_id = int(context.args[0])
        db.unban_user(user_id)
        await update.message.reply_text(f"User {user_id} has been unbanned.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Usage: /unban <user_id>")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if utils.is_banned(user.id):
        await update.message.reply_text("You are banned from using this bot.")
        return
    if not await utils.check_subscription(update, context):
        return
    message = update.message.text
    chat_id = update.effective_chat.id

    if message.startswith('/'):
        return
    if context.user_data.get('awaiting_image_prompt'):
        image_url = utils.generate_image(message)
        db.log_message(user.id, chat_id, message, image_url)
        context.user_data['awaiting_image_prompt'] = False
        await update.message.reply_text(image_url)
    else:
        response = utils.get_grok_response(message)
        db.log_message(user.id, chat_id, message, response)
        await update.message.reply_text(response)

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.inline_query.from_user.id
    if utils.is_banned(user_id):
        return
    query = update.inline_query.query
    if not query:
        return
    response = utils.get_grok_response(query)
    results = [
        {
            'type': 'Article',
            'id': '1',
            'title': 'AI Response',
            'input_message_content': {'message_text': response},
            'description': response[:100],
        }
    ]
    await update.inline_query.answer(results)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if utils.is_banned(update.effective_user.id):
        await query.message.reply_text("You are banned from using this bot.")
        return
    if not await utils.check_subscription(update, context):
        return
    if query.data == 'news':
        news = utils.get_trending_news()
        await query.message.reply_text(news)
    elif query.data == 'image':
        context.user_data['awaiting_image_prompt'] = True
        await query.message.reply_text("Please provide a description for the image you want to generate.")

def setup_handlers(application: Application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CommandHandler("image", image))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("users", users))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(InlineQueryHandler(inline_query))
