-- ============================================================
-- 01. Calidad de datos / inconsistencias
-- Objetivo: detectar nulos, duplicados y problemas referenciales
-- ============================================================

-- 1.1 Tickets sin resolucion (usa flag de calidad del ETL)
SELECT
    COUNT(*) AS tickets_totales,
    SUM(sin_resolucion) AS tickets_sin_resolucion,
    ROUND(100.0 * SUM(sin_resolucion) / COUNT(*), 2) AS pct_sin_resolucion
FROM fact_tickets;

-- 1.1b Outliers de monto en ventas
SELECT
    COUNT(*) AS ventas_totales,
    SUM(es_outlier_monto) AS ventas_outlier,
    ROUND(100.0 * SUM(es_outlier_monto) / COUNT(*), 2) AS pct_outlier
FROM fact_ventas;

-- 1.2 Duplicados potenciales en ventas (misma clave de negocio)
SELECT
    id_venta,
    COUNT(*) AS repeticiones
FROM fact_ventas
GROUP BY id_venta
HAVING COUNT(*) > 1
ORDER BY repeticiones DESC;

-- 1.3 Duplicados potenciales en tickets
SELECT
    ticket_id,
    COUNT(*) AS repeticiones
FROM fact_tickets
GROUP BY ticket_id
HAVING COUNT(*) > 1
ORDER BY repeticiones DESC;

-- 1.4 Ventas sin cliente en el maestro CRM (flag ETL)
SELECT
    SUM(CASE WHEN en_maestro_clientes = 0 THEN 1 ELSE 0 END) AS ventas_huerfanas,
    SUM(CASE WHEN en_maestro_clientes = 1 THEN 1 ELSE 0 END) AS ventas_con_maestro
FROM fact_ventas;

-- 1.5 Tickets sin cliente en el maestro CRM (flag ETL)
SELECT
    SUM(CASE WHEN en_maestro_clientes = 0 THEN 1 ELSE 0 END) AS tickets_huerfanos,
    SUM(CASE WHEN en_maestro_clientes = 1 THEN 1 ELSE 0 END) AS tickets_con_maestro
FROM fact_tickets;

-- 1.5b Evidencia consolidada del punto 5
SELECT hallazgo, severidad, metrica, valor_antes, accion, valor_despues
FROM calidad_reporte
ORDER BY id;

-- 1.6 Clientes del resumen que no estan en el maestro
SELECT
    COUNT(*) AS clientes_fuera_maestro,
    SUM(CASE WHEN monto_total_ventas > 0 THEN 1 ELSE 0 END) AS con_ventas,
    SUM(CASE WHEN cantidad_tickets > 0 THEN 1 ELSE 0 END) AS con_tickets
FROM cliente_resumen
WHERE en_maestro_clientes = 0;
