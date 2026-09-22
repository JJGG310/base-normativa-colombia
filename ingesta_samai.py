#!/usr/bin/env python3
"""Fichas de providencias del Consejo de Estado desde SAMAI (Mi Relatoría).

    python3 ingesta_samai.py "responsabilidad medica" --limite 200
    python3 ingesta_samai.py --check

SAMAI es un ASP.NET WebForms con ScriptManager (postbacks parciales de UpdatePanel,
no una API REST). No hace falta navegador: se replica el postback a mano —
__VIEWSTATE/__EVENTVALIDATION se extraen del HTML y se reenvían en cada petición,
la respuesta viene en el formato «delta» de Microsoft Ajax (bloques
`longitud|tipo|id|contenido|`, la longitud en BYTES utf-8, no en caracteres).

El texto completo NO se puede bajar: `/api/DescargarProvidenciaPublica/...` en
samaicore.consejodeestado.gov.co devuelve 403 pase lo que pase (probado con
distintos `modo`, con el token como Bearer, como query `tokendoc`) pese a que su
propio swagger (samaicore.../swagger/v1/swagger.json) lo marca sin `security`. Es
un bloqueo de infraestructura (Azure), no de la aplicación — investigado
2026-09-22, no resuelto.

Lo que SÍ trae cada tarjeta de resultado, sin una petición aparte por providencia:
radicado, interno, fecha del proceso, clase del proceso, ponente, sala, actor,
demandado, fecha de la providencia, tipo (sentencia/auto) y el hash del documento.
Eso alcanza para una ficha mecánica igual de honesta que la de la Corte Suprema
antes de tener texto — la vigencia y el contenido siguen en `fuente:`.
"""
import argparse, html, os, re, sys, time, urllib.parse, urllib.request
from datetime import date

RAIZ = os.path.dirname(os.path.abspath(__file__))
BASE = "https://samai.consejodeestado.gov.co"
BUSCADOR = BASE + "/TitulacionRelatoria/BuscadorProvidenciasTituladas.aspx"
UA = "Mozilla/5.0"
CORPORACION = "1100103"  # Consejo de Estado, dentro del selector de SAMAI

MESES = dict(zip("enero febrero marzo abril mayo junio julio agosto septiembre "
                 "octubre noviembre diciembre".split(), range(1, 13)))
RE_FECHA_LARGA = re.compile(
    r"(\d{1,2})\s+de\s+(%s)\s+de\s+(\d{4})" % "|".join(MESES), re.I)

RE_TOKEN = re.compile(r'id="(__VIEWSTATE|__VIEWSTATEGENERATOR|__EVENTVALIDATION)" value="([^"]*)"')


def parse_delta(data: bytes):
    """Formato Microsoft Ajax UpdatePanel: bloques `longitud|tipo|id|contenido|`.
    La longitud está en bytes UTF-8 — indexar por caracteres desalinea todo lo que
    viene después del primer acento."""
    partes, i, n = {}, 0, len(data)
    while i < n:
        j = data.find(b"|", i)
        if j == -1:
            break
        try:
            longitud = int(data[i:j])
        except ValueError:
            i = j + 1
            continue
        resto = data[j + 1:]
        tipo_fin = resto.find(b"|")
        tipo = resto[:tipo_fin].decode()
        idc_resto = resto[tipo_fin + 1:]
        idc_fin = idc_resto.find(b"|")
        idc = idc_resto[:idc_fin].decode()
        inicio = j + 1 + tipo_fin + 1 + idc_fin + 1
        partes[(tipo, idc)] = data[inicio:inicio + longitud]
        i = inicio + longitud + 1
    return partes


def _cookies_de(r):
    return [v.split(";")[0] for k, v in r.getheaders() if k.lower() == "set-cookie"]


