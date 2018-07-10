import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, query
from sqlalchemy import create_engine
from starter_catalog import catalog, catalog_items, user

Base = declarative_base()

# for storing users for this application
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Catalog(Base):
    __tablename__ = 'catalog'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    delete_allowed = Column(Integer)
    items = relationship("CatalogItems", back_populates='catalog',
        cascade="all, delete, delete-orphan")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class CatalogItems(Base):
    __tablename__ = 'catalog_items'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(400))
    catalog_id = Column(Integer, ForeignKey('catalog.id'))

    catalog = relationship(Catalog, back_populates = 'items')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }


engine = create_engine('sqlite:///catalog.db')   
Base.metadata.create_all(engine)

if __name__ == '__main__':
    engine = create_engine('sqlite:///catalog.db')
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    for iuser in user:
        usertemp = User(name = iuser['name'], email = iuser['email'], picture = iuser['picture'])
        session.add(usertemp)
    session.commit()

    for icatalog in catalog:
        #tempcatalog = Catalog(name = icatalog['name'], id = icatalog['id'])
        tempcatalog = Catalog(name = icatalog['name'], user_id = icatalog['user_id'])
        session.add(tempcatalog)
    session.commit()
        
    for item in catalog_items:
        for i in item:
            temp = CatalogItems(name = i['name'], description = i['description'], catalog_id = i['catalog_id'])
            session.add(temp)
    session.commit()

    mycatalog = session.query(Catalog).all()

    items = session.query(CatalogItems).filter_by(catalog_id=1).all()

    for icat in mycatalog:
        print icat.id, icat.name
    
    for i in items:
        print i.id, i.name

