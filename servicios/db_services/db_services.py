from datos.sqlite.context.db_context import conn
from datos.sqlite.context.db_context_interface import IDbContext
from models.clientes_model import ClientesModel
from servicios.service_interface import IGenericService

class DbServices(IGenericService[ClientesModel]):
    def __init__(self, conn: IDbContext):
        self.__conn: IDbContext = conn

    def get_all(self) -> list[ClientesModel]: 
        self.__conn.execute('SELECT * FROM CLIENTES')
        datos = self.__conn.fetch_all()

        models: list[ClientesModel] = [] 

        for i in datos:
            model = ClientesModel(
                id_cliente = i[0],
                nombre = i[1],
                email = i[2],
                telefono = i[3],
                direccion = i[4],
                fecha_registro = i[5])
            models.append(model)

        self.__conn.close()
        return models
    
    def get_one_by_id(self, id_cliente: str) -> ClientesModel:
        self.__conn.execute(f'SELECT * FROM CLIENTES WHERE id_cliente = {id_cliente}')
        dato = self.__conn.fetch_one()

        model: ClientesModel = ClientesModel(
            id_cliente = dato[0],
            nombre = dato[1],
            email = dato[2],
            telefono = dato[3],
            direccion = dato[4],
            fecha_registro = dato[5]
        )
        
        self.__conn.close()
        return model
    

db_service = DbServices(conn)