#!/usr/bin/env python3
"""Construye index.db desde los .md y relaciones.csv. El .db es desechable.

    python3 build.py          # reconstruye index.db
    python3 build.py --check  # autotest
"""
import csv, os, re, sqlite3, sys, glob

RAIZ = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(RAIZ, "index.db")

# Relaciones que matan / afectan la vigencia (esquema.md §6)
MATA = ("deroga", "deroga_tacitamente", "subroga", "declara_inexequible")
CONDICIONA = ("declara_exequible_condicionado", "declara_inexequible_parcial")
REFORMA = ("modifica", "adiciona")


def frontmatter(texto):
    """Parser del subconjunto YAML que usa el esquema: `k: v` y `k: [a, b]`."""
    if not texto.startswith("---\n"):
        return {}, texto
    cabeza, _, cuerpo = texto[4:].partition("\n---\n")
    meta = {}
    for linea in cabeza.splitlines():
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        k, _, v = linea.partition(":")
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        meta[k.strip()] = v
    return meta, cuerpo


def fragmentos(cuerpo):
    """Corta el cuerpo en secciones `## clave — titulo`. Devuelve (clave, titulo, texto)."""
    partes = re.split(r"^## +", cuerpo, flags=re.M)[1:]
    salida = []
    for parte in partes:
        encabezado, _, texto = parte.partition("\n")
        clave, _, titulo = encabezado.partition("—")
        # Línea opcional `ubicacion: TITULO ... > CAPITULO ...` justo bajo el encabezado
        ubicacion = ""
        if texto.lstrip().startswith("ubicacion:"):
            linea, _, texto = texto.lstrip().partition("\n")
            ubicacion = linea.partition(":")[2].strip()
        salida.append((clave.strip(), titulo.strip(), ubicacion, texto.strip()))
    return salida


ESQUEMA_SQL = """
CREATE TABLE documentos (
  id TEXT PRIMARY KEY, clase TEXT, tipo TEXT, titulo TEXT, titulo_corto TEXT,
  fecha TEXT, ramas TEXT, estado_general TEXT, corporacion TEXT, sala TEXT,
  ponente TEXT, decision TEXT, hito TEXT, fuente TEXT, verificado TEXT,
  afectaciones TEXT, ruta TEXT);

CREATE TABLE fragmentos (
  id TEXT PRIMARY KEY, doc_id TEXT, clave TEXT, titulo TEXT, ubicacion TEXT, texto TEXT);
CREATE INDEX ix_frag_doc ON fragmentos(doc_id);

CREATE TABLE relaciones (
  origen TEXT, tipo TEXT, destino TEXT, fecha TEXT, nota TEXT, fuente TEXT);
CREATE INDEX ix_rel_destino ON relaciones(destino);
CREATE INDEX ix_rel_origen ON relaciones(origen);

CREATE VIRTUAL TABLE busqueda USING fts5(id UNINDEXED, titulo, texto, tokenize='unicode61 remove_diacritics 2');

-- Afectaciones agrupadas por destino. group_concat ignora los NULL.
CREATE VIEW afectaciones AS SELECT destino,
  group_concat(CASE WHEN tipo IN {MATA} AND fecha <= date('now') THEN origen||' ('||tipo||')' END, ' | ') AS mata,
  group_concat(CASE WHEN tipo = 'suspende'  AND fecha <= date('now') THEN origen END, ' | ') AS suspendido,
  group_concat(CASE WHEN tipo IN {CONDICIONA} THEN origen||': '||COALESCE(nota,'SIN NOTA') END, ' | ') AS condicion,
  group_concat(CASE WHEN tipo IN {REFORMA}    THEN origen||' ('||tipo||')' END, ' | ') AS reformas
FROM relaciones GROUP BY destino;

-- Vigencia derivada, nunca almacenada (esquema.md §2.2 y §7).
CREATE VIEW vigencia AS SELECT
  f.id AS articulo, f.doc_id, d.titulo_corto, f.titulo AS epigrafe,
  CASE WHEN a.mata IS NOT NULL THEN 'MUERTO'
       WHEN a.suspendido IS NOT NULL THEN 'SUSPENDIDO'
       WHEN a.condicion IS NOT NULL THEN 'VIGENTE_CONDICIONADO'
       WHEN a.reformas IS NOT NULL THEN 'VIGENTE_REFORMADO'
       ELSE 'VIGENTE' END AS estado,
  a.mata, a.suspendido, a.condicion, a.reformas, d.verificado
FROM fragmentos f
JOIN documentos d ON d.id = f.doc_id
LEFT JOIN afectaciones a ON a.destino = f.id OR a.destino = f.doc_id
WHERE f.clave LIKE 'art:%';
""".format(MATA=str(MATA), CONDICIONA=str(CONDICIONA), REFORMA=str(REFORMA))

COLS = ("id clase tipo titulo titulo_corto fecha ramas estado_general corporacion "
        "sala ponente decision hito fuente verificado afectaciones ruta").split()


