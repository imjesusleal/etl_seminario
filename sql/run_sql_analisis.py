"""Ejecuta las consultas analiticas del punto 4 contra novashop_analitico.db."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "output" / "novashop_analitico.db"
SQL_DIR = Path(__file__).resolve().parent

FILES = [
    "04_vistas_intermedias.sql",
    "01_calidad_datos.sql",
    "02_metricas_negocio.sql",
    "03_hipotesis_valor_vs_soporte.sql",
]


def split_statements(sql_text: str) -> list[str]:
    # Quita comentarios de linea y separa por ;
    without_line_comments = re.sub(r"--.*?$", "", sql_text, flags=re.MULTILINE)
    parts = [p.strip() for p in without_line_comments.split(";")]
    return [p for p in parts if p]


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"No existe {DB_PATH}. Ejecuta primero: python main.py"
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        for file_name in FILES:
            path = SQL_DIR / file_name
            print("\n" + "=" * 72)
            print(f"ARCHIVO: {file_name}")
            print("=" * 72)
            statements = split_statements(path.read_text(encoding="utf-8"))

            for idx, statement in enumerate(statements, start=1):
                preview = " ".join(statement.split())[:110]
                print(f"\n-- Consulta {idx}: {preview}...")
                cur = conn.execute(statement)
                if statement.lstrip().upper().startswith(("SELECT", "WITH")):
                    rows = cur.fetchall()
                    if not rows:
                        print("(sin filas)")
                        continue
                    headers = rows[0].keys()
                    print(" | ".join(headers))
                    for row in rows[:25]:
                        print(" | ".join(str(row[h]) for h in headers))
                    if len(rows) > 25:
                        print(f"... ({len(rows) - 25} filas mas)")
                else:
                    conn.commit()
                    print("(ok)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
