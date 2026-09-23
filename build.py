#!/usr/bin/env python3
"""Construye index.db desde los .md y relaciones.csv. El .db es desechable.

    python3 build.py          # reconstruye index.db
    python3 build.py -v       # + top 20 normas origen de aristas que faltan por cargar
    python3 build.py --check  # autotest
"""
import csv, datetime, os, re, sqlite3, sys, glob

RAIZ = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(RAIZ, "index.db")

# Relaciones que matan / afectan la vigencia (esquema.md §6)
# `subroga` reemplaza el texto: el artículo sigue existiendo con otro contenido.
# `declara_inexequible` mata solo con evidencia de que fue total (ver vista vigencia).
MATA = ("deroga", "deroga_tacitamente")
CONDICIONA = ("declara_exequible_condicionado", "declara_inexequible_parcial")
REFORMA = ("modifica", "adiciona", "subroga")
PARCIAL = "INEXEQUIBLE EN PARTE — alcance no registrado; verificar en la sentencia qué apartes cayeron"

# Nota de vigencia que la fuente (Senado/SUIN) pone al inicio del propio texto:
# «<Artículo derogado por…>», «<Artículo INEXEQUIBLE>». Si no está al inicio (p. ej.
# «PARÁGRAFO. <Artículo INEXEQUIBLE>») o es parcial («salvo…», «en lo referente…»), no cuenta.
# También «<Ley 1288 de 2009 declarada INEXEQUIBLE>» (el artículo lo creó una ley que cayó entera).
RE_MARCA = re.compile(r"<(?:Art[íi]culo (?:declarado )?(?:derogad[oa]|INEXEQUIBLE)"
                      r"|Ley [^<>]{1,40}? (?:derogada|declarada INEXEQUIBLE))[^>]{0,300}>?", re.I)
# El mismo marcador puede venir en el epígrafe (Senado: «Artículo derogado por…»;
# Gestor: «Comité de seguimiento.(Derogado por el art»).
RE_EPIGRAFE = re.compile(r"^<?Art[íi]culo (?:declarado )?(?:derogad[oa]|INEXEQUIBLE)|\(Derogad[oa] por", re.I)
# «derogado a partir del 2 de abril de 2026», «efectos diferidos hasta el …»: si la fecha
# es futura, todavía no muere (misma regla que las fechas de relaciones.csv).
RE_FECHA = re.compile(r"(\d{1,2}) de (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|"
                      r"octubre|noviembre|diciembre) de (\d{4})", re.I)
MESES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()
RE_PARCIAL = re.compile(r"en lo |en cuanto|parcial|salvo|excepto", re.I)
RE_EMBEBIDO = re.compile(r"A?RT[ÍI]CULO \d")  # artículo siguiente pegado por el parser
# Tipos que comparten numeración: un destino con uno se resuelve al doc cargado con el otro.
ALIAS = {"ley": "ley-estatutaria", "ley-estatutaria": "ley",
         "decreto": "decreto-ley", "decreto-ley": "decreto"}
# Fecha de efecto: vacía o mal formada cuenta como ya surtida (no como futura).
EF = "(r.fecha <= date('now') OR r.fecha NOT GLOB '[0-9][0-9][0-9][0-9]-*')"
TOTAL = "(lower(COALESCE(r.nota,'')) LIKE '%total%' OR COALESCE(f.marca,'') LIKE '%inexequible%')"


def marca(texto, epigrafe=""):
    """Marcador de muerte total en el epígrafe o al inicio del texto del artículo, o None."""
    if RE_EPIGRAFE.search(epigrafe or "") and not RE_PARCIAL.search(epigrafe):
        m = epigrafe[:200]
    else:
        e = RE_EMBEBIDO.search(texto, 1)
        m = RE_MARCA.search(texto[:e.start()] if e else texto)
        m = m.group(0)[:200] if m and m.start() < 100 and not RE_PARCIAL.search(m.group(0)) else None
    hoy = datetime.date.today().isoformat()
    if m and any("%s-%02d-%02d" % (a, MESES.index(me.lower()) + 1, int(d)) > hoy
                 for d, me, a in RE_FECHA.findall(m)):
        return None
    return m


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
  id TEXT PRIMARY KEY, doc_id TEXT, clave TEXT, titulo TEXT, ubicacion TEXT, texto TEXT, marca TEXT);
