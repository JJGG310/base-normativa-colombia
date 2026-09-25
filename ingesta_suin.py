#!/usr/bin/env python3
"""Extrae normativa de SUIN-Juriscol a partir de sus capturas en archive.org.

    python3 ingesta_suin.py Decretos/1731310 --id co:decreto:982:1996 --tipo decreto \\
        --titulo "Decreto 982 de 1996 - …" --ramas agrario --salida normativa/co-decreto-982-1996.md
    python3 ingesta_suin.py --check

El SUIN actual es un CMS de MinJusticia sin los documentos; las páginas viejas
(`viewDocument.asp?ruta=…` o `?id=…`) siguen en la Wayback Machine. Se toma la captura 200
más reciente: la vigencia que se lee es la de ESA fecha, y por eso `verificado` es la fecha
de la captura, no la de hoy (esquema.md §8, fuente 10).

Cada artículo vive en su `<div id="toggle_N">`. Los bloques de vigencia son listas
`resumenvigencias` desplegables: «Afecta la vigencia de» son aristas salientes (de otra
norma, no se emiten aquí: guardar_relaciones solo reescribe las entrantes); el resto son
entrantes. Una etiqueta que no se reconoce se reporta, no se adivina.
"""
import argparse, html, json, os, re, sys, urllib.request

from ingesta_senado import bajar, guardar_relaciones, TIPO_NORMA

RAIZ = os.path.dirname(os.path.abspath(__file__))
ACCION = {"derogado": "deroga", "modificado": "modifica", "adicionado": "adiciona",
          "subrogado": "subroga", "sustituido": "subroga"}
# «Artículo Séptimo.», «Artículo undécimo.», «Artículo decimotercero.» (Decreto 982/1996).
ORDINAL = dict((w, str(n)) for n, ws in enumerate([
    [], ["primero", "unico"], ["segundo"], ["tercero"], ["cuarto"], ["quinto"], ["sexto"],
    ["septimo", "setimo"], ["octavo"], ["noveno"], ["decimo"], ["undecimo", "decimoprimero"],
    ["duodecimo", "decimosegundo"], ["decimotercero"], ["decimocuarto"], ["decimoquinto"],
    ["decimosexto"], ["decimoseptimo"], ["decimoctavo"], ["decimonoveno"], ["vigesimo"]]) for w in ws)
RE_REF = re.compile(r"(?:Art[íi]culo\s+([\dA-Za-z\-]+)\s+)?(ACTO LEGISLATIVO|DECRETO LEY|DECRETO|LEY)"
                    r"\s+([\d\.]+)\s+de\s+(\d{4})", re.I)
RE_SENT = re.compile(r"Sentencia\s+(C|SU|T)-?\s*(\d+)\s+de\s+(\d{4})", re.I)
RE_BLOQUE = re.compile(r'<p style="font-weight:bold;">(.*?)<span class="toctoggle">.*?'
                       r'<div style="display: none;"[^>]*>(.*?)</div>', re.S)
RE_ITEM = re.compile(r'<li class="referencia"><span>(.*?)</span>\s*(?:<a[^>]*>(.*?)</a>)?', re.S)


def captura(ruta):
    """(url de la captura cruda, AAAA-MM-DD) de la última captura 200 de SUIN."""
    cdx = "https://web.archive.org/cdx/search/cdx?url=www.suin-juriscol.gov.co/viewDocument.asp?%s" \
          "&output=json&filter=statuscode:200" % (("ruta=" + ruta) if "/" in ruta else ("id=" + ruta))
    with urllib.request.urlopen(cdx, timeout=120) as r:
        filas = json.load(r)[1:]
    if not filas:
        sys.exit("archive.org no tiene capturas 200 de " + ruta)
    ts, original = filas[-1][1], filas[-1][2]
    return "https://web.archive.org/web/%sid_/%s" % (ts, original), "%s-%s-%s" % (ts[:4], ts[4:6], ts[6:8])


def texto(frag):
    frag = re.sub(r"<br\s*/?>", "\n", frag)
    frag = re.sub(r"</p>", "\n\n", frag)
    t = html.unescape(re.sub(r"<[^>]+>", "", frag)).replace("\xa0", " ")
    return "\n\n".join(" ".join(l.split()) for l in re.split(r"\n\s*\n", t) if l.strip())


