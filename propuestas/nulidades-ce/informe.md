# Nulidades del Consejo de Estado: ¿se puede «matar» por nulidad?

Análisis de solo lectura (2026-09-30). Nada escrito en el repo. Todo lo de abajo sale de `jurisprudencia/co-ce-*.md`,
`relaciones.csv` e `index.db` tal como estaban hoy. Scripts y datos de apoyo: ver «Archivos» al final.

## 0. Conclusión

1. **Matar automáticamente desde la relatoría (`interpreta` + «Decisión (relatoría)») no es seguro y no hay que hacerlo.**
   Los valores reales de la relatoría son `ACCEDE`, `NIEGA`, `NO APLICA`…, nunca «nulidad»; `ACCEDE` significa también «se
   admite la demanda» o «se avoca el control inmediato». Ejemplo: `co:ce:11001-03-27-000-2018-00020-00:2018` (ACCEDE) es un
   auto admisorio y cuelga de `co:decreto:2250:2017` entero, que sigue vivo.
2. **Leyendo la parte resolutiva sí se puede, con una regla estricta** (declarar la nulidad + decreto con número y año, sin
   sub-parte para «total»). En las 780 fichas con resolutiva la regla produce 13 aristas, todas correctas leídas a mano.
   Pero **hoy no hay ninguna nulidad TOTAL con destino cargado**: las 3 totales son de decretos que no están en la base
   (`co:decreto:4994:2009`, `co:decreto:2474:2008:art:44` y `:art:48`). Lo que sí hay son **6 artículos de DUR con nulidad
   PARCIAL** (1067, 1073, 1075) que hoy salen `VIGENTE` sin ningún aviso. Eso se arregla con un aviso, no con una muerte.
3. **La mejor veta para matar no son las fichas sino el propio texto de la base:** 3 artículos cargados dicen literalmente
   «Artículo declarado NULO por el Consejo de Estado» (`co:decreto:1082:2015:art:2.2.1.2.5.1`, `:2.2.1.2.5.3`,
   `co:decreto:1474:1997:art:8`) y salen `VIGENTE`; otros 21 traen notas de nulidad parcial. Ver §4.d.
4. Propuesta mínima: dos tipos nuevos (`declara_nulo` mata; `declara_nulo_parcial` avisa). El parche añade unas 25 líneas a
   `build.py` (la mitad son asserts y comentarios), 14 a `export.py` y 29 a `esquema.md`. Probado con los `--check` de ambos
   (copias en el scratchpad, sin tocar el repo).

## 1. Cuantificación

| Qué | Cifra |
|---|---|
| Fichas CE | 2.283: 873 de CENDOJ (780 con `## resuelve`, 93 sin) y 1.410 de SAMAI (solo metadatos: ni decisión ni norma demandada) |
| Fichas CE con `decision:` en el frontmatter | **0** (ni `nulidad` ni `niega-nulidad`) |
| «Decisión (relatoría)» con la palabra NULIDAD | **0** de 873. Valores: NO APLICA 291, NIEGA 228, ACCEDE 214, vacío 28, CONFIRMA 23, ACCEDE PARCIALMENTE 19, INHIBITORIO 11, DECLARA IMPROCEDENTE 10, REVOCA 7, ANULA 2, CONCEDE 1… |
| «Decisión (relatoría)» favorable (ACCEDE*, ANULA, CONCEDE) | 240 |
| Fichas con fórmula de nulidad en el `## resuelve` («declarar la nulidad…», «declárase nula…») | 39 |
| …de las cuales la relatoría dice favorable | 22 (el 56 %); las otras 17 dicen CONFIRMA 5, NO APLICA 4, NIEGA 3, vacío 2, REVOCA 2, INHIBITORIO 1 |
| …y son nulidad de un acto general | 7 decretos + 6 resoluciones/circulares. El resto: 1 decreto de nombramiento, 9 actos particulares (contratos, tributos), 8 nulidad electoral (3 declaran, 5 confirman), 8 ruido (nulidad procesal, admisión, citas de la sentencia de primera instancia) |
| Fichas con «Norma demandada» | 310 (unas 211 son control inmediato de legalidad de 2020, donde ACCEDE = «avoca») |
| Aristas `interpreta` «CENDOJ: norma demandada» | 27 (25 fichas): **24 a norma entera, 3 a artículo concreto** |
| …con destino en norma CARGADA | **3**: `co:decreto:2250:2017` (norma entera, ACCEDE, auto admisorio), `co:decreto:1071:2015` (norma entera, FALTA DE COMPETENCIA), `co:decreto:1625:2016:art:1.5.7.1` (NIEGA). **0** son nulidades |
| Aristas cuya ficha dice ACCEDE* | 5 (`4994/2009`, `2025/2009`, `935/2013:art:2`, `2250/2017`, `1014/2020`); solo la de `2250/2017` está cargada y es un falso positivo |
| Fichas cuya resolutiva anula (parcial o total) un decreto **cargado** | 4: `co:ce:11001-03-15-000-2015-02578-00:2016`, `…-2013-00114-00:2020`, `…-2015-00158-00:2022`, `…-2021-00207-00:2023` → 6 artículos de DUR. **Ninguna** tiene arista `interpreta` (3 no traen «Norma demandada»; 1 la trae pero a un decreto no cargado) |

