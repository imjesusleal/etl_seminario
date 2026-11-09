-- ============================================================
-- 04. Vistas intermedias para analisis recurrente / Power BI
-- ============================================================

DROP VIEW IF EXISTS v_cliente_valor_soporte;
DROP VIEW IF EXISTS v_tickets_pendientes_alto_valor;
DROP VIEW IF EXISTS v_ventas_mensuales;

CREATE VIEW v_cliente_valor_soporte AS
SELECT
    id_cliente,
    nombre,
    email,
    fecha_registro,
    cantidad_ventas,
    monto_total_ventas,
    ticket_promedio,
    cantidad_tickets,
    tickets_abiertos,
    tickets_en_progreso,
    tickets_cerrados,
    tickets_sin_resolucion,
    en_maestro_clientes,
    CASE
        WHEN monto_total_ventas = 0 THEN 'sin_ventas'
        WHEN monto_total_ventas < 500 THEN 'bajo'
        WHEN monto_total_ventas < 1500 THEN 'medio'
        ELSE 'alto'
    END AS segmento_valor,
    CASE
        WHEN cantidad_tickets = 0 THEN 0
        ELSE ROUND(100.0 * tickets_sin_resolucion / cantidad_tickets, 2)
    END AS pct_sin_resolucion
FROM cliente_resumen;

CREATE VIEW v_tickets_pendientes_alto_valor AS
SELECT
    t.ticket_id,
    t.fecha_creacion,
    t.id_cliente,
    COALESCE(r.nombre, 'Sin maestro') AS nombre,
    r.monto_total_ventas,
    t.tema,
    t.estado,
    t.resolucion
FROM fact_tickets t
INNER JOIN cliente_resumen r ON r.id_cliente = t.id_cliente
WHERE r.monto_total_ventas >= (
        SELECT AVG(monto_total_ventas)
        FROM cliente_resumen
        WHERE monto_total_ventas > 0
      )
  AND (
        t.estado IN ('Abierto', 'En progreso')
        OR t.sin_resolucion = 1
      );

CREATE VIEW v_ventas_mensuales AS
SELECT
    strftime('%Y-%m', fecha) AS anio_mes,
    COUNT(*) AS cantidad_ventas,
    SUM(cantidad) AS unidades,
    ROUND(SUM(total_venta), 2) AS monto_total
FROM fact_ventas
WHERE fecha IS NOT NULL
GROUP BY strftime('%Y-%m', fecha);