def sesion():
    """GET a la portada para que emita ASP.NET_SessionId — el buscador por sí solo
    no lo emite, y sin él el postback falla con «Validation of viewstate MAC
    failed» (probado 2026-09-22). Luego GET al buscador ya con esa cookie."""
    req = urllib.request.Request(BASE + "/", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        cookies = "; ".join(dict.fromkeys(_cookies_de(r)))  # dedup preservando orden

    req2 = urllib.request.Request(BUSCADOR, headers={"User-Agent": UA, "Cookie": cookies})
    with urllib.request.urlopen(req2, timeout=30) as r:
        cuerpo = r.read().decode("utf-8", "replace")
    tokens = {m.group(1): m.group(2) for m in RE_TOKEN.finditer(cuerpo)}
    return cookies, tokens


def postback(cookies, tokens, event_target, campos):
    datos = dict(campos)
    datos.update({
        "ctl00$ScriptManager1": "ctl00$MainContent$PanelUpdate|" + event_target,
        "__EVENTTARGET": event_target,
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": tokens["__VIEWSTATE"],
        "__VIEWSTATEGENERATOR": tokens["__VIEWSTATEGENERATOR"],
        "__EVENTVALIDATION": tokens["__EVENTVALIDATION"],
        "__ASYNCPOST": "true",
    })
    cuerpo = urllib.parse.urlencode(datos).encode()
    req = urllib.request.Request(BUSCADOR, data=cuerpo, headers={
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-MicrosoftAjax": "Delta=true",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": cookies,
        "Referer": BUSCADOR,
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def actualizar_tokens(tokens, delta):
    for campo in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION"):
        v = delta.get(("hiddenField", campo))
        if v:
            tokens[campo] = v.decode("utf-8", "replace")


def panel(delta):
    return delta.get(("updatePanel", "MainContent_PanelUpdate"), b"").decode("utf-8", "replace")


def campos_busqueda(texto):
    return {
        "ctl00$MainContent$CorporacionesTitulanDataList": CORPORACION,
        "ctl00$MainContent$BusquedaRapidaTextBox": texto,
    }


def fecha_iso(texto_largo):
    m = RE_FECHA_LARGA.search(texto_largo or "")
    if not m:
        return ""
    return "%04d-%02d-%02d" % (int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1)))


def formatear_radicado(num23):
    """76001233301020140132301 (23 dígitos) -> 76001-23-33-010-2014-01323-01."""
    if not re.fullmatch(r"\d{23}", num23):
        return num23
    grupos = (5, 2, 2, 3, 4, 5, 2)
    partes, i = [], 0
    for g in grupos:
        partes.append(num23[i:i + g])
        i += g
    return "-".join(partes)


RE_TARJETA = re.compile(
    r'id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_HypRadicado_(\d+)"[^>]*>([^<]*)</a>')

CAMPOS_TARJETA = {
    "interno": "LblInterno", "fecha_proceso": "LblFECHAPROC",
    "clase_proceso": "LblClaseProceso", "ponente": "LblPonente",
    "sala": "LbNombreSalaDecision", "actor": "LblActor", "demandado": "LblDemandado",
    "fecha_providencia": "Label1", "tipo": "LblTIPOPROVIDENCIA",
    "hash": "Lblhash",
}


def extraer_tarjetas(panel_html):
    doc = html.unescape(panel_html)
    tarjetas = []
    for m in RE_TARJETA.finditer(doc):
        idx = m.group(1)
        t = {"radicado": m.group(2).strip()}
        for clave, sufijo in CAMPOS_TARJETA.items():
            cm = re.search(
                r'id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_%s_%s"[^>]*>([^<]*)'
                % (sufijo, idx), doc)
            t[clave] = cm.group(1).strip() if cm else ""
        tarjetas.append(t)
    return tarjetas


SALA_SLUG = re.compile(r"[^a-z0-9]+")
TILDES = str.maketrans("áéíóúñ", "aeioun")


def slug(texto):
    return SALA_SLUG.sub("-", texto.lower().translate(TILDES)).strip("-")


def ficha(t):
    fecha_prov = fecha_iso(t["fecha_providencia"]) or fecha_iso(t["fecha_proceso"])
    anio = fecha_prov[:4] if fecha_prov else t["radicado"][17:21]
    radicado_fmt = formatear_radicado(t["radicado"])
    sid = "co:ce:%s:%s" % (radicado_fmt, anio)
    certificado = t["hash"].replace("Certificado:", "").strip()
    fuente = BASE + "/vistas/casos/list_procesos.aspx?guid=" + t["radicado"] + CORPORACION

    fm = ["---", "id: " + sid, "tipo: " + ("auto" if "auto" in t["tipo"].lower() else "sentencia"),
          "corporacion: consejo-estado", "sala: " + slug(t["sala"]),
          "titulo: Radicado %s — Consejo de Estado, %s" % (radicado_fmt, t["sala"]),
          "ponente: " + t["ponente"], "fecha: " + fecha_prov,
          "expediente: " + radicado_fmt, "ramas: [contencioso-administrativo, administrativo]",
          "afectaciones: no-aplica", "fuente: " + fuente,
          "verificado: " + date.today().isoformat(), "---", ""]
    fm += ["## ficha", "",
           "Interno: %s" % t["interno"],
           "Clase del proceso: %s" % t["clase_proceso"],
           "Actor: %s" % t["actor"],
           "Demandado: %s" % t["demandado"],
           "Certificado del documento: %s" % certificado, "",
           "**No se pudo bajar el texto íntegro**: el endpoint de descarga de SAMAI "
           "(samaicore.consejodeestado.gov.co) devuelve 403 desde este acceso. Esta "
           "ficha es solo los metadatos que trae el buscador — consultar `fuente:` "
           "para el expediente completo.", ""]
    return sid, "\n".join(fm)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("termino", nargs="?")
    p.add_argument("--limite", type=int, default=100)
    p.add_argument("--paginas", type=int, default=50)
    p.add_argument("--pausa", type=float, default=1.0)
    p.add_argument("--check", action="store_true")
    a = p.parse_args()

    if a.check:
        check()
        print("check OK")
        return
    if not a.termino:
        sys.exit("falta el término de búsqueda")

    destino_dir = os.path.join(RAIZ, "jurisprudencia")
    cookies, tokens = sesion()
    delta = postback(cookies, tokens, "ctl00$MainContent$BusquedaRapidaLinkButton",
                     campos_busqueda(a.termino))
    d = parse_delta(delta)
    actualizar_tokens(tokens, d)

    escritas, vistas = 0, 0
    for pagina in range(a.paginas):
        tarjetas = extraer_tarjetas(panel(d))
        if not tarjetas:
            break
        for t in tarjetas:
            if not t["radicado"]:
                continue
            vistas += 1
            sid, md = ficha(t)
            ruta = os.path.join(destino_dir, sid.replace(":", "-") + ".md")
            if os.path.exists(ruta):
                continue
            with open(ruta, "w", encoding="utf-8") as fh:
                fh.write(md)
            escritas += 1
            print("  %s  %s" % (sid, t["fecha_providencia"]))
            if escritas >= a.limite:
                print("%d fichas escritas, %d vistas" % (escritas, vistas))
                return
        time.sleep(a.pausa)
        delta = postback(cookies, tokens,
                         "ctl00$MainContent$ResultadoBusqueda1$PaginaSiguienteLinkButton",
                         campos_busqueda(a.termino))
        d = parse_delta(delta)
        actualizar_tokens(tokens, d)

    print("%d fichas escritas, %d vistas" % (escritas, vistas))


def check():
    assert fecha_iso("viernes, 26 de septiembre de 2025") == "2025-09-26"
    assert formatear_radicado("76001233301020140132301") == "76001-23-33-010-2014-01323-01"
    assert slug("Sección Tercera (Subsección A)") == "seccion-tercera-subseccion-a"

    panel_html = '''
    <a id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_HypRadicado_0" href="x">76001233301020140132301</a>
    <span id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_LblInterno_0">72358</span>
    <span id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_LblFECHAPROC_0">martes, 4 de febrero de 2025</span>
    <span id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_LblClaseProceso_0">LEY 1437 REPARACION DIRECTA</span>
    <span id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_LblPonente_0">FERNANDO PARDO</span>
    <span id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_LbNombreSalaDecision_0">Sección Tercera (Subsección A)</span>
    <span id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_LblActor_0">CARLOS SALGAR</span>
    <span id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_LblDemandado_0">EPS SELVA SALUD</span>
    <span id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_Label1_0">viernes, 26 de septiembre de 2025</span>
    <span id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_LblTIPOPROVIDENCIA_0">Sentencia</span>
    <span id="MainContent_ResultadoBusqueda1_TitulacionesRepeater_Lblhash_0"> Certificado: CCA57F0C</span>
    '''
    tarjetas = extraer_tarjetas(panel_html)
    assert len(tarjetas) == 1, tarjetas
    t = tarjetas[0]
    assert t["radicado"] == "76001233301020140132301"
    assert t["ponente"] == "FERNANDO PARDO"
    sid, md = ficha(t)
    assert sid == "co:ce:76001-23-33-010-2014-01323-01:2025", sid
    assert "corporacion: consejo-estado" in md
    assert "Actor: CARLOS SALGAR" in md

    # parse_delta: la longitud es en bytes UTF-8, no en caracteres — "área" pesa
    # más bytes que letras y desalinearía todo lo que viene después sin esto.
    bloque1 = "área".encode("utf-8")
    payload = b"%d|hiddenField|__VIEWSTATE|%s|%d|hiddenField|__EVENTVALIDATION|ok|" % (
        len(bloque1), bloque1, len(b"ok"))
    d = parse_delta(payload)
    assert d[("hiddenField", "__VIEWSTATE")] == bloque1
    assert d[("hiddenField", "__EVENTVALIDATION")] == b"ok"


if __name__ == "__main__":
    main()
