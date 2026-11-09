import os

from dotenv import load_dotenv

from custom_errors.db_exceptions import DbNotFound
from datos.sqlite.context.db_context import SqliteCtx
from datos.sqlite.context.db_context_interface import IDbContext
from models.clientes_model import ClientesModel
from servicios.service_interface import IGenericService


class DbServices(IGenericService[ClientesModel]):
    def __init__(self, conn: IDbContext | None = None):
        self.__conn = conn

    def _get_conn(self) -> IDbContext:
        if self.__conn is not None:
            return self.__conn

        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))
        conn_str = os.getenv("CONNSTRING")
        if not conn_str:
            raise DbNotFound("Falta CONNSTRING en .env")
        if not os.path.isabs(conn_str):
            conn_str = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../", conn_str)
            )
        return SqliteCtx(conn_str)

    def get_all(self) -> list[ClientesModel]:
        conn = self._get_conn()
        try:
            conn.execute("SELECT * FROM CLIENTES")
            datos = conn.fetch_all()
            models: list[ClientesModel] = []
            for i in datos:
                models.append(
                    ClientesModel(
                        id_cliente=i[0],
                        nombre=i[1],
                        email=i[2],
                        telefono=i[3],
                        direccion=i[4],
                        fecha_registro=i[5],
                    )
                )
            return models
        finally:
            # Cierra solo conexiones efimeras (re-run friendly)
            if self.__conn is None:
                conn.close()

    def get_one_by_id(self, id_cliente: str) -> ClientesModel:
        conn = self._get_conn()
        try:
            conn.execute(f"SELECT * FROM CLIENTES WHERE id_cliente = {int(id_cliente)}")
            dato = conn.fetch_one()
            return ClientesModel(
                id_cliente=dato[0],
                nombre=dato[1],
                email=dato[2],
                telefono=dato[3],
                direccion=dato[4],
                fecha_registro=dato[5],
            )
        finally:
            if self.__conn is None:
                conn.close()


db_service = DbServices()
