# coding: utf8
"""
A quick and dirty script to build the vorbis/postgres database
"""

import os
if os.path.dirname(__file__):
    os.chdir(os.path.dirname(__file__))

from sqlalchemy import create_engine
engine = create_engine('postgres://kalamar:kalamar@localhost/kalamar', echo=True)

from sqlalchemy import Column, Integer, String, Binary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Morceaux(Base):
    __tablename__ = 'morceaux_bak'
    
    id = Column(Integer, primary_key=True)
    genre = Column(String)
    artist = Column(String)
    album = Column(String)
    title = Column(String)
    no = Column(Integer)
    data = Column(Binary)

    def __init__(self, genre, artist, album, title, no, data):
        self.genre = genre
        self.artist = artist
        self.album = album
        self.title = title
        self.no = no
        self.data = data

    def __repr__(self):
        return "<Morceaux(%r, %r, %r, %r, %r, <data len=%i>)>" % (self.genre,
            self.artist, self.album, self.title, self.no, len(self.data))

metadata = Base.metadata
metadata.drop_all(engine)
metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

basedir = u'fs_vorbis_classified'
attr = {}
import os
for attr['genre'] in os.listdir(basedir):
    for attr['artist'] in os.listdir(basedir + 
        '/%(genre)s' % attr):
        for attr['album'] in os.listdir(basedir + 
        '/%(genre)s/%(artist)s' % attr):
            for name in os.listdir(basedir +
            '/%(genre)s/%(artist)s/%(album)s' % attr): 
                attr['no'] = int(name[:2])
                attr['title'] = name[5:-4]
                f = basedir + u'/%(genre)s/%(artist)s/%(album)s/' % attr + name
                attr['data'] = open(f).read()
                assert len(attr['data']) == os.stat(f).st_size
                m = Morceaux(**attr)
                session.add(m)
session.commit()

import pprint
pprint.pprint(session.query(Morceaux).all())

format = '/%(genre)s/%(artist)s/%(album)s/%(no)02i - %(title)s.ogg'
for morceau in session.query(Morceaux):
    dico = {}
    for key in morceau.__dict__:
        if type(morceau.__dict__[key]) is str:
            dico[key] = unicode(morceau.__dict__[key], 'utf-8')
        else:
            dico[key] = morceau.__dict__[key]
    if open(basedir + (format % dico)).read() != str(morceau.data):
        print 'CONTENT DIFFERS', morceau

