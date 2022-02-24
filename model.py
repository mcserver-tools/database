import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy.orm import relationship

Base = sqlalchemy.ext.declarative.declarative_base()

class Address(Base):
    """Address representation."""

    __tablename__ = "address"
    address_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    address = sqlalchemy.Column(sqlalchemy.String, unique=True)

class McServer(Base):
    """McServer representation."""

    __tablename__ = "mcserver"
    mcserver_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    address = sqlalchemy.Column(sqlalchemy.String, unique=True)
    ping = sqlalchemy.Column(sqlalchemy.Float)
    version = sqlalchemy.Column(sqlalchemy.String)
    online_players = sqlalchemy.Column(sqlalchemy.Integer)
    players = relationship("Player")

class Player(Base):
    """Player representation."""

    __tablename__ = "player"
    player_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    playername = sqlalchemy.Column(sqlalchemy.String)
    mcserver_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("mcserver.mcserver_id"), nullable=False)
