#!/usr/bin/env python3
"""Fichas de providencias de la Corte Suprema desde el API del CENDOJ.

    python3 ingesta_cendoj.py CIVIL 2025 --limite 40
    python3 ingesta_cendoj.py PENAL 2024 --terminos "casación,nulidad" --limite 100
    python3 ingesta_cendoj.py --check

La Corte Suprema no publica un índice descargable: el portal solo expone un GraphQL
que **exige término de búsqueda** (con la consulta vacía devuelve 0 resultados). Así
que el recorrido se hace por términos amplios y se deduplica por el número de la
providencia — no es «toda la Corte Suprema», es lo que esos términos alcanzan, y se
anota cuántos trae cada corrida.

El texto **no** sale del API: `getContentSearch` devuelve una vista previa con elisiones
(«(…)») alrededor de los términos buscados, y una providencia con huecos presentada como
su texto es justo lo que este proyecto no puede permitirse. Se baja el .docx original por
`downloadFile` y se extrae de `word/document.xml`. Las providencias que la Corte solo
publica en PDF se saltan: se anotan, no se rellenan.

La sala PENAL no se puede cargar hoy: `downloadFile` devuelve 404 para todas sus rutas
(probado con cuatro variantes el 2026-09-11), y la vista previa del API no sirve de
reemplazo — además de elidir, mete espacios dentro de las palabras para resaltar los
términos («R a dic a ción»). Civil y laboral funcionan.
"""
import argparse, html, io, json, os, re, sys, time, urllib.request, zipfile
from datetime import date

RAIZ = os.path.dirname(os.path.abspath(__file__))
API = "https://consultaprovidenciasbk.cortesuprema.gov.co/api"
CABECERAS = {"Content-Type": "application/json", "Accept": "application/json",
             "User-Agent": "Mozilla/5.0"}
PORTAL = "https://consultaprovidencias.cortesuprema.gov.co/"
DESCARGA = "https://consultaprovidenciasbk.cortesuprema.gov.co/downloadFile"

# Términos amplios: sirven de rastrillo, no de criterio. Cualquier providencia de la
# sala cae en alguno de ellos.
TERMINOS = ["recurso", "sentencia", "demanda", "proceso", "derecho", "prueba"]
RAMAS = {"CIVIL": "civil, comercial, procesal", "LABORAL": "laboral, seguridad-social",
         "PENAL": "penal, procesal"}
RE_TITULO = re.compile(r"^([A-Z]{2,4})(\d+)\s*-\s*(\d{4})")
# Civil y laboral escriben el radicado entre corchetes; penal entre paréntesis.
RE_RADICADO = re.compile(r"[\[(]([0-9\-]+)[\])]")
# El fallo cierra con el bloque de firma electrónica: no es parte de la decisión.
RE_FIRMA = re.compile(r"Este documento fue generado con firma electrónica.*$", re.S | re.I)


def consultar(query):
    req = urllib.request.Request(API, data=json.dumps({"query": query}).encode(),
                                 headers=CABECERAS)
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.loads(r.read().decode("utf-8"))
    if d.get("errors"):
        raise RuntimeError(d["errors"])
    return d["data"]


def buscar(sala, anio, termino, start=0, clase=""):
    q = ('query { getSearchResult(searchQuery: { query: "%s", typeOfQuery: "%s", '
         'start: %d, isExact: false, magistrate: "", year: "%s", autoSentencia: "%s", '
         'order: "", roomTutelas: "", addedQueries: [] }) { numOfResults searchResults '
         '{ id title doctor fechaCreacion ano autoSentencia } } }'
         % (termino.replace('"', ''), sala, start, anio, clase))
    return consultar(q)["getSearchResult"]


