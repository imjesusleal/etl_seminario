from datos.csv.context.csv_context import CsvContext, csv_ctx
from models.ventas_model import VentasModel
from servicios.service_interface import IGenericService


class CsvServices(IGenericService[VentasModel]):
    def __init__(self, ctx: CsvContext):
        self.__ctx = ctx

    def get_all(self) -> list[VentasModel]: 
        datos = self.__ctx.datos.to_dict(orient="records")
    
        models: list[VentasModel] = [] 
        for i in datos:
            model = VentasModel(
                id_venta = i['id_venta'],
                fecha = i['fecha'],
                producto = i['producto'],
                cantidad = i['cantidad'],
                precio_unitario = i['precio_unitario'],
                id_cliente = i['id_cliente'],
            )
            
            models.append(model)

        return models
    
    def get_one_by_id(self, cliente_id: int) -> VentasModel:
        datos = self.__ctx.datos
        
        model: VentasModel = VentasModel()

        for i in datos:
            if i['cliente_id'] == cliente_id:
                model = VentasModel(
                id_venta = i['id_venta'],
                fecha = i['fecha'],
                producto = i['producto'],
                cantidad = i['cantidad'],
                precio_unitario = i['precio_unitario'],
                id_cliente = i['id_cliente'],
                )
            
        return model
    

csv_service = CsvServices(csv_ctx)