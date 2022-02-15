import sqlalchemy
import sqlalchemy.ext.declarative

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
    players = sqlalchemy.Column(sqlalchemy.Integer)
