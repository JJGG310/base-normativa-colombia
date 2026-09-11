#!/usr/bin/env python3
"""Extrae Decretos Únicos Reglamentarios del Gestor Normativo de Función Pública.

    python3 ingesta_gestor.py 74000 --id co:decreto:1067:2015 \\
        --titulo "Decreto 1067 de 2015 - DUR Sector Relaciones Exteriores" \\
        --fecha 2015-05-26 --ramas "migratorio, internacional-publico" \\
        --salida normativa/co-decreto-1067-2015.md
    python3 ingesta_gestor.py --check

secretariasenado no publica los DUR (404), así que esta es la fuente para ellos.
El argumento es el `i=` interno del Gestor, no el número del decreto: el índice de
DUR está en `norma.php?i=62255`.

Dos trampas de esta fuente:
  - El `<meta charset>` declara ISO-8859-1 y el contenido es UTF-8. Hacerle caso al
    meta destroza todas las tildes.
  - Los artículos usan numeración decimal (2.2.1.1.1), no enteros, así que el corte
    y el orden no se pueden reutilizar tal cual de ingesta_senado.
"""
import argparse, os, re, sys
from datetime import date

from ingesta_senado import bajar, limpiar, fecha_de, guardar_relaciones, TIPO_NORMA

RAIZ = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=%s"
ANCLA = re.compile(r'<a\s+[^>]*name="([\d.]+)"[^>]*>', re.I)

ACCION = {"modificado": "modifica", "adicionado": "adiciona", "derogado": "deroga",
          "sustituido": "subroga", "subrogado": "subroga"}
# El formato real trae artículo definido y contracción:
# "(Modificado por el Art. 1 del Decreto 124 de 2021)".
RE_AFECTA = re.compile(
    r"(%s)\s+por\s+(?:el\s+)?(?:art[íi]?c?u?l?o?s?\.?\s*([\d\.]+)\s+d?e?l?\s+)?"
    r"(Decreto|Ley|Resoluci[óo]n)\s+([\d\.]+)\s+de\s+(\d{4})" % "|".join(ACCION), re.I)


def articulos(doc):
    """Corta por las anclas `name="2.2.1.1.1"`, que es la numeración real del DUR."""
    anclas = list(ANCLA.finditer(doc))
    salida, vistos = [], set()
    for k, m in enumerate(anclas):
        num = m.group(1).strip(".")
        fin = anclas[k + 1].start() if k + 1 < len(anclas) else len(doc)
        cuerpo = limpiar(doc[m.end():fin])
        if not cuerpo or num in vistos:
            continue
        vistos.add(num)
        # "ARTÍCULO 2.2.1.1.1. Concurrencias de las Misiones. <texto>"
        enc = re.match(r"ART[IÍ]CULO\s+[\d\.]+\s*\.?\s*(.{3,120}?)\.\s+", cuerpo)
        epi, texto = ("", cuerpo)
        if enc:
            epi, texto = enc.group(1).strip(), cuerpo[enc.end():].strip()
        salida.append((num, " ".join(epi.split()), texto))
    return salida


def aristas(arts, id_norma, fuente):
    """Las notas de vigencia vienen en el propio cuerpo, no en un .js aparte."""
    filas, sin_parsear = [], []
    for num, _epi, texto in arts:
        destino = "%s:art:%s" % (id_norma, num)
        for m in RE_AFECTA.finditer(texto):
            accion, art_org, tipo, num_org, anio = m.groups()
            tipo_n = TIPO_NORMA.get(tipo.lower(), tipo.lower())
            origen = "co:%s:%s:%s" % (tipo_n, num_org.replace(".", "").lstrip("0") or "0", anio)
            if art_org:
                origen += ":art:" + art_org.strip(".")
            f, nota = fecha_de(texto[m.start():m.start() + 220], anio)
            filas.append((origen, ACCION[accion.lower()], destino, f, nota, fuente))
        if re.search(r"\b(?:Modificad|Adicionad|Derogad)", texto) and not RE_AFECTA.search(texto):
            sin_parsear.append((destino, texto[:100]))
    vistos, unicas = set(), []
    for f in filas:
        if (f[0], f[1], f[2]) not in vistos:
            vistos.add((f[0], f[1], f[2]))
            unicas.append(f)
    return unicas, sin_parsear


def check():
    doc = ('<a name="2.2.1.1.1"></a><p>ARTÍCULO 2.2.1.1.1. Concurrencias de las Misiones. '
           'Establecer las concurrencias así: texto. Modificado por art. 1 de Decreto 1407 de 2024 '
           'Ministerio de Relaciones Exteriores</p>'
           '<a name="2.2.1.1.2"></a><p>ARTÍCULO 2.2.1.1.2. Otra cosa. Contenido del segundo. '
           '(Derogado por el Decreto 484 de 2026)</p>')
    arts = articulos(doc)
    assert [a[0] for a in arts] == ["2.2.1.1.1", "2.2.1.1.2"], arts
    assert arts[0][1] == "Concurrencias de las Misiones", arts[0]
    assert arts[0][2].startswith("Establecer las concurrencias"), arts[0][2][:50]

    filas, _ = aristas(arts, "co:decreto:1067:2015", "x")
    assert ("co:decreto:1407:2024:art:1", "modifica",
            "co:decreto:1067:2015:art:2.2.1.1.1") == filas[0][:3], filas[0]
    assert ("co:decreto:484:2026", "deroga",
            "co:decreto:1067:2015:art:2.2.1.1.2") == filas[1][:3], filas[1]
    print("check OK")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("i", help="id interno del Gestor (índice de DUR en norma.php?i=62255)")
    for a in ("id", "titulo", "ramas", "salida"):
        p.add_argument("--" + a, required=True)
    p.add_argument("--fecha", required=True)   # el Gestor no trae la línea del Diario Oficial
    p.add_argument("--corto", default="")
    p.add_argument("--tipo", default="decreto")
    p.add_argument("--minimo", type=int, default=0)
    a = p.parse_args()

    url = BASE % a.i
    doc = bajar(url, enc="utf-8")          # el meta miente: dice ISO-8859-1, es UTF-8
    arts = articulos(doc)
    if a.minimo and len(arts) < a.minimo:
        sys.exit("ABORTA: %d artículos, se esperaban al menos %d" % (len(arts), a.minimo))
    if not arts:
        sys.exit("no se extrajo ningún artículo — revisar el formato de la fuente")
    filas, sin_parsear = aristas(arts, a.id, url)

    fm = ["---", "id: " + a.id, "tipo: " + a.tipo, "titulo: " + a.titulo]
    if a.corto:
        fm.append("titulo_corto: " + a.corto)
    fm += ["fecha: " + a.fecha, "ramas: [%s]" % a.ramas, "estado_general: vigente",
           "afectaciones: " + ("cargadas" if filas else "pendiente"),
           "fuente: " + url, "verificado: " + date.today().isoformat(), "---", ""]
    for num, epi, txt in arts:
        fm += ["## art:%s — %s" % (num, epi), "", txt, ""]

    destino = a.salida if os.path.isabs(a.salida) else os.path.join(RAIZ, a.salida)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(fm))
    guardar_relaciones(RAIZ, a.id, filas)
    print("%d artículos -> %s" % (len(arts), a.salida))
    print("%d aristas -> relaciones.csv" % len(filas))
    if sin_parsear:
        print("%d notas no reconocidas (NO se inventaron aristas)" % len(sin_parsear))


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
