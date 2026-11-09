# Datasets Power BI — NovaShop

CSVs exportados desde `novashop_analitico.db` (post-ETL).

## Recomendado para el modelo
- Hechos: `fact_ventas.csv`, `fact_tickets.csv`
- Dimensiones: `dim_clientes.csv`, `dim_inventario.csv`
- Tabla analitica principal: `cliente_resumen.csv` o `v_cliente_valor_soporte.csv`
- KPIs: `kpis.csv`
- Soporte prioritario: `v_tickets_pendientes_alto_valor.csv`
- Serie temporal: `v_ventas_mensuales.csv`

Encoding: UTF-8 with BOM (`utf-8-sig`) para Excel/Power BI en Windows.

## Relacion sugerida
`dim_clientes[id_cliente] 1—* fact_ventas[id_cliente]`
`dim_clientes[id_cliente] 1—* fact_tickets[id_cliente]`
`cliente_resumen[id_cliente]` como tabla puente/analitica

Nota: inventario no se relaciona a ventas (sin clave de producto confiable).