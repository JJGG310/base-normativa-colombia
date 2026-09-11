#!/usr/bin/env python3
"""Extrae fichas de sentencias de la relatoría de la Corte Constitucional.

    python3 ingesta_relatoria.py co:cc:c-443:2019 co:cc:c-284:2015
    python3 ingesta_relatoria.py --del-grafo --limite 50   # las que ya cita relaciones.csv
    python3 ingesta_relatoria.py --check

Cada sentencia son ~260.000 caracteres: pasarlas por el modelo es inviable y además
innecesario. El texto abre con los **descriptores y restrictores** que escribe la
propia relatoría de la Corte — el resumen oficial, corto y citable — y cierra con el
RESUELVE. Con eso se arma la ficha entera de forma mecánica, sin que nada dependa de
lo que el modelo crea recordar.

La `subregla` redactada (esquema.md §4) NO la produce este script: eso exige leer la
sentencia y se reserva para las marcadas `hito`.
"""
import argparse, html, os, re, sqlite3, sys, time, urllib.request
from datetime import date

RAIZ = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(RAIZ, "fuentes", "cache")
UA = {"User-Agent": "Mozilla/5.0"}
BASE = "https://www.corteconstitucional.gov.co/relatoria/%s/%s-%s-%s.htm"

MESES = dict(zip("enero febrero marzo abril mayo junio julio agosto septiembre "
                 "octubre noviembre diciembre".split(), range(1, 13)))
RE_ID = re.compile(r"^co:cc:(c|t|su)-(\d+):(\d{4})$", re.I)


def url_de(sid):
    m = RE_ID.match(sid)
    if not m:
        raise ValueError("id de sentencia no reconocido: %s" % sid)
    serie, num, anio = m.group(1).upper(), m.group(2), m.group(3)
    return BASE % (anio, serie, num, anio[2:])


def bajar(url):
    """Con caché y reintentos, por lo mismo que en ingesta_senado: una descarga que
    falla en silencio produce una ficha vacía que parece una ficha."""
    os.makedirs(CACHE, exist_ok=True)
    ruta = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9_.-]", "_", url)[-180:])
    if os.path.exists(ruta) and os.path.getsize(ruta) > 2000:
        with open(ruta, encoding="utf-8") as fh:
            return fh.read()
    ultimo = None
    for intento in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                doc = r.read().decode("iso-8859-1", "replace")   # la relatoría no es UTF-8
            if len(doc) > 2000:
                with open(ruta, "w", encoding="utf-8") as fh:
                    fh.write(doc)
                return doc
            ultimo = "respuesta de %d bytes" % len(doc)
        except Exception as e:
            ultimo = e
        time.sleep(2 * (intento + 1))
    raise RuntimeError("no se pudo bajar %s: %s" % (url, ultimo))


def plano(doc):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", doc, flags=re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", t)).split())


# El descriptor es una corrida de MAYÚSCULAS que termina en `-`. No sirve partir por
# `/`: los descriptores consecutivos van pegados, sin separador entre ellos.
RE_DESCRIPTOR = re.compile(
    r"(?:^|\s|/)([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ0-9]*(?:\s+[A-ZÁÉÍÓÚÑÜ0-9,.()]+){0,9})-\s+")


def descriptores(txt):
    """El bloque de apertura: `CONCEPTO EN MAYÚSCULAS- restrictor`, uno tras otro."""
    corte = txt.find("Referencia")
    cabeza = txt[:corte if 0 < corte < 6000 else 4000]
    marcas = list(RE_DESCRIPTOR.finditer(cabeza))
    salida = []
    for k, m in enumerate(marcas):
        fin = marcas[k + 1].start() if k + 1 < len(marcas) else len(cabeza)
        restrictor = " ".join(cabeza[m.end():fin].strip(" /").split())
        if len(restrictor) > 240:                 # la fuente le pega extractos del cuerpo
            restrictor = restrictor[:240].rsplit(" ", 1)[0] + "…"
        if len(restrictor) >= 5:
            salida.append("%s — %s" % (" ".join(m.group(1).split()), restrictor))
    return salida


