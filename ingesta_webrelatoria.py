#!/usr/bin/env python3
"""Fichas del Consejo de Estado con texto, desde la relatoría de la Rama Judicial (CENDOJ).

    python3 ingesta_webrelatoria.py "NULIDAD SIMPLE" --limite 200
    python3 ingesta_webrelatoria.py --check

`jurisprudencia.ramajudicial.gov.co/WebRelatoria` es JSF/PrimeFaces: se replica a mano el
POST parcial (término + corporación CE + ViewState), se pagina la tabla de a 100 y cada
fila ya trae la relatoría (NR, radicado, sustento normativo, norma demandada, fecha,
sección, ponente, actor, demandado, decisión, tema). El PDF íntegro es público en
`FileReferenceServlet?corp=ce&file=<NR>`: de ahí sale la parte resolutiva — la de SAMAI da
403 (cola.md), por eso las 1.415 fichas de SAMAI son solo metadatos. Si el radicado y el
año coinciden, la ficha de CENDOJ reemplaza a la de SAMAI.

El buscador no busca por radicado: se recorre por términos del TEMA, como la Corte Suprema.

Aristas: el sustento normativo -> `cita`; la norma demandada -> `interpreta`. Ninguna
afecta vigencia a propósito: «DECLARA NULIDAD» en la relatoría no dice si la nulidad fue
parcial, y una arista que mata un artículo vivo es peor que una ausente.
"""
import argparse, csv, fcntl, html, http.cookiejar, os, re, sys, time, urllib.parse, urllib.request
from datetime import date

import fitz  # PyMuPDF, ya usado por ingesta_cendoj

from ingesta_relatoria import resuelve
from ingesta_samai import slug

RAIZ = os.path.dirname(os.path.abspath(__file__))
URL = "https://jurisprudencia.ramajudicial.gov.co/WebRelatoria/consulta/index.xhtml"
DOC = "https://jurisprudencia.ramajudicial.gov.co/WebRelatoria/FileReferenceServlet?corp=%s&ext=&file=%s"
NOMBRE = {"CE": "Consejo de Estado", "CSJ": "Corte Suprema de Justicia"}
RE_CAMPO = re.compile(r"<b>([A-ZÁÉÍÓÚÑ ]+?)\s*:\s*</b></font><font[^>]*>(.*?)</font>(?:<br>|</div>)", re.S)
RE_NORMA = re.compile(r"\b(LEY|DECRETO LEY|DECRETO|ACTO LEGISLATIVO)\s+(\d+)\s+DE\s+(\d{4})", re.I)
# Artículo en los dos formatos: «- ARTÍCULO 164 NUMERAL 2» (Consejo de Estado) y «art. 1324 inc. 2» (Corte Suprema).
RE_ART = re.compile(r"(?:ART[ÍI]CULOS?|\bart\.?)\s+(\d+(?:\.\d+)*(?:-\d+)?(?:\s?(?-i:[A-XZ])(?![^\W\d_])(?!\s*\d))?)", re.I)
# Nombres con una sola norma posible. «Código Penal» (Decreto 100/1980 o Ley 599/2000) y «Código de
# Procedimiento Penal» (Ley 600/2000 o 906/2004) NO: dependen de la fecha de los hechos.
NOMBRES = [(r"constituci[óo]n pol[íi]tica", "co:constitucion:1991"),
           (r"c[óo]digo civil", "co:ley:84:1873"),
           (r"c[óo]digo de comercio", "co:decreto:410:1971"),
           (r"c[óo]digo general del proceso", "co:ley:1564:2012"),
           (r"c[óo]digo de procedimiento civil", "co:decreto:1400:1970"),
           (r"c[óo]digo sustantivo del trabajo", "co:decreto-ley:2663:1950"),
           (r"c[óo]digo procesal del trabajo", "co:decreto:2158:1948"),
           (r"c[óo]digo de la infancia y la adolescencia", "co:ley:1098:2006"),
           (r"c[óo]digo de procedimiento administrativo y de lo contencioso", "co:ley:1437:2011"),
           (r"estatuto tributario", "co:decreto:624:1989"),
           (r"c[óo]digo general disciplinario", "co:ley:1952:2019"),
           (r"c[óo]digo disciplinario [úu]nico", "co:ley:734:2002")]
