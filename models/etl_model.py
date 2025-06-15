from dataclasses import dataclass

from pandas import DataFrame

from models.clientes_model import ClientesModel
from models.inventario_model import InventarioModel
from models.tickets_model import TicketsModel
from models.ventas_model import VentasModel

@dataclass
class ETLModelCommand:
    clientes: list[ClientesModel]
    tickets: list[TicketsModel]
    ventas: list[VentasModel]
    inventario: list[InventarioModel]

@dataclass
class ETLModelDataframe:
    clientes: DataFrame
    tickets: DataFrame
    ventas: DataFrame
    inventario: DataFrame
