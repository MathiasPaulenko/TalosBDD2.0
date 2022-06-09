import logging
import os
from sqlite3.dbapi2 import Connection

import records
import sqlite3

from settings import settings

DB_HOME = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir) + '/../data') + os.sep


class TestSQLiteDatabase(records.Database):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            super().__init__('sqlite:///' + settings.SQLITE['sqlite_home'])
            self.db_type = 'sqlite3'
            self.logger.debug(f"The sqlite db was generated correctly in the path: {settings.SQLITE['sqlite_home']}")
        except (Exception,) as ex:
            self.logger.error(f"There was an error initializing the sqlite db:")
            self.logger.error(f"{ex}")


def sqlite_db():
    if settings.SQLITE['enable']:
        logger = logging.getLogger(__name__)
        try:
            connection: Connection = sqlite3.connect(settings.SQLITE['sqlite_home'])
            logger.debug(f"The sqlite db was generated correctly in the path: {settings.SQLITE['sqlite_home']}")
            return connection
        except (Exception,) as ex:
            logger.error(f"There was an error initializing the sqlite db:")
            logger.error(f"{ex}")
            return None
