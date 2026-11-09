-- ============================================================
-- 02. Metricas de negocio
-- Objetivo: seleccion, filtros, agregaciones, joins y orden
-- ============================================================

-- 2.1 Ranking de clientes por facturacion
SELECT
    r.id_cliente,
    COALESCE(r.nombre, 'Sin maestro') AS nombre,
    r.monto_total_ventas,
    r.cantidad_ventas,
    r.ticket_promedio,
    r.cantidad_tickets,
    r.tickets_sin_resolucion
FROM cliente_resumen r
WHERE r.monto_total_ventas > 0
ORDER BY r.monto_total_ventas DESC
LIMIT 20;

-- 2.2 Ventas mensuales
SELECT
    strftime('%Y-%m', fecha) AS anio_mes,
    COUNT(*) AS cantidad_ventas,
    SUM(cantidad) AS unidades,
    ROUND(SUM(total_venta), 2) AS monto_total
FROM fact_ventas
WHERE fecha IS NOT NULL
GROUP BY strftime('%Y-%m', fecha)
ORDER BY anio_mes;

-- 2.3 Tickets por tema y estado
SELECT
    tema,
    estado,
    COUNT(*) AS cantidad
FROM fact_tickets
GROUP BY tema, estado
ORDER BY tema, cantidad DESC;

-- 2.4 Join resumen + ventas (+ maestro si existe)
-- Nota: en este dataset el CRM no comparte IDs con ventas/tickets;
-- por eso se usa LEFT JOIN a dim_clientes y se prioriza cliente_resumen.
SELECT
    r.id_cliente,
    COALESCE(c.nombre, r.nombre, 'Sin maestro') AS nombre,
    c.id_cliente IS NOT NULL AS esta_en_crm,
    COUNT(v.id_venta) AS cantidad_ventas,
    ROUND(SUM(v.total_venta), 2) AS monto_total,
    ROUND(AVG(v.total_venta), 2) AS ticket_promedio
FROM cliente_resumen r
INNER JOIN fact_ventas v ON v.id_cliente = r.id_cliente
LEFT JOIN dim_clientes c ON c.id_cliente = r.id_cliente
GROUP BY r.id_cliente, COALESCE(c.nombre, r.nombre, 'Sin maestro'), esta_en_crm
HAVING SUM(v.total_venta) >= 1000
ORDER BY monto_total DESC
LIMIT 15;

-- 2.5 Inventario auxiliar: stock bajo por categoria
SELECT
    categoria,
    COUNT(*) AS productos,
    SUM(stock_actual) AS stock_total,
    ROUND(AVG(precio_costo), 2) AS costo_promedio,
    SUM(CASE WHEN stock_actual <= 10 THEN 1 ELSE 0 END) AS productos_stock_bajo
FROM dim_inventario
GROUP BY categoria
ORDER BY productos_stock_bajo DESC, categoria;