def construir(db_path=DB, raiz=RAIZ):
    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    con.executescript(ESQUEMA_SQL)
    avisos = []

    for clase in ("normativa", "jurisprudencia"):
        for ruta in sorted(glob.glob(os.path.join(raiz, clase, "*.md"))):
            with open(ruta, encoding="utf-8") as fh:
                meta, cuerpo = frontmatter(fh.read())
            rel = os.path.relpath(ruta, raiz)
            if not meta.get("id"):
                avisos.append("SIN ID: " + rel)
                continue
            for obligatorio in ("fuente", "verificado", "ramas"):
                if not meta.get(obligatorio):
                    avisos.append("falta %s: %s" % (obligatorio, rel))
            meta["clase"], meta["ruta"] = clase, rel
            if isinstance(meta.get("ramas"), list):
                meta["ramas"] = ",".join(meta["ramas"])
            con.execute("INSERT OR REPLACE INTO documentos VALUES (%s)" % ",".join("?" * len(COLS)),
                        [meta.get(c) for c in COLS])
            for clave, titulo, ubicacion, texto in fragmentos(cuerpo):
                fid = meta["id"] + ":" + clave
                con.execute("INSERT OR REPLACE INTO fragmentos VALUES (?,?,?,?,?,?)",
                            (fid, meta["id"], clave, titulo, ubicacion, texto))
                con.execute("INSERT INTO busqueda VALUES (?,?,?)", (fid, titulo, texto))

    csv_path = os.path.join(raiz, "relaciones.csv")
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as fh:
            for fila in csv.DictReader(fh):
                if not fila.get("origen", "").strip():
                    continue
                con.execute("INSERT INTO relaciones VALUES (?,?,?,?,?,?)",
                            [fila.get(c, "").strip() for c in
                             ("origen", "tipo", "destino", "fecha", "nota", "fuente")])
    con.commit()

    # Aristas que apuntan a algo que no está cargado: no es error, es cola de trabajo.
    huerfanas = con.execute("""SELECT COUNT(*) FROM relaciones r WHERE r.destino NOT IN
        (SELECT id FROM fragmentos) AND r.destino NOT IN (SELECT id FROM documentos)""").fetchone()[0]
    n = lambda t: con.execute("SELECT COUNT(*) FROM " + t).fetchone()[0]
    print("documentos=%d articulos/fichas=%d relaciones=%d destinos_sin_cargar=%d"
          % (n("documentos"), n("fragmentos"), n("relaciones"), huerfanas))
    for a in avisos:
        print("  aviso:", a)
    con.close()
    return avisos


def check():
    """Autotest: lo mínimo que debe fallar si la lógica de vigencia se rompe."""
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    os.makedirs(tmp + "/normativa"); os.makedirs(tmp + "/jurisprudencia")
    with open(tmp + "/normativa/x.md", "w", encoding="utf-8") as fh:
        fh.write("---\nid: co:ley:1:2000\ntipo: ley\ntitulo: T\nramas: [civil]\n"
                 "fuente: http://x\nverificado: 2026-01-01\n---\n\n"
                 "## art:1 — Uno\nTexto uno sobre hipoteca.\n\n"
                 "## art:2 — Dos\nTexto dos.\n\n## art:3 — Tres\nTexto tres.\n"
                 "\n## art:4 — Cuatro\nTexto cuatro.\n")
    with open(tmp + "/relaciones.csv", "w", encoding="utf-8") as fh:
        fh.write("origen,tipo,destino,fecha,nota,fuente\n"
                 "co:ley:2:2001:art:9,deroga,co:ley:1:2000:art:1,2001-01-01,,x\n"
                 "co:cc:c-1:2030,declara_inexequible,co:ley:1:2000:art:2,2030-01-01,,x\n"
                 "co:cc:c-2:2005,declara_exequible_condicionado,co:ley:1:2000:art:3,2005-01-01,solo si se lee asi,x\n"
                 "co:ley:3:2002:art:1,modifica,co:ley:1:2000:art:4,2002-01-01,,x\n")
    construir(tmp + "/i.db", tmp)
    con = sqlite3.connect(tmp + "/i.db")
    est = dict(con.execute("SELECT articulo, estado FROM vigencia"))
    assert est["co:ley:1:2000:art:1"] == "MUERTO", est
    assert est["co:ley:1:2000:art:2"] == "VIGENTE", "inexequibilidad futura no puede matar hoy"
    assert est["co:ley:1:2000:art:3"] == "VIGENTE_CONDICIONADO", est
    assert est["co:ley:1:2000:art:4"] == "VIGENTE_REFORMADO", est
    cond = con.execute("SELECT condicion FROM vigencia WHERE articulo=?",
                       ("co:ley:1:2000:art:3",)).fetchone()[0]
    assert "solo si se lee asi" in cond, "la nota del condicionamiento debe salir siempre"
    # FTS5 sin tildes: buscar "hipoteca" debe pegar aunque se escriba con acento raro
    assert con.execute("SELECT count(*) FROM busqueda WHERE busqueda MATCH 'hipoteca'").fetchone()[0] == 1
    con.close(); shutil.rmtree(tmp)
    print("check OK")


if __name__ == "__main__":
    check() if "--check" in sys.argv else construir()
