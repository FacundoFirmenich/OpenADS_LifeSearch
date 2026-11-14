# P02: revisión ejecutada, jurisdicciones temporales y resultados nuevos

8 de septiembre de 2026. Sucesión aditiva del análisis v4.1, no sustitución de sus fuentes ni declaración de envío editorial.

## Dictamen científico

La base numérica se sostiene: se reprodujeron desde los siete CSV las 42 estimaciones canónicas y las 72 especificaciones, incluidas las 3.024 combinaciones especificación–indicador–objetivo y sus rangos. El cálculo canónico independiente no llama a las funciones del pipeline original; el multiverso sí reutiliza sus funciones numéricas verificadas. Las discrepancias máximas con los CSV históricos son, respectivamente, 3,03×10⁻¹⁵ y 2,28×10⁻¹³: diferencias de precisión numérica, no cambios científicos.

La contribución nueva de esta revisión es una adjudicación explícita por aristas y segmentos. No sustituye el análisis global: distingue qué información conserva y qué estructura oculta. De las 105 relaciones indicador–par, 50 mantienen una dirección estricta bajo las 72 especificaciones y 55 no. Al fijar cada ventana y recorrer sus 24 variantes restantes, 216 de las 315 relaciones indicador–par–ventana tienen dirección invariante y 99 siguen dependiendo de la especificación. Estas cifras no son tasas de confianza ni resultados independientes.

Hay ocho relaciones indicador–par con direcciones opuestas invariantes en distintas ventanas. Éste es un hallazgo descriptivo derivado ahora, no un nuevo muestreo del universo de publicaciones ni una prueba causal de cambios de régimen.

## 1. Qué se reprodujo y con qué alcance

El archivo legado contiene 10.317 asignaciones objetivo–publicación y 9.513 bibcodes únicos. El corte canónico 2000–2023 contiene 9.762 asignaciones y 9.021 bibcodes únicos. Las publicaciones multietiquetadas se conservan; no se trata a los seis objetivos como muestras independientes.

| Objetivo | Asignaciones 2000–2023 | Trayectoria OLS (%) | CYCR interno | LOTO-CYCR | Percentil medio |
|---|---:|---:|---:|---:|---:|
| Encélado | 681 | 19,6941 | 1,3247 | 1,3770 | 0,5600 |
| Europa | 1.287 | 3,1611 | 1,0249 | 1,0481 | 0,5319 |
| Ganímedes | 420 | 4,0784 | 1,2082 | 1,2399 | 0,5890 |
| Marte | 5.327 | 5,9663 | 0,9079 | 0,8136 | 0,4639 |
| Titán | 1.612 | 2,4237 | 1,0293 | 1,0665 | 0,5423 |
| Venus | 435 | 10,4408 | 1,5469 | 1,6296 | 0,5736 |

OLS es `exp(pendiente de log(1+conteo anual))−1`, expresada aquí en porcentaje. No es una tasa física, una previsión ni una estimación de productividad por investigador. CYCR y LOTO-CYCR usan referencias del corpus recuperado por año; no normalizan por campo ni corrigen la asimetría de las consultas ADS.

## 2. Método nuevo: la jurisdicción forma parte de la comparación

Para un indicador m, un par de objetivos (a,b) y un segmento s definido antes de adjudicar sus direcciones, se considera el conjunto de especificaciones existentes compatibles con s. Para cada una se conserva la diferencia entre los valores de a y b. No se promedia el signo hasta convertirlo en una supuesta probabilidad posterior.

Los segmentos son los niveles ya presentes en el diseño: tres ventanas temporales, tres filtros de recuperación, dos atribuciones y cuatro reglas de ponderación; se añade el conjunto completo como referencia global. Son 13 conjuntos de especificaciones solapados y 105 comparaciones por conjunto: 1.365 filas. No son 1.365 experimentos ni una partición de datos independiente.

Se clasifica una arista como dirección invariante A>B o B>A sólo si todas las diferencias del segmento exceden una tolerancia numérica simétrica `1e−12 + 1e−9 max(|a|,|b|)` en esa dirección. La tolerancia no representa equivalencia práctica. Empate numérico, dirección dependiente y no estimable se mantienen separados. Los conteos de direcciones, empates y valores no finitos forman una partición exhaustiva; cada fila conserva su denominador.

