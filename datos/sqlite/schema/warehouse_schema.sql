-- NovaShop: modelo analitico consolidado (destino del ETL)
-- Fuentes originales se mantienen (CSV / JSON / Excel / clientes.db)

DROP TABLE IF EXISTS calidad_reporte;
DROP TABLE IF EXISTS cliente_resumen;
DROP TABLE IF EXISTS fact_ventas;
DROP TABLE IF EXISTS fact_tickets;
DROP TABLE IF EXISTS dim_inventario;
DROP TABLE IF EXISTS dim_clientes;

CREATE TABLE dim_clientes (
    id_cliente INTEGER PRIMARY KEY,
    nombre TEXT,
    email TEXT,
    telefono TEXT,
    direccion TEXT,
    fecha_registro TEXT
);

CREATE TABLE fact_ventas (
    id_venta TEXT PRIMARY KEY,
    fecha TEXT,
    producto TEXT,
    cantidad INTEGER,
    precio_unitario REAL,
    total_venta REAL,
    id_cliente INTEGER,
    en_maestro_clientes INTEGER,
    es_outlier_monto INTEGER
);

CREATE TABLE fact_tickets (
    ticket_id TEXT PRIMARY KEY,
    fecha_creacion TEXT,
    id_cliente INTEGER,
    tema TEXT,
    estado TEXT,
    resolucion TEXT,
    sin_resolucion INTEGER,
    en_maestro_clientes INTEGER
);

-- Dimension auxiliar: sin FK forzada hacia fact_ventas
CREATE TABLE dim_inventario (
    id_producto INTEGER PRIMARY KEY,
    nombre_producto TEXT,
    categoria TEXT,
    stock_actual INTEGER,
    precio_costo REAL,
    proveedor TEXT
);

-- Tabla analitica intermedia para hipotesis comercial/soporte
CREATE TABLE cliente_resumen (
    id_cliente INTEGER PRIMARY KEY,
    nombre TEXT,
    email TEXT,
    fecha_registro TEXT,
    cantidad_ventas INTEGER,
    monto_total_ventas REAL,
    ticket_promedio REAL,
    cantidad_tickets INTEGER,
    tickets_abiertos INTEGER,
    tickets_en_progreso INTEGER,
    tickets_cerrados INTEGER,
    tickets_sin_resolucion INTEGER,
    en_maestro_clientes INTEGER
);

-- Evidencia de calidad de datos (punto 5)
CREATE TABLE calidad_reporte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hallazgo TEXT NOT NULL,
    severidad TEXT NOT NULL,
    metrica TEXT,
    valor_antes TEXT,
    accion TEXT,
    valor_despues TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_ventas_cliente ON fact_ventas (id_cliente);
CREATE INDEX IF NOT EXISTS idx_fact_tickets_cliente ON fact_tickets (id_cliente);
CREATE INDEX IF NOT EXISTS idx_fact_tickets_estado ON fact_tickets (estado);
CREATE INDEX IF NOT EXISTS idx_fact_tickets_tema ON fact_tickets (tema);
CREATE INDEX IF NOT EXISTS idx_fact_ventas_outlier ON fact_ventas (es_outlier_monto);
CREATE INDEX IF NOT EXISTS idx_fact_tickets_sin_resolucion ON fact_tickets (sin_resolucion);
