import os

from sqlalchemy import Column, Integer, Text, create_engine, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    confirmation_code = Column(String(6), nullable=True)
    is_confirmed = Column(Integer, default=0)


db_user = os.getenv('POSTGRES_USER', 'admin')
db_password = os.getenv('POSTGRES_PASSWORD', 'Secret')
db_host = os.getenv('DB_HOST', '127.0.0.1')
db_port = os.getenv('DB_PORT', '55437')
db_name = os.getenv('POSTGRES_DB', 'test_db')

engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

Base.metadata.create_all(engine)