El bootstrap histórico de 2.000 réplicas corresponde únicamente al análisis canónico inclusivo, atribución completa, peso unitario y 2000–2023. Se conserva como referencia histórica separada y no se traslada a segmentos temporales o metodológicos distintos. No se ha calculado cobertura simultánea de todos los segmentos. No se ejecutó aquí de nuevo el bootstrap ni el Monte Carlo nulo de Pareto.

## 3. Las ocho inversiones temporales observadas

Cada celda de dirección resume unanimidad entre las 24 especificaciones del segmento correspondiente. Una ventana no listada no recibe una dirección por inferencia.

| Indicador | Par A / B | Ventana(s) con A>B | Ventana(s) con B>A |
|---|---|---|---|
| OLS | Encélado / Europa | 2000–2023 | 2019–2023 |
| OLS | Encélado / Ganímedes | 2000–2023 | 2019–2023 |
| OLS | Encélado / Venus | 2000–2023 | 2010–2023; 2019–2023 |
| OLS | Europa / Marte | 2010–2023 | 2000–2023 |
| Theil–Sen | Encélado / Europa | 2000–2023 | 2019–2023 |
| Theil–Sen | Encélado / Ganímedes | 2000–2023 | 2019–2023 |
| Theil–Sen | Europa / Ganímedes | 2010–2023 | 2000–2023 |
| Theil–Sen | Europa / Marte | 2010–2023 | 2000–2023 |

La lectura sustantiva es que liderazgo acumulado y liderazgo reciente no son la misma pregunta. La posición canónica de Encélado no puede narrarse como supremacía temporal uniforme. Venus, Europa y Ganímedes adquieren relaciones dominantes en ciertos segmentos recientes incluso cuando su posición de largo plazo es distinta.

No se afirma que las ventanas sean independientes, que exista un punto de cambio identificado ni que una misión haya causado el patrón. Las ventanas son anidadas; las series comparten publicaciones y los dos estimadores de tendencia usan los mismos registros. Un estudio de mecanismos o de cambios temporales requeriría un diseño distinto y una nueva evaluación de incertidumbre.

## 4. Reparaciones efectivamente aplicadas

### Separación de estabilidad metodológica y muestreo

El nuevo `local_jurisdiction_edges.csv` evita que la etiqueta histórica `ROBUST_INVARIANT` sea leída como cobertura simultánea. Mantiene conteos descriptivos, segmento y respaldo canónico histórico en campos distintos. Las 50 direcciones invariantes globales no se presentan automáticamente como 50 efectos significativos.

### Relevancia: corregir la etiqueta, preservar los registros

La vista `enceladus_screening_semantics_corrected.csv` cambia en 483 registros `LOWER_BOUND_INCLUDED` por `TEXT_MATCH_NOT_RELEVANCE_VALIDATED`; conserva también la etiqueta histórica y los otros 258 registros. No se borró ninguna publicación ni se fabricó una evaluación humana. El hecho de ser subconjunto del corpus no demuestra ser cota inferior del conjunto de publicaciones relevantes.

Se comprobaron además las dos implementaciones de coincidencia estricta usadas para Encélado —subcadena en el cálculo y límites de palabra en la auditoría—: sobre estos registros producen el mismo conjunto. No se encontró una discrepancia empírica que justifique alterar sus cifras. Esto no demuestra equivalencia de ambas reglas sobre cualquier texto futuro.

### Referencias de citas: diagnóstico antes de cambiar el estimando

En las 144 referencias objetivo–año canónicas LOTO no hay conjuntos externos vacíos ni medias nulas: el mínimo tamaño externo es 69 y la menor media de citas es 6,217235. El riesgo general de referencias degeneradas requiere manejo explícito en futuras ampliaciones, pero no explica ni invalida los resultados canónicos actuales.

La regla histórica de percentil es rango promedio entre empates dividido por el número de publicaciones del año. Aplicar `percentil≥0,90` selecciona entre el 9,7598% y el 10,6952% de cada referencia anual canónica. No selecciona exactamente el 10% por construcción. Se conserva el cálculo y se precisa la etiqueta: participación por encima del umbral 0,90 del percentil empírico con rango promedio. Forzar exactamente 10% mediante otra convención sería una sensibilidad nueva, no una corrección silenciosa.

### Geografía y calibración

Debe reemplazarse “independent axis” por “additional dimension” salvo que se aporte una prueba específica de independencia. Se preservan los límites de cobertura de afiliaciones y la separación entre presencia en una publicación, participación institucional, concepto de misión y misión aprobada. Esta revisión no ejecutó otra vez el módulo completo de afiliaciones.

## 5. Texto en inglés incorporable al manuscrito