def origen_de(ref):
    """«Artículo 52 DECRETO 230 de 2008» -> co:decreto:230:2008:art:52; sentencias aparte."""
    ref = " ".join(html.unescape(re.sub(r"<[^>]+>", "", ref)).replace("\xa0", " ").split())
    s = RE_SENT.search(ref)
    if s:
        return "co:cc:%s-%s:%s" % (s.group(1).lower(), s.group(2).zfill(3), s.group(3)), ref
    m = RE_REF.search(ref)
    if not m:
        return None, ref
    o = "co:%s:%s:%s" % (TIPO_NORMA[m.group(2).lower()], m.group(3).replace(".", ""), m.group(4))
    return (o + ":art:" + m.group(1).lower() if m.group(1) else o), ref


def aristas(bloque, destino, fecha, fuente, sin_parsear):
    filas = []
    for etiqueta, ref in RE_ITEM.findall(bloque):
        et = " ".join(html.unescape(etiqueta).replace("\xa0", " ").split()).lower()
        o, ref = origen_de(ref or "")
        tipo = next((v for k, v in ACCION.items() if et.startswith(k)), None)
        if o and o.startswith("co:cc:"):
            tipo = {"exequible": "declara_exequible", "inexequible": "declara_inexequible"}.get(
                et.replace("declarado ", "").replace("declarada ", ""))
        if not (o and tipo):
            sin_parsear.append((destino, et, ref))
            continue
        filas.append((o, tipo, destino, fecha, "SUIN: %s %s" % (et, ref), fuente))
    return filas


