import os
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography, Geometry
from dotenv import load_dotenv

load_dotenv()

# 1. Database Setup
# Note: For Supabase transaction mode (port 6543), disable prepared statements
# by passing server_settings as shown below to prevent connection issues.
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(
    DATABASE_URL, 
    pool_size=5, 
    max_overflow=10,
    connect_args={"server_settings": {"jit": "off"}} # Required for some Supabase setups
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# 2. Define the Models
class Listing(Base):
    __tablename__ = "listings"
    id = Column(UUID(as_uuid=True), primary_key=True)
    source = Column(String)
    price = Column(Numeric)
    location = Column(Geography('POINT'))

class Building(Base):
    __tablename__ = "buildings"
    id = Column(UUID(as_uuid=True), primary_key=True)
    building_name = Column(String)
    footprint = Column(Geometry('POLYGON', srid=4326))

# 3. Dependency to get DB session
async def get_db():
    async with async_session() as session:
        yield session

# 4. FastAPI Setup
app = FastAPI(title="Real Estate Geo-Engine API")

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Simple route to verify database connectivity."""
    try:
        # Execute a simple PostGIS version check to ensure DB is connected
        from sqlalchemy import text
        result = await db.execute(text("SELECT PostGIS_Version();"))
        version = result.scalar()
        return {"status": "healthy", "postgis_version": version}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)