from dataclasses import dataclass

@dataclass
class VentasModel:
    id_venta: int
    fecha: str
    producto: str
    cantidad: int
    precio_unitario: float
    id_cliente: int