CREATE INDEX ix_frag_doc ON fragmentos(doc_id);

CREATE TABLE relaciones (
  origen TEXT, tipo TEXT, destino TEXT, fecha TEXT, nota TEXT, fuente TEXT);
CREATE INDEX ix_rel_destino ON relaciones(destino);
CREATE INDEX ix_rel_origen ON relaciones(origen);

CREATE VIRTUAL TABLE busqueda USING fts5(id UNINDEXED, titulo, texto, tokenize='unicode61 remove_diacritics 2');

-- Vigencia derivada, nunca almacenada (esquema.md §2.2 y §7). Subconsultas por
-- artículo (destino = artículo o su norma): una fila por artículo, sin duplicados.
-- Una arista a la norma entera (destino = doc_id) afecta a todos sus artículos.
-- Un declara_inexequible sin prueba de total queda como aviso «en parte», salvo que el
-- artículo se haya modificado/subrogado DESPUÉS de la sentencia: el texto vigente es
-- posterior y el aviso ya no le aplica (la arista sigue en afectado_por).
CREATE VIEW vigencia AS SELECT articulo, doc_id, titulo_corto, epigrafe,
  CASE WHEN mata IS NOT NULL THEN 'MUERTO'
       WHEN suspendido IS NOT NULL THEN 'SUSPENDIDO'
       WHEN condicion IS NOT NULL THEN 'VIGENTE_CONDICIONADO'
       WHEN reformas IS NOT NULL THEN 'VIGENTE_REFORMADO'
       ELSE 'VIGENTE' END AS estado,
  mata, suspendido, condicion, reformas, verificado
