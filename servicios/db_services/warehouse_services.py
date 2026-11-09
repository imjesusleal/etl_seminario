import os

from pandas import DataFrame

from datos.sqlite.context.warehouse_context import WarehouseContext, build_warehouse_context
from models.etl_model import ETLModelDataframe


class WarehouseServices:
    """Carga el modelo analitico consolidado en SQLite."""

    def __init__(self):
        self.__schema_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../datos/sqlite/schema/warehouse_schema.sql",
            )
        )

    def load(
        self,
        dfs: ETLModelDataframe,
        cliente_resumen: DataFrame,
        calidad_reporte: DataFrame | None = None,
    ) -> str:
        ctx: WarehouseContext = build_warehouse_context()
        ctx.apply_schema(self.__schema_path)
        conn = ctx.connection

        self._to_sql(dfs.clientes, "dim_clientes", conn)
        self._to_sql(dfs.ventas, "fact_ventas", conn)
        self._to_sql(dfs.tickets, "fact_tickets", conn)
        self._to_sql(dfs.inventario, "dim_inventario", conn)
        self._to_sql(cliente_resumen, "cliente_resumen", conn)
        if calidad_reporte is not None and not calidad_reporte.empty:
            self._to_sql(calidad_reporte, "calidad_reporte", conn)

        conn.commit()
        db_path = conn.execute("PRAGMA database_list").fetchone()[2]
        ctx.close()
        return db_path

    @staticmethod
    def _to_sql(df: DataFrame, table_name: str, conn) -> None:
        prepared = df.copy()
        datetime_cols = prepared.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns
        for col in datetime_cols:
            prepared[col] = prepared[col].dt.strftime("%Y-%m-%d %H:%M:%S")
        prepared = prepared.convert_dtypes()
        prepared.to_sql(table_name, conn, if_exists="append", index=False)


warehouse_service = WarehouseServices()
