from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config.config import settings
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_async_engine(settings.sqlalchemy_database_url, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session 