import asyncio
from app.database import engine, Base
import app.models # register all models

async def create_tables():
    async with engine.begin() as conn:
        print("Creating all tables in PostgreSQL...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("All tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_tables())
