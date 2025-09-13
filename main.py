# from fastapi import FastAPI
# from routes import employees
# from database import connect_to_mongo, close_mongo_connection

# app = FastAPI(title="Employee API - Assessment")

# # Include employee routes
# app.include_router(employees.router)

# # Connect to DB on startup
# @app.on_event("startup")
# async def startup_db_client():
#     await connect_to_mongo()

# # Close DB on shutdown
# @app.on_event("shutdown")
# async def shutdown_db_client():
#     close_mongo_connection()

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://localhost:27017"  # replace with your MongoDB URI

client = None
db = None

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client["employee_db"]  # database name

def close_mongo_connection():
    global client
    if client:
        client.close()

