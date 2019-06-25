import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# from flask_login import UserMixin

Base = declarative_base()

# class Owner(Base, UserMixin):


class Owner(Base):
    __tablename__ = 'ownerDetails'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), unique=True)
    picture = Column(String(3250), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
        }


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    image = Column(String(3050), nullable=False)

    owner_id = Column(Integer, ForeignKey('ownerDetails.id'))
    owner = relationship(Owner)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'image': self.image
        }


class MenuItem(Base):
    __tablename__ = 'menu_item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    price = Column(String(8))
    description = Column(String(250))

    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)

    owner_id = Column(Integer, ForeignKey('ownerDetails.id'))
    owner = relationship(Owner)

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'restaurant_id': self.restaurant_id,
        }


engine = create_engine('sqlite:///restaurantmenu.db')


Base.metadata.create_all(engine)
