import os

from models.etl_model import ETLModelCommand, ETLModelDataframe
from pandas import DataFrame
import pandas as pd

from servicios.db_services.warehouse_services import warehouse_service


class ETLService():
    TEMAS_VALIDOS = {
        "consulta general": "Consulta general",
        "error en el sistema": "Error en el sistema",
        "problema de acceso": "Problema de acceso",
        "problema de facturacion": "Problema de facturación",
        "problema de facturación": "Problema de facturación",
    }
    ESTADOS_VALIDOS = {
        "abierto": "Abierto",
        "en progreso": "En progreso",
        "cerrado": "Cerrado",
    }
    CATEGORIAS_VALIDAS = {
        "electronica": "Electrónica",
        "electrónica": "Electrónica",
        "hogar": "Hogar",
        "juguetes": "Juguetes",
        "ropa": "Ropa",
        "alimentos": "Alimentos",
    }

    def __init__(self, etl_data: ETLModelCommand):
        self.etl_data = etl_data
        self.calidad_reporte: DataFrame = DataFrame(
            columns=["hallazgo", "severidad", "metrica", "valor_antes", "accion", "valor_despues"]
        )

    def transform(self) -> ETLModelDataframe:
        clientes_df = DataFrame(self.etl_data.clientes)
        tickets_df = DataFrame(self.etl_data.tickets)
        ventas_df = DataFrame(self.etl_data.ventas)
        inventario_df = DataFrame(self.etl_data.inventario)
        return ETLModelDataframe(clientes_df, tickets_df, ventas_df, inventario_df)

    def normalizar(self, dfs: ETLModelDataframe) -> None:
        """Homogeneiza nombres/tipos para el modelo analitico."""
        if "cliente_id" in dfs.tickets.columns and "id_cliente" not in dfs.tickets.columns:
            dfs.tickets = dfs.tickets.rename(columns={"cliente_id": "id_cliente"})

        rename_inventario = {
            "ID_Producto": "id_producto",
            "Nombre_Producto": "nombre_producto",
            "Categoria": "categoria",
            "Stock_Actual": "stock_actual",
            "Precio_Costo": "precio_costo",
            "Proveedor": "proveedor",
        }
        dfs.inventario = dfs.inventario.rename(
            columns={k: v for k, v in rename_inventario.items() if k in dfs.inventario.columns}
        )

        dfs.clientes["id_cliente"] = pd.to_numeric(dfs.clientes["id_cliente"], errors="coerce").astype("Int64")
        dfs.ventas["id_cliente"] = pd.to_numeric(dfs.ventas["id_cliente"], errors="coerce").astype("Int64")
        dfs.tickets["id_cliente"] = pd.to_numeric(dfs.tickets["id_cliente"], errors="coerce").astype("Int64")
        dfs.inventario["id_producto"] = pd.to_numeric(dfs.inventario["id_producto"], errors="coerce").astype("Int64")

        dfs.ventas["cantidad"] = pd.to_numeric(dfs.ventas["cantidad"], errors="coerce")
        dfs.ventas["precio_unitario"] = pd.to_numeric(dfs.ventas["precio_unitario"], errors="coerce")
        dfs.inventario["stock_actual"] = pd.to_numeric(dfs.inventario["stock_actual"], errors="coerce")
        dfs.inventario["precio_costo"] = pd.to_numeric(dfs.inventario["precio_costo"], errors="coerce")

        for col in ["producto"]:
            if col in dfs.ventas.columns:
                dfs.ventas[col] = dfs.ventas[col].astype(str).str.strip()

    def limpiar(self, dfs: ETLModelDataframe) -> None:
        before = {
            "clientes": len(dfs.clientes),
            "ventas": len(dfs.ventas),
            "tickets": len(dfs.tickets),
            "inventario": len(dfs.inventario),
        }

        dfs.clientes = dfs.clientes.drop_duplicates(subset=["id_cliente"], keep="first")
        dfs.ventas = dfs.ventas.drop_duplicates(subset=["id_venta"], keep="first")
        dfs.tickets = dfs.tickets.drop_duplicates(subset=["ticket_id"], keep="first")
        dfs.inventario = dfs.inventario.drop_duplicates(subset=["id_producto"], keep="first")

        # Filas sin clave primaria usable
        dfs.clientes = dfs.clientes.dropna(subset=["id_cliente"])
        dfs.ventas = dfs.ventas.dropna(subset=["id_venta", "id_cliente"])
        dfs.tickets = dfs.tickets.dropna(subset=["ticket_id", "id_cliente"])
        dfs.inventario = dfs.inventario.dropna(subset=["id_producto"])

        after = {
            "clientes": len(dfs.clientes),
            "ventas": len(dfs.ventas),
            "tickets": len(dfs.tickets),
            "inventario": len(dfs.inventario),
        }
        self._add_calidad(
            hallazgo="Duplicados / filas sin clave",
            severidad="media",
            metrica="registros_por_tabla",
            valor_antes=str(before),
            accion="drop_duplicates por PK + dropna de claves",
            valor_despues=str(after),
        )

    def estandarizar_categorias(self, dfs: ETLModelDataframe) -> None:
        temas_antes = sorted(dfs.tickets["tema"].dropna().astype(str).unique().tolist())
        estados_antes = sorted(dfs.tickets["estado"].dropna().astype(str).unique().tolist())
        cats_antes = sorted(dfs.inventario["categoria"].dropna().astype(str).unique().tolist())

        dfs.tickets["tema"] = dfs.tickets["tema"].map(self._norm_tema)
        dfs.tickets["estado"] = dfs.tickets["estado"].map(self._norm_estado)
        dfs.inventario["categoria"] = dfs.inventario["categoria"].map(self._norm_categoria)

        self._add_calidad(
            hallazgo="Categorias inconsistentes / casing",
            severidad="baja",
            metrica="tema_estado_categoria",
            valor_antes=str({"temas": temas_antes, "estados": estados_antes, "categorias": cats_antes}),
            accion="Normalizacion a catalogo controlado (strip + mapa canonico)",
            valor_despues=str(
                {
                    "temas": sorted(dfs.tickets["tema"].dropna().unique().tolist()),
                    "estados": sorted(dfs.tickets["estado"].dropna().unique().tolist()),
                    "categorias": sorted(dfs.inventario["categoria"].dropna().unique().tolist()),
                }
            ),
        )

    def handle_null(self, dfs: ETLModelDataframe) -> None:
        nulos_resolucion = int(
            dfs.tickets["resolucion"].isna().sum()
            + (dfs.tickets["resolucion"].astype(str).str.strip() == "").sum()
        )

        dfs.tickets["sin_resolucion"] = (
            dfs.tickets["resolucion"].isna()
            | (dfs.tickets["resolucion"].astype(str).str.strip() == "")
            | (dfs.tickets["resolucion"].astype(str).str.strip().str.lower() == "sin resolucion")
            | (dfs.tickets["resolucion"].astype(str).str.strip().str.lower() == "none")
            | (dfs.tickets["resolucion"].astype(str).str.strip().str.lower() == "nan")
        ).astype(int)

        dfs.tickets["resolucion"] = dfs.tickets["resolucion"].where(
            ~dfs.tickets["sin_resolucion"].astype(bool),
            "Sin resolucion",
        )

        for col in ["nombre", "email", "telefono", "direccion"]:
            if col in dfs.clientes.columns:
                dfs.clientes[col] = dfs.clientes[col].fillna("Sin dato")

        pct = round(100.0 * nulos_resolucion / max(len(dfs.tickets), 1), 2)
        self._add_calidad(
            hallazgo="Valores nulos en resolucion de tickets",
            severidad="alta",
            metrica="pct_tickets_sin_resolucion",
            valor_antes=f"{nulos_resolucion} nulos/vacios (~{pct}%)",
            accion="Flag sin_resolucion=1 y placeholder 'Sin resolucion' (sin borrar filas)",
            valor_despues=f"flag_activos={int(dfs.tickets['sin_resolucion'].sum())}",
        )

    def format_handling(self, dfs: ETLModelDataframe) -> None:
        for df_name, col in [
            ("clientes", "fecha_registro"),
            ("ventas", "fecha"),
            ("tickets", "fecha_creacion"),
        ]:
            df = getattr(dfs, df_name)
            before_invalid = int(pd.to_datetime(df[col], errors="coerce").isna().sum())
            df[col] = pd.to_datetime(df[col], errors="coerce")
            after_invalid = int(df[col].isna().sum())
            if before_invalid or after_invalid:
                self._add_calidad(
                    hallazgo=f"Fechas mal formateadas en {df_name}.{col}",
                    severidad="media" if after_invalid else "baja",
                    metrica="fechas_invalidas",
                    valor_antes=str(before_invalid),
                    accion="to_datetime(errors='coerce')",
                    valor_despues=str(after_invalid),
                )

    def marcar_integridad_referencial(self, dfs: ETLModelDataframe) -> None:
        ids_maestro = set(dfs.clientes["id_cliente"].dropna().astype(int).tolist())

        dfs.ventas["en_maestro_clientes"] = dfs.ventas["id_cliente"].isin(ids_maestro).astype(int)
        dfs.tickets["en_maestro_clientes"] = dfs.tickets["id_cliente"].isin(ids_maestro).astype(int)

        ventas_huerfanas = int((dfs.ventas["en_maestro_clientes"] == 0).sum())
        tickets_huerfanos = int((dfs.tickets["en_maestro_clientes"] == 0).sum())

        self._add_calidad(
            hallazgo="Integridad referencial cliente (ventas/tickets vs CRM)",
            severidad="alta",
            metrica="registros_huerfanos",
            valor_antes=f"ventas_huerfanas={ventas_huerfanas}; tickets_huerfanos={tickets_huerfanos}",
            accion="No se eliminan. Se marca en_maestro_clientes=0/1 para analisis y auditoria",
            valor_despues="flags persistidos en fact_ventas y fact_tickets",
        )

        # Inventario vs ventas: sin clave confiable
        productos_venta = set(dfs.ventas["producto"].dropna().astype(str).str.lower().unique())
        productos_inv = set(dfs.inventario["nombre_producto"].dropna().astype(str).str.lower().unique())
        overlap = len(productos_venta.intersection(productos_inv))
        self._add_calidad(
            hallazgo="Integracion producto ventas-inventario",
            severidad="alta",
            metrica="overlap_nombres_producto",
            valor_antes=f"ventas_unicos={len(productos_venta)}; inventario_unicos={len(productos_inv)}; overlap={overlap}",
            accion="Inventario queda auxiliar; no se fuerza join a ventas",
            valor_despues="sin FK producto en el modelo analitico",
        )

    def detectar_outliers(self, dfs: ETLModelDataframe) -> None:
        monto = dfs.ventas["total_venta"]
        q1 = monto.quantile(0.25)
        q3 = monto.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        dfs.ventas["es_outlier_monto"] = ((monto < lower) | (monto > upper)).astype(int)
        outliers = int(dfs.ventas["es_outlier_monto"].sum())

        self._add_calidad(
            hallazgo="Valores atipicos en total_venta",
            severidad="media",
            metrica="outliers_iqr_total_venta",
            valor_antes=f"q1={round(q1,2)}; q3={round(q3,2)}; lower={round(lower,2)}; upper={round(upper,2)}",
            accion="Flag es_outlier_monto=1 (no se eliminan filas)",
            valor_despues=f"outliers={outliers} de {len(dfs.ventas)}",
        )

    def ordenar(self, dfs: ETLModelDataframe) -> None:
        dfs.clientes = dfs.clientes.sort_values(by="id_cliente")
        dfs.ventas = dfs.ventas.sort_values(by="id_cliente")
        dfs.tickets = dfs.tickets.sort_values(by="id_cliente")
        dfs.inventario = dfs.inventario.sort_values(by="id_producto")

    def crear_columna_calculada(self, df: DataFrame) -> None:
        df["total_venta"] = df["precio_unitario"] * df["cantidad"]

    def crear_cliente_resumen(self, dfs: ETLModelDataframe) -> DataFrame:
        ids_clientes = pd.concat(
            [
                dfs.clientes[["id_cliente"]],
                dfs.ventas[["id_cliente"]],
                dfs.tickets[["id_cliente"]],
            ],
            ignore_index=True,
        ).dropna().drop_duplicates()

        ventas_agg = (
            dfs.ventas.groupby("id_cliente", as_index=False)
            .agg(
                cantidad_ventas=("id_venta", "count"),
                monto_total_ventas=("total_venta", "sum"),
            )
        )
        ventas_agg["ticket_promedio"] = (
            ventas_agg["monto_total_ventas"] / ventas_agg["cantidad_ventas"]
        )

        tickets_base = dfs.tickets.copy()
        tickets_base["es_abierto"] = (tickets_base["estado"] == "Abierto").astype(int)
        tickets_base["es_en_progreso"] = (tickets_base["estado"] == "En progreso").astype(int)
        tickets_base["es_cerrado"] = (tickets_base["estado"] == "Cerrado").astype(int)
        if "sin_resolucion" not in tickets_base.columns:
            tickets_base["sin_resolucion"] = 0

        tickets_agg = (
            tickets_base.groupby("id_cliente", as_index=False)
            .agg(
                cantidad_tickets=("ticket_id", "count"),
                tickets_abiertos=("es_abierto", "sum"),
                tickets_en_progreso=("es_en_progreso", "sum"),
                tickets_cerrados=("es_cerrado", "sum"),
                tickets_sin_resolucion=("sin_resolucion", "sum"),
            )
        )

        resumen = (
            ids_clientes.merge(dfs.clientes, on="id_cliente", how="left")
            .merge(ventas_agg, on="id_cliente", how="left")
            .merge(tickets_agg, on="id_cliente", how="left")
        )

        resumen["en_maestro_clientes"] = resumen["nombre"].notna().astype(int)
        for col in [
            "cantidad_ventas",
            "monto_total_ventas",
            "ticket_promedio",
            "cantidad_tickets",
            "tickets_abiertos",
            "tickets_en_progreso",
            "tickets_cerrados",
            "tickets_sin_resolucion",
        ]:
            resumen[col] = resumen[col].fillna(0)

        columnas = [
            "id_cliente",
            "nombre",
            "email",
            "fecha_registro",
            "cantidad_ventas",
            "monto_total_ventas",
            "ticket_promedio",
            "cantidad_tickets",
            "tickets_abiertos",
            "tickets_en_progreso",
            "tickets_cerrados",
            "tickets_sin_resolucion",
            "en_maestro_clientes",
        ]
        return resumen[columnas].sort_values(by="id_cliente").reset_index(drop=True)

    def generar_reporte_calidad(self) -> DataFrame:
        if self.calidad_reporte.empty:
            return self.calidad_reporte
        return self.calidad_reporte.reset_index(drop=True)

    def output(
        self,
        dfs: ETLModelDataframe,
        cliente_resumen: DataFrame,
        calidad_reporte: DataFrame | None = None,
    ) -> None:
        os.makedirs("output", exist_ok=True)
        # Salida primaria para analisis/Power BI: ClienteResumen
        # AgrupadoDetalle queda como evidencia secundaria (puede expandir filas)
        detalle = self.merge(dfs)
        with pd.ExcelWriter("output/output.xlsx", engine="openpyxl") as file:
            cliente_resumen.to_excel(file, sheet_name="ClienteResumen", index=False)
            dfs.clientes.to_excel(file, sheet_name="Clientes", index=False)
            dfs.ventas.to_excel(file, sheet_name="Ventas", index=False)
            dfs.tickets.to_excel(file, sheet_name="Tickets", index=False)
            dfs.inventario.to_excel(file, sheet_name="Inventario", index=False)
            if calidad_reporte is not None and not calidad_reporte.empty:
                calidad_reporte.to_excel(file, sheet_name="Calidad", index=False)
            detalle.to_excel(file, sheet_name="AgrupadoDetalle", index=False)

        if calidad_reporte is not None and not calidad_reporte.empty:
            calidad_reporte.to_csv("output/calidad_reporte.csv", index=False, encoding="utf-8-sig")

    def load_warehouse(
        self,
        dfs: ETLModelDataframe,
        cliente_resumen: DataFrame,
        calidad_reporte: DataFrame | None = None,
    ) -> str:
        return warehouse_service.load(dfs, cliente_resumen, calidad_reporte)

    def merge(self, dfs: ETLModelDataframe) -> DataFrame:
        return dfs.clientes.merge(dfs.ventas, on="id_cliente", how="left").merge(
            dfs.tickets, on="id_cliente", how="left"
        )

    def _add_calidad(
        self,
        hallazgo: str,
        severidad: str,
        metrica: str,
        valor_antes: str,
        accion: str,
        valor_despues: str,
    ) -> None:
        self.calidad_reporte = pd.concat(
            [
                self.calidad_reporte,
                DataFrame(
                    [
                        {
                            "hallazgo": hallazgo,
                            "severidad": severidad,
                            "metrica": metrica,
                            "valor_antes": valor_antes,
                            "accion": accion,
                            "valor_despues": valor_despues,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

    def _norm_tema(self, value):
        if pd.isna(value):
            return "Sin clasificar"
        key = str(value).strip().lower()
        return self.TEMAS_VALIDOS.get(key, str(value).strip().title())

    def _norm_estado(self, value):
        if pd.isna(value):
            return "Sin clasificar"
        key = str(value).strip().lower()
        return self.ESTADOS_VALIDOS.get(key, str(value).strip().title())

    def _norm_categoria(self, value):
        if pd.isna(value):
            return "Sin clasificar"
        key = str(value).strip().lower()
        return self.CATEGORIAS_VALIDAS.get(key, str(value).strip().title())