TIPO = {"ley": "ley", "decreto ley": "decreto-ley", "decreto": "decreto", "acto legislativo": "acto-legislativo"}


def abrir(op, req, timeout):
    """El servidor da 502 y cortes cuando se le pide mucho seguido: esperar y reintentar,
    no tumbar la corrida entera por una petición."""
    for intento in range(5):
        try:
            return op.open(req, timeout=timeout).read()
        except Exception as e:
            if intento == 4:
                raise
            print("  … %s; reintento en %ds" % (e, 60 * (intento + 1)), flush=True)
            time.sleep(60 * (intento + 1))


class Sesion:
    def __init__(self, corp="CE"):
        self.corp = corp
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.op.addheaders = [("User-Agent", "Mozilla/5.0")]
        d = abrir(self.op, URL, 90).decode("utf-8", "replace")
        self.vs = re.search(r'name="javax.faces.ViewState"[^>]*value="([^"]+)"', d).group(1)

    def post(self, datos):
        datos.update({"javax.faces.partial.ajax": "true", "resultForm": "resultForm",
                      "javax.faces.ViewState": self.vs})
        r = urllib.request.Request(URL, data=urllib.parse.urlencode(datos).encode(), headers={
            "Faces-Request": "partial/ajax", "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"})
        return abrir(self.op, r, 180).decode("utf-8", "replace")

    def buscar(self, termino):
        r = self.post({"javax.faces.source": "resultForm:j_idt49", "javax.faces.partial.execute": "@all",
                       "javax.faces.partial.render": "resultForm:travResultCorp resultForm:searchResultPanel resultForm:jurisTable",
                       "resultForm:j_idt49": "resultForm:j_idt49", "resultForm:temaInput": termino.upper(),
                       "resultForm:j_idt42": self.corp})
        total = re.search(NOMBRE[self.corp] + r":\s*(\d+)", r)
        return int(total.group(1)) if total else 0, filas(r)

    def pagina(self, primero):
        return filas(self.post({
            "javax.faces.source": "resultForm:jurisTable", "javax.faces.partial.execute": "resultForm:jurisTable",
            "javax.faces.partial.render": "resultForm:jurisTable", "resultForm:jurisTable": "resultForm:jurisTable",
            "resultForm:jurisTable_pagination": "true", "resultForm:jurisTable_first": str(primero),
            "resultForm:jurisTable_rows": "100", "resultForm:jurisTable_encodeFeature": "true"}))

    def texto_pdf(self, nr):
        doc = abrir(self.op, DOC % (self.corp.lower(), nr), 180)
        if doc.startswith(b"%PDF"):
            return "".join(p.get_text() for p in fitz.open(stream=doc, filetype="pdf"))
        # Las viejas vienen en Word (.doc OLE o .docx): `textutil` es de macOS, sin dependencias.
        if doc[:4] in (b"\xd0\xcf\x11\xe0", b"PK\x03\x04"):
            import subprocess, tempfile
            with tempfile.NamedTemporaryFile(suffix=".doc" if doc[0] == 0xd0 else ".docx") as tmp:
                tmp.write(doc)
                tmp.flush()
                return subprocess.run(["textutil", "-convert", "txt", "-stdout", tmp.name],
                                      capture_output=True, check=True).stdout.decode("utf-8", "replace")
        raise RuntimeError("NR %s: la descarga no es PDF ni Word (%d bytes)" % (nr, len(doc)))


def limpio(s):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", s)).split())


