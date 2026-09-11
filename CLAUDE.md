# Base de datos normativa de Colombia

Corpus de normativa y jurisprudencia colombiana, en markdown, con un grafo de
afectaciones.

**Para qué existe:** para darle contexto de derecho colombiano a cualquier IA — no
es una herramienta de consulta para personas. El entregable real es
`contexto.jsonl` (`python3 export.py`): registros autocontenidos que se pueden
cargar en un RAG, pegar en un prompt o entregar a otro modelo.

Eso define la prioridad de todo el diseño: **un registro tiene que seguir siendo
correcto cuando se recupera solo**, sin su norma alrededor. Por eso la vigencia se
calcula y se incrusta en cada registro, y por eso un artículo muerto sale con una
advertencia adentro. Un chunk que viaja sin su estado hace que la IA que lo reciba
cite un artículo derogado con total confianza.

`esquema.md` es el contrato completo. Este archivo es lo mínimo para operar.

---

## Reglas duras

**1. Nunca escribas el texto de un artículo o de una sentencia de memoria.**
Ni parafraseado, ni "reconstruido", ni "aproximado". Se copia de la fuente oficial
(`esquema.md` §8) o no se escribe. Un artículo inventado que suena bien es el peor
resultado posible de este proyecto: nadie lo detecta hasta que ya se usó en un
proceso. Si no se pudo obtener la fuente, se anota en `cola.md` y se sigue.

**2. La vigencia no se opina, se consulta.** Antes de afirmar que un artículo está
vigente, se consulta la vista `vigencia`. Si el artículo no está en la base, la
respuesta es *«no está cargado»* — nunca *«está vigente»*.

**3. Si `verificado` tiene más de 12 meses, se advierte al citarlo.**

**4. Toda afirmación que se le devuelva a Juan lleva su ID.** `co:ley:1564:2012:art:82`,
no "el CGP dice". El ID es verificable; la paráfrasis no.

---

## Exportar (el entregable)

```bash
python3 build.py                    # .md + relaciones.csv -> index.db (desechable)
python3 export.py                   # index.db -> contexto.jsonl (todo)
python3 export.py familia penal     # solo esas ramas
python3 export.py --check           # autotest: un artículo muerto debe salir advertido
```

Cada línea de `contexto.jsonl` lleva `id`, `cita` lista para usar, `texto`, `estado`,
`advertencia`, `afectado_por` y `fuente`. Es lo que se le entrega a otra IA.

## Consultar (para trabajar sobre la base, no es el producto)

```bash
sqlite3 index.db "<consulta>"
```

```sql
-- ¿Está vigente? (SIEMPRE empezar por aquí)
SELECT * FROM vigencia WHERE articulo = 'co:ley:1564:2012:art:82';

-- Texto del artículo
SELECT texto FROM fragmentos WHERE id = 'co:ley:1564:2012:art:82';

-- Búsqueda por contenido (FTS5, ignora tildes)
SELECT id, titulo FROM busqueda WHERE busqueda MATCH 'caducidad AND contractual' LIMIT 20;

-- Qué le pasó a este artículo, en orden
SELECT tipo, origen, fecha, nota FROM relaciones
WHERE destino = 'co:ley:1564:2012:art:82' ORDER BY fecha;

-- Qué dijo la jurisprudencia sobre él
SELECT r.origen, f.texto FROM relaciones r
JOIN fragmentos f ON f.doc_id = r.origen AND f.clave = 'subregla'
WHERE r.destino = 'co:ley:1564:2012:art:82';

-- Todo lo muerto de una norma
SELECT articulo, mata FROM vigencia WHERE doc_id = 'co:ley:1564:2012' AND estado = 'MUERTO';

-- Por rama
SELECT id, titulo FROM documentos WHERE ramas LIKE '%familia%';

-- Cadena de reformas hacia atrás (el grafo, con CTE recursivo)
WITH RECURSIVE cadena(id, tipo, fecha, salto) AS (
  SELECT destino, tipo, fecha, 0 FROM relaciones WHERE destino = 'co:ley:1564:2012:art:82'
  UNION ALL
  SELECT r.destino, r.tipo, r.fecha, salto+1 FROM relaciones r JOIN cadena c ON r.origen = c.id
  WHERE salto < 6)
SELECT * FROM cadena;
```

---

## Agregar contenido

1. El `.md` en `normativa/` o `jurisprudencia/`, con el formato de `esquema.md` §3 y §4.
2. Las afectaciones (deroga, modifica, declara_inexequible…) **solo** en
   `relaciones.csv` — nunca dentro del `.md`. Una arista en dos lados se desincroniza.
3. `python3 verificar.py normativa/<archivo>.md` — contrasta los artículos extraídos
   contra el índice de la propia fuente (el `<select>` de senado, los encabezados en
   el Gestor). Un parser que se come artículos no falla ruidosamente: entrega un
   archivo que parece correcto. Sin `faltan 0` no se cierra el tick.
4. `python3 build.py`. Si imprime avisos, se corrigen antes de dar por cerrado.
5. Commit.

`python3 build.py --check` corre el autotest de la lógica de vigencia. Si se toca
`build.py`, tiene que seguir pasando.

---

## Estado del proyecto

`cola.md` es la cola de ingesta y el estado del loop: `[ ]` pendiente, `[~]` en curso,
`[x]` hecho, `[!]` bloqueado con motivo.

`destinos_sin_cargar` que imprime `build.py` no es un error: son aristas que apuntan a
normas todavía no cargadas. Es señal de qué falta, no de que algo esté roto.
