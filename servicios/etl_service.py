from models.etl_model import ETLModelCommand, ETLModelDataframe
from pandas import DataFrame
import pandas as pd

class ETLService():
    def __init__(self, etl_data: ETLModelCommand):
        self.etl_data = etl_data

    def transform(self) -> ETLModelDataframe:
        clientes_df = DataFrame(self.etl_data.clientes)
        tickets_df = DataFrame(self.etl_data.tickets)
        ventas_df = DataFrame(self.etl_data.ventas)
        inventario_df = DataFrame(self.etl_data.inventario)

        dfs = ETLModelDataframe(clientes_df, tickets_df,ventas_df, inventario_df)

        return dfs

    def limpiar(self, dfs: ETLModelDataframe) -> None:
        dfs.clientes.drop_duplicates(inplace=True)
        dfs.ventas.drop_duplicates(inplace=True)
        dfs.tickets.drop_duplicates(inplace=True)
        dfs.inventario.drop_duplicates(inplace=True)
    
    def handle_null(self, dfs: ETLModelDataframe) -> None:
        dfs.clientes.fillna('Sin resolucion',inplace=True)
        dfs.ventas.fillna('Sin resolucion',inplace=True)
        dfs.tickets.fillna('Sin resolucion',inplace=True)
        dfs.inventario.fillna('Sin resolucion',inplace=True)

    def format_handling(self, dfs: ETLModelDataframe) -> None:
        dfs.clientes['fecha_registro'] = pd.to_datetime(dfs.clientes['fecha_registro'], errors='coerce')
        dfs.ventas['fecha'] = pd.to_datetime(dfs.ventas['fecha'], errors='coerce')
        dfs.tickets['fecha_creacion'] = pd.to_datetime(dfs.tickets['fecha_creacion'], errors='coerce')

    def ordenar(self, dfs: ETLModelDataframe) -> None:
        dfs.clientes = dfs.clientes.sort_values(by='id_cliente')
        dfs.ventas = dfs.ventas.sort_values(by='id_cliente')
        dfs.tickets = dfs.tickets.sort_values(by='id_cliente')
        dfs.inventario = dfs.inventario.sort_values(by='id_producto')

    def crear_columna_calculada(self, df: DataFrame) -> None:
        df['total_venta'] = df['precio_unitario'] * df['cantidad']

    def output(self, dfs: ETLModelDataframe) -> None:
        dfs_final = self.merge(dfs)
        with pd.ExcelWriter('output/output.xlsx', engine='openpyxl') as file:
            dfs.clientes.to_excel(file, sheet_name='Clientes', index=False)
            dfs.ventas.to_excel(file, sheet_name='Ventas', index=False)
            dfs.tickets.to_excel(file, sheet_name='Tickets', index=False)
            dfs.inventario.to_excel(file, sheet_name='Inventario', index=False)
            dfs_final.to_excel(file, sheet_name='Agrupado', index=False)

    def merge(self, dfs: ETLModelDataframe) -> DataFrame: 
        dfs_final = dfs.clientes.merge(dfs.ventas, on='id_cliente', how='left').merge(dfs.tickets, on='id_cliente', how='left')
        return dfs_final