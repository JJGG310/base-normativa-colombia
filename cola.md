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
- [x] jurisprudencia de la Corte Constitucional — **617 fichas**: todas las sentencias que afectan vigencia en los 8 códigos. 99% con descriptores oficiales, 100% con parte resolutiva, 99% con la decisión clasificada. Cubren el estado de 867 artículos.
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
- [!] `co:decreto:1067:2015` — DUR Relaciones Exteriores: **404 en senado**. Los Decretos Únicos Reglamentarios viven en el Gestor Normativo de Función Pública; necesita otro parser.
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
- [!] `co:decreto:1165:2019` — Regulación Aduanera: misma situación que el 1067/2015, no está en senado.

### P2: cargada (13 de 15)

`./cargar_p2.sh`. Las dos que faltan son Decretos Únicos Reglamentarios, que no
están en secretariasenado. La fecha de expedición ya no se escribe a mano: sale de
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

- [ ] parser de la relatoría: descriptores, RESUELVE, expediente, ponente
- [ ] la cola de sentencias sale sola del grafo: `SELECT DISTINCT origen FROM relaciones WHERE origen LIKE 'co:cc:%'`

## Pendientes de la fuente senado (no bloquean, mejoran)

- [ ] `concordancias` (713 cajas en la Constitución): remisiones normativa↔normativa. No afectan vigencia, sí navegación.
- [ ] tipo de relación `renumera`: el AL 2/2015 renumeró artículos (el 262 pasó a 261). Hoy se ignora; el artículo viejo y el nuevo quedan sin enlazar.
- [ ] SUIN-Juriscol sigue caído por `curl` (bloqueo de bot, no TLS). Sirve como segunda fuente para cotejar afectaciones.

## P3 — Por definir

- [ ] `subregla` redactada para las sentencias `hito`. Exige que el modelo lea la
  providencia (~260.000 caracteres cada una), así que es una decisión de presupuesto,
  no un tick más. Las fichas ya sirven sin esto.
- [ ] Consejo de Estado y Corte Suprema: otra fuente, otro parser. Hoy el corpus solo
  tiene Corte Constitucional, y eso deja fuera casación civil, laboral y penal, y todo
  el contencioso. Es el hueco más grande que queda.

Se llena cuando P1 esté cerrado y se vea qué falta de verdad al usar la base.
Candidatos: internacional privado, propiedad intelectual (Decisión 486 CAN),
minero-energético, urbanístico (Ley 388/1997), electoral, agrario (Ley 160/1994).

---

## Bloqueados

_(vacío — aquí van las `[!]` con motivo, URL que falló y fecha)_
