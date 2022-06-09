import sqlite3
try:
    import psycopg2
except ModuleNotFoundError:
    raise ModuleNotFoundError("Please install the psycopg2 module to use this functionality.")


try:
    import mysql.connector
    from mysql.connector import errorcode
except ModuleNotFoundError:
    raise ModuleNotFoundError("Please install the mysql module to use this functionality.")

MYSQL = "mysql"
SQLITE = "sqlite"
POSTGRESQL = "postgresql"


class SQLWrapper:
    host = None
    user = None
    password = None
    db_name = None
    db_sql_type = None
    session = None
    connection = None
    query = None
    port = None

    def __init__(self, db_sql_type, db_name, host=None, user=None, password=None, port=None):
        """
        Create an object for SQLWrapper class
        :param db_sql_type:
        :param db_name:
        :param host:
        :param user:
        :param password:
        :param port:
        :return:
        """
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.db_sql_type = db_sql_type
        self.port = port

    def connect(self):
        """
        Establish connection to database
        :return self.session:
        """
        if self.db_sql_type == MYSQL:
            try:
                self.connection = mysql.connector.connect(
                    database=self.db_name,
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port
                )
                self.session = self.connection.cursor()
            except mysql.connector.Error as e:
                print(format(e))
        elif self.db_sql_type == SQLITE:
            try:
                self.connection = sqlite3.connect(self.db_name)
                self.session = self.connection.cursor()
            except sqlite3.Error as e:
                print(format(e))
        elif self.db_sql_type == POSTGRESQL:
            try:
                self.connection = psycopg2.connect(
                    host=self.host,
                    database=self.db_name,
                    user=self.user,
                    password=self.password
                )
                self.session = self.connection.cursor()
            except psycopg2.Error as e:
                print(format(e))
        return self.session

    def query(self, query):
        """
        Make a query
        :param query:
        :return self.query:
        """
        query = query.lower()
        if self.db_sql_type == MYSQL:
            try:
                self.query = self.session.execute(query)
                if 'select' not in query:
                    self.connection.commit()
            except mysql.connector.Error as e:
                if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print('Username and/or password entered incorrectly.')
                elif e.errno == errorcode.ER_BAD_DB_ERROR:
                    print('Required database not found.')
                elif e.errno == errorcode.CR_CONN_HOST_ERROR:
                    print('Wrong host required.')
                elif e.errno == errorcode.ER_IS_QUERY_INVALID_CLAUSE:
                    print('Poorly formulated query.')
                else:
                    print(format(e))
            except (Exception,) as ex:
                print(ex)

        elif self.db_sql_type == SQLITE:
            try:
                self.query = self.session.execute(query)
                self.connection.commit()
            except sqlite3.Error as e:
                print(format(e.args))
        elif self.db_sql_type == POSTGRESQL:
            try:
                self.query = self.session.execute(query)
            except psycopg2.Error as e:
                print(format(e))
        else:
            raise ValueError('Database is not implemented')

        return self.query

    def disconnect(self):
        """
        Disconnect from database
        :param:
        :return self.connection:
        """
        self.session.close()
        self.connection.close()
