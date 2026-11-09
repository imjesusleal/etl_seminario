# Cómo levantar el proyecto (NovaShop ETL)

Guía rápida para clonar, instalar dependencias y correr el pipeline en local (Windows / macOS / Linux).

- Presentación / narrativa del TP: [`README.md`](./README.md)  
- Detalle técnico: [`DOCUMENTACION_TECNICA.md`](./DOCUMENTACION_TECNICA.md)

---

## 1. Requisitos

- **Python 3.12+** (recomendado 3.12)
- pip
- (Opcional) Power BI Desktop, para consumir los CSVs de `output/powerbi/`

Verificar:

```bash
python --version
```

En Windows, si `python` no responde, usá la ruta del instalador, por ejemplo:

```powershell
& "$env:LocalAppData\Programs\Python\Python312\python.exe" --version
```

---

## 2. Abrir el proyecto

```bash
cd "ruta/al/repo/etl_seminario"
```

Archivos de entrada que deben existir en la raíz:

| Archivo | Descripción |
|---------|-------------|
| `clientes.db` | CRM (SQLite) |
| `datos_ventas.csv` | Ventas |
| `soporte_tecnico.json` | Tickets |
| `inventario.xlsx` | Inventario |
| `.env` | Rutas de conexiones |

---

## 3. Entorno virtual (recomendado)

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Configuración (`.env`)

En la raíz del repo:

```env
CONNSTRING = 'clientes.db'
WAREHOUSE_CONNSTRING = 'output/novashop_analitico.db'
```

- `CONNSTRING`: base origen de clientes  
- `WAREHOUSE_CONNSTRING`: destino analítico (se crea/actualiza al correr el ETL)

---

## 5. Correr el ETL (paso principal)

Desde la raíz del proyecto:

```bash
python main.py
```

Eso ejecuta **Extract → Transform → Load** y genera:

| Salida | Contenido |
|--------|-----------|
| `output/novashop_analitico.db` | Warehouse SQLite |
| `output/output.xlsx` | Excel analítico |
| `output/calidad_reporte.csv` | Auditoría de calidad |
| `output/powerbi/*.csv` | CSVs limpios para Power BI |
| `logs/etl.logs` | Log del pipeline |

---

## 6. Pasos opcionales

### Consultas SQL (punto 4)

```bash
python sql/run_sql_analisis.py
```

### EDA (punto 7)

```bash
python -m eda.eda_analisis
```

Figuras y conclusiones en `output/eda/`.  
Notebook: `notebooks/01_eda_novashop.ipynb`.

### Re-exportar solo CSVs de Power BI

```bash
python -m servicios.export.powerbi_export
```

---

## 7. Conectar Power BI

1. Abrí Power BI Desktop  
2. **Obtener datos → Texto/CSV** (o carpeta)  
3. Apuntá a `output/powerbi/`  
4. Empezá por:
   - `cliente_resumen.csv` o `v_cliente_valor_soporte.csv`
   - `fact_ventas.csv` / `fact_tickets.csv`
   - `kpis.csv`
5. Guía corta de modelado: `output/powerbi/README_POWERBI.md`

---

## 8. Estructura útil del repo

```text
etl_seminario/
├── main.py                 # entrada del ETL
├── .env
├── requirements.txt
├── SETUP.md                # esta guía
├── README.md               # documentación del TP
├── datos_ventas.csv
├── soporte_tecnico.json
├── inventario.xlsx
├── clientes.db
├── servicios/              # ETL, export PBI, etc.
├── eda/                    # análisis exploratorio
├── sql/                    # consultas y vistas
├── notebooks/
└── output/                 # artefactos generados
    ├── novashop_analitico.db
    ├── output.xlsx
    ├── eda/
    └── powerbi/
```

---

## 9. Problemas frecuentes

| Problema | Qué revisar |
|----------|-------------|
| `python` no se reconoce | Instalar Python 3.12 y/o usar la ruta completa del ejecutable |
| Falta un módulo (`pandas`, `seaborn`, …) | `pip install -r requirements.txt` con el venv activo |
| `No existe output/novashop_analitico.db` | Correr primero `python main.py` |
| Error al leer Excel/CSV/JSON/DB | Verificar que los archivos fuente estén en la raíz y que `.env` sea correcto |
| Power BI muestra mal caracteres | Los CSV salen en `utf-8-sig` (pensado para Windows/PBI) |

---

## 10. Orden recomendado de trabajo

```bash
pip install -r requirements.txt
python main.py
python sql/run_sql_analisis.py
python -m eda.eda_analisis
```

Luego abrir `output/powerbi/` en Power BI.

---

## 11. Realineación de IDs CRM (ya aplicada)

Los `id_cliente` de ventas/tickets fueron alineados parcialmente con `clientes.db` para que el join tenga sentido, dejando ~25% de huérfanos a propósito.

- Script: `scripts/realinear_ids_clientes.py`
- Backup original: `datos/backup_pre_realineacion/`
- No hace falta volver a correrlo salvo que restaures el backup.