def filas(respuesta):
    """Una fila de la tabla -> dict con los campos de la relatoría."""
    salida = []
    for m in re.finditer(r'<tr data-ri="\d+" data-rk="(\d+)".*?<span id="resultForm:jurisTable:\d+:descrip">(.*?)</span>',
                         respuesta, re.S):
        f = {k.strip().lower(): limpio(v) for k, v in RE_CAMPO.findall(html.unescape(m.group(2)))}
        lineas = [limpio(x) for x in re.split(r"<br>", m.group(2))]
        f["nr"] = m.group(1)
        f.setdefault("sala", lineas[0] if lineas else "")   # Corte Suprema: «SALA DE CASACIÓN CIVIL…» sin etiqueta
        f["radicado"] = next((x for x in lineas if re.fullmatch(r"\d{5}-\d{2}-\d{2}-\d{3}-\d{4}-\d{5}-\d{2}", x)), "")
        f["tipo"] = next((x.lower() for x in lineas if x in ("SENTENCIA", "AUTO", "CONCEPTO")), "")
        # TEMA trae el resto de la relatoría, en bloques: descriptores, «Problema jurídico:», la
        # pregunta, «Respuesta al problema jurídico: Si», el extracto y los descriptores del
        # siguiente. Lleva <font> anidados (el resaltado del término), así que no sale con RE_CAMPO.
        t = re.search(r"<b>TEMA\s*:\s*</b></font><font[^>]*>(.*)</font>\s*</div>", m.group(2), re.S)
        f["tema"], f["problemas"] = tema(t.group(1)) if t else ([], [])
        salida.append(f)
    return salida


def tema(crudo):
    """-> (descriptores, [(pregunta, respuesta, extracto)])."""
    t = html.unescape(re.sub(r"<(?!br)[^>]+>", "", re.sub(r"<br\s*/?>", "<br>", crudo)))
    parrafos = [" ".join(x.split()) for x in t.split("<br><br>")]
    parrafos = [x.replace("<br>", " ").strip() for x in parrafos if x.replace("<br>", "").strip()]
    desc, problemas, actual = [], [], None
    for x in parrafos:
        if re.fullmatch(r"Problema jur[íi]dico:?", x):
            actual = ["", "", []]
            problemas.append(actual)
        elif actual is not None and not actual[0]:
            actual[0] = x
        elif actual is not None and x.startswith("Respuesta al problema jur"):
            actual[1] = x.split(":", 1)[1].strip()
        elif not re.search(r"[a-záéíóúñ]", x):      # todo en mayúsculas: descriptores
            desc += [d.strip() for d in x.split(" / ") if d.strip()]
            actual = None
        elif actual is not None:
            actual[2].append(x)
    return list(dict.fromkeys(desc)), [(p, r, "\n\n".join(e)) for p, r, e in problemas if p]


def _arts(base):
    """Artículos de la norma cargada; None si no está cargada. Una ley puede estar cargada como
    estatutaria u orgánica (build.py ALIAS)."""
    tipos = [base] + [base.replace(":ley:", ":%s:" % t, 1) for t in ("ley-estatutaria", "ley-organica")] if ":ley:" in base else [base]
    for b in tipos:
        try:
            with open(os.path.join(RAIZ, "normativa", b.replace(":", "-") + ".md"), encoding="utf-8") as fh:
                return {m.group(1).lower() for m in map(re.compile(r"## art:(\S+)").match, fh) if m}
        except FileNotFoundError:
            pass
    return None


def normas(campo):
    """«LEY 1437 DE 2011 - ARTÍCULO 164 NUMERAL 2 / Código Civil art. 1973» -> IDs. Lo que no se
    reconoce se omite: una arista a la norma equivocada es peor que una ausente."""
    ids = []
    for trozo in campo.split("/"):
        m = RE_NORMA.search(trozo)
        base = ("co:%s:%s:%s" % (TIPO[" ".join(m.group(1).lower().split())], m.group(2), m.group(3)) if m else
                next((i for n, i in NOMBRES if re.match(r"\s*" + n, trozo, re.I)), None))
        if not base:
            continue
        a = RE_ART.search(trozo[m.end():] if m else trozo)
        art = re.sub(r"\s", "", a.group(1)).lower() if a else ""
        # «ARTÍCULO 155.5» es el art. 155, numeral 5: la numeración decimal real (DUR) tiene 3+ niveles.
        if art.count(".") == 1:
            art = art.split(".")[0]
        # La relatoría a veces cita un artículo que la norma no tiene (Ley 99/1993 art. 150): la arista
        # queda en la norma, no en un artículo inexistente (build.py lo avisa como extracción perdida).
        cargados = _arts(base) if art else None
        ids.append(base + (":art:" + art if art and (cargados is None or art in cargados) else ""))
    return list(dict.fromkeys(ids))