def contenido(doc_path):
    """Texto del .docx original. El API solo da vistas previas con elisiones."""
    req = urllib.request.Request(DESCARGA, data=json.dumps({"path": doc_path}).encode(),
                                 headers=CABECERAS)
    with urllib.request.urlopen(req, timeout=120) as r:
        crudo = r.read()
    if crudo[:2] != b"PK":
        return ""
    with zipfile.ZipFile(io.BytesIO(crudo)) as z:
        if "word/document.xml" not in z.namelist():
            return ""
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    # Sin separar por párrafo el documento queda en una línea; y las etiquetas se
    # quitan SIN meter espacio, porque Word parte las palabras en varios <w:t>.
    t = re.sub(r"</w:p>", "\n", xml)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(re.sub(r"[ \t]+", " ", t))
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip()


def limpiar(texto):
    t = re.sub(r"<br\s*/?>|</p>|</h\d>", "\n", texto, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t\xa0]+", " ", t)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip()


def identificar(titulo):
    """«SC2428-2024 [2018-03988-00].pdf» -> (co:csj:sc-2428:2024, 2018-03988-00)."""
    m = RE_TITULO.match(titulo.strip())
    if not m:
        return "", ""
    rad = RE_RADICADO.search(titulo)
    return "co:csj:%s-%s:%s" % (m.group(1).lower(), m.group(2), m.group(3)), \
           (rad.group(1) if rad else "")


def resuelve(texto):
    """La parte resolutiva: desde el último RESUELVE/FALLA hasta el final."""
    marcas = list(re.finditer(r"(?m)^\s*(RESUELVE|FALLA|SE RESUELVE|DECIDE)\s*:?\s*$", texto))
    return texto[marcas[-1].start():].strip() if marcas else ""


