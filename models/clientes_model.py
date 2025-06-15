from dataclasses import dataclass

@dataclass
class ClientesModel:
    id_cliente: int
    nombre: str
    email: str
    telefono: str
    direccion: str
    fecha_registro: str
