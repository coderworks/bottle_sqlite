from os import read
import sqlite3
from sqlite3 import Error
from . import utils

class DB:

    def __init__(self, filename, tablename, columns, c_types):

        self.__table      = tablename
        self.__columns    = columns
        self.__connection, self.__debug = DB.__connect(filename, tablename, columns, c_types)
        self.__version,    self.__debug = DB.__get_version(self.__connection)
        self.__totalrows,  self.__debug = self.totalrows
        self.__dbsize     = utils.check_file_size(filename)
        self.__disksize   = utils.check_disksize()
        
    @property
    def settings(self):

        settings = {
            "dbsize"     : self.__dbsize,
            "version"    : self.__version,
            "debug"      : self.__debug,
            "table"      : self.__table,
            "columns"    : self.__columns,
            "connection" : self.__connection,
            "totalrows"  : self.__totalrows,
            "disksize"   : self.__disksize
        }

        return settings

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, value):
        self.__debug = value

    @property
    def connection(self):
        return self.__connection
    
    @property
    def totalrows(self):
        query = "SELECT COUNT(id) FROM " + self.__table +  ";"

        rowID, rows, debug = DB.__execute_command( self.__connection, query )
        rows = rows[0]
        rows = str(rows)[1:-2]
        return rows, debug
    
    # Private
    @staticmethod
    def __create_connection(filename):

        try:
            return sqlite3.connect(filename), ""

        except Error as e:
            return None, "Error:" + str(e)
    
    @staticmethod
    def __create_table(connection, table, columns, c_types):

        s = ""
        for column, c_type in zip (columns, c_types):
            s += column + " " + c_type + ", "

        command = "CREATE TABLE IF NOT EXISTS " + table \
                + " ( id INTEGER PRIMARY KEY, " + s[:-2] + " ); "

        try:
            cursor = connection.cursor()
            cursor.execute(command)
            return ""
            
        except Error as e:
            return "Error:" + str(e)

    @staticmethod
    def __connect(filename, table, columns, c_types):

        connection, debug = DB.__create_connection(filename)

        if debug == "":
            return connection, DB.__create_table(connection, table, columns, c_types)
        else: 
            return None, debug

    @staticmethod
    def __get_version(connection):

        query = "select sqlite_version();"
        rowid, rows, debug = DB.__execute_command(connection, query)

        return str( rows[0] )[2:-3], debug

    @staticmethod
    def __execute_command(connection, command, values = None):

        cursor = connection.cursor()

        try:
            debug = ""
            if values == None:
                cursor.execute(command)

            else:
                cursor.execute(command, values)

            connection.commit()

        except Error as e:
            debug = "Error:" + str(e)

        finally:
            return cursor.lastrowid, cursor.fetchall(), debug

    # Public
    def create_row(self, values):

        # Funny oneliner. 'values' aka ('?') are added in the execute
        query = "INSERT INTO " + self.__table \
            + " (" + ", ".join(self.__columns) + \
                ") VALUES " + str( (len(self.__columns)) * \
                    ('?',) ).replace("'", "") + ";"

        return DB.__execute_command(self.__connection, query, values)

    def read_rows(self):

        query = "SELECT * FROM " + self.__table + ";"

        return DB.__execute_command(self.__connection, query )

    def read_row(self, searchId):
        
        query = "SELECT * FROM " + self.__table + " WHERE id=" + str(searchId) + ";"

        return DB.__execute_command(self.__connection, query )

    def update_row(self, searchId, values):

        # Funny oneliner. 'values' aka ('?') are added in the execute
        query = "UPDATE " + self.__table \
                + " SET " + \
                    ", ".join( [str(column + "=?") for column in self.__columns] ) \
                        + " WHERE id=" + str(searchId) + ";"

        return DB.__execute_command(self.__connection, query, values )

    def delete_row(self, searchId):

        query = "DELETE FROM " + self.__table + " WHERE id=" + str(searchId) + ";"

        return DB.__execute_command(self.__connection, query )