Notas: (a) la base tiene 193 decretos + 16 decretos-ley y ninguna resolución, circular, ordenanza ni acuerdo: la mayoría de lo
anulado por el CE (resoluciones, circulares) no tiene dónde caer. (b) `ingesta_webrelatoria.py` documenta que la relatoría dice
«DECLARA NULIDAD», pero `decision()` exige la palabra NULIDAD en el campo y esa palabra no aparece nunca: la función no
produce nada (código muerto; lo que dice el docstring no coincide con los datos).

## 2. Lectura de la parte resolutiva

### 2.1 Muestra

71 fichas leídas completas (`muestra_71.csv`, etiqueta manual hecha **antes** de ver la salida de la regla), estratificadas por
lo que dice una regla simple (R1, abajo): todas las de nulidad total (11), parcial (12), condicionada (2) y «condicionada sin
nulidad» (5), y por sorteo suspensión decretada 8/27, suspensión negada 5/11, «estese a lo resuelto» 4/13, inhibitoria 4/11,
niega/rechaza 6/75, control inmediato 6/271, resto 8/342. Además leí completas las 39 fichas con fórmula de nulidad, las 35
cuya «Norma demandada» es un decreto/ley y las de «inaplícase». Etiquetas de la muestra: nulidad parcial de acto general 11,
nulidad de acto particular 11, procedimental 10, admisión 7, control inmediato (no avoca/rechaza/ajustado) 5, condicionada 5,
suspensión negada 4, niega 4, resolutiva mal extraída 3, inhibitoria 3, avoca 2, suspensión decretada 2, otro 2,
**nulidad total de acto general 1**, nulidad implícita 1.

### 2.2 R1: reglas simples sobre el texto («declárase la nulidad», «suspensión provisional», «niégase»…)

| Pregunta | Resultado en la muestra |
|---|---|
| ¿Hay alguna nulidad declarada? | precisión 23/25 = 92 %, recall 23/24 = 96 % (falsos positivos: 2 resolutivas mal extraídas; falso negativo: el Decreto 595/2020, ver 2.5) |
| ¿Es nulidad TOTAL de una norma identificada? | **1/11 = 9 %** de las predichas «total». Las otras: 8 actos particulares, 1 mixta (arts. 44 y 48 totales + parciales), 1 basura |
| ¿Es nulidad PARCIAL de una norma general? | 9/12 = 75 % (las otras 3 son actos particulares) |
| «Suspensión decretada» | **1/8 = 12 %**: 7 son autos admisorios cuyo texto dice «tendiente a obtener la declaratoria de nulidad, previa suspensión provisional» |
| «Suspensión negada» | 4/5; la quinta es «no reponer» (mantiene una suspensión ya decretada): signo invertido |
| «Legalidad condicionada, sin nulidad» | 5/5 |
| «Estese a lo resuelto / cosa juzgada» | 1/4 (recusaciones y remisiones usan la misma fórmula) |