def decision(campo):
    c = campo.upper()
    if "NULIDAD" in c and ("DECLARA" in c or "ANULA" in c) and "NIEGA" not in c:
        return "nulidad"
    if "NIEGA" in c and "NULIDAD" in c:
        return "niega-nulidad"
    return ""


def ficha(f, texto):
    fecha = "-".join(reversed(f.get("fecha", "").split("/"))) if re.fullmatch(r"\d\d/\d\d/\d{4}", f.get("fecha", "")) else ""
    if not (f["radicado"] and fecha):
        return None, None
    sid = "co:ce:%s:%s" % (f["radicado"], fecha[:4])
    sala = f.get("seccion", "") or f.get("sección", "")
    dec = decision(f.get("decision", ""))
    fm = ["---", "id: " + sid, "tipo: " + (f["tipo"] if f["tipo"] in ("auto", "concepto") else "sentencia"),
          "corporacion: consejo-estado", "sala: " + (slug(sala) or "sin-dato"),
          "titulo: Radicado %s — Consejo de Estado, %s" % (f["radicado"], sala.title() or "sin sección"),
          "ponente: " + f.get("ponente", ""), "fecha: " + fecha, "expediente: " + f["radicado"],
          "ramas: [contencioso-administrativo, administrativo]"]
    if dec:
        fm.append("decision: " + dec)
    fm += ["afectaciones: no-aplica", "fuente: " + DOC % ("ce", f["nr"]), "verificado: " + date.today().isoformat(), "---", ""]
    fm += ["## ficha", "", "NR (relatoría CENDOJ): " + f["nr"]]
    for k, etiqueta in (("actor", "Actor"), ("demandado", "Demandado"), ("decision", "Decisión (relatoría)"),
                        ("norma demandada", "Norma demandada"), ("sustento normativo", "Sustento normativo")):
        if f.get(k):
            fm.append("%s: %s" % (etiqueta, f[k]))
    fm.append("")
    res = resuelve(" ".join(texto.split()))
    if not res:   # dentro de `## ficha`: export.py la advierte como SOLO METADATOS
        fm += ["**No se pudo extraer la parte resolutiva** del texto íntegro: esta ficha no dice qué "
               "se decidió. Consultar `fuente:`.", ""]
    if f.get("tema"):
        fm += ["## descriptores", "", "\n".join("- " + d for d in f["tema"]), ""]
    if f.get("problemas"):
        # Pregunta, respuesta y extracto son de la relatoría del Consejo de Estado, no redactados aquí.
        fm += ["## problema-juridico", ""]
        for p, r, e in f["problemas"]:
            fm += [p, ""] + (["Respuesta de la relatoría: " + r, ""] if r else []) + (
                ["Extracto (relatoría):", "", "\n".join("> " + l if l else ">" for l in e.split("\n")), ""] if e else [])
    if res:
        fm += ["## resuelve", "", res, ""]
    return sid, "\n".join(fm)


def guardar_aristas(sid, filas_nuevas):
    """Idempotente: reescribe las aristas CENDOJ que salen de esta providencia."""
    ruta = os.path.join(RAIZ, "relaciones.csv")
    with open(os.path.join(RAIZ, ".relaciones.lock"), "w") as candado:
        fcntl.flock(candado, fcntl.LOCK_EX)
        with open(ruta, encoding="utf-8") as fh:
            previas = [r for r in csv.reader(fh) if r and r[0] != "origen"
                       and not (r[0] == sid and r[4].startswith("CENDOJ:"))]
        with open(ruta, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["origen", "tipo", "destino", "fecha", "nota", "fuente"])
            w.writerows(previas + filas_nuevas)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("termino")
    p.add_argument("--corp", default="CE", choices=["CE", "CSJ"])
    p.add_argument("--limite", type=int, default=100)
    p.add_argument("--pausa", type=float, default=1.0)
    a = p.parse_args()

    s = Sesion(a.corp)
    total, fs = s.buscar(a.termino)
    print("«%s»: %d providencias (%s)" % (a.termino, total, NOMBRE[a.corp]))
    cuenta = {"escritas": 0, "enlazadas": 0, "saltadas": 0, "fallidas": 0}
    procesar = procesar_ce if a.corp == "CE" else procesar_csj
    primero = 0
    while fs and sum(cuenta.values()) < a.limite:
        for f in fs:
            if sum(cuenta.values()) >= a.limite:
                break
            try:
                r = procesar(s, f)
            except Exception as e:
                print("  [!] NR %s: %s" % (f["nr"], e))
                r = "fallidas"
            cuenta[r] += 1
            if r in ("escritas", "enlazadas"):
                time.sleep(a.pausa)
        primero += 100
        if primero >= total:
            break
        fs = s.pagina(primero)
    print(", ".join("%d %s" % (v, k) for k, v in cuenta.items()))


