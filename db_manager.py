"""Module for managing the database"""

from threading import Lock

import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from database.model import Address, Base, McServer, Player

try:
    from discordbot.mcserver import McServer as McServerObj
except:
    pass

INSTANCE = None

class DBManager():
    """Class that manages the database"""

    def __init__(self):
        if INSTANCE is None:
            db_connection = sqlalchemy.create_engine("sqlite:///database/addresses.db", connect_args={'check_same_thread': False})
            Base.metadata.create_all(db_connection)

            session_factory = sessionmaker(db_connection, autoflush=False)
            self._Session = scoped_session(session_factory)
            self.session = self._Session()

            self.lock = Lock()

    # def __del__(self):
        # self._Session.remove()

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
            old_mcserver.online_players = mcserver_obj.online_players
            for player in mcserver_obj.players:
                old_player = self.session.query(Player).filter_by(playername=player).first()
                if old_player != None:
                    old_player.mcserver_id = old_mcserver.mcserver_id
                else:
                    temp_player = Player(playername=player, mcserver_id=old_mcserver.mcserver_id)
                    self.session.add(temp_player)
        else:
            new_mcserver = McServer(address=mcserver_obj.address[0], ping=mcserver_obj.ping, version=mcserver_obj.version, online_players=mcserver_obj.online_players)
            self.session.add(new_mcserver)
            for player in mcserver_obj.players:
                temp_player = Player(playername=player, mcserver_id=new_mcserver.mcserver_id)
                self.session.add(temp_player)

        self.lock.release()
        self.commit()

    def update_players_nocommit(self, mcserver_obj):
        self.lock.acquire(blocking=True)

        mcserver = self.session.query(McServer).filter_by(address=mcserver_obj.address[0]).first()
        mcserver.online_players = mcserver_obj.online_players

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
        ret_list = [McServerObj((item.address, "25565"), item.ping, item.version, item.online_players, []) for item in self.session.query(McServer).all()]
        self.lock.release()
        return ret_list

    def get_number_of_mcservers(self):
        return self.session.query(McServer).count()

INSTANCE = DBManager()