def procesar(doc, id_norma, fuente):
    """(artículos, aristas, sin_parsear, estado_general)."""
    sin_parsear, filas = [], []
    # Estado de la norma entera: el bloque `tablita` del encabezado.
    estado = re.search(r'(?:Estado del documento|ESTADO DE VIGENCIA):?\s*</b>(?:</span>)?\s*(?:<b>)?'
                       r'(?:<span[^>]*>)?([^<]+)<', doc)
    estado = (estado.group(1).strip(" .").lower() if estado else "")
    fin = re.search(r"dej[óo] de estar vigente la norma</p></td>\s*<td[^>]*><p>(\d\d)/(\d\d)/(\d{4})", doc)
    fecha_fin = "%s-%s-%s" % (fin.group(3), fin.group(2), fin.group(1)) if fin else ""
    tabla = re.search(r'id="tablita">(.*?)</ul>', doc, re.S)
    if tabla:
        filas += aristas(tabla.group(1), id_norma, fecha_fin, fuente, sin_parsear)

    arts, vistos = [], set()
    for bloque in re.split(r'<a name="ver_\d+"></a>\s*<div', doc.split("<form")[0])[1:]:
        # Solo el PRIMER <strong> del bloque: más adentro está el «Artículo 17.» que el artículo
        # transcribe de la norma que reforma (Decreto 982/1996 art. séptimo).
        i = bloque.find("<strong>")
        cab = re.compile(r"<strong>\s*(?:<em>)?\s*Art[íi]culo\s+(\d+[A-Za-z\-]*?|[A-Za-zÁÉÍÓÚáéíóú]+)\s*[º°o]?\s*\.?\s*(?:</em>)?\s*</strong>"
                         r"\s*(?:<em>([^<]{2,200})</em>)?", re.I).match(bloque, i) if i >= 0 else None
        if not cab:
            continue
        num = cab.group(1).lower()
        num = ORDINAL.get(num.replace("é", "e").replace("í", "i"), num)
        if not re.fullmatch(r"\d+[a-z\-]*", num):
            sin_parsear.append((id_norma, "encabezado", cab.group(0)))
            continue
        if num in vistos:
            continue
        vistos.add(num)
        destino = "%s:art:%s" % (id_norma, num)
        cuerpo = bloque[cab.end():]
        for titulo, lista in RE_BLOQUE.findall(cuerpo):
            if "Afecta la vigencia" not in titulo:
                filas += aristas(lista, destino, "", fuente, sin_parsear)
        cuerpo = RE_BLOQUE.sub("", cuerpo)
        epi = " ".join((cab.group(2) or "").split()).rstrip(" .")
        arts.append((num, epi, texto(cuerpo)))
    return arts, filas, sin_parsear, estado


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ruta", help="«Decretos/1731310» o el id numérico de SUIN")
    for a in ("id", "tipo", "titulo", "ramas", "salida", "fecha"):
        p.add_argument("--" + a, required=True)
    p.add_argument("--minimo", type=int, default=1)
    a = p.parse_args()

    url, fecha_captura = captura(a.ruta)
    doc = bajar(url)
    # Unas capturas son ISO-8859-1 y otras UTF-8 (Decreto 939/2017): «artÃ­culo» delata la segunda.
    if doc.count("Ã") > 20:
        doc = doc.encode("latin-1", "replace").decode("utf-8", "replace")
    arts, filas, sin_parsear, estado = procesar(doc, a.id, url)
    if len(arts) < a.minimo:
        sys.exit("ABORTA: %d artículos, se esperaban al menos %d" % (len(arts), a.minimo))
    # La fecha de expedición no se infiere de la página (los formatos de SUIN cambian entre
    # capturas): se pasa a mano, leída del encabezado.
    muerta = estado.startswith("derogad") or "inexequible" in estado
    fm = ["---", "id: " + a.id, "tipo: " + a.tipo, "titulo: " + a.titulo, "fecha: " + a.fecha,
          "ramas: [%s]" % a.ramas, "estado_general: " + ("derogada" if muerta else "vigente"),
          "afectaciones: " + ("cargadas" if filas else "pendiente"),
          "fuente: " + url, "verificado: " + fecha_captura, "---", ""]
    for num, epi, txt in arts:
        fm += ["## art:%s — %s" % (num, epi), "", txt, ""]
    with open(os.path.join(RAIZ, a.salida), "w", encoding="utf-8") as fh:
        fh.write("\n".join(fm))
    guardar_relaciones(RAIZ, a.id, filas)
    print("%d artículos -> %s (captura %s, estado SUIN: %s)" % (len(arts), a.salida, fecha_captura, estado or "?"))
    print("%d aristas -> relaciones.csv" % len(filas))
    for d, e, r in sin_parsear:
        print("   no reconocida (NO se inventó arista): %s [%s] %s" % (d, e, r))


def check():
    doc = ('<b>Estado del documento: </b><b><span style="color:red;">Derogado.</span></b>'
           '<div style="display: none;" id="tablita"><ul class="resumenvigencias"><li class="referencia">'
           '<span>Derogado\xa0</span><a href="#">Artículo 52\xa0DECRETO 230 de 2008</a></li></ul>'
           '<p>Fecha en la cual dejó de estar vigente la norma</p></td><td x><p>30/01/2008<br></p>'
           '<a name="ver_1"></a><div id="toggle_1"><div><p><strong>Artículo 1º.</strong><em>Objeto. </em> Texto uno. </p>'
           '<p style="font-weight:bold;">Afecta la vigencia de: <span class="toctoggle">[x]</span></p>'
           '<div style="display: none;" id="z"><ul class="resumenvigencias"><li class="referencia">'
           '<span>Modifica\xa0</span><a>Artículo 11 DECRETO 2664 de 1994</a></li></ul></div></div></div>'
           '<a name="ver_2"></a><div id="toggle_2"><p><strong>Artículo 2º.</strong> Dos. </p></div>')
    arts, filas, sp, estado = procesar(doc, "co:decreto:9:1996", "u")
    assert [x[0] for x in arts] == ["1", "2"], arts
    assert arts[0][1] == "Objeto" and arts[0][2] == "Texto uno." and "2664" not in arts[0][2], arts[0]
    assert filas == [("co:decreto:230:2008:art:52", "deroga", "co:decreto:9:1996", "2008-01-30",
                      "SUIN: derogado Artículo 52 DECRETO 230 de 2008", "u")], filas
    assert estado == "derogado" and not sp
    print("check OK")


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
