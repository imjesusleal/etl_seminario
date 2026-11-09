import os
import sqlite3
from sqlite3 import Connection

from dotenv import load_dotenv


class WarehouseContext:
    """Conexion al SQLite analitico (destino del ETL)."""

    def __init__(self, conn_str: str):
        if not conn_str:
            raise Exception("Falta WAREHOUSE_CONNSTRING en el entorno")
        self.__conn_str = conn_str
        os.makedirs(os.path.dirname(os.path.abspath(conn_str)) or ".", exist_ok=True)
        self.__conn: Connection = sqlite3.connect(self.__conn_str)

    @property
    def connection(self) -> Connection:
        return self.__conn

    def apply_schema(self, schema_path: str) -> None:
        with open(schema_path, "r", encoding="utf-8") as schema_file:
            self.__conn.executescript(schema_file.read())
        self.__conn.commit()

    def close(self) -> None:
        if self.__conn:
            self.__conn.close()


def build_warehouse_context() -> WarehouseContext:
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))
    default_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../output/novashop_analitico.db")
    )
    conn_str = os.getenv("WAREHOUSE_CONNSTRING", default_path)
    if not os.path.isabs(conn_str):
        conn_str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../", conn_str)
        )
    return WarehouseContext(conn_str)
