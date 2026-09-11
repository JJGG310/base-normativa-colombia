#!/usr/bin/env python3
"""Contrasta los artículos de cada .md contra el índice de la propia fuente.

    python3 verificar.py                 # todas las normas de senado
    python3 verificar.py normativa/co-ley-472-1998.md

La fuente trae su propio índice: un <select name="listabookmarks"> con una opción
por artículo. Si el parser se comió artículos, aquí se ve — el conteo solo no basta,
porque un artículo perdido y uno partido en dos se cancelan.
"""
import glob, os, re, sys

from ingesta_senado import bajar, paginas

OPCION = re.compile(r'<option value="[^"]*#(\d+[A-Za-z]?)"[^>]*>\s*([^<]+?)\s*</option>', re.I)


def indice_fuente(url):
    """Números de artículo que la fuente lista en su propio selector."""
    nums = set()
    for _, doc in paginas(url):
        for ancla, etiqueta in OPCION.findall(doc):
            if re.fullmatch(r"\d+[A-Za-z]?", etiqueta):
                nums.add(etiqueta.upper())
    return nums


def indice_gestor(url):
    """El Gestor no trae selector: el índice son los encabezados en línea propia."""
    from ingesta_senado import limpiar
    doc = re.sub(r"<style.*?</style>|<script.*?</script>", "", bajar(url, enc="utf-8"),
                 flags=re.S | re.I)
    return {m.group(1).strip(".").upper()
            for m in re.finditer(r"^ART[IÍ]CULO\s+([\d][\d\.]*)", limpiar(doc), re.I | re.M)}


def revisar(ruta):
    texto = open(ruta, encoding="utf-8").read()
    fuente = re.search(r"^fuente: (\S+)", texto, re.M)
    if not fuente:
        return None
    propios = {n.upper() for n in re.findall(r"^## art:(\S+)", texto, re.M)}
    if "secretariasenado" in fuente.group(1):
        fuente_nums = indice_fuente(fuente.group(1))
    elif "funcionpublica" in fuente.group(1):
        fuente_nums = indice_gestor(fuente.group(1))
    else:
        return None
    faltan = sorted(fuente_nums - propios, key=lambda s: (len(s), s))
    sobran = sorted(propios - fuente_nums, key=lambda s: (len(s), s))
    print("%-46s %4d arts · índice %4d · faltan %d%s" % (
        os.path.basename(ruta), len(propios), len(fuente_nums), len(faltan),
        (": " + ", ".join(faltan[:15])) if faltan else ""))
    if sobran:
        print("%-46s   %d no listados en el índice: %s" % ("", len(sobran), ", ".join(sobran[:15])))
    return len(faltan)


if __name__ == "__main__":
    rutas = sys.argv[1:] or sorted(glob.glob(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "normativa", "*.md")))
    total = sum(filter(None, (revisar(r) or 0 for r in rutas)))
    print("faltantes en total: %d" % total)
