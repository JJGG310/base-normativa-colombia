# Cola de ingesta

Estado del proyecto y del loop. Se lee al abrir cada tick y se actualiza al cerrarlo.

`[ ]` pendiente · `[~]` en curso · `[x]` hecho · `[!]` bloqueado (con motivo al lado)

Los conteos de artículos llevan `~` porque son estimados **solo para decidir si una
norma se parte en bloques**. No son dato: el número real se toma de la fuente.

---

## Procedimiento de cada tick

Una entrada por tick. Nunca dos. Un tick que abarca de más se queda a medias y deja
basura a medio escribir que el siguiente tick no sabe interpretar.

1. **Abrir `cola.md`.** Si hay una entrada `[~]`, esa es la del tick (quedó a medias);
   si no, la primera `[ ]` de la prioridad más alta.
2. **Marcarla `[~]` y guardar `cola.md` ya**, antes de trabajar. Si el tick muere,
   el siguiente sabe dónde quedó.
3. **El texto se extrae con script, nunca copiándolo a través del modelo.**
   Para secretariasenado.gov.co ya está `ingesta_senado.py` y sirve para todos los
   códigos de P1. Para una fuente nueva se escribe su parser una vez. Esto no es
   optimización: un script no puede inventar un artículo, un modelo transcribiendo sí.
   Como la extracción es mecánica, **no hay que partir las normas grandes en bloques**
   — el Código Civil entero cuesta lo mismo que un artículo. Partir solo aplica si
   alguna fuente obliga a transcripción manual.
4. **Obtener el texto de la fuente oficial** (`esquema.md` §8, en ese orden de
   preferencia). Si la primera fuente falla, se intenta la siguiente. Si fallan todas:
   `[!]` con el motivo y la URL que falló, y se pasa a la siguiente entrada.
   **Jamás se rellena con el texto que el modelo recuerda.**
5. **Verificar la extracción antes de darla por buena**: contar artículos contra el
   número conocido de la norma, y revisar 3 artículos sueltos (uno del principio, uno
   del medio, uno del final) contra la fuente. Un parser que se come el 20% de los
   artículos no falla ruidosamente, entrega un archivo que parece correcto.