Es decir: R1 sirve para **filtrar** («aquí hay algo de nulidad, leer») y no para **decidir** una muerte.

### 2.3 R2: extractor estricto (`regla.py`, la que se propone)

Un numeral del `## resuelve` califica solo si: (i) empieza con «declarar[se] la nulidad [parcial] de…» o «declárase nula[s]…»;
(ii) nombra un **decreto con número y año** en ese mismo numeral, sin otro objeto de por medio (actuación, sentencia,
resolución, circular, acuerdo, ordenanza, ley); (iii) alcance TOTAL solo si entre el verbo y el decreto no hay «expresión»,
«aparte», «frase», «numeral», «inciso», «parágrafo», «literal»…, o dice «integridad/totalidad»; (iv) se descarta si el
resuelve tiene más de 3.500 caracteres (46 de 780; de ellas solo 4 tienen fórmula de nulidad: 3 arrastran sentencias
enteras y 1 es una resolución, no un decreto) o si trata de un nombramiento/elección; (v) el destino tiene que estar cargado (o quedar marcado «no cargado»).

- Sobre las 780 resolutivas: **12 numerales / 13 aristas (contando la extensión de efectos de `…-2013-00114-00:2020`), 8 fichas**.
  Leídas a mano: **13/13 correctas** en alcance y en decreto/artículo; 1 más se excluye a propósito (`co:ce:11001-03-28-000-2022-00212-00:2023`,
  Decreto 1555/2022, nombramiento).
- Sobre la muestra de 71: TP 8, FP 0, FN 1 (el Decreto 595/2020, nulidad implícita) respecto de «nulidad de un decreto».
- Recall: de 9 fichas que anulan un decreto, 8 las coge; se le escapa el Decreto 595/2020 (control inmediato: «no se
  encontró ajustado a derecho», sin la palabra nulidad; `co:ce:11001-03-15-000-2020-01833-00:2020`).
- **Advertencia honesta:** la regla se afinó mirando estas mismas 39 fichas (sesgo de ajuste). La precisión sobre fichas nuevas
  hay que medirla en la próxima tanda antes de fiarse; por eso todo lo que emite pasa por revisión humana (§4.c).

### 2.4 ¿De la propia resolutiva se sabe CUÁL artículo? Sí; la relatoría no lo dice

En las 8 fichas la resolutiva nombra decreto y artículo (y sub-parte) literalmente. La relatoría, en cambio, dice **qué se
demandó**, no qué cayó, y a veces ni eso:

- 5 de las 8 no traen «Norma demandada» (1814/2015, 1851/2015, 1073/2015, 2474/2008, 1555/2022); solo 3 tienen arista
  `interpreta` (2025/2009, 4994/2009, 935/2013) y ninguna a un destino cargado. Captura 3/8 frente a 8/8 de la resolutiva.
- La anotación «(Anulado)» de la relatoría no da el alcance: `DECRETO 935 DE 2013 – ARTÍCULO 2 (anulado)` y la resolutiva
  anula solo unos «apartes» de ese artículo. Leída como total mataría un artículo que sigue vivo.
- La relatoría dice `NIEGA` de una sentencia que declara nulos dos literales del Decreto 1073/2015
  (`co:ce:11001-03-26-000-2021-00207-00:2023`).
- La resolutiva usa la numeración del DUR aunque cite el decreto que la introdujo («artículo 2.2.6.1.7 del Decreto 1814 de
  2015», `co:ce:11001-03-15-000-2015-02578-00:2016`): el artículo vive en `co:decreto:1067:2015`. El puente existe en
  `relaciones.csv` (`co:decreto:1814:2015:art:1 adiciona co:decreto:1067:2015:art:2.2.6.1.7`, ídem 1851→1075). Y la
  resolutiva puede extender el efecto a otro artículo (`…-2013-00114-00:2020`, numeral SEGUNDO: 935/2013 art. 2 → DUR 1073 art. 2.2.5.1.3.4.1.2).

