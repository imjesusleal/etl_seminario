from datos.json.context.json_context import JsonContext, json_ctx
from models.tickets_model import TicketsModel
from servicios.service_interface import IGenericService

class JsonServices(IGenericService[TicketsModel]):
    def __init__(self, json_ctx: JsonContext):
        self.__ctx = json_ctx
    

    def get_all(self) -> list[TicketsModel]: 
        datos = self.__ctx.datos
        
        models: list[TicketsModel] = [] 

        for i in datos:
            model = TicketsModel(
                ticket_id = i['ticket_id'],
                fecha_creacion = i['fecha_creacion'],
                id_cliente = i['cliente_id'],
                tema = i['tema'],
                estado = i['estado'],
                resolucion = i['resolucion']
            )
            models.append(model)

    
        return models
    
    def get_one_by_id(self, cliente_id: int) -> TicketsModel:
        datos = self.__ctx.datos
        
        model: TicketsModel = TicketsModel()

        for i in datos:
            if i['cliente_id'] == cliente_id:
                model = TicketsModel(
                ticket_id = i['ticket_id'],
                fecha_creacion = i['fecha_creacion'],
                id_cliente = i['cliente_id'],
                tema = i['tema'],
                estado = i['estado'],
                resolucion = i['resolucion']
            )

        return model

json_service = JsonServices(json_ctx)