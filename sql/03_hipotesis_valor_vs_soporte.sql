-- ============================================================
-- 03. Hipotesis de analisis
-- Pregunta: ¿Los clientes de mayor valor concentran mas tickets
-- abiertos / sin resolucion (facturacion / error de sistema)?
-- ============================================================

-- 3.1 Segmentacion por cuartiles de valor (aprox. con NTILE)
WITH base AS (
    SELECT *
    FROM cliente_resumen
    WHERE monto_total_ventas > 0
),
segmentos AS (
    SELECT
        *,
        NTILE(4) OVER (ORDER BY monto_total_ventas) AS cuartil_valor
    FROM base
)
SELECT
    cuartil_valor,
    COUNT(*) AS clientes,
    ROUND(AVG(monto_total_ventas), 2) AS monto_promedio,
    ROUND(AVG(cantidad_tickets), 2) AS tickets_promedio,
    ROUND(AVG(tickets_abiertos + tickets_en_progreso), 2) AS tickets_abiertos_o_progreso_prom,
    ROUND(AVG(tickets_sin_resolucion), 2) AS sin_resolucion_prom,
    ROUND(SUM(tickets_sin_resolucion) * 1.0 / NULLIF(SUM(cantidad_tickets), 0), 4) AS tasa_sin_resolucion
FROM segmentos
GROUP BY cuartil_valor
ORDER BY cuartil_valor;

-- 3.2 Top 20% de facturacion vs resto (Pareto simplificado)
WITH ordenados AS (
    SELECT
        *,
        SUM(monto_total_ventas) OVER () AS monto_global,
        SUM(monto_total_ventas) OVER (ORDER BY monto_total_ventas DESC) AS monto_acum
    FROM cliente_resumen
    WHERE monto_total_ventas > 0
),
marcados AS (
    SELECT
        *,
        CASE WHEN monto_acum <= monto_global * 0.20 THEN 'Top20_monto' ELSE 'Resto' END AS segmento_pareto
    FROM ordenados
)
SELECT
    segmento_pareto,
    COUNT(*) AS clientes,
    ROUND(SUM(monto_total_ventas), 2) AS monto_total,
    ROUND(100.0 * SUM(monto_total_ventas) / MAX(monto_global), 2) AS pct_monto,
    SUM(cantidad_tickets) AS tickets_totales,
    SUM(tickets_abiertos + tickets_en_progreso) AS tickets_pendientes,
    SUM(tickets_sin_resolucion) AS tickets_sin_resolucion,
    ROUND(
        100.0 * SUM(tickets_sin_resolucion) / NULLIF(SUM(cantidad_tickets), 0),
        2
    ) AS pct_tickets_sin_resolucion
FROM marcados
GROUP BY segmento_pareto
ORDER BY segmento_pareto DESC;

-- 3.3 Clientes de alto valor con soporte critico
SELECT
    r.id_cliente,
    COALESCE(r.nombre, 'Sin maestro') AS nombre,
    ROUND(r.monto_total_ventas, 2) AS monto_total_ventas,
    r.cantidad_tickets,
    r.tickets_abiertos,
    r.tickets_en_progreso,
    r.tickets_sin_resolucion,
    ROUND(
        100.0 * r.tickets_sin_resolucion / NULLIF(r.cantidad_tickets, 0),
        2
    ) AS pct_sin_resolucion
FROM cliente_resumen r
WHERE r.monto_total_ventas >= (
        SELECT AVG(monto_total_ventas)
        FROM cliente_resumen
        WHERE monto_total_ventas > 0
      )
  AND r.cantidad_tickets > 0
  AND (r.tickets_abiertos + r.tickets_en_progreso + r.tickets_sin_resolucion) > 0
ORDER BY r.monto_total_ventas DESC, r.tickets_sin_resolucion DESC
LIMIT 25;

-- 3.4 Temas de soporte en clientes de alto valor
WITH alto_valor AS (
    SELECT id_cliente
    FROM cliente_resumen
    WHERE monto_total_ventas >= (
        SELECT AVG(monto_total_ventas)
        FROM cliente_resumen
        WHERE monto_total_ventas > 0
    )
)
SELECT
    t.tema,
    COUNT(*) AS tickets,
    SUM(CASE WHEN t.estado IN ('Abierto', 'En progreso') THEN 1 ELSE 0 END) AS pendientes,
    SUM(t.sin_resolucion) AS sin_resolucion
FROM fact_tickets t
INNER JOIN alto_valor a ON a.id_cliente = t.id_cliente
GROUP BY t.tema
ORDER BY pendientes DESC, sin_resolucion DESC, tickets DESC;

-- 3.5 Correlacion operativa simple: buckets de valor vs tasa de tickets
SELECT
    CASE
        WHEN monto_total_ventas = 0 THEN '0_sin_ventas'
        WHEN monto_total_ventas < 500 THEN '1_bajo'
        WHEN monto_total_ventas < 1500 THEN '2_medio'
        ELSE '3_alto'
    END AS bucket_valor,
    COUNT(*) AS clientes,
    ROUND(AVG(cantidad_tickets), 2) AS tickets_promedio,
    ROUND(AVG(tickets_sin_resolucion), 2) AS sin_resolucion_promedio,
    ROUND(AVG(CASE WHEN cantidad_tickets > 0 THEN 1.0 ELSE 0.0 END), 4) AS pct_clientes_con_ticket
FROM cliente_resumen
GROUP BY 1
ORDER BY 1;
