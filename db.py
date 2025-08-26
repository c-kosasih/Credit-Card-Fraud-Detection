from sqlalchemy import Column, String, Float, Integer, Date, DateTime, TIMESTAMP, func, BigInteger, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = ""

# Connection timeout and pool settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using
    pool_recycle=3600,   # Recycle connections every hour
    connect_args={"connect_timeout": 10}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)
    
class RawTransaction(Base):
    __tablename__ = "raw_transactions"
    id = Column(Integer, primary_key=True, index=True)
    trans_date_trans_time = Column(DateTime, nullable=False)
    cc_num = Column(BigInteger, nullable=False)
    merchant = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    amt = Column(Float, nullable=False)
    first = Column(String(100))
    last = Column(String(100))
    gender = Column(String(1))  
    street = Column(String(255))
    city = Column(String(255))
    state = Column(String(10))
    zip = Column(Integer)
    lat = Column(Float)
    long = Column(Float)
    city_pop = Column(Integer)
    job = Column(String(255))
    dob = Column(DateTime, nullable=False)
    trans_num = Column(String(255), unique=True, index=True)
    unix_time = Column(BigInteger)
    merch_lat = Column(Float)
    merch_long = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(BigInteger, primary_key=True, index=True)
    trans_date_trans_time = Column(DateTime, nullable=False)
    cc_num = Column(BigInteger, nullable=False)
    merchant = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    amt = Column(Float, nullable=False)
    first = Column(String(50))
    last = Column(String(50))
    gender = Column(String(1))
    street = Column(String(200))
    city = Column(String(100))
    state = Column(String(10))
    zip = Column(Integer)
    lat = Column(Float)
    long = Column(Float)
    city_pop = Column(Integer)
    job = Column(String(100))
    dob = Column(Date)
    trans_num = Column(String(50), nullable=False)
    unix_time = Column(BigInteger, nullable=False)
    merch_lat = Column(Float)
    merch_long = Column(Float)
    prediction = Column(SmallInteger)
    created_at = Column(TIMESTAMP, server_default=func.now())
    



