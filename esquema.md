# Esquema — Base de datos normativa de Colombia

Este archivo es **el contrato**. Todo lo que entre a la base cumple esto o no entra.
Si algo no encaja, se cambia el esquema aquí primero, no se improvisa en el archivo.

---

## 1. Principios (no negociables)

1. **La unidad atómica es el artículo**, no la norma. Toda cita, todo enlace y toda
   búsqueda apuntan a un artículo.
2. **La vigencia se calcula, nunca se guarda.** No existe un campo `vigencia:`. El
   estado de un artículo se deriva de `relaciones.csv`. Un campo guardado se
   desactualiza y miente; una derivación no.
3. **La rama del derecho es una etiqueta, no una carpeta.** Una norma puede tener
   varias ramas. Jamás se duplica una norma para meterla en dos ramas.
4. **Los `.md` son la fuente de verdad. El `index.db` es desechable** y se
   reconstruye con `python3 build.py`. Nunca se edita el `.db` a mano.
5. **Todo registro declara su fuente y la fecha en que se verificó.** Sin `fuente:`
   y `verificado:` el registro es inservible: no se puede auditar ni re-chequear.
6. **Nada se transcribe de memoria.** El texto de un artículo se copia de la fuente
   oficial. Si no se pudo obtener, se deja el artículo fuera y se anota en `cola.md`.
   Un artículo inventado o parafraseado es peor que un artículo ausente.

---

## 2. IDs canónicos

Formato: minúsculas, sin tildes, separado por `:`. Nunca cambian una vez publicados.

### Normativa
```
co:<tipo>:<numero>:<anio>[:art:<articulo>]
```
| Tipo | Ejemplo |
|---|---|
| Constitución | `co:constitucion:1991:art:42` |
| Ley | `co:ley:1564:2012:art:82` |
| Ley estatutaria | `co:ley-estatutaria:1581:2012:art:5` |
| Decreto ley | `co:decreto-ley:1421:1993:art:12` |
| Decreto | `co:decreto:1074:2015:art:2` |
| Resolución | `co:resolucion:0312:2019:art:3` |
| Acto legislativo | `co:acto-legislativo:1:2005` |
| Circular | `co:circular:100-000016:2023` |

Artículos con sufijo: `art:82a` (art. 82A), `art:82-1` (art. 82-1). La letra va
pegada y en minúscula aunque la fuente escriba «82-A» o «82 A».
Parágrafos e incisos **no** son nodos propios: van dentro del texto del artículo.

**Derecho comunitario** (no lo expide el Congreso colombiano, pero aplica directo en
Colombia): prefijo propio, nunca `co:`.
```
can:decision:<numero>:<anio>[:art:<articulo>]
```
Ejemplo: `can:decision:486:2000:art:134` (Comunidad Andina, propiedad industrial).

### Jurisprudencia
```
co:<corporacion>:<sala-o-tipo>-<numero>:<anio>
```
| Corporación | Ejemplo |
|---|---|
| Corte Constitucional | `co:cc:c-284:2015`, `co:cc:t-760:2008`, `co:cc:su-214:2016` |
| Corte Suprema | `co:csj:sc-2107:2018`, `co:csj:sp-1234:2020`, `co:csj:sl-455:2021` |
| Consejo de Estado | `co:ce:11001-03-25-000-2015-00025-00:2019` |
| Consejo Superior Judicatura | `co:csj-jd:2019-00123:2021` |

---

## 3. Archivos de normativa — `normativa/`

Un archivo por norma: `co-ley-1564-2012.md` (el ID con `-` en vez de `:`).

````markdown
---
id: co:ley:1564:2012
tipo: ley
titulo: Código General del Proceso
titulo_corto: CGP
fecha: 2012-07-12
ramas: [procesal, civil, comercial, familia]
estado_general: vigente
fuente: https://www.suin-juriscol.gov.co/viewDocument.asp?ruta=Leyes/1683063
verificado: 2026-09-10
---

## art:82 — Requisitos de la demanda

