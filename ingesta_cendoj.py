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
su texto es justo lo que este proyecto no puede permitirse. Se baja el original por
`downloadFile` y se extrae de `word/document.xml` (los «.doc» de la Corte son OOXML con
extensión vieja). Lo que la Corte solo publica en PDF (laboral 2023, ni una en .docx) se
extrae con PyMuPDF; un PDF escaneado o con páginas sin capa de texto no se carga.
Las 12.950 «providencias» de laboral 2023 son resultados del índice: cada una sale 2-4
veces (carpeta PERMANENTE/DESCONGESTION, «Dr.X»/«Dr. X», .pdf/.doc), y varias rutas están
muertas (404): por eso una descarga fallida deja probar la siguiente copia.

La sala PENAL: el buscador indexa una ruta con la carpeta del magistrado
(`PENAL/<año>/Dr. X/Sentencia/<archivo>`) que no existe en el storage real — el archivo
vive en `PENAL/<año>/<archivo>`, sin esa carpeta intermedia. `downloadFile` con la ruta
tal cual devuelve 404; con la ruta recortada, 200. Confirmado 2026-09-19 contra 5
providencias de 2022 a 2025.
"""
import argparse, html, io, json, os, re, sys, time, urllib.error, urllib.request, zipfile
from datetime import date

import fitz  # PyMuPDF — solo para las providencias que la Corte no publica en .docx

from ingesta_relatoria import fecha_en

RAIZ = os.path.dirname(os.path.abspath(__file__))
API = "https://consultaprovidenciasbk.cortesuprema.gov.co/api"
CABECERAS = {"Content-Type": "application/json", "Accept": "application/json",
             "User-Agent": "Mozilla/5.0"}
PORTAL = "https://consultaprovidencias.cortesuprema.gov.co/"
DESCARGA = "https://consultaprovidenciasbk.cortesuprema.gov.co/downloadFile"

# Términos amplios: sirven de rastrillo, no de criterio. Cualquier providencia de la
# sala cae en alguno de ellos.
TERMINOS = ["recurso", "sentencia", "demanda", "proceso", "derecho", "prueba"]
# Los «.doc» de la Corte son OOXML (zip) con extensión vieja: contenido() los lee por su firma.
LEGIBLES = (".docx", ".doc", ".pdf")
RAMAS = {"CIVIL": "civil, comercial, procesal", "LABORAL": "laboral, seguridad-social",
         "PENAL": "penal, procesal"}
RE_TITULO = re.compile(r"^([A-Z]{2,4})(\d+)\s*-\s*(\d{4})")
# Civil y laboral escriben el radicado entre corchetes; penal entre paréntesis.
RE_RADICADO = re.compile(r"[\[(]([0-9\-]+)[\])]")
# El fallo cierra con el bloque de firma electrónica: no es parte de la decisión.
RE_FIRMA = re.compile(r"Este documento fue generado con firma electrónica.*$", re.S | re.I)
# Los PDF de la Sala Laboral repiten en cada página el pie «SCLAJPT-10 V.00» (con
# variantes de OCR: SCLAPT, SCLA3PT, SCLAJ PT- 10, SCLAJPT-IO V.OO) seguido del número de página («17», «I 8»),
# y el encabezado «Radicación n.° 70555». Metidos en el texto parten las frases.
RE_PIE = re.compile(r"(?m)^[ \t]*(?:L\s+)?SCLA[^\n]{0,10}?[\dIO.]{1,4}\s*[Vv][ .,]*[\dOoD]{1,3}[ \t]*(?:\n|$)"
                    r"(?:[ \t]*[\dIl]{1,3}(?:[ \t]+[\dIl]{1,2})?[ \t]*(?:\n|$))?")
RE_RAD = re.compile(r"(?m)^[ \t]*Radicaci[óo]n\s*n\s*[.°º ]*\s*[\d\-]+[ \t]*(?:\n|$)")
# El ponente encabeza la providencia: «LUIS ANTONIO HERNÁNDEZ BARBOSA\nMagistrado ponente».
RE_PONENTE = re.compile(r"(?m)^[ \t]*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ.]+(?:[ \t]+[A-ZÁÉÍÓÚÑ.]+){1,5})[ \t]*\n"
                        r"\s*Magistrad[oa] [Pp]onente")


def sin_cabeceras(texto):
    """Quita pie y encabezado de página; la primera «Radicación» es la del
    encabezado de la providencia y se queda. Sin pie SCLA no se toca nada: en los
    .docx civiles «Radicación n.° …» encabeza de verdad cada salvamento y aclaración."""
    t = RE_PIE.sub("", texto)
    if t == texto:
        return texto
    m = RE_RAD.search(t)
    return t[:m.end()] + RE_RAD.sub("", t[m.end():]) if m else t


def decision_de(parte):
    """`casa` / `no-casa` solo cuando la resolutiva lo dice sin ambigüedad. Otras
    decisiones (revisión infundada, confirma, inadmite…) no están en el vocabulario de
    esquema.md §4 y quedan vacías; si dice ambas cosas, también."""
    # «CASA … NO CASA en lo demás» es casación parcial: casa.
    parte = re.sub(r"(?i)\bno\s+casa(?:r)?\s+en\s+(?:todo\s+)?lo\s+dem[áa]s", "", parte[:1500])
    no = re.search(r"(?i)\bno\s+casa(?:r)?\b", parte)
    # «CASAR OFICIOSA Y PARCIALMENTE el fallo», «Se casa parcialmente y de oficio el fallo».
    si = re.search(r"(?i)\bcasa(?:r)?(?:\s*,|\s+(?:\w+mente|oficios\w+|de\s+oficio|parcial|la|el|los|las|para)\b)",
                   re.sub(r"(?i)\bno\s+casa(?:r)?\b", "", parte))
    return "" if bool(no) == bool(si) else ("no-casa" if no else "casa")


def decision_texto(cuerpo, parte):
    """Si la resolutiva que quedó es la de instancia («RESUELVE: MODIFICAR el fallo…»),
    la de casación está en la fórmula «…por autoridad de la ley, CASA…» que la precede."""
    d = decision_de(parte)
    if not d:
        formulas = list(re.finditer(r"(?i)autoridad\s+de\s+la\s+ley\s*,?", cuerpo))
        if formulas:
            d = decision_de(cuerpo[formulas[-1].end():formulas[-1].end() + 600])
    return d


def abrir(req, timeout):
    """urlopen con un reintento a los 15 s si el servidor da 5xx: el de la Corte suelta
    502 sueltos, y uno en la búsqueda abortaba el rastrillo del término entero."""
    for intento in (0, 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code < 500 or intento:
                raise
            time.sleep(15)


def consultar(query):
    req = urllib.request.Request(API, data=json.dumps({"query": query}).encode(),
                                 headers=CABECERAS)
    d = json.loads(abrir(req, 90).decode("utf-8"))
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


def ruta_real(doc_path, sala):
    """PENAL: el buscador mete una carpeta de magistrado que no existe en el storage
    real; el archivo vive en PENAL/<año>/<archivo>, sin ella."""
    if sala != "PENAL":
        return doc_path
    m = re.match(r"(/var/www/html/Index/PENAL/\d{4}/)", doc_path)
    return m.group(1) + doc_path.rsplit("/", 1)[-1] if m else doc_path


def contenido(doc_path):
    """Texto del original. El API solo da vistas previas con elisiones."""
    req = urllib.request.Request(DESCARGA, data=json.dumps({"path": doc_path}).encode(),
                                 headers=CABECERAS)
    crudo = abrir(req, 120)
    if crudo[:2] == b"PK":
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
    if crudo[:4] == b"%PDF":
        doc = fitz.open(stream=crudo, filetype="pdf")
        paginas = [p.get_text() for p in doc]
        t = sin_cabeceras("\n".join(paginas))
        t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip()
        # Escaneado sin capa de texto, o con capa solo en unas páginas (p. ej. un salvamento
        # anexado como imagen): no se rellena ni se hace OCR y la ficha no se carga. Una
        # página de solo firmas trae ~40 caracteres (pie y radicado): unas pocas son normales.
        vacias = sum(len(x.strip()) < 50 for x in paginas)
        return t if vacias <= 0.15 * len(doc) else ""
    return ""


def alterna(path):
    """El índice lista la carpeta del magistrado como «Dr.X» y como «Dr. X», y de cada par
    solo una vive (laboral 2023: la de PERMANENTE sin espacio, la .doc de DESCONGESTIÓN sin
    espacio…): ante un 404 se prueba la otra."""
    if re.search(r"/Dra?\. ", path):
        return re.sub(r"/(Dra?\.) ", r"/\1", path)
    return re.sub(r"/(Dra?\.)(?=\S)", r"/\1 ", path)


def descargar(path, pausa):
    try:
        return contenido(path)
    except urllib.error.HTTPError as e:
        if e.code != 404 or alterna(path) == path:
            raise
        time.sleep(pausa)
        return contenido(alterna(path))


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
    """La parte resolutiva: desde el último RESUELVE/FALLA/DECISIÓN hasta el final.

    "DECISIÓN" (a veces numerada "XI. DECISIÓN") es el encabezado que usa la mayoría
    de la Sala Laboral — sin este patrón, el 54% de las providencias de la Corte
    Suprema ya cargadas se quedaban sin `## resuelve` pese a tenerlo en el texto.
    """
    marcas = list(re.finditer(
        r"(?m)^\s*(?:[IVXLCDM]+\.\s*)?(RESUELVE|FALLA|SE RESUELVE|DECIDE|DECISI[ÓO]N)\s*:?\s*$",
        texto))
    return texto[marcas[-1].start():].strip() if marcas else ""


def ficha(res, sala, texto):
    sid, radicado = identificar(res["title"])
    cuerpo = RE_FIRMA.sub("", texto).strip()
    parte = resuelve(cuerpo)
    # La fecha sale del encabezado del texto, no de `fechaCreacion` del API: esa es la
    # de publicación en el portal y no coincidía en 1.942 de 2.322 providencias.
    fecha = fecha_en(cuerpo[:8000], sid.rsplit(":", 1)[-1])
    ponente = re.sub(r"^Dr[a]?\.\s*", "", (res.get("doctor") or "").strip())
    if not ponente:
        m = RE_PONENTE.search(cuerpo[:3000])
        ponente = " ".join(m.group(1).split()).title() if m else ""
    fm = ["---", "id: " + sid, "tipo: " + ("auto" if res.get("autoSentencia") == "AUTO"
                                           else "sentencia"),
          "corporacion: corte-suprema", "sala: " + sala.lower(),
          "titulo: %s de %s — Corte Suprema, Sala de Casación %s"
          % (sid.split(":")[2].upper().replace("-", " "), res.get("ano", ""), sala.title()),
          "ponente: " + ponente, "fecha: " + fecha, "decision: " + decision_texto(cuerpo, parte),
          "expediente: " + radicado, "ramas: [%s]" % RAMAS.get(sala, ""),
          "afectaciones: no-aplica", "fuente: " + PORTAL,
          "verificado: " + date.today().isoformat(), "---", ""]
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
    vistos, escritas, fallos, sin_texto = set(), 0, set(), 0
    for termino in a.terminos.split(","):
        start, secas = 0, 0
        # Corte para no paginar media hora un término que ya no trae nada legible
        # (ni .docx, .doc ni .pdf) — evita quedarse dando vueltas sobre resultados vacíos.
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
                # La misma providencia a veces sale en .pdf Y en .docx (duplicada);
                # nos quedamos con cualquiera de los dos formatos legibles.
                if not res["title"].lower().endswith(LEGIBLES):
                    continue
                sid, _ = identificar(res["title"])
                ruta = os.path.join(destino_dir, sid.replace(":", "-") + ".md")
                if not sid or sid in vistos or os.path.exists(ruta):
                    vistos.add(sid)
                    continue
                vistos.add(sid)
                time.sleep(a.pausa)
                try:
                    texto = descargar(ruta_real(res["id"], a.sala), a.pausa)
                except Exception as e:
                    print("  [!] %s: %s" % (sid, e))
                    fallos.add(sid)
                    # El índice lista rutas muertas («Dr.X» sin espacio, carpeta equivocada)
                    # junto a la viva de la misma providencia: se deja probar la siguiente copia.
                    vistos.discard(sid)
                    continue
                if len(texto) < 500:
                    sin_texto += 1
                    fallos.discard(sid)
                    continue
                _, md = ficha(res, a.sala, texto)
                with open(ruta, "w", encoding="utf-8") as fh:
                    fh.write(md)
                escritas += 1
                fallos.discard(sid)
                print("  %s  %d KB" % (sid, len(md) // 1024))
                if escritas >= a.limite:
                    break
            secas = 0 if any(x["title"].lower().endswith(LEGIBLES) for x in resultados) else secas + 1
            start += len(resultados)
            time.sleep(a.pausa)
    print("%d fichas escritas, %d providencias sin ruta viva, %d sin texto extraíble, %d vistas"
          % (escritas, len(fallos), sin_texto, len(vistos)))


def check():
    assert identificar("SC2428-2024 [2018-03988-00].pdf") == ("co:csj:sc-2428:2024",
                                                              "2018-03988-00")
    assert identificar("AC3200-2024 [2024-00782-00].docx")[0] == "co:csj:ac-3200:2024"
    assert identificar("no es una providencia.pdf") == ("", "")
    assert alterna("/x/LABORAL/2023/Dr.Omar Angel/Sentencias/SL1.pdf") == "/x/LABORAL/2023/Dr. Omar Angel/Sentencias/SL1.pdf"
    assert alterna("/x/2023/Dra. Ana Ruiz/Sentencias/SL1.doc") == "/x/2023/Dra.Ana Ruiz/Sentencias/SL1.doc"
    assert alterna("/x/PENAL/2024/SP1-2024.docx") == "/x/PENAL/2024/SP1-2024.docx", "sin carpeta de magistrado no hay variante"
    assert "SL1-2023.doc".endswith(LEGIBLES) and not "SL1-2023.xls".endswith(LEGIBLES)

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

    # Camino PDF: providencias que la Corte no publica en .docx (sala laboral 2023).
    doc_pdf = fitz.open()
    doc_pdf.new_page().insert_text((72, 72), "RESUELVE CASAR la sentencia recurrida.\n"
                                   + "\n".join("línea %d de la providencia de prueba" % i for i in range(20)))
    pdf_bytes = doc_pdf.tobytes()
    doc_pdf.new_page()  # segunda página sin capa de texto (escaneada): 50 % de páginas vacías
    pdf_escaneado = doc_pdf.tobytes()

    class _FalsaPDF:
        def __init__(s_, *a_, **k_): pass
        def read(s_): return pdf_bytes
        def __enter__(s_): return s_
        def __exit__(s_, *a_): return False
    urllib.request.urlopen = lambda *a_, **k_: _FalsaPDF()
    try:
        t_pdf = contenido("x")
    finally:
        urllib.request.urlopen = _real
    assert "CASAR la sentencia recurrida" in t_pdf, t_pdf
    pdf_bytes = pdf_escaneado
    urllib.request.urlopen = lambda *a_, **k_: _FalsaPDF()
    try:
        assert contenido("x") == "", "PDF con páginas sin texto: no se carga ni se rellena"
    finally:
        urllib.request.urlopen = _real

    # 404 en la carpeta «Dr.X»: se prueba «Dr. X» (y un 404 sin variante no se reintenta).
    _c, llamadas = contenido, []
    def _contenido(p_):
        llamadas.append(p_)
        if "Dr.Omar" in p_:
            raise urllib.error.HTTPError(p_, 404, "x", {}, None)
        return "ok"
    globals()["contenido"] = _contenido
    try:
        assert descargar("/x/Dr.Omar/a.pdf", 0) == "ok" and llamadas == ["/x/Dr.Omar/a.pdf", "/x/Dr. Omar/a.pdf"], llamadas
    finally:
        globals()["contenido"] = _c

    t = limpiar("<br><p> Bogotá </p><br><p>RESUELVE</p><br><p> CASAR la sentencia. </p>")
    assert "Bogotá" in t and "<p>" not in t, t
    assert resuelve(t).startswith("RESUELVE"), resuelve(t)
    assert "CASAR la sentencia." in resuelve(t), resuelve(t)
    # Sin marca de parte resolutiva no se inventa una.
    assert resuelve("Texto sin resolutiva") == ""
    assert resuelve("motiva\nXI. DECISIÓN\nNO CASA la sentencia.").startswith("XI. DECISIÓN")

    penal = "/var/www/html/Index/PENAL/2024/Dr. Gerson Chaverra Castro/Sentencia/SP1900-2024(58712).docx"
    assert ruta_real(penal, "PENAL") == "/var/www/html/Index/PENAL/2024/SP1900-2024(58712).docx"
    civil = "/var/www/html/Index/CIVIL/2024/Dra. X/12.- Diciembre/Sentencias/SC1-2024.docx"
    assert ruta_real(civil, "CIVIL") == civil, "solo PENAL se recorta"

    sid, md = ficha({"title": "SL1234-2025 [2020-00111-01].pdf", "doctor": "Dra. Ana Ruiz",
                     "fechaCreacion": "2025-03-04T10:00:00Z", "ano": 2025,
                     "autoSentencia": "SENTENCIA"}, "LABORAL",
                    "Bogotá, D. C., cuatro (4) de marzo de dos mil veinticinco (2025).\n"
                    "Texto.\n\nRESUELVE\n\nCASAR la sentencia.\n\n"
                    "Este documento fue generado con firma electrónica y código 123")
    assert sid == "co:csj:sl-1234:2025", sid
    assert "ponente: Ana Ruiz" in md and "expediente: 2020-00111-01" in md, md
    assert "firma electrónica" not in md, "el bloque de firma no se limpió"
    assert "## resuelve" in md and "## texto" in md, md
    assert "fecha: 2025-03-04" in md and "decision: casa" in md, md

    pdf = ("SCLA.IPT 10 V O\nANA RUIZ\nMagistrada ponente\nSL1-2023\nRadicación n.° 95988\n"
           "Bogotá, D. C., veinte (20) de septiembre de dos mil\nveintitrés (2023).\n"
           "la reliquidación de las\nSCLA3PT-10 V.00\nI 8\n\nRadicación n.° 95988\nprestaciones")
    t = sin_cabeceras(pdf)
    assert "SCLA" not in t and "I 8" not in t and t.count("Radicación") == 1, t
    assert fecha_en(t, "2023") == "2023-09-20", fecha_en(t, "2023")
    assert fecha_en(t, "2022") == "", "si el año no es el del ID, no hay fecha"
    assert fecha_en("Acta 16\n\nSincelejo, diecisiete (17) de mayo de dos mil veintitrés\n(2023).",
                    "2023") == "2023-05-17", "sesión fuera de Bogotá"
    assert RE_PONENTE.search(t).group(1) == "ANA RUIZ"
    assert decision_de("RESUELVE\nNO CASA la sentencia") == "no-casa"
    assert decision_de("Primero. Casar la sentencia proferida") == "casa"
    assert decision_de("CASA PARCIALMENTE la sentencia") == "casa"
    assert decision_de("NO CASA la sentencia. CASA la otra") == "", "ambas: vacío"
    assert decision_de("Declarar infundado el recurso de revisión") == ""
    assert decision_de("CASA la sentencia en cuanto al trabajo suplementario. NO CASA en lo demás.") == "casa"
    assert decision_de("Segundo. CASAR OFICIOSA Y PARCIALMENTE la sentencia recurrida") == "casa"
    assert decision_de("Se casa parcialmente y de oficio el fallo proferido") == "casa"
    assert decision_de("SEGUNDO: Casar parcialmente, de oficio, el fallo de segunda instancia") == "casa"
    assert decision_de("2°. CASAR PARCIALMENTE DE MANERA OFICIOSA, únicamente a fin de") == "casa"
    assert decision_de("Primero. CASAR, dada la prosperidad de los cargos, la sentencia") == "casa"
    assert decision_de("Casar parcial y oficiosamente la sentencia") == "casa"
    assert decision_de("SEGUNDO. CASA PARCIALMENTE para CONCEDER de oficio el sustituto") == "casa"
    assert decision_texto("administrando justicia … y por autoridad de la ley, CASA PARCIALMENTE la sentencia. "
                          "RESUELVE: MODIFICAR el fallo", "RESUELVE: MODIFICAR el fallo") == "casa"
    print("check OK")


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
