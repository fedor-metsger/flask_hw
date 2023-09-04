
import atexit
import os

from sqlalchemy import Column, DateTime, Integer, String, create_engine, func, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
PG_DB = os.getenv("PG_DB", "adverts")
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = os.getenv("PG_PORT", 5432)
PG_DSN = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"


engine = create_engine(PG_DSN)
atexit.register(engine.dispose)

Session = sessionmaker(bind=engine)
Base = declarative_base()


class Advert(Base):
    __tablename__ = "advert"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    owner = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)