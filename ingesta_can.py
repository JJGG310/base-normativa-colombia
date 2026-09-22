#!/usr/bin/env python3
"""Extrae una Decisión de la Comunidad Andina desde su PDF oficial.

    python3 ingesta_can.py <url_o_ruta_pdf> --id can:decision:486:2000 \
        --titulo "Decisión 486 de 2000 - Régimen Común sobre Propiedad Industrial" \
        --fecha 2000-09-14 --ramas "propiedad-intelectual, comercial, internacional-publico" \
        --minimo 270 --salida normativa/can-decision-486-2000.md

Mecánico, igual que ingesta_senado.py: el texto sale del PDF con PyMuPDF, nunca
del modelo. La Decisión no trae notas de vigencia al pie como senado — las
reformas de otras Decisiones (632/2006, 689/2008...) quedan `afectaciones: pendiente`
hasta que se rastreen aparte.
"""
import argparse, os, re, sys, urllib.request
from datetime import date

import fitz  # PyMuPDF

UA = {"User-Agent": "Mozilla/5.0"}
RE_PIE = re.compile(r"(?m)^-\s*\d+\s*-\s*$")
RE_ARTICULO = re.compile(r"(?m)^Art[íi]culo\s+(\d+)\.-\s*")
RE_TRANSITORIA = re.compile(
    r"(?m)^(PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|S[ÉE]PTIMA|OCTAVA|NOVENA|D[ÉE]CIMA)\.-\s*")
RE_TITULO = re.compile(r"(?m)^(TITULO|T[ÍI]TULO)\s+([IVXL]+)\s*$")
RE_CAPITULO = re.compile(r"(?m)^(CAP[ÍI]TULO)\s+([IVXL]+)\s*$")
RE_DISPOSICION = re.compile(
    r"(?m)^DISPOSICIONES\s+(GENERALES|FINALES|COMPLEMENTARIAS|TRANSITORIAS)\s*$")


def bajar(origen):
    if origen.startswith("http"):
        req = urllib.request.Request(origen, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        tmp = "/tmp/_can_descarga.pdf"
        with open(tmp, "wb") as fh:
            fh.write(data)
        return tmp
    return origen


def texto_completo(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    crudo = "\n".join(p.get_text() for p in doc)
    return RE_PIE.sub("", crudo)


def ubicaciones(texto):
    """Para cada offset del texto, título/capítulo vigente en ese punto."""
    titulo = capitulo = ""
    lineas = texto.split("\n")
    pos = 0
    mapa = []  # (offset, titulo, capitulo)
    for i, linea in enumerate(lineas):
        siguiente = lineas[i + 1].strip() if i + 1 < len(lineas) else ""
        m = RE_TITULO.match(linea) or RE_CAPITULO.match(linea)
        d = RE_DISPOSICION.match(linea)
        if m:
            texto_encabezado = "%s %s — %s" % (m.group(1).title(), m.group(2), siguiente)
            if m.re is RE_TITULO:
                titulo, capitulo = texto_encabezado, ""
            else:
                capitulo = texto_encabezado
            mapa.append((pos, titulo, capitulo))
        elif d:
            titulo, capitulo = "Disposiciones " + d.group(1).title(), ""
            mapa.append((pos, titulo, capitulo))
        pos += len(linea) + 1
    return mapa


def ubicacion_en(mapa, offset):
    actual = ("", "")
    for pos, t, c in mapa:
        if pos > offset:
            break
        actual = (t, c)
    return " > ".join(x for x in actual if x)


def limpiar(fragmento):
    return re.sub(r"[ \t]+", " ", fragmento).strip(" \n")


def procesar(ruta_pdf):
    texto = texto_completo(ruta_pdf)
    mapa = ubicaciones(texto)
    arts = []

    matches = list(RE_ARTICULO.finditer(texto))
    for k, m in enumerate(matches):
        num = m.group(1)
        fin = matches[k + 1].start() if k + 1 < len(matches) else len(texto)
        cuerpo = limpiar(texto[m.end():fin])
        if cuerpo:
            arts.append((num, "", ubicacion_en(mapa, m.start()), cuerpo))

    ORDINAL = {"primera": "1", "segunda": "2", "tercera": "3", "cuarta": "4",
               "quinta": "5", "sexta": "6", "septima": "7", "séptima": "7",
               "octava": "8", "novena": "9", "decima": "10", "décima": "10"}
    tmatches = list(RE_TRANSITORIA.finditer(texto))
    for k, m in enumerate(tmatches):
        nombre = m.group(1).lower()
        fin = tmatches[k + 1].start() if k + 1 < len(tmatches) else len(texto)
        cuerpo = limpiar(texto[m.end():fin])
        num = "transitorio-" + ORDINAL.get(nombre, nombre)
        if cuerpo:
            arts.append((num, "", ubicacion_en(mapa, m.start()), cuerpo))

    return arts


def main():
    p = argparse.ArgumentParser()
    p.add_argument("origen", help="URL o ruta local del PDF oficial")
    for a in ("id", "titulo", "ramas", "salida"):
        p.add_argument("--" + a, required=True)
    p.add_argument("--fecha", required=True)
    p.add_argument("--corto", default="")
    p.add_argument("--minimo", type=int, default=0)
    a = p.parse_args()
    raiz = os.path.dirname(os.path.abspath(__file__))

    ruta_pdf = bajar(a.origen)
    arts = procesar(ruta_pdf)
    if not arts:
        sys.exit("no se extrajo ningún artículo — revisar el formato del PDF")
    if a.minimo and len(arts) < a.minimo:
        sys.exit("ABORTA: %d artículos, se esperaban al menos %d. No se escribe %s."
                 % (len(arts), a.minimo, a.salida))

    fm = ["---", "id: " + a.id, "tipo: decision", "titulo: " + a.titulo]
    if a.corto:
        fm.append("titulo_corto: " + a.corto)
    fm += ["fecha: " + a.fecha, "ramas: [%s]" % a.ramas, "estado_general: vigente",
           "afectaciones: pendiente", "fuente: " + a.origen,
           "verificado: " + date.today().isoformat(), "---", ""]
    for num, epi, ubicacion, txt in arts:
        fm.append("## art:%s — %s" % (num, epi))
        if ubicacion:
            fm.append("ubicacion: " + ubicacion)
        fm += ["", txt, ""]

    destino = a.salida if os.path.isabs(a.salida) else os.path.join(raiz, a.salida)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(fm))
    print("%d artículos -> %s" % (len(arts), a.salida))


if __name__ == "__main__":
    main()
