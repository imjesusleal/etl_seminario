"""
Realinea id_cliente de ventas/tickets con el CRM (clientes.db).

Objetivo pedagogico:
- ~75% de los IDs operativos matchean el maestro
- ~25% quedan huerfanos a proposito (calidad / integridad referencial)

Uso:
  python scripts/realinear_ids_clientes.py
"""

from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / "datos" / "backup_pre_realineacion"
SEED = 42
PCT_MATCH = 0.75


def main() -> None:
    rng = np.random.default_rng(SEED)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    ventas_path = ROOT / "datos_ventas.csv"
    tickets_path = ROOT / "soporte_tecnico.json"
    db_path = ROOT / "clientes.db"

    # Backup una sola vez
    for src in [ventas_path, tickets_path]:
        dst = BACKUP_DIR / src.name
        if not dst.exists():
            shutil.copy2(src, dst)

    with sqlite3.connect(db_path) as conn:
        crm_ids = pd.read_sql("SELECT ID_Cliente AS id_cliente FROM CLIENTES", conn)[
            "id_cliente"
        ].astype(int).tolist()

    ventas = pd.read_csv(ventas_path)
    with open(tickets_path, "r", encoding="utf-8") as f:
        tickets_raw = json.load(f)
    tickets = pd.DataFrame(tickets_raw)

    # Frecuencia por ID operativo (priorizar los mas usados para subir % de filas con match)
    freq = (
        pd.concat(
            [
                ventas["id_cliente"].astype(int).rename("id"),
                tickets["cliente_id"].astype(int).rename("id"),
            ]
        )
        .value_counts()
        .sort_values(ascending=False)
    )
    unique_ops = freq.index.astype(int).tolist()

    n_match = min(int(len(unique_ops) * PCT_MATCH), len(crm_ids))
    # Tomamos los IDs mas frecuentes (con leve shuffle dentro del top para no ser 100% determinista por orden)
    top_ids = unique_ops[:n_match]
    top_ids = list(rng.permutation(top_ids))
    crm_assigned = list(rng.permutation(crm_ids))[:n_match]

    mapping: dict[int, int] = {
        int(old): int(new) for old, new in zip(top_ids, crm_assigned)
    }

    orphan_base = 9000
    orphan_i = 1
    for old in unique_ops:
        if old not in mapping:
            mapping[old] = orphan_base + orphan_i
            orphan_i += 1

    ventas["id_cliente"] = ventas["id_cliente"].astype(int).map(mapping)
    tickets["cliente_id"] = tickets["cliente_id"].astype(int).map(mapping)

    ventas.to_csv(ventas_path, index=False)
    with open(tickets_path, "w", encoding="utf-8") as f:
        json.dump(tickets.to_dict(orient="records"), f, ensure_ascii=False, indent=4)

    # Metricas
    crm_set = set(crm_ids)
    ventas_match = ventas["id_cliente"].isin(crm_set).mean()
    tickets_match = tickets["cliente_id"].isin(crm_set).mean()
    overlap_ids = len(set(ventas["id_cliente"]) & set(tickets["cliente_id"]) & crm_set)

    print("Realineacion OK")
    print(f"  IDs operativos unicos originales: {len(unique_ops)}")
    print(f"  IDs mapeados a CRM: {n_match} ({PCT_MATCH:.0%})")
    print(f"  IDs huerfanos: {len(unique_ops) - n_match}")
    print(f"  % filas ventas con CRM: {ventas_match:.1%}")
    print(f"  % filas tickets con CRM: {tickets_match:.1%}")
    print(f"  IDs en CRM ∩ ventas ∩ tickets: {overlap_ids}")
    print(f"  Backup en: {BACKUP_DIR}")
    print("  Siguiente paso: python main.py")


if __name__ == "__main__":
    main()
