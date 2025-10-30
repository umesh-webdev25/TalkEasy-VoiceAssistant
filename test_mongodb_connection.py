import asyncio
import os
from services.database_service import DatabaseService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_connection():
    """Test MongoDB connection"""
    print("🧪 Testing MongoDB connection...")
    
    db_service = DatabaseService()
    connected = await db_service.connect()
    
    if connected:
        print("✅ MongoDB connection successful!")
        print(f"📊 Database name: {db_service.db_name}")
        
        # Run additional tests
        if db_service.is_connected():
            print("✅ Database is connected")
            await db_service.test_database_operations()
        
        await db_service.close()
    else:
        print("❌ MongoDB connection failed - using in-memory storage")

if __name__ == "__main__":
    asyncio.run(test_connection())