### 2.5 Trampas encontradas (todas vistas en el corpus)

| Trampa | Dónde | Efecto si se automatiza mal |
|---|---|---|
| ACCEDE = «se admite» / «se avoca» | `co:ce:11001-03-27-000-2018-00020-00:2018`; 7 autos admisorios en la muestra (6 contra el Decreto 1408/2021, 1 contra el 1419/2019) | mata decretos vivos |
| «previa suspensión provisional» en un auto admisorio | los mismos 7 | falsa suspensión |
| **Inaplicación** («inaplícanse los artículos 23 y 45 de la Ley 2080 de 2021, por contrarios…»), relatoría `NO APLICA` | `co:ce:11001-03-15-000-2021-00982-00:2021` y 3 más | mata artículos de `co:ley:2080:2021`, que siguen vivos (efecto entre partes) |
| Resolutiva que cita la sentencia de primera instancia («…la cual quedará así: “Primero: declarar la nulidad…”») o hasta 44.539 caracteres | `…-2006-00652-02:2017`, `…-2011-00583-00:2018`, `…-2008-00091-01:2015` | nulidades inventadas de sentencias revocadas |
| CONFIRMA una sentencia que declaró nulidad (electoral) | 5 fichas | doble conteo / dirección errada |
| Nulidad de acto particular con formato idéntico | 11 de 71 | mata un decreto de nombramiento o una resolución que no es norma |
| Nulidad procesal («declarar la nulidad de la actuación») | `co:ce:11001-03-15-000-2020-01289-00:2020` | asigna la nulidad al acto que se estaba controlando |
| Nulidad implícita («no se encontró ajustado a derecho», efectos hacia futuro) | `…-2020-01833-00:2020` | falso negativo |
| Auto que suspende, pero solo un inciso o una expresión | `co:ce:11001-03-26-000-2021-00207-00:2022`, `…-2018-00113-01:2022` (Decreto 92/2017) | `suspende` pondría todo el artículo SUSPENDIDO |

## 3. Cuestiones jurídico-semánticas para Juan (con mi recomendación)

1. **Efectos en el tiempo (ex tunc / ex nunc).** La ley solo dice que la sentencia de nulidad hace cosa juzgada erga omnes
   (`co:ley:1437:2011:art:189`); no fija desde cuándo, y la propia providencia a veces lo modula (2 de 8 casos leídos:
   «Los efectos de la presente providencia rigen hacia futuro», Decreto 595/2020; «sin perjuicio de las situaciones individuales
   y concretas de carácter definitivo… consolidado», `…-2013-00114-00:2020`). *Recomendación:* la vista `vigencia` solo responde
   «¿rige hoy?»: MUERTO en ambos casos; la modulación viaja copiada en la `nota`. No crear tipos aparte por efecto: la base no
   modela «vigente en la fecha X» y fingirlo sería peor que el aviso. Juan decide si algún día quiere un campo de efecto.
2. **Suspensión provisional ≠ muerte.** Es transitoria (termina con la sentencia o el levantamiento, que puede estar en otra
   ficha o no estar cargada) y casi siempre parcial (`co:ce:11001-03-26-000-2021-00207-00:2022`: un inciso y una expresión).
   Hoy no hay ninguna arista `suspende` en `relaciones.csv` (0 de 47.537) y `suspende` pone **todo** el artículo en SUSPENDIDO
   (vista `vigencia`, columna `suspendido`). *Recomendación:* no derivar `suspende` de las fichas; si se quiere, a mano y solo para
   suspensión de un artículo entero, con «hasta la sentencia» en la nota.
