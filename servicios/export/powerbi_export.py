"""
Exporta CSVs limpios desde el warehouse analitico para Power BI.

Salida: output/powerbi/
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "output" / "novashop_analitico.db"
DEFAULT_OUT = ROOT / "output" / "powerbi"
VIEWS_SQL = ROOT / "sql" / "04_vistas_intermedias.sql"

# Tablas base del modelo
TABLES = [
    "dim_clientes",
    "fact_ventas",
    "fact_tickets",
    "dim_inventario",
    "cliente_resumen",
    "calidad_reporte",
]

# Vistas analiticas (se crean/actualizan antes de exportar)
VIEWS = [
    "v_cliente_valor_soporte",
    "v_tickets_pendientes_alto_valor",
    "v_ventas_mensuales",
]


def apply_views(conn: sqlite3.Connection, views_sql: Path = VIEWS_SQL) -> None:
    if not views_sql.exists():
        raise FileNotFoundError(f"No existe el SQL de vistas: {views_sql}")
    conn.executescript(views_sql.read_text(encoding="utf-8"))
    conn.commit()


def _export_relation(conn: sqlite3.Connection, name: str, out_dir: Path) -> int:
    df = pd.read_sql_query(f"SELECT * FROM {name}", conn)
    path = out_dir / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return len(df)


def build_kpis(conn: sqlite3.Connection) -> pd.DataFrame:
    resumen = pd.read_sql_query("SELECT * FROM cliente_resumen", conn)
    tickets = pd.read_sql_query("SELECT * FROM fact_tickets", conn)
    ventas = pd.read_sql_query("SELECT * FROM fact_ventas", conn)

    con_ventas = resumen[resumen["monto_total_ventas"] > 0]
    alto = con_ventas[con_ventas["monto_total_ventas"] >= con_ventas["monto_total_ventas"].mean()]

    kpis = [
        {"kpi": "monto_total_ventas", "valor": float(ventas["total_venta"].sum()), "descripcion": "Facturacion total"},
        {"kpi": "cantidad_ventas", "valor": int(len(ventas)), "descripcion": "Cantidad de ventas"},
        {"kpi": "clientes_con_ventas", "valor": int(con_ventas["id_cliente"].nunique()), "descripcion": "Clientes con al menos una venta"},
        {"kpi": "cantidad_tickets", "valor": int(len(tickets)), "descripcion": "Tickets totales"},
        {
            "kpi": "pct_tickets_sin_resolucion",
            "valor": round(100.0 * tickets["sin_resolucion"].mean(), 2) if len(tickets) else 0,
            "descripcion": "% tickets sin resolucion",
        },
        {
            "kpi": "tickets_pendientes",
            "valor": int(tickets["estado"].isin(["Abierto", "En progreso"]).sum()),
            "descripcion": "Tickets Abierto + En progreso",
        },
        {
            "kpi": "clientes_alto_valor_con_ticket_pendiente",
            "valor": int(
                alto[
                    (alto["tickets_abiertos"] + alto["tickets_en_progreso"] > 0)
                    | (alto["tickets_sin_resolucion"] > 0)
                ]["id_cliente"].nunique()
            ),
            "descripcion": "Alto valor con soporte pendiente/sin resolucion",
        },
        {
            "kpi": "pct_ventas_huerfanas_crm",
            "valor": round(100.0 * (1 - ventas["en_maestro_clientes"].mean()), 2) if len(ventas) else 0,
            "descripcion": "% ventas sin match en CRM",
        },
    ]
    return pd.DataFrame(kpis)


def export_powerbi_csvs(
    db_path: str | Path = DEFAULT_DB,
    out_dir: str | Path = DEFAULT_OUT,
) -> Path:
    db_path = Path(db_path)
    out_dir = Path(out_dir)

    if not db_path.exists():
        raise FileNotFoundError(
            f"No existe el warehouse {db_path}. Ejecuta primero: python main.py"
        )

    out_dir.mkdir(parents=True, exist_ok=True)

    exported: dict[str, int] = {}
    with sqlite3.connect(db_path) as conn:
        apply_views(conn)
        for name in TABLES + VIEWS:
            exported[name] = _export_relation(conn, name, out_dir)

        kpis = build_kpis(conn)
        kpis.to_csv(out_dir / "kpis.csv", index=False, encoding="utf-8-sig")
        exported["kpis"] = len(kpis)

    manifest = pd.DataFrame(
        [{"dataset": k, "filas": v, "archivo": f"{k}.csv"} for k, v in exported.items()]
    )
    manifest.to_csv(out_dir / "manifest.csv", index=False, encoding="utf-8-sig")

    readme = "\n".join(
        [
            "# Datasets Power BI — NovaShop",
            "",
            "CSVs exportados desde `novashop_analitico.db` (post-ETL).",
            "",
            "## Recomendado para el modelo",
            "- Hechos: `fact_ventas.csv`, `fact_tickets.csv`",
            "- Dimensiones: `dim_clientes.csv`, `dim_inventario.csv`",
            "- Tabla analitica principal: `cliente_resumen.csv` o `v_cliente_valor_soporte.csv`",
            "- KPIs: `kpis.csv`",
            "- Soporte prioritario: `v_tickets_pendientes_alto_valor.csv`",
            "- Serie temporal: `v_ventas_mensuales.csv`",
            "",
            "Encoding: UTF-8 with BOM (`utf-8-sig`) para Excel/Power BI en Windows.",
            "",
            "## Relacion sugerida",
            "`dim_clientes[id_cliente] 1—* fact_ventas[id_cliente]`",
            "`dim_clientes[id_cliente] 1—* fact_tickets[id_cliente]`",
            "`cliente_resumen[id_cliente]` como tabla puente/analitica",
            "",
            "Nota: inventario no se relaciona a ventas (sin clave de producto confiable).",
        ]
    )
    (out_dir / "README_POWERBI.md").write_text(readme, encoding="utf-8")
    return out_dir


if __name__ == "__main__":
    destino = export_powerbi_csvs()
    print(f"CSVs Power BI exportados en: {destino}")
