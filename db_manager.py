import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from database.model import Base, Address

instance = None

class DBManager():
    def __init__(self):
        global instance
        if instance == None:
            db_connection = sqlalchemy.create_engine("sqlite:///database/addresses.db")
            Base.metadata.create_all(db_connection)

            session_factory = sessionmaker(db_connection)
            self._Session = scoped_session(session_factory)
            self.session = self._Session()

            instance = self

    def __delete__(self):
        self._Session.remove()

    def add_address(self, address):
        new_address = Address(address=address)
        self.session.add(new_address)
        try:
            self.session.commit()
        except:
            self.session.rollback()

    def get_number_of_elements(self):
        return self.session.query(Address).count()

    def get_address(self, index):
        return self.session.query(Address).get(index).address

    def get_stored_addresses(self):
        return [item.address for item in self.session.query(Address).all()]

instance = DBManager()