Salvo disposición en contrario, la demanda con que se promueva todo proceso
deberá reunir los siguientes requisitos:

1. La designación del juez a quien se dirija.
...
````

**Campos del frontmatter**

| Campo | Obligatorio | Notas |
|---|---|---|
| `id` | sí | ID canónico de la norma, sin `:art:` |
| `tipo` | sí | `constitucion`, `ley`, `ley-estatutaria`, `decreto`, `decreto-ley`, `resolucion`, `acto-legislativo`, `circular` |
| `titulo` | sí | Título oficial completo |
| `titulo_corto` | no | Como se cita en la práctica: `CGP`, `CPACA`, `CST` |
| `fecha` | sí | `AAAA-MM-DD` de expedición |
| `ramas` | sí | Lista, ver §5 |
| `estado_general` | sí | `vigente`, `derogada`, `subrogada`, `compilada` — solo de la norma como un todo; la vigencia por artículo se calcula |
| `fuente` | sí | URL exacta de donde se obtuvo el texto |
| `verificado` | sí | `AAAA-MM-DD` en que se cotejó contra la fuente |
| `afectaciones` | sí | `pendiente` o `cargadas`. Mientras esté `pendiente`, **todos** sus artículos se exportan como `VIGENCIA_NO_VERIFICADA` |

`ubicacion: TÍTULO … > CAPÍTULO …` puede ir como primera línea bajo el encabezado de
un artículo. Sitúa al modelo que lo reciba suelto: «art. 86» no dice nada, «Título II,
Cap. 4 — De la protección de los derechos» sí.

**Encabezado de artículo**: `## art:<num> — <epígrafe>`. El epígrafe es el que trae
la norma; si no tiene, se deja `## art:<num> —` y nada más. No se inventan epígrafes.

**Marcas dentro del texto** (las pone la ingesta, nunca a mano):

- `[TACHADO: …]` — texto que la fuente publica tachado (`<S>` en senado): ya no rige
  (inexequible, nulo o derogado; el marcador que lo precede, p. ej.
  `<Aparte tachado INEXEQUIBLE>`, dice cuál). Se conserva para que la cita sea
  completa, pero no es texto vigente. `export.py` advierte en todo registro no muerto
  que lo contenga.
- Los marcadores editoriales de vigencia (`<Artículo derogado por …>`,
  `<Artículo modificado por …>`, `<Aparte tachado INEXEQUIBLE>`) se conservan. Los que
  solo remiten a cajas que no viajan (`<Ver Notas del Editor>`, `<Ver Notas de
  Vigencia>`) y el pie de navegación de la fuente se quitan.

---

## 4. Archivos de jurisprudencia — `jurisprudencia/`

Un archivo por providencia: `co-cc-c-284-2015.md`.

**No se guarda el texto completo de la sentencia.** Se guarda una ficha. El texto
completo vive en `fuente:`. Una sentencia de la Corte son 200 páginas y el 95% no
aporta a una consulta; lo que vale es la subregla.

````markdown
---
id: co:cc:c-284:2015
tipo: sentencia
corporacion: corte-constitucional
sala: plena
ponente: María Victoria Calle Correa
fecha: 2015-05-13
expediente: D-10455
ramas: [constitucional, civil, familia]
decision: inexequible-parcial
hito: true
fuente: https://www.corteconstitucional.gov.co/relatoria/2015/C-284-15.htm
verificado: 2026-09-10
---

## problema-juridico

¿Vulnera el legislador la reserva de ley estatutaria al regular ... ?

## subregla

<La regla que la providencia deja sentada, en 2-5 frases, redactada como norma
aplicable a casos futuros. Esto es lo único que se va a leer en el 90% de las
consultas — se escribe con cuidado.>

## salvamentos

<Solo si los hay y cambian algo. Si no, se omite la sección.>
````

**Campos propios**

