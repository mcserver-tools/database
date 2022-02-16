import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from threading import Lock

from database.model import Base, Address, McServer

try:
    from discordbot.mcserver import McServer as McServerObj
except:
    pass

instance = None

class DBManager():
    def __init__(self):
        global instance
        if instance == None:
            db_connection = sqlalchemy.create_engine("sqlite:///database/addresses.db", connect_args={'check_same_thread': False})
            Base.metadata.create_all(db_connection)

            session_factory = sessionmaker(db_connection)
            self._Session = scoped_session(session_factory)
            self.session = self._Session()

            self.lock = Lock()

    def __delete__(self):
        self._Session.remove()

    def add_address(self, address):
        new_address = Address(address=address)
        self.session.add(new_address)
        try:
            self.session.commit()
        except:
            self.session.rollback()

    def get_number_of_addresses(self):
        return self.session.query(Address).count()

    def get_address(self, index):
        return self.session.query(Address).get(index).address

    def get_addresses(self):
        return [item.address for item in self.session.query(Address).all()]

    def clear_mcservers(self):
        self.lock.acquire(blocking=True)

        self.session.query(McServer).delete()
        try:
            self.session.commit()
        except:
            self.session.rollback()

        self.lock.release()

    def add_mcserver_nocommit(self, mcserver_obj):
        self.lock.acquire(blocking=True)

        old_mcserver = self.session.query(McServer).filter_by(address=mcserver_obj.address[0]).first()
        if old_mcserver != None:
            old_mcserver.address = mcserver_obj.address[0]
            old_mcserver.ping = mcserver_obj.ping
            old_mcserver.version = mcserver_obj.version
            old_mcserver.players = mcserver_obj.players
        else:
            new_mcserver = McServer(address=mcserver_obj.address[0], ping=mcserver_obj.ping, version=mcserver_obj.version, players=mcserver_obj.players)
            self.session.add(new_mcserver)

        self.lock.release()

    def update_players_nocommit(self, mcserver_obj):
        self.lock.acquire()

        mcserver = self.session.query(McServer).filter_by(address=mcserver_obj.address[0]).first()
        mcserver.players = mcserver_obj.players

        self.lock.release()

    def commit(self):
        self.lock.acquire()
        try:
            self.session.commit()
        except:
            self.session.rollback()
        self.lock.release()

    def get_mcservers(self):
        self.lock.acquire(blocking=True)
        ret_list = [McServerObj((item.address, "25565"), item.ping, item.version, item.players) for item in self.session.query(McServer).all()]
        self.lock.release()
        return ret_list

    def get_number_of_mcservers(self):
        return self.session.query(McServer).count()

instance = DBManager()