3. **Nulidad parcial de un artículo.** No mata: el resto rige. *Recomendación:* `declara_nulo_parcial` → `VIGENTE_CONDICIONADO`
   con la condición «NULIDAD PARCIAL — <qué cayó>» y una advertencia propia en el export (la de `VIGENTE_CONDICIONADO` dice
   «La Corte lo declaró exequible bajo una interpretación específica»: falsa para esto). No se toca el texto del artículo
   (regla 1: el texto es de la fuente); en los 6 artículos de DUR de la lista, el texto cargado **todavía trae la frase
   anulada** (verificado: p. ej. `co:decreto:1067:2015:art:2.2.6.1.7` sigue diciendo «Contra la decisión que niegue…no procede
   recurso alguno»).
4. **Acto ya derogado antes del fallo.** Ej. `co:ce:11001-03-26-000-2009-00024-00:2017` anula en 2017 artículos del Decreto 2474
   de 2008. *Recomendación:* registrar igual; `mata` acumula todas las causas (`group_concat`) y `MUERTO` no cambia. Lo único
   que cambia es el efecto en el tiempo (punto 1), que va en la nota.
5. **Qué fecha.** La de la providencia (`fecha` de la ficha). La ejecutoria no consta en la relatoría; el esquema pide la fecha
   en que «surte efecto». *Recomendación:* fecha de la providencia + «ejecutoria no verificada» en la nota. Como la vista
   compara con hoy y las sentencias son pasadas, no cambia el resultado.
6. **Dónde poner la arista cuando el decreto es modificatorio de un DUR.** *Recomendación:* solo en el artículo del DUR que
   el lector consulta. No en `co:decreto:1814:2015:art:1`: es un contenedor de todo el capítulo añadido y una nulidad ahí
   lo mataría entero.
7. **«Legalidad condicionada» / «ajustado a derecho» del CE** (control inmediato; 5 de 71, todas resoluciones no cargadas) y
   **«niega la nulidad»** (blindaje, cosa juzgada solo por la causa petendi, `co:ley:1437:2011:art:189`). No propongo tipos
   nuevos: no cambian la vigencia y hoy no hay dónde aplicarlos. Decisión de Juan.
8. **Cascada** (art. 189: la nulidad de una ordenanza o acuerdo deja sin efectos «en lo pertinente» sus decretos
   reglamentarios) y **reproducción** de actos anulados (`co:ley:1437:2011:art:237`): no modelables desde el grafo actual.
9. **Nulidad implícita en el control inmediato** («no se encontró ajustado a derecho», con «(Anulado)» de la relatoría):
   1 de 39 hoy. *Recomendación:* revisión manual caso a caso; no a regla.

## 4. Propuesta mínima

### 4.a Tipo nuevo y vigencia (`parche_build.diff`, `parche_export.diff`; NO aplicados)

- Hacen falta **dos** tipos: `declara_nulo` (nulidad total; mata como `deroga`, a norma entera o a artículo) y
  `declara_nulo_parcial` (como `declara_inexequible_parcial`: vigente, con la `nota` que dice qué cayó). Reusar
  `declara_inexequible` no sirve: el texto de advertencia dice «la Corte» y `TOTAL` se decide con la palabra «total» en la nota.
- `esquema.md`: 2 filas en la tabla de tipos, «los primeros diez son relaciones de afectación», nueva §6.1 (cuándo se registra,
  cuándo no, destino, fecha, nota) y dos ajustes en la regla 1 y 3 de §7. Texto exacto en `parche_build.diff` (primer archivo).
- `build.py` (parche): `MATA += declara_nulo`; `CONDICIONA += declara_nulo_parcial`; constante `NULO_PARCIAL`; en la condición,
  «NULIDAD PARCIAL — <nota>» (y «alcance no registrado» si la nota viene vacía: aviso, nunca muerte); 6 asserts nuevos en
  `check()`: total mata, parcial no mata y muestra qué cayó, fecha futura no mata, a norma entera mata, parcial sin nota avisa.
  Una arista `declara_nulo_parcial` no depende de la fecha (igual que las otras de `CONDICIONA`).
