from models.clientes_model import ClientesModel
from models.etl_model import ETLModelCommand, ETLModelDataframe
from models.inventario_model import InventarioModel
from models.tickets_model import TicketsModel
from models.ventas_model import VentasModel
from servicios.json_services.json_services import json_service
from servicios.csv_services.csv_services import csv_service
from servicios.excel_services.excel_services import excel_service
from servicios.db_services.db_services import db_service
from .etl_service import ETLService


class MainService():
    def __init__(self):
        self.datos_clientes: list[ClientesModel] = []
        self.datos_tickets: list[TicketsModel] = []
        self.datos_ventas: list[VentasModel] = []
        self.datos_inventario: list[InventarioModel] = []

        self.etl_service: ETLService = None

        self.__command: ETLModelCommand = None 
        self.__dfs: ETLModelDataframe = None

    @property
    def dfs(self) -> ETLModelDataframe:
        return self.__dfs

    def cargar_datos(self) -> None:
        self.datos_clientes = db_service.get_all()
        self.datos_tickets = json_service.get_all()
        self.datos_ventas = csv_service.get_all()
        self.datos_inventario = excel_service.get_all()

    def inyect(self):
        self.__command = ETLModelCommand(self.datos_clientes, self.datos_tickets, self.datos_ventas, self.datos_inventario)
        self.etl_service = ETLService(self.__command)

    def transform(self):
        self.__dfs = self.etl_service.transform()

    def manejar_datos(self) -> None:
        self.etl_service.limpiar(self.__dfs)
        self.etl_service.handle_null(self.__dfs)
        self.etl_service.format_handling(self.__dfs)
        self.etl_service.ordenar(self.__dfs)
        self.etl_service.crear_columna_calculada(self.__dfs.ventas)
        self.etl_service.output(self.__dfs)


main_service = MainService()