| Campo | Obligatorio | Notas |
|---|---|---|
| `corporacion` | sí | `corte-constitucional`, `corte-suprema`, `consejo-estado`, `consejo-superior-judicatura` |
| `sala` | sí | `plena`, `civil`, `penal`, `laboral`, `revision`, `seccion-primera`… |
| `ponente` | sí | Nombre completo |
| `expediente` | no | Radicado |
| `decision` | sí | `exequible`, `inexequible`, `inexequible-parcial`, `exequible-condicionado`, `estese-a-lo-resuelto`, `inhibitoria`, `casa`, `no-casa`, `nulidad`, `niega-nulidad`, `tutela-concede`, `tutela-niega` |
| `hito` | no | `true` si sienta o cambia línea jurisprudencial |

`export.py` incluye `corporacion`, `ponente` y `decision` en cada registro de
jurisprudencia. Una ficha sin texto de la providencia (p. ej. Consejo de Estado cuando
SAMAI da 403: la sección `## ficha` dice «No se pudo bajar el texto íntegro») sale con
la advertencia «SOLO METADATOS, SIN TEXTO VERIFICADO».

Las normas que la providencia interpreta o declara inexequibles **no van en el `.md`**:
van en `relaciones.csv`. Una sola fuente de verdad para las aristas.

---

## 5. Ramas del derecho (etiquetas)

Vocabulario cerrado. Agregar una rama es editar esta lista, no improvisar un tag.

```
constitucional      civil            familia          penal
procesal            comercial        laboral          seguridad-social
administrativo      contencioso-administrativo        tributario
migratorio          internacional-publico             internacional-privado
arbitraje           insolvencia      ambiental        agrario
disciplinario       notarial-registral                datos-personales
consumo             competencia      propiedad-intelectual
transporte          aduanero         policivo         electoral
minero-energetico   salud            urbanistico      contratacion-estatal
financiero          etnico
```

Se etiqueta por **lo que la norma regula**, no por dónde se estudia en la facultad.
El CGP es `procesal` y también `civil`, `comercial` y `familia`, porque se aplica ahí.

---

## 6. `relaciones.csv` — el grafo

Un archivo, append-only, una arista por línea. **Esto es todo el grafo.** No hay
nodos de relación en los `.md`; si una arista aparece en dos lados, una de las dos
se va a desactualizar.

```csv
origen,tipo,destino,fecha,nota,fuente
```

| Columna | Notas |
|---|---|
| `origen` | ID que produce el efecto (el artículo reformador, la sentencia) |
| `tipo` | Ver tabla abajo |
| `destino` | ID que recibe el efecto (el artículo afectado) |
| `fecha` | `AAAA-MM-DD` en que **surte efecto** (no la de expedición si hay vacancia) |
| `nota` | Texto libre corto. Obligatorio en `declara_exequible_condicionado` |
| `fuente` | De dónde se sacó la afirmación |

**Tipos de relación**

| Tipo | Efecto sobre la vigencia del destino |
|---|---|
| `deroga` | Lo mata |
| `deroga_tacitamente` | Lo mata (marcar cuando sea interpretación, no texto expreso) |
| `subroga` | Reemplaza su texto; el artículo sigue vivo con el texto nuevo (cuenta como reforma) |
| `declara_inexequible` | Lo mata desde la fecha |
| `declara_inexequible_parcial` | Sigue vivo, mutilado — `nota` dice qué cayó |
| `modifica` | Sigue vivo, con otro texto |
| `adiciona` | Sigue vivo, con más texto |
| `suspende` | Muerto temporalmente — `nota` dice hasta cuándo |
| `declara_exequible` | No cambia nada, pero blinda |
| `declara_exequible_condicionado` | Sigue vivo **solo si se lee como dice `nota`** |
| `reglamenta` | No afecta vigencia |
| `compila` | No afecta vigencia |
| `desarrolla` | No afecta vigencia |
| `interpreta` | No afecta vigencia (jurisprudencia sobre el artículo) |
| `cita` | No afecta vigencia |
| `concordancia` | No afecta vigencia (remisión normativa) |
| `renumera` | No afecta vigencia — el `origen` es el número viejo, el `destino` el número vigente |

Los primeros ocho son **relaciones de afectación**: `build.py` los usa para calcular
vigencia. Los demás son navegación.