def procesar_ce(s, f):
    if not (f.get("radicado") and re.fullmatch(r"\d\d/\d\d/\d{4}", f.get("fecha", ""))):
        return "saltadas"
    destino = os.path.join(RAIZ, "jurisprudencia", "co-ce-%s-%s.md" % (f["radicado"], f["fecha"][-4:]))
    if os.path.exists(destino) and "## resuelve" in open(destino, encoding="utf-8").read():
        return "saltadas"
    sid, md = ficha(f, s.texto_pdf(f["nr"]))
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write(md)
    fecha, url = re.search(r"^fecha: (\S+)", md, re.M).group(1), DOC % ("ce", f["nr"])
    guardar_aristas(sid, [(sid, "cita", d, fecha, "CENDOJ: sustento normativo", url)
                          for d in normas(f.get("sustento normativo", ""))]
                    + [(sid, "interpreta", d, fecha, "CENDOJ: norma demandada; decisión: %s" % f.get("decision", ""), url)
                       for d in normas(f.get("norma demandada", ""))])
    return "escritas"


def procesar_csj(s, f):
    """La Corte Suprema: la ficha sale igual que en ingesta_cendoj (texto íntegro); si ya existe
    (portal de la Corte), solo se le agregan las aristas de la FUENTE FORMAL de la relatoría."""
    import ingesta_cendoj
    num = f.get("número de providencia", "")
    proceso = re.sub(r"^[A-Z]+\s+", "", f.get("número de proceso", ""))
    sid, _ = ingesta_cendoj.identificar("%s [%s]" % (num, proceso))
    fecha = "-".join(reversed(f.get("fecha", "").split("/")))
    if not sid or not re.fullmatch(r"\d{4}-\d\d-\d\d", fecha):
        return "saltadas"
    destino = os.path.join(RAIZ, "jurisprudencia", sid.replace(":", "-") + ".md")
    url = DOC % ("csj", f["nr"])
    r = "enlazadas"
    if not os.path.exists(destino):
        sala = next((x for x in ("CIVIL", "LABORAL", "PENAL") if x in f.get("sala", "")), "")
        if not sala:
            return "saltadas"
        res = {"title": "%s [%s]" % (num, proceso), "ano": sid[-4:], "doctor": f.get("ponente", "").title(),
               "autoSentencia": "AUTO" if "AUTO" in f.get("tipo de providencia", "") else "SENTENCIA"}
        sid, md = ingesta_cendoj.ficha(res, sala, s.texto_pdf(f["nr"]))
        md = md.replace("fuente: " + ingesta_cendoj.PORTAL, "fuente: " + url)
        with open(destino, "w", encoding="utf-8") as fh:
            fh.write(md)
        r = "escritas"
    guardar_aristas(sid, [(sid, "cita", d, fecha, "CENDOJ: fuente formal", url)
                          for d in normas(f.get("fuente formal", ""))])
    return r


