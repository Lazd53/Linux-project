import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(250))


class Award(Base):
    __tablename__ = 'award'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description
        }

class Bio(Base):
    __tablename__ = 'bio'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    description = Column(String(1000))
    discipline = Column(String(100))
    award_id = Column(Integer, ForeignKey('award.id'))
    award = relationship(Award)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description
        }

engine = create_engine('sqlite:///sciawards.db')

Base.metadata.create_all(engine)
