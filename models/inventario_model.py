from dataclasses import dataclass

@dataclass
class InventarioModel:
    id_producto: int
    nombre_producto: str
    categoria: str
    stock_actual: int
    precio_costo: float
    proveedor: str