def resuelve(txt):
    """La parte resolutiva es la ÚLTIMA aparición de RESUELVE: las anteriores son
    citas dentro del cuerpo de la providencia."""
    i = txt.upper().rfind("RESUELVE")
    if i < 0:
        return ""
    cuerpo = txt[i + len("RESUELVE"):]
    fin = re.search(r"(Notif[ií]quese|C[óo]piese|Cumplase|C[úu]mplase)", cuerpo)
    return cuerpo[:fin.start() if fin else 4000].strip(" .:-")


def decision_de(res):
    alto = res.upper()
    inex = "INEXEQUIB" in alto
    cond = "CONDICIONAD" in alto or "EN EL ENTENDIDO" in alto
    if inex and (cond or "EXEQUIBILIDAD" in alto):
        return "inexequible-parcial"
    if inex:
        return "inexequible"
    if cond:
        return "exequible-condicionado"
    if "EXEQUIB" in alto:
        return "exequible"
    if "INHIBIRSE" in alto or "INHIBIDA" in alto:
        return "inhibitoria"
    if "ESTESE A LO RESUELTO" in alto or "ESTARSE A LO RESUELTO" in alto:
        return "estese-a-lo-resuelto"
    return ""


def metadatos(txt):
    meta = {}
    m = re.search(r"Expediente[s]?:?\s*([A-Z]{1,3}-[\d\.]+(?:\s*(?:y|,)\s*[A-Z]{0,3}-?[\d\.]+)*)", txt)
    if m:
        meta["expediente"] = " ".join(m.group(1).split())
    m = re.search(r"Magistrad[oa]\s+(?:Ponente|Sustanciador[a]?)\s*:?\s*"
                  r"([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{6,60}?)\s*(?:\.|Bogot|La\s+Sala|SENTENCIA|I\.\s)", txt)
    if m:
        meta["ponente"] = " ".join(m.group(1).split()).title()
    zona = txt[max(0, txt.find("Bogot")):][:400] or txt[:4000]
    m = re.search(r"(?:\((\d{1,2})\)|\b(\d{1,2}))\s+de\s+(%s)\s+de\s+"
                  r"(?:[a-záéíóúñ\s]*?\()?(\d{4})" % "|".join(MESES), zona, re.I)
    if m:
        dia = m.group(1) or m.group(2)
        meta["fecha"] = "%s-%02d-%02d" % (m.group(4), MESES[m.group(3).lower()], int(dia))
    meta["sala"] = "plena" if re.search(r"\bSala\s+Plena\b", txt) else (
        "revision" if re.search(r"Sala\s+\w+\s+de\s+Revisi", txt) else "plena")
    return meta


def ramas_de(sid, con):
    """La sentencia hereda las ramas de los artículos que toca. Sale del grafo, no
    de una opinión sobre de qué 'trata' el fallo."""
    if not con:
        return []
    filas = con.execute("""SELECT DISTINCT d.ramas FROM relaciones r
        JOIN fragmentos f ON f.id = r.destino JOIN documentos d ON d.id = f.doc_id
        WHERE r.origen = ?""", (sid,)).fetchall()
    ramas = sorted({x.strip() for (r,) in filas for x in (r or "").split(",") if x.strip()})
    return ramas


def ficha(sid, con=None):
    url = url_de(sid)
    txt = plano(bajar(url))
    desc, res = descriptores(txt), resuelve(txt)
    if not desc and not res:
        raise RuntimeError("%s: ni descriptores ni parte resolutiva — revisar la fuente" % sid)
    meta = metadatos(txt)
    ramas = ramas_de(sid, con)

    fm = ["---", "id: " + sid, "tipo: sentencia", "corporacion: corte-constitucional",
          "sala: " + meta.get("sala", "plena"),
          "titulo: Sentencia %s de %s" % (sid.split(":")[2].upper(), sid.split(":")[3])]
    for k in ("ponente", "fecha", "expediente"):
        if meta.get(k):
            fm.append("%s: %s" % (k, meta[k]))
    fm += ["ramas: [%s]" % ", ".join(ramas or ["constitucional"]),
           "decision: " + (decision_de(res) or "sin-determinar"),
           "afectaciones: cargadas",
           "fuente: " + url, "verificado: " + date.today().isoformat(), "---", ""]
    if desc:
        fm += ["## descriptores", "", "\n".join("- " + d for d in desc), ""]
    if res:
        fm += ["## resuelve", "", res, ""]
    return "\n".join(fm), meta, len(desc)


