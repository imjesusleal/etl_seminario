"""
Punto 7 - EDA NovaShop (Matplotlib + Seaborn)

Lee el warehouse analitico y genera:
- estadisticas descriptivas
- visualizaciones en output/eda/
- conclusiones alineadas a la hipotesis
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "output" / "novashop_analitico.db"
OUT_DIR = ROOT / "output" / "eda"


def load_tables(db_path: Path = DB_PATH) -> dict[str, pd.DataFrame]:
    if not db_path.exists():
        raise FileNotFoundError(
            f"No existe {db_path}. Ejecuta primero: python main.py"
        )
    with sqlite3.connect(db_path) as conn:
        return {
            "cliente_resumen": pd.read_sql_query("SELECT * FROM cliente_resumen", conn),
            "fact_ventas": pd.read_sql_query("SELECT * FROM fact_ventas", conn),
            "fact_tickets": pd.read_sql_query("SELECT * FROM fact_tickets", conn),
            "dim_inventario": pd.read_sql_query("SELECT * FROM dim_inventario", conn),
        }


def prepare_dates(ventas: pd.DataFrame, tickets: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ventas = ventas.copy()
    tickets = tickets.copy()
    ventas["fecha"] = pd.to_datetime(ventas["fecha"], errors="coerce")
    tickets["fecha_creacion"] = pd.to_datetime(tickets["fecha_creacion"], errors="coerce")
    ventas["anio_mes"] = ventas["fecha"].dt.to_period("M").astype(str)
    tickets["anio_mes"] = tickets["fecha_creacion"].dt.to_period("M").astype(str)
    return ventas, tickets


def _segmento_valor(monto: float) -> str:
    if monto <= 0:
        return "sin_ventas"
    if monto < 500:
        return "bajo"
    if monto < 1500:
        return "medio"
    return "alto"


def build_eda_frame(resumen: pd.DataFrame) -> pd.DataFrame:
    df = resumen.copy()
    df["segmento_valor"] = df["monto_total_ventas"].apply(_segmento_valor)
    df["pct_sin_resolucion"] = df.apply(
        lambda r: (100.0 * r["tickets_sin_resolucion"] / r["cantidad_tickets"])
        if r["cantidad_tickets"] > 0
        else 0.0,
        axis=1,
    )
    df["tiene_ticket"] = (df["cantidad_tickets"] > 0).astype(int)
    return df


def save_describe(tables: dict[str, pd.DataFrame], out_dir: Path) -> dict:
    perfil = {}
    for name, df in tables.items():
        perfil[name] = {
            "filas": int(len(df)),
            "columnas": int(df.shape[1]),
            "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        }
        desc = df.describe(include="all").transpose()
        desc.to_csv(out_dir / f"describe_{name}.csv", encoding="utf-8-sig")
    (out_dir / "perfil_datasets.json").write_text(
        json.dumps(perfil, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return perfil


def plot_distributions(df: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(df.loc[df["monto_total_ventas"] > 0, "monto_total_ventas"], bins=30, ax=axes[0], color="#4F81BD")
    axes[0].set_title("Distribucion monto_total_ventas (>0)")
    axes[0].set_xlabel("Monto total ventas")

    sns.histplot(df["cantidad_tickets"], bins=15, discrete=True, ax=axes[1], color="#C0504D")
    axes[1].set_title("Distribucion cantidad_tickets")
    axes[1].set_xlabel("Tickets por cliente")
    fig.tight_layout()
    fig.savefig(out_dir / "01_distribuciones_numericas.png", dpi=140)
    plt.close(fig)


def plot_categoricas(tickets: pd.DataFrame, inventario: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    tema_order = tickets["tema"].value_counts().index
    sns.countplot(data=tickets, y="tema", order=tema_order, ax=axes[0], color="#4F81BD")
    axes[0].set_title("Tickets por tema")

    estado_order = tickets["estado"].value_counts().index
    sns.countplot(data=tickets, x="estado", order=estado_order, ax=axes[1], color="#9BBB59")
    axes[1].set_title("Tickets por estado")
    fig.tight_layout()
    fig.savefig(out_dir / "02_categoricas_tickets.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    cat_order = inventario["categoria"].value_counts().index
    sns.countplot(data=inventario, x="categoria", order=cat_order, ax=ax, color="#8064A2")
    ax.set_title("Inventario por categoria (auxiliar)")
    fig.tight_layout()
    fig.savefig(out_dir / "03_categoricas_inventario.png", dpi=140)
    plt.close(fig)


def plot_temporal(ventas: pd.DataFrame, tickets: pd.DataFrame, out_dir: Path) -> None:
    ventas_m = ventas.groupby("anio_mes", as_index=False).agg(monto=("total_venta", "sum"), ventas=("id_venta", "count"))
    tickets_m = tickets.groupby("anio_mes", as_index=False).agg(tickets=("ticket_id", "count"))
    serie = ventas_m.merge(tickets_m, on="anio_mes", how="outer").fillna(0).sort_values("anio_mes")

    fig, ax1 = plt.subplots(figsize=(11, 4))
    ax1.plot(serie["anio_mes"], serie["monto"], marker="o", color="#4F81BD", label="Monto ventas")
    ax1.set_ylabel("Monto ventas")
    ax1.set_xlabel("Anio-mes")
    ax1.tick_params(axis="x", rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(serie["anio_mes"], serie["tickets"], marker="s", color="#C0504D", label="Tickets")
    ax2.set_ylabel("Tickets")

    ax1.set_title("Evolucion temporal: ventas vs tickets")
    fig.tight_layout()
    fig.savefig(out_dir / "04_evolucion_temporal.png", dpi=140)
    plt.close(fig)
    serie.to_csv(out_dir / "serie_temporal_ventas_tickets.csv", index=False, encoding="utf-8-sig")


def plot_hipotesis(df: pd.DataFrame, out_dir: Path) -> dict:
    con_ventas = df[df["monto_total_ventas"] > 0].copy()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.boxplot(
        data=con_ventas,
        x="segmento_valor",
        y="cantidad_tickets",
        order=["bajo", "medio", "alto"],
        ax=axes[0],
        color="#4F81BD",
    )
    axes[0].set_title("Tickets por segmento de valor")

    sns.scatterplot(
        data=con_ventas,
        x="monto_total_ventas",
        y="tickets_sin_resolucion",
        hue="segmento_valor",
        ax=axes[1],
        alpha=0.7,
    )
    axes[1].set_title("Valor vs tickets sin resolucion")
    fig.tight_layout()
    fig.savefig(out_dir / "05_hipotesis_valor_vs_tickets.png", dpi=140)
    plt.close(fig)

    corr_cols = [
        "monto_total_ventas",
        "cantidad_ventas",
        "cantidad_tickets",
        "tickets_abiertos",
        "tickets_sin_resolucion",
        "pct_sin_resolucion",
    ]
    corr = con_ventas[corr_cols].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", ax=ax)
    ax.set_title("Correlaciones (clientes con ventas)")
    fig.tight_layout()
    fig.savefig(out_dir / "06_correlaciones.png", dpi=140)
    plt.close(fig)
    corr.to_csv(out_dir / "correlaciones_clientes_con_ventas.csv", encoding="utf-8-sig")

    resumen_seg = (
        con_ventas.groupby("segmento_valor")
        .agg(
            clientes=("id_cliente", "count"),
            monto_promedio=("monto_total_ventas", "mean"),
            tickets_promedio=("cantidad_tickets", "mean"),
            sin_resolucion_promedio=("tickets_sin_resolucion", "mean"),
            pct_con_ticket=("tiene_ticket", "mean"),
        )
        .reindex(["bajo", "medio", "alto"])
    )
    resumen_seg.to_csv(out_dir / "resumen_por_segmento_valor.csv", encoding="utf-8-sig")

    corr_valor_tickets = float(con_ventas["monto_total_ventas"].corr(con_ventas["cantidad_tickets"]))
    corr_valor_sin_res = float(con_ventas["monto_total_ventas"].corr(con_ventas["tickets_sin_resolucion"]))
    return {
        "corr_monto_vs_tickets": round(corr_valor_tickets, 4),
        "corr_monto_vs_sin_resolucion": round(corr_valor_sin_res, 4),
        "resumen_segmentos": resumen_seg.round(3).to_dict(orient="index"),
    }


def plot_outliers(ventas: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.boxplot(data=ventas, y="total_venta", ax=axes[0], color="#4F81BD")
    axes[0].set_title("Boxplot total_venta")

    if "es_outlier_monto" in ventas.columns:
        sns.countplot(data=ventas, x="es_outlier_monto", ax=axes[1], color="#C0504D")
        axes[1].set_title("Flag es_outlier_monto (0/1)")
        axes[1].set_xlabel("Es outlier")
    fig.tight_layout()
    fig.savefig(out_dir / "07_outliers_ventas.png", dpi=140)
    plt.close(fig)


def build_conclusions(metrics: dict, perfil: dict) -> str:
    corr_t = metrics["corr_monto_vs_tickets"]
    corr_s = metrics["corr_monto_vs_sin_resolucion"]
    segs = metrics["resumen_segmentos"]

    if abs(corr_t) < 0.15 and abs(corr_s) < 0.15:
        hipotesis = (
            "No se observa una relacion lineal fuerte entre mayor valor comercial y mayor carga de tickets "
            f"(corr monto-tickets={corr_t}; corr monto-sin_resolucion={corr_s}). "
            "La hipotesis global no se confirma de forma clara."
        )
    elif corr_t > 0.15 or corr_s > 0.15:
        hipotesis = (
            "Hay indicios de asociacion positiva entre valor y soporte "
            f"(corr monto-tickets={corr_t}; corr monto-sin_resolucion={corr_s})."
        )
    else:
        hipotesis = (
            "La asociacion entre valor y soporte tiende a ser nula/negativa "
            f"(corr monto-tickets={corr_t}; corr monto-sin_resolucion={corr_s})."
        )

    lineas = [
        "# Conclusiones EDA - NovaShop",
        "",
        "## Hipotesis",
        "¿Los clientes de mayor valor concentran mas tickets abiertos/sin resolucion?",
        "",
        f"- {hipotesis}",
        "",
        "## Hallazgos exploratorios",
        f"- Datasets perfilados: {', '.join(perfil.keys())}.",
        f"- Segmento alto: tickets promedio={segs.get('alto', {}).get('tickets_promedio')}, "
        f"sin resolucion promedio={segs.get('alto', {}).get('sin_resolucion_promedio')}.",
        f"- Segmento bajo: tickets promedio={segs.get('bajo', {}).get('tickets_promedio')}, "
        f"sin resolucion promedio={segs.get('bajo', {}).get('sin_resolucion_promedio')}.",
        "- Existen clientes alto-valor con tickets pendientes: utiles para priorizacion operativa, "
        "aunque no impliquen concentracion sistematica.",
        "- La serie temporal muestra dinamica de ventas a lo largo del anio; tickets cubren una ventana mas corta.",
        "",
        "## Limitaciones",
        "- Queda un % de ventas/tickets huerfanos vs CRM (integridad parcial a proposito).",
        "- Inventario no se cruza con ventas por falta de clave de producto.",
        "",
        "## Proximos pasos",
        "- Dashboard Power BI sobre cliente_resumen + vistas SQL.",
        "- Monitorear clientes alto-valor con tickets abiertos/sin resolucion.",
    ]
    return "\n".join(lineas)


def run_eda() -> Path:
    sns.set_theme(style="whitegrid")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tables = load_tables()
    ventas, tickets = prepare_dates(tables["fact_ventas"], tables["fact_tickets"])
    tables["fact_ventas"] = ventas
    tables["fact_tickets"] = tickets
    df = build_eda_frame(tables["cliente_resumen"])

    perfil = save_describe(tables, OUT_DIR)
    plot_distributions(df, OUT_DIR)
    plot_categoricas(tickets, tables["dim_inventario"], OUT_DIR)
    plot_temporal(ventas, tickets, OUT_DIR)
    metrics = plot_hipotesis(df, OUT_DIR)
    plot_outliers(ventas, OUT_DIR)

    conclusions = build_conclusions(metrics, perfil)
    (OUT_DIR / "conclusiones_eda.md").write_text(conclusions, encoding="utf-8")
    (OUT_DIR / "metricas_hipotesis.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(conclusions)
    print(f"\nFiguras y tablas guardadas en: {OUT_DIR}")
    return OUT_DIR


if __name__ == "__main__":
    run_eda()
