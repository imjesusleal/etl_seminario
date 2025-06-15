from datos.excel.context.excel_context import excel_ctx, ExcelContext
from models.inventario_model import InventarioModel
from servicios.service_interface import IGenericService


class ExcelServices(IGenericService[InventarioModel]):
    def __init__(self, ctx: ExcelContext):
        self.__ctx = ctx

    def get_all(self) -> list[InventarioModel]: 
        datos = self.__ctx.datos.to_dict(orient="records")
    
        models: list[InventarioModel] = [] 
        for i in datos:
            model = InventarioModel(    
            id_producto = i['ID_Producto'],
            nombre_producto = i['Nombre_Producto'],
            categoria = i['Categoria'],
            stock_actual = i['Stock_Actual'],
            precio_costo = i['Precio_Costo'],
            proveedor = i['Proveedor']
            )
            models.append(model)

        return models
    
    def get_one_by_id(self, id_producto: int) -> InventarioModel:
        datos = self.__ctx.datos.to_dict(orient="records")
        
        for i in datos:
            if i['cliente_id'] == id_producto:
                model = InventarioModel(    
                    id_producto = i['ID_Producto'],
                    nombre_producto = i['Nombre_Producto'],
                    categoria = i['Categoria'],
                    stock_actual = i['Stock_Actual'],
                    precio_costo = i['Precio_Costo'],
                    proveedor = i['Proveedor']
                )

        return model | None
    

excel_service = ExcelServices(excel_ctx)