6. **Extraer las afectaciones** que traiga la fuente (notas de vigencia, "modificado
   por", "derogado por", "declarado inexequible por") y agregarlas a `relaciones.csv`.
   SUIN-Juriscol es la mejor fuente para esto. Solo lo que la fuente afirme: no se
   deduce una derogatoria.
7. **`python3 build.py && python3 export.py`.** Si imprimen avisos o fallan, se
   corrige antes de cerrar. `contexto.jsonl` es el entregable: si no se regenera,
   el tick no sirvió de nada.
8. **Marcar `[x]`**, commit con el ID de lo cargado en el mensaje.
9. Si no quedan `[ ]` en P1, **detener el loop** y reportar. Si quedan, siguiente tick.

**Regla de oro:** ante la duda entre cargar algo incompleto o no cargarlo, no se carga
y se anota qué faltó. La base vale por lo que se puede confiar, no por lo que pesa.

---

## P1 — Troncales

Los siete códigos que cubren el grueso de las consultas, intercalados con la
jurisprudencia hito que los interpreta.

- [x] `co:constitucion:1991` — Constitución Política · **texto cargado**: 380 arts + 78 transitorios (incluidos los de los AL 02/2017 y 02/2021). `afectaciones: pendiente`
- [x] `co:constitucion:1991` — **afectaciones cargadas**: 6.516 aristas, 60 Actos Legislativos, 20 artículos muertos, 4 condicionados. Fuente resuelta: las notas viven en `js/<pagina>.js` (funciones `insRowNN`), no en el HTML. `ingesta_senado.py` ya las extrae para cualquier código de esta fuente.
- [x] jurisprudencia de la Corte Constitucional — **3.517 fichas** (crecida desde las 617 iniciales por rastrillo de más descriptores/años). 99% con descriptores oficiales, 100% con parte resolutiva, 99% con la decisión clasificada.
- [x] `co:ley:1564:2012` — CGP: 628 arts, 133 aristas, 6 muertos (art. 121 por C-443-19), 6 condicionados, reformas hasta 2025
- [x] `co:ley:84:1873` — Código Civil: 2.682/2.684 arts, 797 aristas
- [x] `co:ley:599:2000` — Código Penal: 556 arts (464/476 de la numeración original + adicionados), 787 aristas
- [x] `co:ley:906:2004` — CPP: 554 arts (533/533), 375 aristas
- [x] `co:decreto:410:1971` — C. de Comercio: 2.043 arts (2.035/2.036), 136 aristas
- [x] `co:ley:1437:2011` — CPACA: 311 arts (309/309), 196 aristas
### Jurisprudencia de P1: cerrada por la vía mecánica

Las entradas de «15 sentencias hito por rama» se escribieron antes de tener el
pipeline. Quedaron sin objeto: las 617 fichas cubren todas las ramas de P1 por el
grafo (penal 82, civil-familia 77, penal-procesal 68, laboral 62, comercial 19…),
y lo hacen sin que nadie eligiera a dedo cuáles eran las importantes.

Lo que sí queda pendiente es distinto y más caro — va a P3:

Lo que queda pendiente de jurisprudencia está en P3: es de otra naturaleza.
- [x] `co:decreto-ley:2663:1950` — CST: 497 arts (489/492), 492 aristas

### Normativa de P1: cerrada

8 códigos, 7.737 artículos, cobertura 99,7% contra la numeración oficial. Los ~20
faltantes son artículos que la fuente misma no publica. Recargable con `./cargar_p1.sh`
(caché en `fuentes/`, aborta si una norma queda por debajo de su mínimo).

## P2 — Especializadas

- [x] `co:ley:1563:2012` — Arbitraje: 119 arts
- [x] `co:ley:2136:2021` — Política Integral Migratoria: 91 arts
- [x] `co:decreto:1067:2015` — DUR Relaciones Exteriores: 450 arts, 204 aristas, vía `ingesta_gestor.py 74000`
- [x] `co:ley:100:1993` — Seguridad Social: 289 arts
- [x] `co:ley:80:1993` (82) + `co:ley:1150:2007` (32) — Contratación Estatal
- [x] `co:ley:1116:2006` — Insolvencia: 126 arts
- [x] `co:ley:1098:2006` — Infancia y Adolescencia: 217 arts
- [x] `co:decreto:624:1989` — Estatuto Tributario: 1.151 arts, 1.865 aristas
- [x] `co:ley-estatutaria:1581:2012` — Datos personales: 30 arts (falta el Decreto 1377/2013)
- [x] `co:ley:1801:2016` — Seguridad y Convivencia: 233 arts
- [x] `co:ley:99:1993` — Sistema Nacional Ambiental: 120 arts
- [x] `co:ley:1480:2011` — Estatuto del Consumidor: 84 arts
- [x] `co:ley:1952:2019` — Código General Disciplinario: 266 arts
- [x] `co:ley:769:2002` — Código Nacional de Tránsito: 171 arts
- [x] `co:decreto:1165:2019` — Regulación Aduanera: cargado del normograma DIAN (ver P3).

### P2: cargada (14 de 15)

`./cargar_p2.sh` para las 13 de senado, más `ingesta_gestor.py` para el DUR 1067.
El Decreto 1165/2019 salió del normograma DIAN (ver P3).

**Gestor Normativo de Función Pública** (`funcionpublica.gov.co/eva/gestornormativo/norma.php?i=N`):
accesible, a diferencia de SUIN. El índice de Decretos Únicos Reglamentarios está en
`i=62255`; el 1067/2015 es `i=74000`. Dos trampas: el `<meta charset>` declara
ISO-8859-1 pero el contenido es UTF-8, y los artículos usan numeración decimal
(`2.2.1.1.1`). Las afectaciones vienen inline como
`(Modificado por el Art. 1 del Decreto 124 de 2021)`. La fecha de expedición ya no se escribe a mano: sale de
la línea del Diario Oficial de la propia fuente (salvo el Estatuto Tributario, que
no la publica).

## Fuente de jurisprudencia — relevada, lista para parser

`corteconstitucional.gov.co/relatoria/<año>/<SERIE>-<num>-<aa>.htm` responde bien
(probado C-284-15 y C-443-19). La portada es un cascarón JS, pero las páginas de
sentencia son HTML plano. Ojo: vienen en **ISO-8859-1**, hay que decodificar.

Dos cosas que definen el diseño de la ficha:

1. **Cada sentencia pesa ~263.000 caracteres.** Pasarlas por el modelo es inviable:
   el grafo ya referencia ~1.500 sentencias distintas. La extracción tiene que ser
   mecánica, igual que la normativa.
2. **El texto abre con el bloque de descriptores y restrictores** de la relatoría
   («ACCESO A LA ADMINISTRACION DE JUSTICIA- Garantía del plazo razonable…»). Es el
   resumen oficial de la Corte, corto y citable. Sale gratis y sin riesgo de invención.

Plan: ficha mecánica (descriptores + parte resolutiva + expediente + MP) para todas;
la `subregla` redactada solo para las marcadas `hito`, que sí justifican leerlas.

- [x] parser de la relatoría: descriptores, RESUELVE, expediente, ponente **→ hecho: ingesta_relatoria.py**
- [x] la cola de sentencias sale sola del grafo: `SELECT DISTINCT origen FROM relaciones WHERE origen LIKE 'co:cc:%'` **→ hecho: `ingesta_relatoria.py --del-grafo`**

## Pendientes de la fuente senado (no bloquean, mejoran)

- [x] `concordancias`: las cajas no traían prosa, solo `<A href='ley_0388_1997.html#1'>`
  — `limpiar()` los tiraba antes de que `aristas()` los viera. `descripciones()` ahora
  guarda también el HTML crudo por caja, y `aristas()` reconoce tres patrones de
  `href` (`ley_/decreto_/acto_legislativo_NNN_AAAA`, y la constitución citándose a sí
  misma como `constitucion_politica_AAAA`). Recargada: 10.591 aristas `concordancia`
  nuevas, 10 cajas sin parsear de 2.153 (leyes muy recientes sin link, una sentencia
  listada sin `href`). El mismo patrón sirve para cualquier norma de senado con cajas
  de Concordancias, no solo la Constitución.
- [x] tipo de relación `renumera`: no hacía falta adivinar a partir de las notas
  históricas (ambiguas, `RE_HISTORICA` las descarta a propósito) — la propia fuente
  lo dice en el epígrafe o el cuerpo del artículo vigente ("...anteriormente era el
  artículo 263-A"). `ingesta_senado.py` ahora extrae `RE_RENUMERA` de `arts` después
  de `procesar()`. Solo 3 casos en toda la Constitución (AL 2/2015, electoral):
  262→261, 263→262, 263-A→263. Tipo agregado a `esquema.md`.
- [x] SUIN-Juriscol (2026-09-24): el SPA nuevo es un CMS genérico de MinJusticia **→ resuelto por archive.org (P21, ingesta_suin.py)**
  (`utu.minjusticia.gov.co`, `api-cms.minjusticia.gov.co`), sin API de documentos: los
  `viewDocument.asp` devuelven el cascarón para cualquier UA. **Respaldo:** la Wayback
  Machine guarda capturas (`archive.org/wayback/available?url=www.suin-juriscol.gov.co/viewDocument.asp?ruta=Leyes/1607782`
  → 2025-09-08); sirve para cotejar, no como fuente viva.
- [x] (nota anterior) SUIN-Juriscol: **ya no es bloqueo de bot.** El sitio migró entero a un SPA **→ ver P21**
  Angular ("GovcoFrontendBase") — `curl` con user-agent de navegador ahora responde
  200, pero solo devuelve el cascarón vacío; el contenido lo trae un bundle JS
  cargado por chunks (`main.<hash>.js`, 11 KB, sin URL de API visible — es un loader,
  no el bundle real). Encontrar el endpoint JSON exige devtools de navegador, no
  `curl` ciego: es un tick de investigación aparte, no un reintento. Sigue siendo
  no bloqueante (solo serviría como segunda fuente para cotejar afectaciones).

## P3 — Lo que faltaba de verdad

Diagnóstico del 2026-09-11, con P1 y P2 cerradas. Con 23 normas cargadas la base
cubre los códigos, pero tenía huecos que se ven al primer uso real: **no estaba la
tutela** (el trámite más frecuente del país), ni las demás acciones
constitucionales, ni el estatuto de la administración de justicia. Eso es más
grave que cualquier norma sectorial: el grafo ya cita cientos de sentencias de
tutela contra normas que sí están.

### A — Procesal constitucional y troncal administrativo · **cargada**

- [x] `co:decreto:2591:1991` — tutela: 55 arts
- [x] `co:ley:472:1998` — acciones populares y de grupo: 86
- [x] `co:ley:393:1997` — acción de cumplimiento: 32
- [x] `co:ley-estatutaria:270:1996` — administración de justicia: 231
- [x] `co:ley:600:2000` — CPP anterior (aforados y hechos < 2005): 558
- [x] `co:ley:1708:2014` — extinción de dominio: 220
- [x] `co:ley:2213:2022` — TIC en actuaciones judiciales: 15
- [x] `co:ley:489:1998` — organización de la Administración Pública: 121
- [x] `co:ley:909:2004` — empleo público y carrera administrativa: 59
- [x] `co:ley:1474:2011` — Estatuto Anticorrupción: 136
- [x] `co:ley-estatutaria:1712:2014` — transparencia y acceso a la información: 35
- [x] `co:ley:5:1992` — reglamento del Congreso: 424

### B — Civil, societario, laboral y consumo · **cargada**

- [x] `co:ley:222:1995` (247) · `co:ley:1258:2008` (46) — sociedades y SAS
- [x] `co:ley:1010:2006` — acoso laboral: 19
- [x] `co:ley:776:2002` (23) · `co:ley:1562:2012` (33) — riesgos laborales
- [x] `co:ley:797:2003` — reforma pensional: 24
- [x] `co:ley:1996:2019` — capacidad legal: 63
- [x] `co:decreto:1260:1970` — registro del estado civil: 124
- [x] `co:ley:1257:2008` — violencia contra las mujeres: 37
- [x] `co:ley:1123:2007` — Código Disciplinario del Abogado: 112
- [x] `co:ley-estatutaria:1266:2008` — habeas data financiero: 22
- [x] `co:ley:1915:2018` — derecho de autor: 25

### C — Territorial, ambiental, electoral y víctimas · **cargada**

- [x] `co:ley:388:1997` — ordenamiento territorial: 140
- [x] `co:ley:160:1994` — reforma agraria: 113
- [x] `co:decreto-ley:2811:1974` — Código de Recursos Naturales: 340
- [x] `co:ley:1448:2011` — víctimas y restitución de tierras: 207
- [x] `co:decreto:2241:1986` — Código Electoral: 218
- [x] `co:ley:1475:2011` — partidos políticos: 55
- [x] `co:ley:136:1994` (203) · `co:ley:1551:2012` (50) — régimen municipal
- [x] `co:decreto-ley:1421:1993` — Estatuto Orgánico de Bogotá: 181
- [x] `co:ley:142:1994` — servicios públicos domiciliarios: 186

`./cargar_p3.sh` recarga las tres tandas (todas viven en senado).

**Lo que costó esta tanda** (tres arreglos a `ingesta_senado.py`, todos con el mismo
patrón: la fuente es irregular y el parser fallaba en silencio o se plantaba):

1. La fecha del Diario Oficial se escribe de cuatro formas distintas («de 6 de
   agosto de 1998», «del 2000», «de 26 de agosto 2019», «de 1o. de agosto») y en las
   normas largas el índice de artículos la empujaba más allá del corte de 15.000
   caracteres. 8 normas no se cargaban por esto.
2. La fuente corta la red (ENETUNREACH) tras muchas descargas seguidas. Esperar 2s
   entre reintentos no alcanzaba y se caía el resto de la tanda: ahora espera 20s.
3. **Artículos resueltos en el encabezado** («ARTÍCULO 10. DECLARADO INEXEQUIBLE.»,
   sin cuerpo) se perdían. 22 de la Ley 270 — la misma clase de fallo que ya costó
   823 artículos antes. De ahí salió `verificar.py`.

`python3 verificar.py` contrasta cada `.md` contra el índice de artículos de la propia
fuente (el `<select>` de la página). Hoy: **0 faltantes en las 57 normas de senado**.

### D — Fuera de senado (requieren otra fuente)

- [x] `co:ley:23:1982` — derecho de autor: 260 arts, vía Gestor `i=3431`
- [x] `co:decreto:663:1993` — Estatuto Orgánico del Sistema Financiero: 339 arts, `i=1348`
- [x] `co:decreto-ley:2158:1948` — Código Procesal del Trabajo: 155 arts, `i=5259`.
  Era el hueco más raro del corpus: estaba el CST sin su procesal.
- [x] `co:decreto:1377:2013` — reglamento de datos personales: 28 arts, vía Gestor `i=53646`

**Buscar el `i=` de una norma en el Gestor**: no hay endpoint de búsqueda usable
(el buscador es JS). Sale de una búsqueda web contra `funcionpublica.gov.co`, y una
vez ubicado se anota aquí. El Gestor sirve para normas viejas sin ancla (`<a name>`):
`ingesta_gestor.py` las corta por el encabezado en línea propia.
- [x] `co:decreto:1165:2019` — Regulación Aduanera: **775 artículos**, del normograma
  de la DIAN (`normograma.dian.gov.co/dian/compilacion/docs/decreto_1165_2019.htm`).
  Lo publica el mismo proveedor que senado, así que `ingesta_senado.py` lo cargó sin
  un solo cambio. 2026-09-24: afectaciones **cargadas** (247 aristas: 179 modifica,
  64 adiciona, 4 deroga). Las notas sí viven en `js/`, pero en `docs/js/x.js` y no en
  `basedoc/js/`; `ingesta_senado.py` ahora arma la ruta junto a la página. Las 938 notas
  no reconocidas son todas Concordancias (sin efecto en vigencia).
- [x] `can:decision:486:2000` — propiedad industrial: 280 arts + 3 transitorias, vía
  `ingesta_can.py` (nuevo). Fuente: PDF oficial de FAO Lex
  (`faolex.fao.org/docs/pdf/anc83522.pdf`) — WIPO Lex también lo tiene pero su sitio
  es un SPA sin URL de PDF estable por curl. Extracción con PyMuPDF (`fitz`, ya
  instalado, no fue necesario agregar dependencia). Primer prefijo no-`co:` del
  proyecto (`can:`, agregado a `esquema.md` §2) porque no es norma del Congreso
  colombiano aunque aplique directo. `afectaciones: pendiente` — no se rastrearon
  las Decisiones 632/2006 y 689/2008 que la modifican; export.py ya la marca
  `VIGENCIA_NO_VERIFICADA` correctamente mientras tanto.
- [x] Los 20 DUR completos vía `ingesta_gestor.py` (`./cargar_dur.sh`): 1066-1085,
  todos en `documentos` con sus aristas. El `i=` de cada uno sale del índice del
  Gestor (`norma.php?i=62255`). Verificado 2026-09-22: 11/12 sin faltantes, el 1066
  (interior) tiene 1 artículo sin extraer (`1.1.2.3`) — no bloquea, queda anotado.

## P4 — Sectoriales · **cargada** (`./cargar_p4.sh`)

Salud: `co:ley-estatutaria:1751:2015` (26) · `co:ley:1438:2011` (149) ·
`co:ley:1122:2007` (46) · `co:ley:9:1979` Código Sanitario (617).
Educación y cultura: `co:ley:30:1992` (146) · `co:ley:115:1994` (222) ·
`co:ley:397:1997` (89).
Minero-energético, TIC: `co:ley:685:2001` Código de Minas (362) ·
`co:ley:143:1994` (97) · `co:ley:1341:2009` (74).
Territorial y riesgo: `co:ley-organica:1454:2011` LOOT (40) · `co:ley:1523:2012` (96).
Penal y penitenciario: `co:ley:65:1993` (181) · `co:ley:1709:2014` (107) ·
`co:ley:1826:2017` (44) · `co:ley:2197:2022` (69).
Tributario y administrativo reciente: `co:ley:1819:2016` (376) ·
`co:ley:2010:2019` (61) · `co:ley:2277:2022` (96) · `co:ley:2080:2021` (87) ·
`co:ley:2195:2022` (69) · `co:ley:2069:2020` (72) ·
`co:ley-estatutaria:1755:2015` (2).

Dos avisos de la fuente, no del parser: de la Ley 2010 de 2019 senado publica 61
artículos (el resto quedó absorbido en el Estatuto Tributario) y la Ley 1755 de
2015 son dos artículos, porque su contenido sustituye el título II del CPACA.

### E — Caro o de otra naturaleza (no es un tick mecánico)

- [x] `subregla` redactada para las sentencias `hito`. Exige que el modelo lea la **→ 2026-09-25: las 16 hito tienen subregla, redactada desde pasajes de la fuente**
  providencia (~260.000 caracteres cada una), así que es una decisión de presupuesto,
  no un tick más. Las fichas ya sirven sin esto.
- [x] **Corte Suprema: abierta**, las tres salas con texto íntegro. `ingesta_cendoj.py`
  (`./cargar_csj.sh`). **1.061 providencias**: 840 civil/laboral (2022-2025) + 206 penal
  (2022-2025, cargada el 2026-09-19 tras resolver el punto 4). Cuatro cosas definen
  esta fuente:
  1. El GraphQL (`consultaprovidenciasbk.cortesuprema.gov.co/api`) **exige término de
     búsqueda**: con la consulta vacía devuelve 0. No hay forma de pedir «todo el año»,
     así que se rastrilla por términos amplios y se deduplica. La cobertura es la de
     los términos, no la de la Corte: subir `--limite`, agregar años o agregar términos
     es la perilla.
  2. `getContentSearch` **no devuelve el texto completo**: da una vista previa con
     elisiones `(…)` alrededor de lo buscado. Las primeras fichas salieron con huecos y
     se borraron. El texto íntegro se baja del `.docx` por `downloadFile` y se extrae
     con `zipfile` de la stdlib.
  3. La misma providencia aparece en `.pdf` y en `.docx`: solo se toma el `.docx`. Lo
     que la Corte publica únicamente en PDF se salta — y hay salas-año enteras así
     (laboral 2023: 12.950 providencias, ni un `.docx`). Leerlas exigiría un extractor
     de PDF, que es una dependencia nueva: decisión pendiente, no un tick. **→ resuelto: PyMuPDF ya lo hace
     desde ee89821 (laboral 2023 tiene 1.265 fichas); ver P23-P25.**
  4. **Sala penal — resuelto (2026-09-19)**: no era que la fuente no sirviera los
     archivos, era la ruta. El buscador indexa
     `PENAL/<año>/Dr. X/Sentencia/<archivo>`, pero el storage real no tiene esa
     carpeta de magistrado: vive en `PENAL/<año>/<archivo>`. `downloadFile` con la
     ruta tal cual daba 404; recortada, 200. Confirmado contra 5 providencias
     (2022-2025) antes de cargar las 206. `ruta_real()` en `ingesta_cendoj.py` hace
     el recorte, solo para PENAL.
- [x] Consejo de Estado: **abierto, con matices.** `ingesta_samai.py` (nuevo) replica
  a mano el postback parcial de ASP.NET (ScriptManager + UpdatePanel) contra
  `samai.consejodeestado.gov.co/TitulacionRelatoria/BuscadorProvidenciasTituladas.aspx`
  — no hace falta navegador ni Selenium. Tres cosas que costó entender:
  1. La página del buscador **no emite `ASP.NET_SessionId`** por sí sola — hay que
     pedir primero la portada (`/`) para que la sesión exista, si no el postback
     falla con «Validation of viewstate MAC failed». No es un bug del sitio, es que
     el buscador asume que ya veniste de la portada.
  2. La respuesta viene en el formato «delta» de Microsoft Ajax
     (`longitud|tipo|id|contenido|...`), y la longitud está en **bytes UTF-8, no en
     caracteres** — con texto acentuado (todo el sitio) un parseo por caracteres
     desalinea cada bloque después del primero. Hay que operar sobre `bytes`.
  3. Cada tarjeta de resultado de la "Búsqueda rápida" (texto libre con AND/OR/AND
     NOT) ya trae radicado, interno, fecha del proceso, clase, ponente, sala, actor,
     demandado, fecha de la providencia, tipo y el hash del documento — **sin pedir
     nada por providencia aparte**. De ahí sale una ficha mecánica honesta, igual de
     buena que la de Corte Suprema antes de tener texto.
  - **El texto completo NO se pudo bajar**: `samaicore.consejodeestado.gov.co/api/
    DescargarProvidenciaPublica/{corporacion}/{numProceso}/{hash}/{modo}` devuelve
    **403 siempre**, probado con distintos `modo` (0-4), el token como `Authorization:
    Bearer`, como query `tokendoc` en el endpoint hermano `DescargarProvidenciaSAMAI`
    (ese dio 500) — pese a que el propio swagger del servicio
    (`samaicore.../swagger/v1/swagger.json`, público) marca la ruta **sin
    `security`**, o sea que documentalmente debería ser anónima. Es un bloqueo de
    infraestructura (Azure), no de la lógica de la app: investigado 2026-09-22, sin
    resolver. Cada ficha queda con `fuente:` apuntando al expediente en SAMAI para
    que un humano lo abra directo.
  - Corpus real: "responsabilidad medica" solo ya trae ~158.000 resultados (Página
    1 de 15.803) — esto no es "toda la jurisdicción contenciosa" ni de cerca, es lo
    que alcancen los términos, igual que Corte Suprema. Subir `--limite` o agregar
    términos es la perilla.
  - El backend JSF viejo (`190.217.24.55:8080/WebRelatoria/ce/`) sigue sin responder
    (timeout) — ya no importa, SAMAI es la vía.
- [~] El grafo no conecta la Corte Suprema con la normativa: sus providencias no **→ en curso: aristas `cita` desde la FUENTE FORMAL de CENDOJ (cargar_cendoj.sh)**
  afectan vigencia, así que entran sin aristas. Si se quiere que un artículo muestre
  «qué dijo la casación», hay que extraer las citas del propio texto.

---

## P6 — Vivienda, laboral reciente, financiero, étnico, DUR 2016 · **cargada** (`./cargar_p6.sh`)

Todas con `verificar.py` en `faltan 0` (2026-09-23).

- [x] Vivienda y registro: `co:ley:675:2001` (87) · `co:ley:820:2003` (43) · `co:ley:1579:2012` (104)
- [x] Laboral y pensional: `co:ley:2381:2024` (95) · `co:ley:789:2002` (52) · `co:ley:2101:2021` (8) ·
  `co:ley:2466:2025` (70) — la reforma laboral de 2025; el número se tomó de senado
  («Reforma Laboral para el trabajo decente y digno en Colombia»).
- [x] Penal: `co:ley:1453:2011` (111) · `co:ley:890:2004` (15 — la ley es así de corta).
- [x] Fiscal: `co:ley:610:2000` (69). Disciplinario ya estaba: `co:ley:1952:2019`
  (la 734/2002 que deroga no se cargó).
- [x] Financiero y competencia: `co:ley:1328:2009` (103, incluye 2 transitorios fuera del
  índice) · `co:ley:964:2005` (86) · `co:ley:527:1999` (47) · `co:ley:1340:2009` (34) ·
  `co:ley:256:1996` (33)
- [x] Ambiental y étnico: `co:ley:1333:2009` (70) · `co:ley:70:1993` (68)
- [x] `co:ley:1450:2011` — PND 2010-2014: 276. Arreglo a `ingesta_senado.py`: las
  secciones numeradas del plan («2.6 VIVIENDA Y CIUDADES AMABLES», `name="2.6-IIIII"`)
  entraban como artículos falsos; ahora se saltan.
- [x] DUR vía Gestor: `co:decreto:1833:2016` pensiones (967, `i=85319`) ·
  `co:decreto:780:2016` salud (2291, `i=77813`) · `co:decreto:1625:2016` tributario
  (2130, `i=83233`). Traen 4/8/15 artículos que el índice del Gestor no lista (revisados:
  son artículos reales agregados después, p. ej. megainversiones 1.2.1.28.1.x).
- [x] (resuelto en P10) `co:ley:21:1991` — Convenio 169 OIT. Senado no la publica (`ley_0021_1991.html`
  404). En el Gestor (`i=37032`) `ingesta_gestor.py` la parte mal: los arts. 1-3 de la
  ley chocan con los 1-3 del Convenio y el art. 6 del Convenio (consulta previa, «ARTICULO
  6°» sin punto) queda pegado al 5. Hace falta decidir cómo identificar los artículos del
  tratado (¿`art:convenio-6`?) y ajustar el parser. No se escribió archivo.

## P7 — CPTSS 2025, notarial, estatutarias, PND, reformas tributarias · **cargada** (`./cargar_p7.sh`)

Todas con `verificar.py` en `faltan 0` (2026-09-23), salvo la 294/1996.

- [x] Procesal laboral: `co:ley:2452:2025` (331) — nuevo CPTSS.
- [x] Administrativo, notarial, familia: `co:decreto:19:2012` (238) · `co:decreto:960:1970` (233)
- [x] Estatutarias: `co:ley:1095:2006` (10) · `co:ley-estatutaria:137:1994` (59)
- [x] PND: `co:ley:1753:2015` (268) · `co:ley:1955:2019` (336) · `co:ley:2294:2023` (372)
- [x] Tributario y cartera: `co:ley:6:1992` (140) · `co:ley:223:1995` (285, fecha pasada a
  mano: la fuente escribe «de 22 diciembre 1995» sin «de») · `co:ley:788:2002` (118) ·
  `co:ley:1607:2012` (217) · `co:ley:1943:2018` (122) · `co:ley:1231:2008` (10) ·
  `co:ley:1066:2006` (21) · `co:decreto-ley:403:2020` (166)
- [x] Nacionalidad, insolvencia, vivienda, contratación: `co:ley:43:1993` (39) ·
  `co:ley:2445:2025` (45) · `co:ley:546:1999` (58) · `co:ley:1882:2018` (21)
- [x] `co:ley:294:1996` — 31 de 31. Senado lista el art. 6 pero no publica su texto; se
  tomó del Gestor (`i=5387`) con una marca de fuente al inicio del artículo, y la arista
  Ley 575/2000 art. 3 con nota `manual:`. **Reingestar desde senado borra ese art. 6
  del `.md`** (la arista sí sobrevive: `guardar_relaciones` conserva las `manual:`).
- [x] `co:ley:54:1990` — 9 arts del Gestor (`i=30896`) con `ingesta_gestor.py --anclas-id`
  (acepta `<a id=N>` solo en esta página, los DUR no cambian). El Gestor ahora corta las
  firmas en «Dada en» y quita el número repetido de un artículo sin epígrafe. Aristas:
  4 de Ley 979/2005 (automáticas) + 3 `manual:` — Ley 2447/2025 art. 10 → art. 1 (el
  Gestor escribe «2247», errata: cotejado contra el texto de la 2447 en senado),
  C-700/2013 y C-257/2015 → art. 2 (fecha aproximada). C-075/2007 ya estaba.

## P8 — Ramas faltantes y reformadoras más citadas · **cargada** (2026-09-24, 4 agentes en paralelo)

- [x] Discapacidad: `co:ley:361:1997` (73) · `co:ley-estatutaria:1618:2013` (32) · `co:ley:1346:2009` (50)
- [x] Internacional privado: `co:ley:518:1999` (101, CISG; sus `.js` de vigencia dan 404 → `afectaciones: pendiente`)
- [x] Fuerza pública: `co:ley:1407:2010` CPM (632) · `co:ley:1862:2017` disciplinario militar (252)
- [x] Territorial: `co:ley:617:2000` (97) · `co:ley:715:2001` (114) · `co:ley-organica:152:1994` (52) · `co:ley:1530:2012` (160)
- [x] Cambiario/contable/marítimo: `co:ley:9:1991` (35, Gestor `i=80013`) · `co:decreto:2420:2015`
  (33, Gestor `i=76745`; el grueso son anexos) · `co:decreto:2324:1984` decreto-ley DIMAR (195, Gestor `i=78442`)
- [x] Disciplinario: `co:ley:734:2002` (227) · `co:ley:2094:2021` (75). En la 734, senado lista los arts. 41-43
  pero no los publica: salen del Gestor (`i=4589`) con marca de fuente, + arista `manual:` C-124/2003 → art. 43.
  **Reingestar desde senado los borra del `.md`.**
- [x] Sueltas: `co:ley:1715:2014` (51) · `co:ley:1978:2019` (51) · `co:ley:2300:2023` (10) ·
  `co:ley-estatutaria:1621:2013` (46) · `co:ley:1762:2015` (56)
- [x] Reformadoras: `co:ley:1151:2007` (160) · `co:ley:812:2003` (137) · `co:ley:1111:2006` (78) ·
  `co:ley:488:1998` (155) · `co:ley:633:2000` (134) · `co:ley:863:2003` (69) · `co:ley:795:2003` (114) ·
  `co:ley:49:1990` (83, Gestor `i=6545`) · `co:ley-estatutaria:2430:2024` (93, reforma a la Ley 270)
- [x] `co:ley-estatutaria:2430:2024`: notas de la revisión previa C-134/2023 — resuelto en P10.
- [x] `co:ley:50:1990` y `co:decreto:648:2017` — resueltos en P9.
- [x] Ramas en uso no listadas en `esquema.md` §5 — resuelto en P10.

## P9 — Normas origen más citadas (build.py -v) · **cargada** (2026-09-24)

`cargar_p9.sh`. Todas con `faltan 0`.
- [x] Sentencia `co:cc:c-264:2026` (reforma pensional, Ley 2381/2024; 91 aristas ya en el grafo).
- [x] Senado: `co:ley:510:1999` (123) · `co:ley:1142:2007` (56) · `co:ley:962:2005` (89) ·
  `co:ley:104:1993` (150) · `co:ley:2421:2024` (78; las notas de su `_pr001` no se publican:
  solo 3 cajas) · `co:decreto:2106:2019` decreto-ley (158).
- [x] Normograma DIAN: `co:decreto:360:2021` (148) · `co:decreto:659:2024` (68) ·
  `co:decreto:1643:1991` decreto-ley (110).
- [x] `co:ley:50:1990` (117, 60 aristas) — **normograma de la Cancillería**
  (`cancilleria.gov.co/normograma/compilacion/docs/`), misma plataforma que senado. Python no
  negocia su TLS: se bajó con `curl` al caché de `ingesta_senado` (`fuentes/cache/`) y se ingirió de ahí.
- [x] Gestor, decretos que reforman un DUR, con el nuevo `ingesta_gestor --enteros` (los
  decimales transcritos, «quedará así: ARTÍCULO 2.2.18.1.1…», son texto del artículo que los
  contiene; `verificar.py` lo detecta solo si el archivo no tiene decimales): 1743/2015 (70) ·
  1330/2019 (2) · 2029/2015 (6) · 1851/2015 (2) · 65/2020 (50) · 1835/2021 (22) · 770/2021 (6) ·
  648/2017 (19; la nota anterior de «2 artículos» era otro error del parser) · 1042/2022 (22, sin `--enteros`).
- Arreglos al parser del Gestor: (1) «DECRETA:» ya no hace saltar el art. 1 (la regla de «…así:»
  solo aplica con un artículo previo); (2) encabezados con espacio inicial (« ARTÍCULO 2°.») se
  reconocen en `ingesta_gestor` y en el índice de `verificar.py` — destapó 2 artículos que le
  faltaban al DUR 1083 (2.2.18.3.10, 2.2.18.5.4), ya reingerido: 930, aristas idénticas.

## P10 — Normas origen más citadas, estatutarias, Convenio 169 · **cargada** (2026-09-24)

`cargar_p10.sh`. Todas con `faltan 0`.
- [x] Senado: `co:ley:241:1995` (63) · `co:ley:418:1997` (143) · `co:ley:1849:2017` (58) ·
  `co:ley:1739:2014` (77) · `co:ley:1592:2012` (41) · `co:ley:982:2005` (47) · `co:ley:1430:2010` (68) ·
  `co:ley:1152:2007` (178) · `co:ley:383:1997` (74) · `co:ley-estatutaria:134:1994` (109; la fuente la
  titula «LEY <ESTATUTARIA>», el alias de build.py resuelve las citas a `co:ley:134:1994`).
  Sin `.js` de notas (404) en alguna página: 1849/2017, 982/2005, 1152/2007 (`_pr002`).
- [x] Gestor `--enteros`, reformadores de DUR: `co:decreto:104:2025` (1069) · `1836:2021` y `1167:2023`
  y `1338:2021` (1074) · `1783:2021` (1077) · `1063:2024` (1070) · `1648:2021` (1085) · `1650:2021`
  (1072) · `2348:2015` (1067). DUR de Regalías `co:decreto:1821:2020` (374, 129 aristas).
- [x] `co:ley:21:1991` (Convenio 169 OIT, Gestor `i=37032`, 44). Decisión: como la Ley 518/1999
  (CISG), los artículos del tratado son `art:N` — así se citan («art. 6 del Convenio 169»); los
  arts. 1-3 aprobatorios de la ley quedan en el texto del art. 44, tras la constancia de Cancillería.
  Los arreglos de P9 al parser del Gestor ya lo parten bien (el art. 6 ya no queda pegado al 5).
- [x] `ingesta_senado.aristas()`: la revisión previa de estatutarias dice «declara CONSTITUCIONAL /
  INCONSTITUCIONAL» (no EXEQUIBLE); ahora se lee (sensible a mayúsculas: «Corte Constitucional» no
  cuenta), y «salvo / excepto / las expresiones» marcan parcialidad. Re-ingesta de las 12
  estatutarias: 1957/2019 (JEP) pasa de 3 a 149 aristas de la C-080/2018, 270/1996 de 231 a 276,
  2430/2024 de 0 a 94 (C-134/2023).
- [x] `esquema.md` §5: vocabulario de ramas completado con las etiquetas en uso; `justicia`,
  `notarial` e `internacional` normalizadas a `procesal`/`notarial-registral`/`internacional-publico`.

## P11 — Normas origen más citadas (tras P10) · **cargada** (2026-09-24)

`cargar_p11.sh`. Todas con `faltan 0`.
- [x] Senado: `co:ley:782:2002` (46) · `co:ley:1421:2010` (23) · `co:ley:1395:2010` (122) ·
  `co:ley:1285:2009` (28) · `co:ley:200:1995` (178, `estado_general: derogada` — la propia fuente
  anota su reemplazo por la Ley 734/2002) · `co:ley:2200:2022` (154) · `co:ley:1382:2010` (31) ·
  `co:ley:1617:2013` (138).
- [x] Gestor: decretos-ley `co:decreto:2351:1965` (42, reforma al CST) y `co:decreto:2820:1974`
  (71, igualdad de derechos, reforma al CC); reformadores `--enteros`: `1142:2021` y `804:2021`
  (DUR 1821) · `1381:2024` y `739:2021` (1077) · `1033:2021` (1066) · `1494:2021` (1068) · `149:2024` (1080).
- [x] DIAN: `co:decreto:2229:2023` (plazos 2024, DUR 1625).
- [x] Relatoría `--del-grafo --limite 40`: 36 fichas de sentencias ya citadas (entre ellas la
  C-080/2018, revisión de la estatutaria de la JEP). Fallan C-006, C-194 y C-293 de 2026: la
  relatoría aún no publica descriptores ni resolutiva.
- [x] `ingesta_gestor`:
  - «ARTÍCULO. 8.» (punto tras la palabra) se reconoce (también en `verificar.py`).
  - «ARTÍCULO 11. 1. Los salarios…» ya no se lee como el DUR «11.1»: el espacio tras el primer
    punto solo vale si sigue otro decimal («2. 1.11.10»).
  - Regresión de P9 corregida: `partir()` descartaba los artículos decimales previos a la primera
    ancla (libro 1 de los DUR). Recuperados 1068 (8), 1080 (1.1.1.1), 1082 (1.1.1.1).
  - `fecha_norma` acepta «DECRETO NÚMERO 0149 DE 2024».
  - Re-ingesta de 13 DUR: +21 artículos reales, 0 perdidos. Límite conocido: dos encabezados con
    errata en la fuente («ARTÍCULO 2. 2..3.3.4» en el 780, «ARTÍCULO 2. 7 .1.1.» en el 1080) antes
    salían con ID basura (`2.2`, `2.7`); ahora su texto queda dentro del artículo anterior.
- [x] Corregida la `fuente:` de los 11 documentos del Gestor de P10 (URL anidada `norma.php?i=https://…`).

## P12-P14 — Actos legislativos, leyes y decretos origen con ≥20 aristas · **cargada** (2026-09-24)

Criterio de parada adoptado: cargar todo origen faltante con ≥20 aristas, todos los actos
legislativos citados y todas las sentencias citadas que la relatoría sirva. Por debajo de 20
aristas la cola es larga (≈3.800 normas, casi todas con 1-4 citas).
- [x] P12 `cargar_p12.sh`: 60 de los 61 actos legislativos citados (senado; título = epígrafe de
  la fuente, generado por script; el AL 1/2004 no tiene epígrafe: título del encabezado de su
  único artículo). Todos con `faltan 0`.
- [x] `co:acto-legislativo:1:1999` (2 aristas): la página de senado no trae el articulado (solo **→ P21: articulado desde SUIN vía archive.org**
  epígrafe y la nota aclaratoria del DO 43.662); el normograma de la Cancillería, igual.
- [x] P13 `cargar_p13.sh`: 33 leyes de senado (estatutarias 1757/2015, 130/1994, 1909/2018;
  orgánicas 152/1994, 819/2003, 1454/2011, 2116/2021; 190/1995, 2056/2020, 2155/2021, 446/1998,
  712/2001, 454/1998, 42/1993, 1765/2015…) + decretos-ley 902/2017 y 1122/1999 + Gestor: Ley
  153/1887 (`i=15805`) y Ley 6/1990 (`i=9028`). Ley 689/2001 con `--fecha 2001-08-28` (encabezado).
- [x] `co:ley:57:1887` (30 aristas): senado 404; el Gestor (`i=39535`) responde «No disponible». **→ P20: normograma CREG**
- [x] `co:ley:11:1984` (28 aristas): senado 404; no aparece en el Gestor. **→ P20: normograma Cancillería**
- [x] P14 `cargar_p14.sh`: 26 reformadores de DUR del Gestor (`--enteros`), 7 decretos
  tributarios del normograma DIAN y 2 de **otros normogramas con la plataforma de senado**:
  MinTIC (`normograma.mintic.gov.co/mintic/compilacion/docs/`, Decreto 2640/2022) y Keralty
  (`normograma.com/keralty/compilacion/docs/`, Decreto 1136/2025). Python sí negocia su TLS.
- [!] `co:decreto:2358:2019` art. 16: la fuente numera 15, 17, 16, 17 (errata); el texto del
  16 queda dentro del art. 17 anterior. `faltan 1` aceptado por errata de la fuente.
- [x] `ingesta_gestor`: un «artículo 991 ibídem» en minúscula al inicio de una línea partida se
  tomaba como encabezado y, como el corte solo avanza, se tragaba los 36 artículos siguientes del
  Decreto 431/2017 (10 → 46). El encabezado ahora exige «ARTÍCULO/ARTíCULO/Artículo» (también en
  `verificar.py`). Sin pérdidas en los demás documentos del Gestor.
- [x] Relatoría `--del-grafo --limite 450`: 318 fichas más. 28 sin descriptores ni resolutiva en
  la relatoría (casi todas 2025-2026, aún sin procesar): C-067, C-194, C-293, C-006, C-033,
  C-081, C-048, C-062, C-192, C-197, C-212, C-220 de 2026; C-196, C-504, C-136, C-183, C-206,
  C-224 de 2025; C-280/2024; C-099/2012, C-194/2012, C-682/2012; C-114/2009; C-120/2019,
  C-308/2019; C-1058/2000; C-122/2007, C-140/2007.

## P15 y vigencia de normas muertas enteras · **cargada** (2026-09-24)

`cargar_p15.sh`: `co:ley:905:2004` (25) · `co:ley:2068:2020` (56) · `co:decreto:266:2000` (164,
declarado INEXEQUIBLE entero) y la sentencia `co:cc:c-073:2018` (81 aristas). Con esto no queda
ningún origen cargable con ≥20 aristas (restan `co:ley:57:1887` y `co:ley:11:1984`, bloqueadas, y
la C-067/2026, aún sin publicar en la relatoría).

- [x] **`build.py` no reconocía la muerte de normas enteras** marcada en el texto de cada artículo:
  6 leyes completas salían VIGENTES en `contexto.jsonl` — 104/1993 (derogada por la 418/1997),
  1152/2007 (C-175/09), 1382/2010 (C-366/11, efectos diferidos 2 años), 1530/2012 (derogada por la
  2056/2020), 43/1993 (derogada por la 2332/2023) y 1943/2018 (inexequible desde el 1-1-2020) —,
  más los decretos 266/2000 y 1122/1999. `RE_MARCA` ahora reconoce «<Ley/Decreto/Acto Legislativo
  [declarado] derogado|INEXEQUIBLE…>» sin número, «<Título II. derogado por…>» (137 artículos de
  la Ley 222/1995), «<Derogado por…>» a secas, «<Artículo suprimido…>»; `RE_FECHA` acepta el
  ordinal «1o. de enero». «…transitoriedad…» cuenta como salvedad (Ley 1530, arts. 106-126 y 128,
  exceptuados para los procedimientos en curso). Autotest ampliado (arts. 18-25 del caso de prueba).
  Resultado: MUERTO pasa de 4.036 a 4.879 artículos.
- [x] Aristas `manual:` a la norma entera donde la fuente trae la nota pero algunos artículos no
  la marca: Ley 104/1993 (Ley 418 art. 131), Ley 1152/2007 (C-175/09), Ley 43/1993 (Ley 2332 art.
  54) y los arts. sin marca de los decretos 266/2000 (C-1316/2000) y 1122/1999 (C-923/99).
- Residuo sin clasificar a propósito (ambiguo): «<Seguro colectivo derogado como consecuencia…>»
  (CST, 16 arts.), «<Comisión/Instituto/Corporación suprimida…>» (7), y notas sobre la norma
  citada dentro del artículo («<Artículo 75 de la Ley 23 de 1991 derogado…>», 6).

## Bloqueados

- [x] (resuelto en P10) 2026-09-23 `co:ley:21:1991` (Convenio 169 OIT) — ver P6. Fallaron `secretariasenado.gov.co/senado/basedoc/ley_0021_1991.html` (404) y el parser del Gestor (`norma.php?i=37032`).

## Auditoría de coherencia y P16 (2026-09-24)

- [x] 30 artículos cuyo texto entero es «DECLARADO INEXEQUIBLE» (estatutarias 270/1996,
  134/1994, 130/1994, 137/1994) y ~100 marcas del Gestor sin `<>` («(Derogado Decreto 648 de
  2017, art 10)», «Suprimido por…») salían vivos: `build.RE_INICIO`.
- [x] Leyes orgánicas 1454/2011 y 152/1994 cargadas dos veces (ley / ley-organica): se quitó la
  copia; ALIAS resuelve ley ↔ ley-organica; build avisa «norma duplicada».
- [x] Fechas «solo el año» (31-dic): toman la fecha del origen cargado; si caen en el futuro
  quedan como AAAA (surtidas). C-062/2026 no se aplicaba hasta diciembre.
- [x] Ley 200/1995: estado_general derogada sin arista → `manual:` Ley 734/2002 art. 224
  deroga_tacitamente (nota de vigencia de senado); build avisa si vuelve a pasar.
- [x] Senado: `bookmarkaj` vacío con nombre de índice cortaba el artículo (Ley 1429 art. 2,
  PND 2294 ×56); revisión previa en «Notas de Vigencia» (Ley 1095/2006, C-187/06); «INCONSTITUCIONAL
  por omisión legislativa» = condicionamiento (C-792/14). Re-ingesta completa de senado.
- [x] export: advertencia «parte marcada» para artículos vivos con «<Inciso INEXEQUIBLE>».
- [x] P16 (`./cargar_p16.sh`): 19 leyes de senado + Leyes 29/1982 y 62/1988 (Gestor) con 10-19
  aristas; sentencias del grafo (`ingesta_relatoria.py --del-grafo`).
- [x] Sin fuente: `co:ley:28:1932`, `co:ley:45:1936`, `co:ley:39:1985` (ni senado ni Gestor). **→ P20: normogramas Colpensiones y Cancillería**
- [x] P17 (`./cargar_p17.sh`): 90 decretos origen con 10-19 aristas, del Gestor (IDs verificados
  contra el encabezado de cada página). Decretos 126/2010 y 2637/2004 (INEXEQUIBLES) y 4222/2006
  (derogado por el Decreto 113/2022) muertos enteros según el encabezado: aristas `manual:`.
- [x] ingesta_gestor: el articulado empieza tras «DECRETA» (considerandos que transcriben
  artículos: Decretos 1457/2020, 2371/2019, 829/2020, 1736/2012); tras «quedarán así:» los saltos
  grandes son transcritos (Decreto 198/2013, 126/2010); avisa si el encabezado mata la norma.
- [x] Sin ID en el Gestor: Decretos 939/2017, 617/1954, 982/1996, 1655/1991. **→ P20 (617/1954, 1655/1991) y P21 (939/2017, 982/1996)**
- [x] Notas de muerte de la norma entera en el encabezado de senado que los artículos no
  repetían: A.L. 2/2003 (C-816/04), Ley 241/1995 (Ley 418/1997 art. 131), Ley 734/2002 arts.
  41-43 (completados del Gestor; Ley 1952/2019 art. 265). ingesta_senado ahora avisa.
- [x] Ley 153/1887 arts. 206, 244, 271, 291: el texto quedó en el epígrafe (encabezados de **→ P21: eran 10 artículos (65, 81, 83, 88, 94, 206, 231, 244, 271, 291)**
  sección «3. HURTOS Y ESTAFAS.» al final del artículo anterior). No se pierde texto.

## Auditoría 2 y P18 (2026-09-25)

- [x] Aristas anacrónicas (1.004): nadie reforma lo que aún no existe. En los DUR, «(Decreto 2877
  de 2001, art. 6; adicionado por el Decreto 1567 de 2002)» es la procedencia del texto compilado,
  no una reforma del DUR; senado anota bajo la ley nueva fallos sobre la predecesora («cuyo
  contenido guarda similitud…»): `build.py` los descarta (norma) o los vuelve `concordancia`
  (Corte Constitucional, salvo estatutarias: revisión previa). 22 artículos de DUR revividos.
- [x] Gestor: «Texto subrayado, derogado por…», «Numeral 3 derogado por…» y los numerales
  titulados del EOSF («6. Delegaciones… Derogado por el art. 123, Ley 510 de 1999») son
  derogación parcial (`modifica` + nota), no del artículo: 28 artículos vivos que salían MUERTO.
  El entregable los advierte («parte marcada»).
- [x] Marcas: «(ELIMINADO)», «<Artículo eliminado por…>», «INEXEQUBLE» (errata de la fuente)
  matan; «INEXEQUIBLE con excepción de…» no (ET 657-1, Ley 488/1998 art. 77).
- [x] Advertencia SIN_TEXTO_PROPIO: 133 artículos vivos cuyo texto es solo la nota de la fuente
  («<Artículo sustituido por los artículos 1o. a 23 del Decreto 919 de 1989>», «<Se aplica la
  Decisión 486…>»).
- [x] estado_general: los extractores escriben «vigente» siempre; 25 normas muertas enteras
  corregidas y build avisa si vuelve a pasar. ingesta_gestor acepta `--estado`.
- [x] Gestor: encabezados «ARTÍCULO . 1.» / «ARTÍCULO .2.5.6.4.3.» se perdían sin que verificar
  lo notara (Decreto 762/2018 art. 1, DUR 1073 art. 2.5.6.4.3, DUR 1078 art. 2.2.5.4.7).
  `reingestar_gestor.sh` (nuevo, desde el frontmatter) y re-ingesta completa del Gestor.
- [x] Senado: ancla vacía `name="1-A"` bajo el título cortaba artículos (Ley 1418/2010 arts. 9, 10,
  41); `name="1A"`/`"1B"` con «ARTÍCULO 1o.» (anexo y ley aprobatoria del Protocolo I, Ley
  11/1992) se descartaban como repetidos; subtítulos `503T` de la Ley 9/1979 salían como artículos.
- [x] Senado: cajas de vigencia leídas sin ninguna arista quedan «pendiente» (DIAN, Decreto
  1643/1991: la nota de cada artículo es la fusión DIN→DIAN, no una afectación).
- [x] P18 (`./cargar_p18.sh`): 69 leyes origen con 10-19 aristas. Muertes anotadas solo en el
  encabezado → `manual:` Ley 1288/2009 (C-913/10), Ley 443/1998 art. 38 (Ley 909/2004), Ley
  522/1999 (Ley 1407/2010, con ultractividad), Ley 11/1992 (C-088/93; el Protocolo I sigue).
- [x] Decretos reglamentarios compilados en un DUR y cargados aparte (1333/2007 → DUR 1073,
  1377/2013 → 1074, 198/2013 → 1079, 1474/1997 → 1833/2016): arista `compila` y advertencia
  COMPILADA (citar el DUR). La fuente no anota derogación por artículo, no se inventa.
- [x] Ley 270/1996 art. 209b: su cuerpo trae además el «ARTÍCULO NUEVO.» sin número que adicionó **→ P21: `art:nuevo` propio, vigente**
  el art. 25 de la Ley 1285/2009 (control de legalidad); la fuente no le da ancla ni número. Sale
  dentro de un registro MUERTO (omisión conservadora).
- [x] P19 (`./cargar_p19.sh`): Decretos 777/1992 (i=1454) y 1207/2021 (i=172113); el buscador del
  Gestor responde «No disponible», los IDs salieron de buscador web y se verificaron contra el
  encabezado. Decreto 92/2017 (i=78935), cuyo art. 11 deroga el 777/1992 desde el 1-jun-2017.
- [x] Relatoría 2025-2026: las no publicadas devuelven el cascarón SPA de 8,6 KB (C-067/26, C-196/25);
  31 fichas pendientes hasta que la Corte las publique.
- [x] Consejo de Estado: `DescargarProvidenciaPublica` sigue en 403 (reintentado 2026-09-25). **→ el texto sale de CENDOJ WebRelatoria (PDF público)**

## Vías de acceso nuevas, validadas (2026-09-25)

Probadas en vivo, sin navegador. Falta implementar los extractores.

- **Corte Constitucional, índice Elastic en JSON** (sin autenticación), sacado del JS del sitio nuevo:
  `https://www.corteconstitucional.gov.co/relatoria/buscador_new/?accion=search&tipo=json&searchOption=prov_sentencia&buscar_por=C-196/26&fini=1992-01-01&ffin=2026-12-31&maxprov=5`
  trae `rutahtml`, `prov_f_sentencia` y `prov_f_public`. `?accion=ver_modal_ultimas_providencias&cantidad=50&tipo=json`
  lista las recién publicadas. Sirve para tres cosas:
  1. Saber cuándo sale una sentencia: C-081/26 y C-183/25 ya estaban publicadas y fallaron.
  2. Invalidar caché: hay 84 páginas en `fuentes/cache` que son el cascarón SPA de 8,6 KB. Una
     sentencia aún no publicada queda cacheada vacía y nunca se reintenta.
  3. Corregir citas con el año mal, por la fecha exacta: C-099/12 → C-099/13, C-120/19 → C-120/20,
     C-122/07 → C-122/08, C-194/12 → C-194/13. Sin resolver: C-114/09, C-1058/00, C-682/12.
  El JS se baja con urllib; curl no sigue bien el 301 a minúsculas.
- **Consejo de Estado, texto completo**: `jurisprudencia.ramajudicial.gov.co/WebRelatoria` (CENDOJ,
  JSF/PrimeFaces). Flujo: búsqueda temática por AJAX (corp CE), luego la tabla paginada
  (`jurisTable_rows=100`, NR en `data-rk`), luego el PDF público
  `WebRelatoria/FileReferenceServlet?corp=ce&ext=&file=<NR>`. Probado con NR 2414347: 23 páginas,
  texto extraíble con PyMuPDF y la parte resolutiva completa. El «Reporte» (selección `@all`) da en un
  solo HTML UTF-16 la relatoría de todos los resultados (tema, problema jurídico y respuesta, sustento
  normativo, decisión). No busca por radicado: con «RESPONSABILIDAD MEDICA», 16 de las 1.404 fichas
  SAMAI coinciden. Es una fuente de ingesta nueva, no un parche de SAMAI. Cubre también CSJ y CC.
- **Normogramas de otras entidades en la plataforma de senado/DIAN** (Avance Jurídico). `ingesta_senado`
  los lee tal cual:
  - CREG `gestornormativo.creg.gov.co/gestor/entorno/docs/`: Ley 57/1887 (338 arts., 42 aristas), Decreto 1655/1991.
  - Cancillería `www.cancilleria.gov.co/sites/default/files/Normograma/docs/`: Leyes 11/1984 y 39/1985.
    Python falla por TLS (TLSV1_ALERT_PROTOCOL_VERSION); curl baja. Hace falta un fallback en `bajar`.
  - Colpensiones `normativa.colpensiones.gov.co/colpens/docs/`: Leyes 28/1932 y 45/1936, Decreto 617/1954.
  - También: JEP `jurinfo.jep.gov.co/normograma/compilacion/docs/`, SENA `normograma.sena.edu.co/compilacion/docs/`.
    El ICBF no responde desde aquí.
- **SUIN-Juriscol vía archive.org**: el sitio actual es un CMS de MinJusticia sin los documentos (`utu.minjusticia.gov.co/pages/search`
  da 0 resultados). La CDX de Wayback tiene al menos 50.000 `viewDocument.asp` archivados, con texto y
  estado de vigencia («Derogado… Artículo 52 DECRETO 230 de 2008» para el Decreto 982/1996). La
  vigencia es la de la fecha de la captura: `verificado` debe ser la fecha del snapshot.
- **SISJUR, Alcaldía de Bogotá** (`alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=`): Decreto 939/2017,
  que no está en ninguna otra fuente accesible. Tiene otro formato y necesita parser propio.
- **Buscador del Gestor**: responde «No disponible». Los IDs salen de buscador web y se verifican contra el encabezado.
- [x] Decisión de Juan: admitir en esquema.md §8 normogramas de otras entidades, CENDOJ/Rama Judicial, **→ admitidas el 2026-09-25 (esquema.md §8, fuentes 8-11)**
  capturas de SUIN en archive.org y SISJUR.


## P20-P22, CENDOJ y Corte Constitucional (2026-09-25)

- [x] P20 (`./cargar_p20.sh`): 7 normas bloqueadas, desde normogramas de CREG, Cancillería y
  Colpensiones (mismo formato que senado). `bajar` cae a curl con el TLS viejo de la Cancillería.
  «<NOTA: no incluye análisis de vigencia>» deja `afectaciones: pendiente`.
- [x] Senado: un TÍTULO/CAPÍTULO tras «…quedará así:» es transcripción de otra norma, no corta el
  artículo (Ley 39/1985 arts. 4 y 9, Ley 2421/2024: 60 `ubicacion` falsas).
- [x] P21 (`./cargar_p21.sh`, `ingesta_suin.py`): SUIN vía archive.org, `verificado` = fecha de la
  captura. Decreto 982/1996 (derogado), Decreto 939/2017, A.L. 1/1999. SISJUR no hizo falta.
- [x] Corte Constitucional: índice Elastic en `ingesta_relatoria` (rutahtml). No se cachean el
  cascarón SPA (84 borrados) ni el desafío anti-bot de 2,4 KB (7). `correcciones.csv`: citas con año
  errado confirmadas por la fecha exacta; `build.py` las aplica. 20 fichas nuevas.
- [x] Citas CC sin ficha (2026-09-30, agente cc): 5 entradas nuevas en `correcciones.csv`: C-509/07→C-509/08 (año) y,
  por NÚMERO, C-1058/00→C-1508/00, C-114/09→C-144/09, C-682/12→C-862/12, C-136/25→C-316/25, confirmadas con fecha
  exacta, ponente y resolutiva (las de número exceden «solo el año»: borrar la fila si no se aceptan). Más 3 de leyes
  con el año errado en la propia fuente: 633/2001→633/2000, 25/1892→25/1992, 1474/2021→1474/2011. Sin corregir:
  C-032/04, C-036/97, C-311/92 (solo aristas `interpreta` de la Constitución, sin fecha), C-237/04 (el índice solo
  tiene C-237A/04), C-167/25 (¿C-167/26?) y 6 citas cuya fecha en el grafo no coincide con la del índice (C-198/98,
  C-260/96, C-1336/00, C-078/18, C-1023/12, C-167/14): revisar antes de cargar. 24 sentencias de 2025-2026 siguen sin
  publicar (C-006, 036, 048, 062, 067, 099, 166, 192, 195, 197, 212, 217, 218, 220, 252, 255, 272, 293, 294 de 2026;
  C-167, 206, 224, 504 de 2025).
- [x] Fichas CC de las citas del grafo (`ingesta_relatoria.py --del-grafo --todas`): +332 el 2026-09-30 y +132 el
  2026-10-05, en tandas con `--pausa 3` (el servidor corta tras ~150-250 peticiones seguidas). Las 71 que faltan fallan
  igual en tres pasadas: 23 de 2025-2026 aún sin publicar y 48 que no están en el índice de la Corte (p. ej. C-091/03,
  posible errata de C-1091/03). `--del-grafo` ya salta las fichas existentes. El clasificador de `decision:` tolera
  palabras partidas («I NEXEQUIBLE», «E XEQUIBLES»): 5 fichas corregidas (C-036/23 y C-137/19 → inexequible).
- [x] `./cargar_cendoj.sh` (`ingesta_webrelatoria.py`): los 34 términos recorridos (cerrado 2026-10-06). Consejo de Estado
  con parte resolutiva y aristas `cita`/`interpreta`; Corte Suprema con texto íntegro y aristas `cita` desde la FUENTE
  FORMAL (conecta la casación con la normativa). Hoy: 4.995 fichas CE y 5.900 CSJ; relaciones 66.760.
  Para ampliar: más términos o subir `--limite` (el buscador exige término). Arreglos: providencias guardadas como HTML
  (`ext=html`), `resuelve()` con más fórmulas, menos reintentos ante un documento colgado; una cita a un artículo que la
  norma cargada no tiene baja a la norma (también si la norma está cargada como decreto-ley). 45 NR no entregan
  documento con ninguna extensión (2077554, 2081486, 2085012, 2090472, 2097241, 2097294, 2097488, 2098125-2098128,
  2098203, 2113832, 2113891, 2123470, 2123636, 2131047, 2131332, 2131337, 2131435, 2131831, 2139668, 2148276-2148292,
  2162776, 2163482, 2164305, 2184163, 2417826, 2417898): sin ficha. La nota de las aristas `interpreta` dice «decisión de
  la relatoría (procesal: no dice si hubo nulidad)». AC-2195/2019: la relatoría le da fecha 2018-06-07 (imposible para
  el radicado 2019-00212); sus aristas quedan con el año 2019.
- [x] Nulidades del Consejo de Estado (aprobado por Juan, implementado 2026-10-03; detalle en
  `propuestas/nulidades-ce/informe.md`): tipos `declara_nulo` (mata) y `declara_nulo_parcial` (aviso «NULIDAD
  PARCIAL»); `build.py` reconoce la nota de la fuente «Artículo declarado NULO por el Consejo de Estado» al final del
  texto (Gestor). 3 artículos mueren (Decreto 1082/2015 arts. 2.2.1.2.5.1 y 2.2.1.2.5.3; Decreto 1474/1997 art. 8) y 6 de
  los DUR 1067, 1073 y 1075 quedan condicionados. `nulidades_ce.py` lista (o con `--aplicar` añade) las nulidades de las
  fichas CE: correrlo tras cada tanda de CENDOJ.
- [ ] Nulidades — pendientes: Decreto-ley 1421/1993 arts. 87, 88, 90, 92 y 94 («Artículo NULO - Efectos jurídicos
  prorrogados»: anulados en 2018 con efectos diferidos un año o hasta que regule el Concejo; vigentes con aviso hasta
  verificar si el plazo venció). `nulidades_ce.py` no detecta la ficha rad. 11001-03-26-000-2008-00101-00 (11 nulidades de
  los Decretos 2474/2008 y 2025/2009, hoy no cargados).
- [x] P22 (`cargar_origenes.py`): 2.074 leyes, estatutarias y AL origen desde senado. 79 muertes de la
  norma entera anotadas solo en el encabezado → aristas `manual:` (derogada por artículo/ley concreta,
  o inexequible con su sentencia); 793/2002, 785/2002 y 1530/2012 derogadas salvo los exceptuados.
  `fecha_norma` lee más variantes del Diario Oficial y, sin él, la fecha de expedición del encabezado.
  Leyes aprobatorias de tratados: se cargan los artículos de la ley (tras DECRETA), no los del tratado.
- [x] `origenes_revisar.txt` (96 → 8): ver P23-P25. Quedan las que exigen criterio o fuente (Leyes 13/1992, 794/2003,
  872/2003, 1330/2009, 2168/2021, 1896/2018, 1865/2017 y 105/1913).
- [x] Error operativo 2026-09-25 (`git checkout relaciones.csv` con cargas sin commit) → regla en CLAUDE.md.
- [~] Decretos origen: P23 cargó 50; P26 (`cargar_decretos.py`, 2026-10-06) cargó 177 más (175 del grupo de 3-7 aristas
  y los Decretos 898/2017 y 1851/2021), todos con `faltan 0` y el `i=` verificado contra el `<title>` del Gestor;
  `origenes_sin_cargar` 2.576 → 1.745 aristas. Lo que no se pudo va a `decretos_revisar.txt`: 60 sin `i=` en la caché
  (entre ellos el 130/2010, que sí está en senado), 2 páginas truncadas (2345/2015, 1934/2015), 1 epígrafe ilegible
  (182/2026) y el Código de Procedimiento Civil (Decreto 1400/1970), retirado: su derogación por el art. 626 de la Ley
  1564/2012 es gradual — decisión de Juan (¿arista manual con qué fecha?). Siguiente: el grupo de 1-2 aristas (793
  decretos, ~510 cargables, ~1 h): `nohup python3 cargar_decretos.py --minimo-aristas 1 --maximo-aristas 2 --limite 1000
  > log 2>&1 &`. ingesta_gestor ahora lee «ARTÌCULO» y restaura «ARTÍCULO» en los artículos transcritos de otra norma:
  re-ingestar si se quiere los DUR 1068, 1069, 1073, 1074, 1075, 1077, 1080, 1081, 1082 y 1085 y los Decretos 1247/2022,
  1272/2016, 1625/2016 y 780/2016 (solo cambia esa palabra).
- [x] Grafo interactivo (`grafo/`, Vercel `grafo-one.vercel.app`): regenerado con `grafo/generar.py` el 2026-10-06
  (14.458 nodos, 28.378 enlaces; era la foto del 23-sep con 116 normas y solo la Corte Constitucional). Se publica desde
  `grafo/` con `npx vercel deploy --prod` (la sesión del CLI ya existe). Regenerar y publicar tras cada carga grande.

## P23-P25 y trabajo en paralelo (2026-09-30)

Siete agentes en paralelo más CENDOJ y la Corte Constitucional en segundo plano. `build.py` sin avisos; `contexto.jsonl`
122.932 registros (era 85.443); `origenes_sin_cargar` 5.296 → 2.446 aristas (buena parte: `art:inicio`, ver abajo).

- [x] P23 (`cargar_p23.sh`): 50 decretos y decretos-ley origen del Gestor (262/2000, 16/2014, 20/2014, 25/2014, DL 885/2017
  y 45 reformadores de DUR); cada `i=` verificado contra el `<title>` de la página. Muertos enteros: Decreto 141/2011
  (inexequible, C-276/11) y 934/2021 (derogado por el 821/2022). `fecha_norma` acepta «DEL 2015».
- [x] P24 (`cargar_p24.sh`, `ingesta_suin.py`): 33 de las 37 leyes sin página en senado, desde normogramas de
  Cancillería, Colpensiones, CREG, JEP y SENA, Gestor, SISJUR y SUIN vía archive.org. No cargadas: 633/2001, 25/1892 y
  1474/2021 (errores de año de la fuente, ahora en `correcciones.csv`) y 105/1913 (sin fuente admitida). Recaptura de los 3
  documentos de P21: Wayback no tiene capturas más recientes; siguen con más de 12 meses (ahora el export lo advierte).
- [x] P25 (`cargar_p25.sh`): 23 leyes muertas enteras con arista `declara_inexequible` a nivel de norma (nota
  `manual: total — …`): las Notas de senado dicen solo «Ley INEXEQUIBLE»; la sentencia se halló por búsqueda web y se
  comprobó contra el RESUELVE de su ficha (nombra la ley por número y año). Más la Ley 2281/2023 (C-161/24: efectos
  diferidos; fecha 2026-06-20 = fin de la legislatura 2025-2026, CALCULADA). Para vetarlas: borrar las filas con
  «manual: total — el RESUELVE de la sentencia» o «manual: total, con efectos diferidos».
- [x] Las 22 de `origenes_revisar.txt` con fecha / `verificar` incompleto: `fecha_norma` lee «LEY <ESTATUTARIA> 2453» y
  «LEY ORGÁNICA 2423»; 9 normas con artículos que solo tenían el epígrafe (anclas vacías repetidas) restauradas; 4 con
  numeración por `<sic>`; 2 fechas que eran la de la Ley 424/1998 (2031/2020, 994/2005). Regresión: 2.359 normas de
  senado idénticas salvo las tocadas a propósito.
- [x] Corte Suprema (`ingesta_cendoj.py`): la lectura de PDF ya existía; añade descartar PDF escaneados, aceptar `.doc`
  (OOXML), reintentar rutas muertas y 5xx. Piloto: 100 fichas de laboral 2023 (`co:csj:sl-N:2023`). Carga completa no
  recomendada (muestreo temático con `--terminos`; ~4 h por ~1.800). Fechas con «ñ» o paréntesis (`fecha_en`) corregidas.
- [x] `build.py`: las 1.155 aristas `concordancia` con origen `…:art:inicio` (senado) apuntan a la norma.
- [x] `export.py`: advertencia `VERIFICADO_VIEJO` para normativa con `verificado` de más de 12 meses (regla 3).
- [x] `ingesta_webrelatoria.py`: «ARTÍCULOS 215 Y 216» / «185 A 190» ya no toman Y ni A como letra; una cita a un artículo
  que la norma cargada no tiene baja a arista de la norma. `ingesta_senado.guardar_relaciones` conserva también las
  aristas `CENDOJ:` (una re-ingesta las borraba). `cargar_origenes.epigrafe` lee «LEY <ESTATUTARIA> N» (17 títulos rotos
  corregidos).
- [ ] Seguimientos que no bloquean:
  1. [x] Auditoría (2026-10-05): las cajas de vigencia de senado se partían mal (cada trozo juntaba varios fallos y
     tomaba el INEXEQUIBLE de cualquier parte). `ingesta_senado.py` corregido; 356 normas re-ingestadas (`faltan 0`);
     aristas dudosas 92 → 13 (8 correctas, 4 errores de la fuente, 1 fuera de alcance). Efecto: 244 artículos pierden
     un aviso espurio y 177 ganan un condicionamiento que no se leía; ninguno revive. Los errores de la fuente van en
     `aristas_descartadas.csv` (9) y 3 aristas parciales `manual:` (Ley 272/1996 arts. 2 y 4, C-152/97; Código Civil
     art. 1119, C-190/17). Residuo: un fallo sobre OTRA norma que es exequible o condicionado todavía genera arista.
  2. Aristas `modifica`/`adiciona` que salen de leyes ahora inexequibles (508/1999 → 142/1994 y 286/1996; 719/2001 →
     44/1993; 738/2002 → Código Penal art. 447A) siguen marcando «reformado».
  3. 21 títulos rotos de P22 (el parser no halla el epígrafe): 1076/2006, 1143/2007, 1673/2013, 168/1994, 17/1992,
     1830/2017, 188/1995, 1883/2018, 1958/2019, 225/1995, 263/1996, 287/1996, 375/1997, 376/1997, 377/1997, 413/1997,
     528/1999, 725/2001, 844/2003, 944/2005 y 945/2005.
  4. Ley 660/2001: art. III del tratado y secciones C-E del II sin cargar (anclas con nombre no numérico); `verificar.py`
     no lo detecta y no tiene rama para SISJUR (Leyes 24/1986 y 73/1988).
  5. Pie del sitio en el último artículo de normogramas sin «Fin documento» (Ley 57/1887 art. 338): el `div ir-arriba`
     aparece en cada artículo, no sirve para cortar en el parser; se recorta caso a caso (`recortar` en cargar_p24.sh).
  6. `ingesta_gestor.RE_AFECTA` no lee «el Artículo 8 de la Ley 62 de 1939» ni «Ley 6a.de 1928»; 9 notas «Adicionado
     numerales…» de 262/2000 y 16/2014 quedan sin arista.
  7. Ramas poco naturales en leyes cuyas ramas salen de lo que afectan (Ley 84/1989 «civil, familia»; 262/2000, 16/2014…
     «constitucional»). Leyes 130/1913 y 84/1915 (CREG) con vigencia pendiente: SUIN trae análisis de vigencia.
  8. Corte Suprema: la parte resolutiva incluye aclaraciones y salvamentos de voto en 331 de 2.412 fichas (14 %); cortar en
     el encabezado del voto y regenerar — decisión de Juan. Ley 2453/2025: sus arts. 12, 13 y 16 salieron
     `declara_inexequible_parcial` por la regla estándar, sin revisar a mano.
