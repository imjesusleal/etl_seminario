from dataclasses import dataclass

@dataclass
class TicketsModel:
    ticket_id: int
    fecha_creacion: str
    id_cliente: int
    tema: str
    estado: str
    resolucion: str
