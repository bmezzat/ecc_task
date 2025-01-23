from sqlalchemy import Column, Integer, String, Float, Date, Time, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class CC050(Base):
    __tablename__ = "cc050"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    clearing_member = Column(String)
    account = Column(String)
    margin_type = Column(String)
    margin = Column(Float)


class CI050(Base):
    __tablename__ = "ci050"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    clearing_member = Column(String)
    account = Column(String)
    margin_type = Column(String)
    margin = Column(Float)


class ErrorChecks(Base):
    __tablename__ = "error_checks"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    report = Column(String, nullable=False)
    clearing_member = Column(String)
    account = Column(String)
    margin_type = Column(String)
    margin_cc050 = Column(Float)
    margin_ci050 = Column(Float)


DATABASE_URL = "sqlite:///sqlite.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
