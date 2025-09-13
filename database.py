# from motor.motor_asyncio import AsyncIOMotorClient

# MONGO_URL = "mongodb://localhost:27017"
# DB_NAME = "assessment_db"
# COLLECTION = "employees"

# client = None
# db = None

# async def connect_to_mongo():
#     global client, db
#     client = AsyncIOMotorClient(MONGO_URL)
#     db = client[DB_NAME]
#     await db[COLLECTION].create_index("employee_id", unique=True)

# def close_mongo_connection():
#     client.close()
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "assessment_db"

client = None
db = None

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    print("✅ Connected to MongoDB")

def close_mongo_connection():
    global client
    if client:
        client.close()
        print("🛑 MongoDB connection closed")
