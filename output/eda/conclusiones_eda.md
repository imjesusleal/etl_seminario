# Conclusiones EDA - NovaShop

## Hipotesis
¿Los clientes de mayor valor concentran mas tickets abiertos/sin resolucion?

- No se observa una relacion lineal fuerte entre mayor valor comercial y mayor carga de tickets (corr monto-tickets=0.0015; corr monto-sin_resolucion=-0.0267). La hipotesis global no se confirma de forma clara.

## Hallazgos exploratorios
- Datasets perfilados: cliente_resumen, fact_ventas, fact_tickets, dim_inventario.
- Segmento alto: tickets promedio=0.939, sin resolucion promedio=0.245.
- Segmento bajo: tickets promedio=0.95, sin resolucion promedio=0.307.
- Existen clientes alto-valor con tickets pendientes: utiles para priorizacion operativa, aunque no impliquen concentracion sistematica.
- La serie temporal muestra dinamica de ventas a lo largo del anio; tickets cubren una ventana mas corta.

## Limitaciones
- Queda un % de ventas/tickets huerfanos vs CRM (integridad parcial a proposito).
- Inventario no se cruza con ventas por falta de clave de producto.

## Proximos pasos
- Dashboard Power BI sobre cliente_resumen + vistas SQL.
- Monitorear clientes alto-valor con tickets abiertos/sin resolucion.