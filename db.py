# db.py
from pymongo import MongoClient
import config
import logging
from datetime import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = MongoClient(config.MONGO_URI)
        self.db = self.client[config.MONGO_DB_NAME]
        self.users = self.db.users
        self.messages = self.db.messages

    def add_user(self, user_id, username, is_admin=False, is_banned=False):
        try:
            self.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "username": username,
                        "is_admin": is_admin,
                        "is_banned": is_banned,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")

    def get_user(self, user_id):
        try:
            return self.users.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None

    def ban_user(self, user_id):
        try:
            self.users.update_one(
                {"user_id": user_id},
                {"$set": {"is_banned": True}}
            )
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}")

    def unban_user(self, user_id):
        try:
            self.users.update_one(
                {"user_id": user_id},
                {"$set": {"is_banned": False}}
            )
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {e}")

    def log_message(self, user_id, chat_id, message_text, response_text):
        try:
            self.messages.insert_one({
                "user_id": user_id,
                "chat_id": chat_id,
                "message_text": message_text,
                "response_text": response_text,
                "timestamp": datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Error logging message for user {user_id}: {e}")

    def get_user_count(self):
        try:
            return self.users.count_documents({})
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            return 0

    def get_message_count(self):
        try:
            return self.messages.count_documents({})
        except Exception as e:
            logger.error(f"Error counting messages: {e}")
            return 0

    def get_all_users(self):
        try:
            return list(self.users.find({}))
        except Exception as e:
            logger.error(f"Error fetching all users: {e}")
            return []

db = Database()