- `export.py` (parche): advertencia «NULIDAD_PARCIAL» (sin ella, un artículo con nulidad parcial saldría con la de
  `VIGENTE_CONDICIONADO`, que habla de la Corte), «declarado nulo» en la de MUERTO, chequeo en `violaciones()` y 2 asserts.
- Verificado: aplicado sobre una copia de los `build.py`, `export.py`, `esquema.md` de hoy, `build.py --check` y `export.py --check`
  imprimen `check OK`. Si otro agente toca esos archivos antes, el parche hay que reaplicarlo.

### 4.b Regla de extracción

`regla.py` (R2, §2.3) + `extrae_nulidades.py` (mapeo de destino y CSVs). Para el ingestor: añadir a `procesar_ce` una llamada
que, con el `resuelve` ya extraído, escriba aristas con `nota` que empiece por «CENDOJ:» (así `guardar_aristas` sigue siendo
idempotente). Recomiendo que **no entren solas a `relaciones.csv`**: pasar por `anadir_aristas.py` tras revisar el CSV, como
se hizo con las 79 muertes de P22, hasta que una tanda nueva confirme la precisión.

### 4.c CSVs (formato de `relaciones.csv`, 6 columnas)

- `candidatas.csv` — nulidad TOTAL inequívoca (3). Ninguna tiene el destino cargado, así que hoy son inertes:
  `co:ce:11001-03-26-000-2010-00027-00:2015 → co:decreto:4994:2009`; `co:ce:11001-03-26-000-2009-00024-00:2017 → co:decreto:2474:2008:art:44` y `:art:48`.
  Recomiendo guardarlas hasta que se cargue el decreto. **No hay ninguna candidata total con destino cargado.**
- `candidatas_parciales.csv` — 10 aristas `declara_nulo_parcial`, 6 con destino cargado (las que sí cambian el entregable):

| Destino | Providencia | Qué cayó |
|---|---|---|
| `co:decreto:1067:2015:art:2.2.6.1.7` | `co:ce:11001-03-15-000-2015-02578-00:2016` | expresión «Contra la decisión que niegue…» |
| `co:decreto:1067:2015:art:2.2.6.1.9` | ídem | expresión «No se dará trámite a aquellas solicitudes…» |
| `co:decreto:1073:2015:art:2.2.5.1.3.4.1.2` | `co:ce:11001-03-26-000-2013-00114-00:2020` | «aparte» (efecto extendido por el numeral SEGUNDO) |
| `co:decreto:1075:2015:art:2.3.1.3.2.17` | `co:ce:11001-03-26-000-2015-00158-00:2022` | numeral 2 |
| `co:decreto:1073:2015:art:2.2.3.5.2.2.1.1` | `co:ce:11001-03-26-000-2021-00207-00:2023` | literal f |
| `co:decreto:1073:2015:art:2.2.3.5.2.2.1.4` | ídem | literal a |

  Los 4 sin cargar: `2474/2008` arts. 7 y 88, `2025/2009` art. 9, `935/2013` art. 2.
- `candidatas_extractos.csv` — las 13 con `alcance`, `destino_cargado`, cómo se mapeó y el extracto literal de la resolutiva (≤ 300).
- `candidatas_fuente_nota.csv` — 3 aristas `declara_nulo` sacadas de la **nota de la propia fuente** (no de fichas); ver 4.d.
  El `origen` se arma con el radicado y la fecha que cita la nota (ninguna de las dos sentencias está cargada como ficha: entran
  a `origenes_sin_cargar`, que no es error). La nota dice «de 03/04/2020»: leído día/mes, 2020-04-03; si fuera mes/día, el
  efecto hoy es el mismo.
- `notas_nulidad_en_texto.csv` — los 24 artículos cargados cuyo texto ya dice que el CE anuló algo (3 totales, 21 parciales).

### 4.d Hallazgos que caen en otros dueños (para el orquestador)

