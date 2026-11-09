# NovaShop — Trabajo Práctico Integrador

**Guía para armar la presentación** (tono narrativo, no técnico).  
Para instalar y correr el proyecto: [`SETUP.md`](./SETUP.md).  
Detalle técnico (modelo, SQL, ETL): [`DOCUMENTACION_TECNICA.md`](./DOCUMENTACION_TECNICA.md).

**Equipo:** Grupo 1  
**Rol:** área interna de datos de NovaShop  
**Público:** gerencia comercial y operaciones / soporte

---

## Guion sugerido (~20 minutos)

| Min | Bloque | Qué contar |
|-----|--------|------------|
| 0–2 | Caso | Qué es NovaShop y por qué importa |
| 2–4 | Problema e hipótesis | Qué preguntamos |
| 4–6 | Datos | De dónde salen y qué traen |
| 6–9 | Flujo técnico | Cómo unificamos (sin entrar en código) |
| 9–11 | Calidad | Qué problemas encontramos y qué hicimos |
| 11–14 | Análisis | SQL + EDA: qué vimos |
| 14–17 | Dashboard | KPIs e insights visuales (Power BI) |
| 17–20 | Cierre | Conclusión, limitaciones, mejoras |

---

## 1. Presentación del caso

**NovaShop** es un e-commerce que hoy opera con información dispersa:

- Clientes en un CRM  
- Ventas en un archivo de pedidos  
- Soporte en un sistema de tickets  
- Inventario en una planilla de depósito  

Cada área “ve su pedazo”, pero nadie tiene una visión confiable del cliente completo: cuánto compra y cuánto reclama.

**En una frase:**  
> Queremos una sola fuente de verdad para decidir mejor comercialmente y en soporte.

---

## 2. Problema, pregunta e hipótesis

### Problema de negocio
No se puede consolidar ni analizar bien la operación porque los datos viven en formatos y sistemas distintos, con inconsistencias.

### Objetivo
Unificar esas fuentes en un dataset analítico único y, sobre eso, responder una pregunta de negocio.

### Hipótesis
> ¿Los clientes que más compran concentran más tickets abiertos o sin resolución  
> (sobre todo facturación y errores de sistema)?

Si fuera cierta, soporte debería priorizar distinto a los clientes de alto valor.

---

## 3. Descripción del dataset

Datos académicos que simulan extractos internos de NovaShop.

| Dominio | Origen simulado | Volumen | Qué representa |
|---------|-----------------|---------|----------------|
| Clientes | CRM | ~500 | Maestro de clientes |
| Ventas | Pedidos | 1.000 | Compras |
| Tickets | Mesa de ayuda | 1.000 | Reclamos / consultas |
| Inventario | Depósito | 1.000 | Stock actual |

**Período**
- Ventas: ~may-2024 → may-2025  
- Tickets: ventana más corta (~nov-2024 → may-2025)

**Cómo se relacionan**
- El cruce principal es por **cliente** (ventas + tickets + ficha CRM).  
- Inventario se usa como contexto de stock, **sin forzar** unión a ventas (los nombres de producto no coinciden).

---

## 4. Flujo técnico (versión presentación)

No hace falta mostrar código. La historia es:

```text
4 fuentes distintas
        ↓
   Extraer + limpiar + normalizar
        ↓
   Una sola base analítica
        ↓
   Análisis (SQL / Python) + Power BI
```

**Qué logramos al unificar**
- Tablas limpias de clientes, ventas, tickets e inventario  
- Una vista por cliente: cuánto factura + cuántos tickets tiene  
- Indicadores listos para el dashboard  

**Mensaje para la oral:**  
> El valor no es “juntar archivos”: es dejar datos confiables y cruzables para decidir.

---

## 5. Calidad de datos (qué encontramos / qué hicimos)

| Problema | Impacto | Qué hicimos |
|----------|---------|-------------|
| ~32% de tickets sin resolución | Soporte incompleto | Los marcamos y los medimos (no los escondemos) |
| ~24% de ventas/tickets sin ficha en CRM | Cuesta enriquecer con nombre/email | Los marcamos como huérfanos; no los borramos |
| Nombres de campos distintos entre fuentes | Rompe cruces | Los estandarizamos |
| Inventario no matchea productos de venta | No se puede analizar stock vs demanda | Lo dejamos auxiliar y lo explicamos |
| Ventas atípicas (montos extremos) | Pueden sesgar promedios | Las señalamos, no las eliminamos |

