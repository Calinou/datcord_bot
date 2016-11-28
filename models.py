from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
# Models base, holds all table mappings and metadata.
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    userid = Column(String())
    xp = Column(Integer())
    # lastloc = db.Column(db.JSON())

    def __init__(self, userid, xp=0):
        self.userid = userid
        self.xp = xp

    def __repr__(self):
        return '<userid {}>'.format(self.userid)


class Stamp(Base):
    __tablename__ = 'stamps'

    id = Column(Integer, primary_key=True)
    descriptor = Column(String())
    stamp = Column(String())
    # lastloc = db.Column(db.JSON())

    def __init__(self, descriptor, stamp):
        self.descriptor = descriptor
        self.stamp = stamp

    def __repr__(self):
        return '<stamp: {}>'.format(self.descriptor)
