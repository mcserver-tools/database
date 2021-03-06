"""Module for managing the database"""

from threading import Lock

import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from database.model import Address, Base, McServer, Player

try:
    from discordbot.mcserver import McServer as McServerObj
except ImportError:
    pass

INSTANCE = None

class DBManager():
    """Class that manages the database"""

    def __init__(self):
        if INSTANCE is None:
            db_connection = sqlalchemy.create_engine("sqlite:///database/addresses.db",
                                                     connect_args={'check_same_thread': False})
            Base.metadata.create_all(db_connection)

            session_factory = sessionmaker(db_connection, autoflush=False)
            _session = scoped_session(session_factory)
            self.session = _session()

            self.lock = Lock()

    def add_address(self, address):
        """Add address to database"""

        new_address = Address(address=address)
        self.session.add(new_address)
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            self.session.rollback()

    def get_number_of_addresses(self):
        """Returns number of addresses in database"""

        return self.session.query(Address).count()

    def get_address(self, index):
        """Returns address with given primary key"""

        return self.session.query(Address).get(index).address

    def get_addresses(self):
        """Returns all addresses in database"""

        return [item.address for item in self.session.query(Address).all()]

    def clear_mcservers(self):
        """Deletes all McServer entries in the database"""

        with self.lock:
            self.session.query(McServer).delete()
            self.session.query(Player).delete()
            try:
                self.session.commit()
            except sqlalchemy.exc.IntegrityError:
                self.session.rollback()

    def add_mcserver_nocommit(self, mcserver_obj):
        """Add a McServer object to the database"""

        with self.lock:
            players = []
            for playername in mcserver_obj.players:
                temp_player = Player(name=playername)
                self.session.add(temp_player)
                players.append(temp_player)

            new_mcserver = McServer(address=mcserver_obj.address[0], ping=mcserver_obj.ping,
                                    version=mcserver_obj.version,
                                    online_players=mcserver_obj.online_players,
                                    players=players)
            self.session.add(new_mcserver)

    def commit(self):
        """Commits changes to database"""

        with self.lock:
            try:
                self.session.commit()
            except sqlalchemy.exc.IntegrityError:
                self.session.rollback()

    def get_mcservers(self):
        """Returns all McServer objects in the database"""

        with self.lock:
            ret_list = [McServerObj((item.address, "25565"), item.ping, item.version,
                                    item.online_players, [player.name for player in item.players])
                        for item in self.session.query(McServer).all()]
        return ret_list

    def get_number_of_mcservers(self):
        """Returns the number of McServer objects in the database"""

        return self.session.query(McServer).count()

INSTANCE = DBManager()