**Regla de oro que conviene decir en la expo:**  
> Preferimos marcar y explicar los problemas antes que “maquillar” el dataset.

---

## 6. Análisis exploratorio (qué vimos)

### Pregunta guía
¿Más facturación = más reclamos problemáticos?

### Respuesta corta
**No de forma clara.**  
A nivel agregado, los clientes de mayor valor **no concentran** sistemáticamente más tickets ni más tickets sin resolución.

### Números para la slide
- Correlación valor ↔ cantidad de tickets ≈ **0**  
- Correlación valor ↔ sin resolución ≈ **0** (levemente negativa)  
- Segmento alto y segmento bajo tienen una carga de tickets **parecida**  
- Igual existen **casos puntuales** de alto valor con soporte pendiente → útiles para priorizar

### Lectura de negocio
La hipótesis global no se confirma, pero igual hay acción:

> Armar una lista de **clientes alto valor con tickets abiertos / sin resolución**  
> y darles prioridad operativa.

En temas de soporte (alto valor) aparecen fuerte:  
**Error de sistema**, **Consulta general** y **Problema de facturación**.

*(Figuras en `output/eda/` para pegar en slides.)*

---

## 7. Dashboard / indicadores (Power BI)

Datos listos en `output/powerbi/`.

### KPIs sugeridos de portada
| Indicador | Valor aprox. | Para qué sirve |
|-----------|--------------|----------------|
| Facturación total | ~516.9 mil | Tamaño del negocio en el período |
| Ventas | 1.000 | Volumen transaccional |
| Tickets | 1.000 | Carga de soporte |
| % tickets sin resolución | ~31.8% | Calidad de atención |
| Tickets pendientes | ~665 | Cola abierta / en progreso |
| Alto valor con soporte pendiente | ~147 clientes | Prioridad comercial-operativa |
| % ventas sin match CRM | ~24% | Deuda de calidad de maestro |

### Páginas sugeridas del dashboard
1. **Resumen ejecutivo** (KPIs)  
2. **Valor del cliente vs soporte** (hipótesis)  
3. **Temas y estados de tickets**  
4. **Evolución temporal de ventas**  
5. **Calidad de datos** (huérfanos / sin resolución)

---

## 8. Insights y conclusiones

1. **Unificamos** clientes, ventas, tickets e inventario en una sola base analítica.  
2. **Transparentamos** la calidad: nulos, huérfanos, outliers e inventario no integrable.  
3. La hipótesis “más compra ⇒ más reclamo problemático” **no se sostiene en el agregado**.  
4. Sí hay valor práctico: **priorizar alto valor con soporte pendiente**.  
5. El siguiente paso natural es el **dashboard** como herramienta de seguimiento.

---

## 9. Limitaciones

- Dataset **sintético / académico** (no es un caso real medido en producción).  
- Queda un % de actividad **sin ficha CRM**.  
- **Inventario** no se puede cruzar limpio con ventas.  
- Ventas y tickets no cubren **exactamente el mismo período**.  
- No tenemos SLA, canal, región ni costo de atención.  
- Es análisis **exploratorio**: correlación ≠ causalidad.

---

## 10. Posibles mejoras

1. Mejorar cobertura del maestro de clientes.  
2. Crear un código de producto común (ventas ↔ inventario).  
3. Alinear calendarios de ventas y soporte.  
4. Dashboard en producción con alertas de alto valor + ticket abierto.  
5. Profundizar por cohortes (clientes nuevos vs recurrentes) y por tema de ticket.

---

## Cierre para la oral (30 segundos)

> NovaShop necesitaba una sola verdad de datos.  
> Construimos el flujo para unificar fuentes, controlar calidad y analizar.  
> No vimos que los que más compran reclamen sistemáticamente más,  
> pero sí podemos priorizar mejor los casos de alto valor con soporte pendiente.  
> El dashboard es la forma de llevar eso a la gestión diaria.

---

## Anexo rápido

| Necesito… | Dónde está |
|-----------|------------|
| Instalar y correr | `SETUP.md` |
| Detalle técnico del TP | `DOCUMENTACION_TECNICA.md` |
| Gráficos EDA | `output/eda/` |
| CSVs para Power BI | `output/powerbi/` |
