import os
from pymongo import MongoClient

class DatabaseConfig:
    # MongoDB connection settings
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "student_feedback_db")
    
    @staticmethod
    def get_database():
        """Establish and return MongoDB database connection"""
        client = MongoClient(DatabaseConfig.MONGO_URI)
        return client[DatabaseConfig.DATABASE_NAME]
    
    @staticmethod
    def get_collection(collection_name):
        """Get specific collection from database"""
        db = DatabaseConfig.get_database()
        return db[collection_name]