def ficha(res, sala, texto):
    sid, radicado = identificar(res["title"])
    cuerpo = RE_FIRMA.sub("", texto).strip()
    fm = ["---", "id: " + sid, "tipo: " + ("auto" if res.get("autoSentencia") == "AUTO"
                                           else "sentencia"),
          "corporacion: corte-suprema", "sala: " + sala.lower(),
          "titulo: %s de %s — Corte Suprema, Sala de Casación %s"
          % (sid.split(":")[2].upper().replace("-", " "), res.get("ano", ""), sala.title()),
          "ponente: " + re.sub(r"^Dr[a]?\.\s*", "", (res.get("doctor") or "").strip()),
          "fecha: " + (res.get("fechaCreacion") or "")[:10],
          "expediente: " + radicado, "ramas: [%s]" % RAMAS.get(sala, ""),
          "afectaciones: no-aplica", "fuente: " + PORTAL,
          "verificado: " + date.today().isoformat(), "---", ""]
    parte = resuelve(cuerpo)
    if parte:
        fm += ["## resuelve", "", parte, ""]
    fm += ["## texto", "", cuerpo, ""]
    return sid, "\n".join(fm)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("sala", choices=["CIVIL", "LABORAL", "PENAL"])
    p.add_argument("anio")
    p.add_argument("--terminos", default=",".join(TERMINOS))
    p.add_argument("--limite", type=int, default=40)
    p.add_argument("--pausa", type=float, default=1.2, help="segundos entre peticiones")
    p.add_argument("--clase", default="SENTENCIA", choices=["SENTENCIA", "AUTO", ""],
                   help="la sentencia pesa más que el auto: es lo que se carga por defecto")
    a = p.parse_args()

    destino_dir = os.path.join(RAIZ, "jurisprudencia")
    vistos, escritas, fallos = set(), 0, 0
    for termino in a.terminos.split(","):
        start, secas = 0, 0
        # Hay salas-año que la Corte solo publica en PDF (laboral 2023 trae 12.950
        # providencias y ni un .docx). Sin este corte, el recorrido se pasa media hora
        # paginando resultados que nunca va a poder leer.
        while escritas < a.limite and secas < 15:
            try:
                r = buscar(a.sala, a.anio, termino.strip(), start, a.clase)
            except Exception as e:
                print("  [!] búsqueda %s/%s '%s': %s" % (a.sala, a.anio, termino, e))
                break
            resultados = r.get("searchResults") or []
            if not resultados:
                break
            for res in resultados:
                # La misma providencia sale en .pdf y en .docx: solo del .docx se
                # saca el texto íntegro con la librería estándar.
                if not res["title"].lower().endswith(".docx"):
                    continue
                sid, _ = identificar(res["title"])
                ruta = os.path.join(destino_dir, sid.replace(":", "-") + ".md")
                if not sid or sid in vistos or os.path.exists(ruta):
                    vistos.add(sid)
                    continue
                vistos.add(sid)
                time.sleep(a.pausa)
                try:
                    texto = contenido(res["id"])
                except Exception as e:
                    print("  [!] %s: %s" % (sid, e))
                    fallos += 1
                    continue
                if len(texto) < 500:
                    fallos += 1
                    continue
                _, md = ficha(res, a.sala, texto)
                with open(ruta, "w", encoding="utf-8") as fh:
                    fh.write(md)
                escritas += 1
                print("  %s  %s  %d KB" % (sid, (res.get("fechaCreacion") or "")[:10],
                                           len(md) // 1024))
                if escritas >= a.limite:
                    break
            secas = 0 if any(x["title"].lower().endswith(".docx") for x in resultados) else secas + 1
            start += len(resultados)
            time.sleep(a.pausa)
    print("%d fichas escritas, %d fallidas, %d providencias vistas"
          % (escritas, fallos, len(vistos)))


def check():
    assert identificar("SC2428-2024 [2018-03988-00].pdf") == ("co:csj:sc-2428:2024",
                                                              "2018-03988-00")
    assert identificar("AC3200-2024 [2024-00782-00].docx")[0] == "co:csj:ac-3200:2024"
    assert identificar("no es una providencia.pdf") == ("", "")

    # El .docx parte las palabras en varios <w:t>: al quitar etiquetas no va espacio.
    import zipfile as _z, io as _io
    buf = _io.BytesIO()
    with _z.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml",
                   "<w:p><w:r><w:t>veinti</w:t><w:t>cinco</w:t></w:r></w:p>"
                   "<w:p><w:r><w:t>RESUELVE</w:t></w:r></w:p>")
    global DESCARGA, urllib
    class _Falsa:
        def __init__(s_, *a_, **k_): pass
        def read(s_): return b"PK" + buf.getvalue()[2:]
        def __enter__(s_): return s_
        def __exit__(s_, *a_): return False
    _real = urllib.request.urlopen
    urllib.request.urlopen = lambda *a_, **k_: _Falsa()
    try:
        t = contenido("x")
    finally:
        urllib.request.urlopen = _real
    assert t.startswith("veinticinco"), t
    assert resuelve(t).startswith("RESUELVE"), t

    t = limpiar("<br><p> Bogotá </p><br><p>RESUELVE</p><br><p> CASAR la sentencia. </p>")
    assert "Bogotá" in t and "<p>" not in t, t
    assert resuelve(t).startswith("RESUELVE"), resuelve(t)
    assert "CASAR la sentencia." in resuelve(t), resuelve(t)
    # Sin marca de parte resolutiva no se inventa una.
    assert resuelve("Texto sin resolutiva") == ""

    sid, md = ficha({"title": "SL1234-2025 [2020-00111-01].pdf", "doctor": "Dra. Ana Ruiz",
                     "fechaCreacion": "2025-03-04T10:00:00Z", "ano": 2025,
                     "autoSentencia": "SENTENCIA"}, "LABORAL",
                    "Texto.\n\nRESUELVE\n\nCASAR.\n\n"
                    "Este documento fue generado con firma electrónica y código 123")
    assert sid == "co:csj:sl-1234:2025", sid
    assert "ponente: Ana Ruiz" in md and "expediente: 2020-00111-01" in md, md
    assert "firma electrónica" not in md, "el bloque de firma no se limpió"
    assert "## resuelve" in md and "## texto" in md, md
    print("check OK")


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
