# Documentación técnica — NovaShop

Complemento del [`README.md`](./README.md) (presentación) y de [`SETUP.md`](./SETUP.md) (cómo correr).

---

## 1. Fuentes y diccionario

| Dominio | Archivo | Formato |
|---------|---------|--------|
| Clientes | `clientes.db` (tabla `CLIENTES`) | SQLite |
| Ventas | `datos_ventas.csv` | CSV |
| Tickets | `soporte_tecnico.json` | JSON |
| Inventario | `inventario.xlsx` | Excel |

### Clientes
`ID_Cliente`, `Nombre`, `Email`, `Telefono`, `Direccion`, `Fecha_Registro`

### Ventas
`id_venta`, `fecha`, `producto`, `cantidad`, `precio_unitario`, `id_cliente`

### Tickets
`ticket_id`, `fecha_creacion`, `cliente_id` → normalizado a `id_cliente`, `tema`, `estado`, `resolucion`

### Inventario
`ID_Producto`, `Nombre_Producto`, `Categoria`, `Stock_Actual`, `Precio_Costo`, `Proveedor`  
→ normalizado a snake_case en el warehouse.

### Realineación de IDs
Script: `scripts/realinear_ids_clientes.py`  
Backup: `datos/backup_pre_realineacion/`  
Resultado: ~76% filas ventas/tickets con match CRM; ~24% huérfanos intencionales.

---

## 2. Modelo analítico (destino ETL)

SQLite: `output/novashop_analitico.db`  
Schema: `datos/sqlite/schema/warehouse_schema.sql`

| Tabla | Rol |
|-------|-----|
| `dim_clientes` | Dimensión clientes |
| `fact_ventas` | Hecho ventas (+ `total_venta`, flags calidad) |
| `fact_tickets` | Hecho tickets (+ flags calidad) |
| `dim_inventario` | Dimensión auxiliar (sin FK a ventas) |
| `cliente_resumen` | Tabla analítica por cliente |
| `calidad_reporte` | Auditoría hallazgo → acción |

Flags: `sin_resolucion`, `en_maestro_clientes`, `es_outlier_monto`

---

## 3. Pipeline ETL

Entrada: `python main.py` → `MainService.run()`

1. **Extract** — lee las 4 fuentes  
2. **Transform** — normalizar, limpiar, categorías, nulos, integridad, outliers, `cliente_resumen`  
3. **Load** — warehouse + Excel + CSV calidad + export Power BI  

Logs: `logs/etl.logs`

---

## 4. SQL

Carpeta `sql/`:

| Archivo | Uso |
|---------|-----|
| `01_calidad_datos.sql` | Nulos, duplicados, huérfanos |
| `02_metricas_negocio.sql` | Rankings, series, joins |
| `03_hipotesis_valor_vs_soporte.sql` | Hipótesis |
| `04_vistas_intermedias.sql` | Vistas PBI |
| `run_sql_analisis.py` | Runner |

```bash
python sql/run_sql_analisis.py
```

---

## 5. Calidad (reglas)

| Hallazgo | Acción |
|----------|--------|
| Duplicados / sin clave | Drop por PK |
| Naming inconsistente | Homogeneizar |
| Categorías | Catálogo canónico |
| Resolución nula (~32%) | Flag + placeholder |
| Huérfanos CRM (~24%) | Flag (no borrar) |
| Producto no integrable | Inventario auxiliar |
| Outliers monto | Flag IQR |

Evidencia: `output/calidad_reporte.csv`

---

## 6. EDA

```bash
python -m eda.eda_analisis
```

- Código: `eda/eda_analisis.py`  
- Notebook: `notebooks/01_eda_novashop.ipynb`  
- Salida: `output/eda/`  
- Librerías: Matplotlib + Seaborn  

---

## 7. Export Power BI

Automático al final del Load, o:

```bash
python -m servicios.export.powerbi_export
```

Carpeta: `output/powerbi/`  
Guía: `output/powerbi/README_POWERBI.md`

---

## 8. Hipótesis (resultado técnico)

- Corr monto ↔ tickets ≈ 0.00  
- Corr monto ↔ sin resolución ≈ -0.03  
- Conclusión: hipótesis global no confirmada; sí hay casos prioritarios alto valor + soporte pendiente.
