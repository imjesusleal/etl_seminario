# Especificación del dashboard — NovaShop (Power BI)

Guía de **qué debe mostrar** el dashboard.  
Datos listos en `output/powerbi/`.  
Cómo importar/modelar: `output/powerbi/README_POWERBI.md`.

**Objetivo del dashboard:** comunicar el caso NovaShop a gerencia comercial y soporte, conectado a la hipótesis y a los hallazgos del análisis.

**Hipótesis a reflejar visualmente:**  
¿Los clientes de mayor valor concentran más tickets abiertos / sin resolución?

---

## 1. Principios de diseño

1. **Primero la pregunta de negocio**, después los gráficos.  
2. Cada página tiene **un mensaje** (no mezclar todo).  
3. Los KPIs de portada deben poder leerse en **10 segundos**.  
4. Incluir **filtros** útiles: segmento de valor, tema, estado, período.  
5. Cerrar con una lectura accionable (prioridad de atención), no solo “bonito”.

---

## 2. Modelo de datos sugerido (resumen)

| Dataset | Rol en PBI |
|---------|------------|
| `v_cliente_valor_soporte.csv` o `cliente_resumen.csv` | Tabla analítica principal (cliente) |
| `fact_ventas.csv` | Hecho ventas |
| `fact_tickets.csv` | Hecho tickets |
| `dim_clientes.csv` | Dimensión cliente (nombre, email, etc.) |
| `v_tickets_pendientes_alto_valor.csv` | Lista prioritaria |
| `v_ventas_mensuales.csv` | Serie temporal |
| `kpis.csv` | Tarjetas de portada (opcional) |
| `dim_inventario.csv` | Página auxiliar / contexto (sin join a ventas) |
| `calidad_reporte.csv` | Página de calidad |

Relaciones principales: por `id_cliente`.  
**No forzar** relación inventario ↔ ventas.

---

## 3. Páginas obligatorias

### Página 1 — Resumen ejecutivo

**Mensaje:** “Así está el negocio unificado en una sola vista.”

**Debe mostrar**
- Cards / KPIs:
  - Facturación total
  - Cantidad de ventas
  - Cantidad de tickets
  - % tickets sin resolución
  - Tickets pendientes (Abierto + En progreso)
  - Clientes alto valor con soporte pendiente
  - % ventas sin match en CRM (calidad)
- 1 texto corto o título con el rol: *Área de datos → Comercial / Soporte*

**No hace falta** meter acá el detalle de temas o tablas largas.

---

### Página 2 — Hipótesis: valor vs soporte

**Mensaje:** “¿Más compra implica más reclamo problemático?”

**Debe mostrar**
- Distribución o comparación de tickets por **segmento de valor** (`bajo` / `medio` / `alto` / `sin_ventas`)
- Comparación de **sin resolución** por segmento
- Scatter o matriz: `monto_total_ventas` vs `cantidad_tickets` / `tickets_sin_resolucion`
- (Opcional) Top clientes por monto con indicador de tickets pendientes

**Conclusión visible en la página (cuadro de texto):**  
> A nivel agregado la hipótesis no se confirma con fuerza;  
> igual priorizamos casos de alto valor con soporte pendiente.

Fuente recomendada: `v_cliente_valor_soporte.csv`

---

### Página 3 — Operación de soporte

**Mensaje:** “Dónde está trabada la atención.”

**Debe mostrar**
- Tickets por **tema**
- Tickets por **estado** (Abierto / En progreso / Cerrado)
- Cruce tema × estado (matriz o barras apiladas)
- % o cantidad **sin resolución**
- Filtros por tema / estado / segmento de valor

Fuente: `fact_tickets.csv` (+ cliente si hace falta)

---

### Página 4 — Prioridad comercial-operativa

**Mensaje:** “A quién atender primero.”

**Debe mostrar**
- Tabla de **clientes alto valor con tickets pendientes / sin resolución**
- Columnas mínimas sugeridas:
  - cliente (nombre o id)
  - monto total ventas
  - tema
  - estado
  - fecha del ticket
  - resolución / flag sin resolución
- Ranking o top N por monto

Fuente: `v_tickets_pendientes_alto_valor.csv`

Esta página es clave para la exposición: es el **insight accionable**.

---

### Página 5 — Evolución temporal

**Mensaje:** “Cómo se movió la operación en el tiempo.”

**Debe mostrar**
- Serie de **monto de ventas por mes**
- Serie de **cantidad de tickets por mes** (si el período lo permite)
- Nota visible: ventas cubren ~12 meses; tickets una ventana más corta

Fuente: `v_ventas_mensuales.csv` + agregación mensual de tickets

---

### Página 6 — Calidad de datos (opcional pero recomendada)

**Mensaje:** “Qué limitaciones tiene lo que estamos mirando.”

**Debe mostrar**
- % / cantidad de tickets sin resolución
- % ventas/tickets huérfanos vs CRM
- (Opcional) outliers de monto
- Inventario como dato auxiliar **sin cruce forzado** a ventas
- Tabla o cards desde `calidad_reporte.csv` / `kpis.csv`

Sirve para defender el trabajo técnico en la oral.

---

## 4. Segmentadores / filtros mínimos

En (casi) todas las páginas:

- Segmento de valor  
- Tema de ticket  
- Estado de ticket  
- Período (mes / año), si el modelo lo permite  

Opcional: cliente individual (buscador).

---

## 5. Qué NO hace falta mostrar

- Código del ETL  
- Diccionarios de columnas completos  
- Join inventado producto↔stock  
- Demasiados gráficos decorativos sin lectura  
- Toda la tabla cruda de 1000 ventas en portada  

---

## 6. Checklist de aceptación del dashboard

- [ ] Hay portada con KPIs claros  
- [ ] Hay una página explícita de la **hipótesis**  
- [ ] Hay una página de **prioridad** (alto valor + soporte pendiente)  
- [ ] Se ve soporte por tema/estado  
- [ ] Hay alguna vista temporal  
- [ ] Se menciona o visualiza **calidad/limitaciones**  
- [ ] Los filtros permiten explorar sin romper el relato  
- [ ] Alguien del equipo puede explicar cada página en 1 minuto  

---

## 7. Relación con la presentación oral

Orden sugerido al mostrar PBI:

1. Resumen ejecutivo  
2. Hipótesis (valor vs soporte) → decir el resultado  
3. Prioridad operativa (la lista accionable)  
4. Soporte por temas  
5. (Si sobra tiempo) Temporal + calidad  

Cierre hablado:

> Unificamos los datos, controlamos calidad y, aunque la hipótesis global no se confirma, el dashboard nos deja priorizar clientes de alto valor con soporte pendiente.