FROM (SELECT f.id AS articulo, f.doc_id, d.titulo_corto, f.titulo AS epigrafe, d.verificado,
  NULLIF(rtrim(COALESCE((SELECT group_concat(r.origen||' ('||r.tipo||')', ' | ') FROM relaciones r
      WHERE r.destino IN (f.id, f.doc_id) AND {EF} AND (r.tipo IN {MATA}
        OR (r.tipo = 'declara_inexequible' AND {TOTAL}))) || ' | ', '')
    || COALESCE('marcador de la fuente: ' || f.marca, ''), ' |'), '') AS mata,
  (SELECT group_concat(r.origen, ' | ') FROM relaciones r
      WHERE r.destino IN (f.id, f.doc_id) AND r.tipo = 'suspende' AND {EF}) AS suspendido,
  (SELECT group_concat(r.origen||': '||CASE WHEN r.tipo = 'declara_inexequible' THEN '{PARCIAL}'
        ELSE COALESCE(NULLIF(r.nota,''),'SIN NOTA') END, ' | ') FROM relaciones r
      WHERE r.destino IN (f.id, f.doc_id) AND (r.tipo IN {CONDICIONA}
        OR (r.tipo = 'declara_inexequible' AND {EF} AND NOT {TOTAL} AND NOT EXISTS (
          SELECT 1 FROM relaciones r2 WHERE r2.destino = f.id AND r2.tipo IN ('modifica','subroga')
            AND r2.fecha > r.fecha AND r.fecha GLOB '[0-9][0-9][0-9][0-9]-*')))) AS condicion,
  (SELECT group_concat(r.origen||' ('||r.tipo||')', ' | ') FROM relaciones r
      WHERE r.destino IN (f.id, f.doc_id) AND r.tipo IN {REFORMA}) AS reformas
FROM fragmentos f JOIN documentos d ON d.id = f.doc_id WHERE f.clave LIKE 'art:%');
""".format(MATA=str(MATA), CONDICIONA=str(CONDICIONA), REFORMA=str(REFORMA),
           EF=EF, TOTAL=TOTAL, PARCIAL=PARCIAL)

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
            frags = fragmentos(cuerpo)
            for clave, titulo, ubicacion, texto in frags:
                # esquema §4: de una sentencia se guarda la ficha, no el texto completo.
                # Solo si no hay nada más se deja un extracto, marcado como tal.
                if clase == "jurisprudencia" and clave == "texto":
                    if len(frags) > 1:
                        continue
                    if len(texto) > 4000:
                        texto = texto[:4000] + "\n\n[… extracto; texto completo en la fuente]"
                fid = meta["id"] + ":" + clave
                con.execute("INSERT OR REPLACE INTO fragmentos VALUES (?,?,?,?,?,?,?)",
                            (fid, meta["id"], clave, titulo, ubicacion, texto,
                             marca(texto, titulo) if clave.startswith("art:") else None))
                con.execute("INSERT INTO busqueda VALUES (?,?,?)", (fid, titulo, texto))

    docs = {r[0] for r in con.execute("SELECT id FROM documentos")}

    def destino(d):
        p = d.split(":")
        if len(p) >= 4 and ":".join(p[:4]) not in docs and p[1] in ALIAS:
            alt = [p[0], ALIAS[p[1]]] + p[2:]
            if ":".join(alt[:4]) in docs:
                return ":".join(alt)
        return d

    csv_path = os.path.join(raiz, "relaciones.csv")
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as fh:
            for fila in csv.DictReader(fh):
                if not fila.get("origen", "").strip():
                    continue
                v = [fila.get(c, "").strip() for c in
                     ("origen", "tipo", "destino", "fecha", "nota", "fuente")]
                v[0], v[2] = destino(v[0]), destino(v[2])
                con.execute("INSERT INTO relaciones VALUES (?,?,?,?,?,?)", v)
    con.commit()

    # Aristas cuyo ORIGEN (la norma o sentencia que reforma/deroga) no está cargado:
    # no es error, es cola de trabajo. Los destinos siempre están cargados porque las
    # aristas se extraen de la norma afectada.
    sin_origen = [r[0] for r in con.execute("""SELECT origen FROM relaciones WHERE origen NOT IN
        (SELECT id FROM fragmentos) AND origen NOT IN (SELECT id FROM documentos)""")]
    faltan = {}
    for o in sin_origen:
        k = ":".join(o.split(":")[:4])
        faltan[k] = faltan.get(k, 0) + 1
    # Una arista que apunta a un artículo de una norma YA cargada, y ese artículo no
    # existe, solo puede significar que la extracción perdió artículos. Es la señal
    # que delata al parser cuando se come parte del texto sin fallar.
    perdidos = con.execute("""SELECT COUNT(*) FROM relaciones r JOIN documentos d
        ON r.destino LIKE d.id || ':art:%' WHERE r.destino NOT IN (SELECT id FROM fragmentos)""").fetchone()[0]
    if perdidos:
        avisos.append("%d aristas apuntan a artículos INEXISTENTES de normas cargadas "
                      "— la extracción perdió texto" % perdidos)

    malas = con.execute("""SELECT COUNT(*) FROM relaciones WHERE fecha <> ''
        AND fecha NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'""").fetchone()[0]
    if malas:
        avisos.append("%d relaciones con fecha mal formada (no AAAA-MM-DD) — se tratan "
                      "como ya surtidas; corregir en relaciones.csv" % malas)

    # Una reforma no puede surtir efecto antes del año de la norma que la hace
    # (p. ej. Ley 2010 de 2019 fechada 2018-12-28): la fecha está mal y la vista la usa.
    imposibles = sum(1 for o, f in con.execute("SELECT origen, fecha FROM relaciones")
                     if o.split(":")[3:4] and o.split(":")[3].isdigit() and f[:4].isdigit()
                     and f[:4] < o.split(":")[3])
    if imposibles:
        avisos.append("%d relaciones con fecha anterior al año de su norma origen — "
                      "corregir en relaciones.csv" % imposibles)

    n = lambda t: con.execute("SELECT COUNT(*) FROM " + t).fetchone()[0]
    print("documentos=%d articulos/fichas=%d relaciones=%d origenes_sin_cargar=%d aristas / %d normas"
          % (n("documentos"), n("fragmentos"), n("relaciones"), len(sin_origen), len(faltan)))
    if "-v" in sys.argv:
        for k, c in sorted(faltan.items(), key=lambda x: -x[1])[:20]:
            print("  falta %-40s %d aristas" % (k, c))
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
                 "\n## art:4 — Cuatro\nTexto cuatro.\n"
                 "\n## art:5 — Cinco\nTexto cinco.\n\n## art:6 — Seis\nTexto seis.\n"
                 "\n## art:7 —\n<Artículo INEXEQUIBLE>\n\n## art:8 —\n<Artículo derogado por la Ley 9 de 2001>\n"
                 "\n## art:9 —\n<Artículo derogado en lo referente a X, por la Ley 9 de 2001> Texto.\n"
                 "\n## art:10 — Diez\nTexto diez. ARTÍCULO 10A. <Artículo derogado por la Ley 9 de 2001>\n"
                 "\n## art:11 — Once\nTexto once.\n"
                 "\n## art:12 — Artículo derogado por el artículo 87 de la Ley 2080 de 2021\nModifíquese el X.\n"
                 "\n## art:13 — Artículo derogado a partir del 2 de abril de 2099 por el artículo 1 de la Ley 9 de 2098\nT.\n"
                 "\n## art:14 — Catorce\n<Ley 1288 de 2009 declarada INEXEQUIBLE>\n"
                 "\n## art:15 — Comité.(Derogado por el art\n26, Decreto 1017 de 2025). Texto.\n"
                 "\n## art:16 — Dieciséis\nTexto.\n\n## art:17 — Diecisiete\nTexto.\n")
    with open(tmp + "/normativa/y.md", "w", encoding="utf-8") as fh:
        fh.write("---\nid: co:ley:5:2005\ntipo: ley\ntitulo: T\nramas: [civil]\n"
                 "fuente: http://x\nverificado: 2026-01-01\n---\n\n## art:1 — Uno\nTexto.\n")
    for num, anio in ((7, 2007), (9, 2009)):  # normas enteras derogadas (hoy y en 2099)
        with open(tmp + "/normativa/n%d.md" % num, "w", encoding="utf-8") as fh:
            fh.write("---\nid: co:ley:%d:%d\ntipo: ley\ntitulo: T\nramas: [civil]\nfuente: http://x\n"
                     "verificado: 2026-01-01\n---\n\n## art:1 — Uno\nT.\n\n## art:2 — Dos\nT.\n" % (num, anio))
    with open(tmp + "/jurisprudencia/s.md", "w", encoding="utf-8") as fh:
        fh.write("---\nid: co:csj:sc-1:2020\ntipo: sentencia\nramas: [civil]\n"
                 "fuente: http://x\nverificado: 2026-01-01\n---\n\n## resuelve\nCasa.\n\n## texto\nTodo.\n")
    with open(tmp + "/relaciones.csv", "w", encoding="utf-8") as fh:
        fh.write("origen,tipo,destino,fecha,nota,fuente\n"
                 "co:ley:2:2001:art:9,deroga,co:ley:1:2000:art:1,2001-01-01,,x\n"
                 "co:cc:c-1:2030,declara_inexequible,co:ley:1:2000:art:2,2030-01-01,,x\n"
                 "co:cc:c-2:2005,declara_exequible_condicionado,co:ley:1:2000:art:3,2005-01-01,solo si se lee asi,x\n"
                 "co:ley:3:2002:art:1,modifica,co:ley:1:2000:art:4,2002-01-01,,x\n"
                 "co:ley:3:2002:art:2,subroga,co:ley:1:2000:art:5,2002-01-01,,x\n"
                 "co:cc:c-3:2010,declara_inexequible,co:ley:1:2000:art:6,2010-01-01,,x\n"
                 "co:cc:c-4:1993,declara_inexequible,co:ley:1:2000:art:7,93-12-31,,x\n"
                 "co:ley:4:2003,deroga,co:ley-estatutaria:1:2000:art:11,2003-01-01,,x\n"
                 "co:ley:6:2006,modifica,co:ley:5:2005,2006-01-01,,x\n"
                 "co:ley:6:2006:art:1,modifica,co:ley:5:2005:art:1,2006-01-01,,x\n"
                 "co:ley:8:2008:art:3,deroga,co:ley:7:2007,2008-01-01,,x\n"
                 "co:ley:8:2008:art:4,deroga,co:ley:9:2009,2099-01-01,,x\n"
                 "co:cc:c-481:2019,declara_inexequible,co:ley:1:2000:art:16,2019-10-03,,x\n"
                 "co:ley:2010:2019,modifica,co:ley:1:2000:art:16,2019-12-31,,x\n"
                 "co:cc:c-481:2019,declara_inexequible,co:ley:1:2000:art:17,2019-10-03,,x\n"
                 "co:ley:1943:2018,modifica,co:ley:1:2000:art:17,2018-12-28,,x\n")
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
    assert est["co:ley:1:2000:art:5"] == "VIGENTE_REFORMADO", "subrogar reemplaza el texto, no mata"
    assert est["co:ley:1:2000:art:6"] == "VIGENTE_CONDICIONADO", "inexequible sin prueba de total no mata"
    assert est["co:ley:1:2000:art:7"] == "MUERTO", "marcador + fecha de 2 dígitos no es futura"
    assert est["co:ley:1:2000:art:8"] == "MUERTO", "marcador de derogatoria en el texto"
    assert est["co:ley:1:2000:art:9"] == "VIGENTE", "derogatoria parcial no mata"
    assert est["co:ley:1:2000:art:10"] == "VIGENTE", "el marcador de un artículo pegado no cuenta"
    assert est["co:ley:1:2000:art:11"] == "MUERTO", "alias ley-estatutaria -> ley"
    assert est["co:ley:1:2000:art:12"] == "MUERTO", "marcador en el epígrafe (Senado)"
    assert est["co:ley:1:2000:art:13"] == "VIGENTE", "marcador con fecha futura aún no mata"
    assert est["co:ley:1:2000:art:14"] == "MUERTO", "«Ley … declarada INEXEQUIBLE»"
    assert est["co:ley:1:2000:art:15"] == "MUERTO", "marcador «(Derogado por» en el epígrafe (Gestor)"
    assert est["co:ley:1:2000:art:16"] == "VIGENTE_REFORMADO", "reforma posterior a la sentencia: sin aviso en parte"
    assert est["co:ley:1:2000:art:17"] == "VIGENTE_CONDICIONADO", "reforma anterior a la sentencia: aviso sigue"
    assert est["co:ley:7:2007:art:1"] == est["co:ley:7:2007:art:2"] == "MUERTO", "deroga a la norma entera"
    assert est["co:ley:9:2009:art:1"] == "VIGENTE", "deroga a la norma entera con fecha futura"
    assert "c-4:1993" in con.execute("SELECT mata FROM vigencia WHERE articulo='co:ley:1:2000:art:7'").fetchone()[0]
    assert con.execute("SELECT count(*) FROM vigencia WHERE articulo='co:ley:5:2005:art:1'").fetchone()[0] == 1
    assert con.execute("SELECT count(*) FROM fragmentos WHERE clave='texto'").fetchone()[0] == 0
    # FTS5 sin tildes: buscar "hipoteca" debe pegar aunque se escriba con acento raro
    assert con.execute("SELECT count(*) FROM busqueda WHERE busqueda MATCH 'hipoteca'").fetchone()[0] == 1
    con.close(); shutil.rmtree(tmp)
    print("check OK")


if __name__ == "__main__":
    check() if "--check" in sys.argv else construir()
