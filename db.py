
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Sequence,
    Float,
    PrimaryKeyConstraint,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.sql import *
import pyodbc

def db_connect():
    engine = create_engine("mssql+pyodbc://Automation:4u10ma13@DESKTOP-PI85UQD/WHDataCards?driver=SQL+Server+Native+Client+11.0&trusted_connection=yes")
    return engine

Base = declarative_base()

class Faction(Base):
    __tablename__ = "faction"
    faction_id = Column(Integer, primary_key=True)
    name = Column(String)


class Unit(Base):
    __tablename__ = "unit"
    unit_id = Column(Integer, primary_key=True)
    faction_id = Column(Integer, ForeignKey("faction.faction_id"))
    name = Column(String)
    meta = Column(String)
    keywords = Column(String)

class PointsValue(Base):
    __tablename__ = "pointsvalue"
    pv_id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey("unit.unit_id"))
    amount = Column(Integer)
    points = Column(Integer)
    
engine = db_connect()

Faction.__table__.create(bind=engine, checkfirst=True)
Unit.__table__.create(bind=engine, checkfirst=True)
PointsValue.__table__.create(bind=engine, checkfirst=True)
# PointsValue