def check():
    global _arts
    real, _arts = _arts, lambda base: None  # las aserciones de abajo no dependen de lo cargado
    fila = ('<tr data-ri="0" data-rk="2416998" class="x"><td><span id="resultForm:jurisTable:0:descrip">'
            '<div><font><b>CONSEJO DE ESTADO</b></font><br><font color="7D3B05"><b>NR: </b></font><font>2416998</font><br>'
            '<font>54001-23-33-000-2019-00014-01</font><br><font></font><br><font>SENTENCIA</font><br>'
            '<font color="7D3B05"><b>SUSTENTO NORMATIVO : </b></font><font>LEY 1437 DE 2011 -  ARTÍCULO 164 NUMERAL 2 '
            'LITERAL I / CONSTITUCIÓN POLÍTICA - ARTÍCULO 90 / DECRETO 1082 DE 2015 - ARTÍCULO 2.2.1.1.1</font><br>'
            '<font color="7D3B05"><b>FECHA : </b></font><font>24/08/2026</font><br>'
            '<font color="7D3B05"><b>SECCION : </b></font><font>SECCION TERCERA SUBSECCIÓN B</font><br>'
            '<font color="7D3B05"><b>DECISION : </b></font><font>DECLARA NULIDAD</font><br>'
            '<font color="7D3B05"><b>TEMA : </b></font><font>DAÑO / <font style="x">MÉDICA</font> A SOLDADO'
            '<br><br>Problema jurídico:<br><br>¿Procede? <br><br>Respuesta al problema jurídico: Si<br><br>[L]a regla es X.'
            '<br><br>OTRO TEMA / MÁS<br><br>Problema jurídico:<br><br></font></div></span></td></tr>')
    f = filas(fila)[0]
    assert f["nr"] == "2416998" and f["radicado"] == "54001-23-33-000-2019-00014-01" and f["tipo"] == "sentencia", f
    assert f["fecha"] == "24/08/2026" and f["tema"] == ["DAÑO", "MÉDICA A SOLDADO", "OTRO TEMA", "MÁS"], f
    assert f["problemas"] == [("¿Procede?", "Si", "[L]a regla es X.")], f["problemas"]
    assert normas(f["sustento normativo"]) == ["co:ley:1437:2011:art:164", "co:constitucion:1991:art:90",
                                                "co:decreto:1082:2015:art:2.2.1.1.1"], normas(f["sustento normativo"])
    assert normas("Código Civil art. 1973 / Código de Comercio art. 1324 inc. 2 / Ley 820 de 2003 art. 20 / "
                  "Ley 105 de 1931 / Código Penal art. 239 / Estatuto Tributario art. 555-2 / "
                  "Constitución Política de Colombia art. 333 / Código General del Proceso art. 28 núm. 1 / "
                  "Ley 1437 de 2011 art. 10 A / LEY 1437 DE 2011 - ARTÍCULO 155.5") == [
        "co:ley:84:1873:art:1973", "co:decreto:410:1971:art:1324", "co:ley:820:2003:art:20", "co:ley:105:1931",
        "co:decreto:624:1989:art:555-2", "co:constitucion:1991:art:333", "co:ley:1564:2012:art:28",
        "co:ley:1437:2011:art:10a", "co:ley:1437:2011:art:155"], normas("x")
    assert normas("LEY 100 DE 1993 - ARTÍCULOS 215 Y 216 / LEY 2080 DE 2021 - ARTÍCULO 185 A 190 / "
                  "LEY 1437 DE 2011 ARTÍCULO 136 A") == [
        "co:ley:100:1993:art:215", "co:ley:2080:2021:art:185", "co:ley:1437:2011:art:136a"], normas("x")
    _arts = lambda base: {"20"}  # norma cargada con solo el art. 20: el art. 150 citado no existe
    assert normas("LEY 99 DE 1993 - ARTÍCULO 150 / LEY 99 DE 1993 - ARTÍCULO 20") == [
        "co:ley:99:1993", "co:ley:99:1993:art:20"], normas("x")
    _arts = real
    sid, md = ficha(f, "…administrando justicia en nombre de la República FALLA PRIMERO: NIÉGASE. Cópiese")
    assert sid == "co:ce:54001-23-33-000-2019-00014-01:2026" and "decision: nulidad" in md, md
    assert "## resuelve\n\nPRIMERO: NIÉGASE" in md, md
    print("check OK")


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