1. **Vía de mayor seguridad: la nota de la fuente.** 24 artículos cargados (19 en `co:decreto:1625:2016`) traen «declarado nulo…
   Consejo de Estado» y hoy salen `VIGENTE`. 3 son totales y literales; una regex de nota final
   (`Artículo declarado NULO…`, `NOTA: El artículo N fue declarado NULO…`) da 3 aciertos y 0 falsos positivos en todo el corpus.
   Es el mismo tipo de «marcador de la fuente» que `build.py` ya lee para «derogado/INEXEQUIBLE», pero al final del texto. Sale
   más barato y más seguro que leer sentencias. (`co:decreto:1474:1997` está `compilada` y `afectaciones: pendiente`: sale
   `VIGENCIA_NO_VERIFICADA` aunque se cargue la arista.)
2. **`nota` de la arista `interpreta` engaña al lector.** Exportada tal cual dice «CENDOJ: norma demandada; decisión: ACCEDE»:
   13 registros de `co:decreto:2250:2017` (auto admisorio) y 1.998 de `co:decreto:1071:2015` («FALTA DE COMPETENCIA») la llevan en
   `afectado_por`. Una IA lee «ACCEDE» como «prosperó la demanda». Cambiar la nota (sin la palabra de la relatoría, o con la
   primera frase de la resolutiva) y no emitir arista a norma entera desde autos procesales. Dueño: `ingesta_webrelatoria.py`.
3. `decision()` en `ingesta_webrelatoria.py` es código muerto (§1, nota b). Su docstring atribuye la no-arista de muerte a que la
   relatoría no distingue nulidad total de parcial: lo cierto es que además la relatoría ni siquiera dice «nulidad».
4. `RE_NORMA` no reconoce «DECRETO REGLAMENTARIO», «DECRETO LEGISLATIVO» ni «DECRETO NACIONAL»: `co:decreto:595:2020`,
   `co:decreto:546:2020` no generan arista.
5. Volumen: 4 fichas de 873 (0,5 %) tocan un decreto cargado; el universo del CE es mucho mayor. Para subir el rendimiento,
   buscar en CENDOJ por tema los DUR cargados («DECRETO ÚNICO REGLAMENTARIO»…) en vez de recorrer términos genéricos (sin probar:
   ese host es del orquestador).
6. Sugerencia de línea para `cola.md`: «Nulidades CE: R2 (`regla.py`) da 13 aristas revisadas; tras aplicar el parche, cargar
   `candidatas_parciales.csv` (6 con destino cargado) y `candidatas_fuente_nota.csv`; medir precisión en la tanda siguiente».

## 5. ¿Es seguro automatizar «matar»?

- Desde la relatoría: **no**. Ni por `interpreta` ni por «Decisión».
- Desde la resolutiva con R2: la regla es segura en lo que emite (13/13), pero el conjunto que puede matar (total + cargado) es
  **vacío hoy**, y se afinó sobre estos mismos datos. No hay nada que matar por esta vía todavía.
- Lo que sí conviene ya: aviso de nulidad parcial en 6 artículos de DUR y, para matar, los 3 artículos cuya fuente lo dice
  literalmente. Orden sugerido: (1) parche de tipos, (2) `candidatas_fuente_nota.csv` + `candidatas_parciales.csv` por
  `anadir_aristas.py` tras revisarlas, (3) corregir la `nota` de las `interpreta`, (4) medir R2 en la próxima tanda antes de
  automatizar el ingestor.

## Archivos (todo en `<scratchpad>/nulidades/`)

`informe.md` · `parche_build.diff` (esquema.md + build.py) · `parche_export.diff` · `candidatas.csv` ·
`candidatas_parciales.csv` · `candidatas_extractos.csv` · `candidatas_fuente_nota.csv` · `notas_nulidad_en_texto.csv` ·
`muestra_71.csv` (etiqueta manual vs. R1 vs. R2) · `regla.py` (R2) · `extrae_nulidades.py` (genera los CSV; solo lectura) ·
`clasifica.py` (R1) · `analiza.py`, `cuant.py`, `gt.py`, `ver.py` (cuantificación y muestra) · `work/` (copias con el parche aplicado).
