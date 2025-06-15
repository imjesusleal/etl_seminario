from custom_errors.db_exceptions import DbNotFound
from .db_context_interface import IDbContext
import sqlite3
from sqlite3 import Connection, Cursor
from dotenv import load_dotenv
import os

class SqliteCtx(IDbContext):
    def __init__(self, conn_str: str):

        self.__conn_str = conn_str 

        if not self.__conn_str:
            raise Exception("No me mandaste el str connection chabon")

        self.__conn: Connection = self._create_conn()
        self.__cursor: Cursor = self.__create_cursor()

   
    def _create_conn(self) -> Connection:
        return sqlite3.connect(self.__conn_str)

    def __create_cursor(self) -> Cursor: 
        return self.__conn.cursor()

    def execute(self, query: str) -> None:
        self.__cursor.execute(query)

    def fetch_one(self):
        try:
            return self.__cursor.fetchone()
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener un registro: {e}")

    def fetch_all(self):
        try:
            return self.__cursor.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener todos los registros: {e}")
    
    def close(self):
        if self.__cursor:
            self.__cursor.close()
        if self.__conn:
            self.__conn.close()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
try:
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))
    conn = SqliteCtx(os.getenv('CONNSTRING'))
except Exception as ex:
    raise DbNotFound(f'No consegui la base de datos. {ex}')