def check():
    """Verifica el parseo sobre texto fijo: sin red, sin depender de la Corte."""
    txt = ("C-443-19 Sentencia C-443/19 DEMANDA DE INCONSTITUCIONALIDAD- Competencia de la "
           "Corte Constitucional ACCESO A LA ADMINISTRACION DE JUSTICIA- Garantía del plazo "
           "razonable para adelantar etapas/ LEGISLADOR- Amplio margen de configuración "
           "Referencia: Expediente D-12981 Demanda de inconstitucionalidad contra el artículo "
           "121 (parcial) del Código General del Proceso Actor: Eulin Abreo Magistrado "
           "Sustanciador: LUIS GUILLERMO GUERRERO PÉREZ Bogotá D. C., veinticinco (25) de "
           "septiembre de dos mil diecinueve (2019) La Sala Plena resolvió. RESUELVE se cita "
           "aquí en el cuerpo. Luego mas texto. RESUELVE PRIMERO.- DECLARAR LA INEXEQUIBILIDAD "
           "de la expresión de pleno derecho, y la EXEQUIBILIDAD CONDICIONADA del resto, en el "
           "entendido de que la nulidad debe alegarse. Notifíquese y cúmplase")
    d = descriptores(txt)
    assert len(d) >= 3, d
    assert d[0].startswith("DEMANDA DE INCONSTITUCIONALIDAD —"), d[0]

    r = resuelve(txt)
    assert r.startswith("PRIMERO.- DECLARAR LA INEXEQUIBILIDAD"), r[:80]
    assert "Notifíquese" not in r, "la fórmula de cierre no va en la parte resolutiva"
    assert "se cita aquí en el cuerpo" not in r, "se tomó un RESUELVE del cuerpo, no el final"

    assert decision_de(r) == "inexequible-parcial", decision_de(r)
    assert decision_de("DECLARAR EXEQUIBLE el artículo") == "exequible"
    assert decision_de("INHIBIRSE de emitir pronunciamiento") == "inhibitoria"

    m = metadatos(txt)
    assert m["expediente"] == "D-12981", m
    assert m["fecha"] == "2019-09-25", m
    assert m["ponente"] == "Luis Guillermo Guerrero Pérez", m
    assert m["sala"] == "plena", m

    assert url_de("co:cc:c-443:2019").endswith("/relatoria/2019/C-443-19.htm"), url_de("co:cc:c-443:2019")
    assert url_de("co:cc:su-214:2016").endswith("/relatoria/2016/SU-214-16.htm")
    print("check OK")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ids", nargs="*")
    p.add_argument("--del-grafo", action="store_true",
                   help="toma las sentencias que relaciones.csv ya cita y aún no tienen ficha")
    p.add_argument("--limite", type=int, default=25)
    a = p.parse_args()

    con = sqlite3.connect(os.path.join(RAIZ, "index.db")) if os.path.exists(
        os.path.join(RAIZ, "index.db")) else None
    ids = list(a.ids)
    if a.del_grafo and con:
        # Prioriza las que más artículos afectan: son las que más peso tienen.
        ids += [r[0] for r in con.execute("""SELECT origen, COUNT(*) n FROM relaciones
            WHERE origen LIKE 'co:cc:%' AND tipo LIKE 'declara%'
              AND origen NOT IN (SELECT id FROM documentos)
            GROUP BY origen ORDER BY n DESC""").fetchall()][:a.limite]

    ok = fallos = 0
    for sid in ids:
        destino = os.path.join(RAIZ, "jurisprudencia", sid.replace(":", "-") + ".md")
        try:
            texto, meta, nd = ficha(sid, con)
        except Exception as e:
            print("  [!] %s: %s" % (sid, e))
            fallos += 1
            continue
        with open(destino, "w", encoding="utf-8") as fh:
            fh.write(texto)
        ok += 1
        print("  %s  %s  %d descriptores" % (sid, meta.get("fecha", "sin fecha"), nd))
    print("%d fichas escritas, %d fallidas" % (ok, fallos))


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