### Local jurisdiction of pairwise conclusions

We define each comparison by its indicator, target pair and declared analytical jurisdiction. The existing 72-specification design contains three temporal windows, each with 24 combinations of retrieval, attribution and team-weighting rules. Within a jurisdiction, an ordering is specification-invariant only if its direction is preserved across every compatible specification, subject to an explicit numerical equality tolerance. This is a finite-design statement, not a posterior probability, a population-level significance result or simultaneous sampling coverage.

Across the complete specification universe, 50 of the 105 indicator–pair relations have an invariant direction and 55 remain specification-dependent. Conditioning on the three temporal windows yields 216 invariant directions among 315 indicator–pair–window relations, while 99 remain specification-dependent. These counts describe overlapping analytical comparisons and are not independent replications.

Eight indicator–pair relations exhibit opposite invariant directions in different windows. For example, Enceladus exceeds Venus on the OLS trajectory over 2000–2023 under all 24 compatible specifications, whereas Venus exceeds Enceladus over both 2010–2023 and 2019–2023 under all 24 specifications of each window. Enceladus similarly exceeds Europa and Ganymede over 2000–2023 but is exceeded by both over 2019–2023 for OLS and Theil–Sen. The broad-window ordering therefore does not summarize every temporal jurisdiction. These are descriptive reversals in nested windows, not identified causal effects or independent confirmations of a change point.

### Distinct uncertainty and measurement layers

The archived 2,000-replicate paper-cluster bootstrap pertains to the canonical inclusive, full-assignment, unit-weight, 2000–2023 specification. Its pairwise exceedance frequencies are retained separately from specification counts; they do not confer joint coverage across the multiverse or its segments. We do not interpret a frequent ordering as the probability that a target is scientifically preferable.

The strict-text subset is defined by title/keyword matches, not by validated relevance. Accordingly, its machine label is `TEXT_MATCH_NOT_RELEVANCE_VALIDATED`, with historical labels retained. Likewise, the upper-citation indicator is explicitly the share with average-rank empirical percentile at least 0.90; finite samples and citation ties mean its pooled yearly prevalence need not equal exactly ten percent. Geographic structure is an additional measurement dimension, without an assumed statistical-independence claim.

### Revised concluding paragraph

The contribution is an auditable, jurisdiction-aware map of scientific attention rather than a universal ranking of astrobiological targets. Independent numerical reproduction preserves the canonical rank transitions, while the new segment analysis exposes directions that are stable locally but reverse across temporal scopes. The appropriate scientific object is thus a collection of explicitly conditioned comparisons with distinct measurement and uncertainty layers. Neither publication scale, citation reception nor trajectory identifies habitability, mission return, labour productivity or funding priority from this corpus alone.

## 6. Implementación, reproducibilidad y límite editorial

`reproduce_p02.py` calcula las estimaciones independientes, reproduce las funciones numéricas del multiverso y genera las vistas nuevas. La vista de ejecución omite exactamente la importación de matplotlib y su configuración gráfica mediante AST; no altera las funciones numéricas, no inserta módulos ficticios y no invoca `main()` ni dibuja figuras. Las 886 líneas del original fueron leídas antes de ejecutarlo. Una instalación gráfica aislada intentada previamente fue cancelada al hacerse innecesaria; no se instaló ni actualizó esa dependencia en el entorno global.

El entorno observado usa Python 3.11.9, NumPy 2.4.4, pandas 3.0.2 y SciPy 1.17.1, distintos del lock histórico. La coincidencia numérica se verificó expresamente; no se declara una reproducción del entorno fijado ni una ejecución completa de los 25 grupos del test histórico. `verify_revision.py` verifica por separado los conteos y estados de las 1.365 aristas y la preservación de las 741 filas de cribado.

Se recuperaron 56 de los 60 miembros del manifiesto v4.1: los siete CSV, el pipeline, los resultados, el test y ambos PDF están presentes y verificados. Siguen faltando README, notas v4.1 y los dos TeX exactos. La copia comprimida truncada permanece en cuarentena. Este documento es una adenda desarrollada con resultados ejecutados, no un supuesto paquete v4.2 completo ni un manuscrito ya recompilado para envío.

El siguiente cierre editorial requiere recuperar los TeX exactos o producir una reconstrucción nueva declarada, incorporar estos resultados y validar tablas, referencias y PDF. La agenda de fuentes y el sesgo de recuperación siguen siendo límites científicos reales; una batería numérica correcta no los elimina.
