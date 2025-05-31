# main.py
import config
from telegram.ext import Application
import bot
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    bot.setup_handlers(application)
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=["message", "inline_query", "callback_query"])

if __name__ == "__main__":
    main()