---

## 7. Vigencia calculada

`build.py` genera la vista `vigencia`. La regla, en orden:

1. ¿Hay `deroga` / `deroga_tacitamente` con `fecha <= hoy`, `declara_inexequible`
   total (nota «total» o marcador `<Artículo INEXEQUIBLE>` en el texto), o marcador
   de la fuente (ver abajo)? → **muerto** (con el ID de lo que lo mató). Un
   `declara_inexequible` sin evidencia de ser total → **vigente con condición**
   («inexequible en parte, verificar»), **salvo** que el artículo tenga un `modifica`
   o `subroga` con fecha posterior a la de la sentencia: el texto vigente es
   posterior y el aviso no le aplica (la arista sigue en `afectado_por`).
2. ¿Hay `suspende` vigente? → **suspendido**.
3. ¿Hay `declara_exequible_condicionado` o `declara_inexequible_parcial`? →
   **vigente con condición** (se devuelve la `nota`, siempre).
4. ¿Hay `modifica` / `adiciona` / `subroga`? → **vigente reformado** (con la cadena).
5. Ninguna → **vigente**.

**Aristas a la norma entera.** Si `destino` es el ID de la norma (sin `:art:`), la
arista afecta a todos sus artículos con la misma regla y la misma fecha de efecto:
`co:ley:2452:2025:art:331,deroga,co:decreto:2158:1948,2026-04-02,…` mata todos los
artículos del CPTSS desde esa fecha (antes, no). Un `declara_inexequible` a la norma
entera solo mata si la `nota` dice «total»; si no, deja el aviso «en parte» en todos.

**Marcadores de la fuente** (sin arista, se leen del `.md`): al inicio del texto
`<Artículo derogado…>`, `<Artículo INEXEQUIBLE>` o `<Ley … derogada>` / `<Ley …
declarada INEXEQUIBLE>` (el artículo lo creó una ley que cayó entera); o en el
epígrafe `Artículo derogado…` / `Artículo INEXEQUIBLE…` (Senado) o `(Derogado por…`
(Gestor). No cuentan si son parciales («en lo…», «salvo», «parcial»…) ni si traen una
fecha futura («derogado a partir del 2 de abril de 2099»).

Si un artículo no está en la base, la respuesta correcta es *«no está cargado»*,
nunca *«está vigente»*. La ausencia no es prueba de vigencia.

Lo mismo aplica a la norma completa: mientras su frontmatter diga
`afectaciones: pendiente`, sus artículos salen como **`VIGENCIA_NO_VERIFICADA`**, no
como vigentes. Un `relaciones.csv` vacío significa «no se ha mirado», no «no hay
reformas» — y afirmar vigencia sin haber mirado es el error más caro que puede
cometer esta base, porque se propaga a toda IA que consuma el corpus.

---

## 8. Fuentes admitidas

En orden de preferencia. Se prefiere siempre la de arriba disponible.

| # | Fuente | Para qué |
|---|---|---|
| 1 | **SUIN-Juriscol** (suin-juriscol.gov.co) | Normativa + afectaciones ya trazadas. La mejor para `relaciones.csv` |
| 2 | **Gestor Normativo** — Función Pública (funcionpublica.gov.co/eva/gestornormativo) | Normativa administrativa, decretos únicos |
| 3 | **Secretaría del Senado** (secretariasenado.gov.co) | Códigos con notas de vigencia al pie |
| 4 | **Relatoría Corte Constitucional** (corteconstitucional.gov.co/relatoria) | Sentencias C, T, SU |
| 5 | **Corte Suprema** (cortesuprema.gov.co) | Casación civil, penal, laboral |
| 6 | **Consejo de Estado** (consejodeestado.gov.co) | Nulidad, contencioso |
| 7 | **Diario Oficial / Imprenta Nacional** | Texto original cuando hay duda |

Fuentes **no** admitidas como origen de texto: blogs, resúmenes de firmas, wikis,
y el conocimiento previo del modelo. Sirven para *encontrar* qué buscar, nunca para
llenar un campo.
