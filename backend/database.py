from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'netflix_clone')

client = AsyncIOMotorClient(mongo_url)
database = client[db_name]

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return database

async def close_database():
    """Close database connection."""
    client.close()

# Create indexes for better performance
async def create_indexes():
    """Create database indexes."""
    # User indexes
    await database.users.create_index("email", unique=True)
    await database.users.create_index("username", unique=True)
    
    # Profile indexes
    await database.profiles.create_index("user_id")
    await database.profiles.create_index([("user_id", 1), ("name", 1)], unique=True)
    
    # Content indexes
    await database.content.create_index("tmdb_id", unique=True)
    await database.content.create_index("content_type")
    await database.content.create_index("genre_ids")
    await database.content.create_index("average_rating")
    
    # Watch history indexes
    await database.watch_history.create_index([("profile_id", 1), ("content_id", 1)], unique=True)
    await database.watch_history.create_index("profile_id")
    await database.watch_history.create_index("last_watched")
    
    # My list indexes
    await database.my_list.create_index([("profile_id", 1), ("content_id", 1)], unique=True)
    await database.my_list.create_index("profile_id")
    
    # Review indexes
    await database.reviews.create_index([("profile_id", 1), ("content_id", 1)], unique=True)
    await database.reviews.create_index("content_id")
    await database.reviews.create_index("created_at")
    
    # Review reaction indexes
    await database.review_reactions.create_index([("profile_id", 1), ("review_id", 1)], unique=True)
    await database.review_reactions.create_index("review_id")
    
    # Recommendation indexes
    await database.recommendations.create_index("profile_id")
    await database.recommendations.create_index("score")
    await database.recommendations.create_index("created_at")
    
    print("Database indexes created successfully")