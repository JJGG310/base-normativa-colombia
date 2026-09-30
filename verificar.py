#!/usr/bin/env python3
"""Contrasta los artículos de cada .md contra el índice de la propia fuente.

    python3 verificar.py                 # todas las normas de senado
    python3 verificar.py normativa/co-ley-472-1998.md

La fuente trae su propio índice: un <select name="listabookmarks"> con una opción
por artículo. Si el parser se comió artículos, aquí se ve — el conteo solo no basta,
porque un artículo perdido y uno partido en dos se cancelan.
"""
import glob, os, re, sys

from ingesta_senado import ANCLA, articulos_tras_decreta, bajar, num_ancla, paginas

OPCION = re.compile(r'<option value="[^"]*#(\d+[A-Za-z]?)"[^>]*>\s*([^<]+?)\s*</option>', re.I)


def indice_fuente(url):
    """Números de artículo que la fuente lista en su propio selector.

    El normograma de la DIAN no trae selector: ahí el índice son los encabezados."""
    from ingesta_senado import limpiar
    nums, encabezados, subtitulos = set(), set(), set()
    for _, doc in paginas(url):
        # Si en la mayoría de las anclas numéricas el encabezado dice otro número que su `name`
        # («name=5» → «ARTÍCULO 4o-bis», Ley 178/1994; «name=1» → «ARTÍCULO 1A.», Ley 303/1996), los
        # `name` (y el selector) son posiciones, no números de artículo: el índice sale de los encabezados.
        cab = [(m.group(1).upper(), num_ancla(m.group(1), limpiar(m.group(2))).upper()) for m in ANCLA.finditer(doc)
               if re.fullmatch(r"\d+[A-Za-z]?", m.group(1)) and re.match(r"\s*ART[IÍ]CULO\s+\d", limpiar(m.group(2)), re.I)]
        posicional = sum(n != h for n, h in cab) > len(cab) / 2
        for ancla, etiqueta in ([] if posicional else OPCION.findall(doc)):
            if re.fullmatch(r"\d+[A-Za-z]?", etiqueta):
                nums.add(etiqueta.upper())
        # El selector solo lista las anclas `bookmarkaj`: los artículos con un `<A
        # name>` pelado no salen ahí, y eran justo los que el parser perdía.
        nums |= {num_ancla(m.group(1), limpiar(m.group(2))).upper() for m in ANCLA.finditer(doc)
                 if re.fullmatch(r"\d+[A-Za-z]?", m.group(1)) and re.match(r"\s*ART", limpiar(m.group(2)), re.I)}
        # Anclas con nombre ajeno («Nivel001», «TITULO PRE») y encabezado de artículo:
        # el parser las saltaba y el índice tampoco las veía (ET 580-1, C.Co. 508).
        for m in ANCLA.finditer(doc):
            h = re.match(r"\s*ART[IÍ]CULO\s+(\d+(?:-\d+)?[A-Za-z]?)(?<![oO])", limpiar(m.group(2)), re.I)
            if h and not re.match(r"\d|transitorio", m.group(1), re.I):
                nums.add(h.group(1).upper())
        nums = {n for n in nums if not re.fullmatch(r"\d+F", n)}   # Ley 1/1980 dentro del C.Co.
        # «503T» = subtítulo «DE LAS ALARMAS.» (Ley 9/1979): el selector lo lista, no es artículo.
        subtitulos |= {m.group(1).upper() for m in ANCLA.finditer(doc) if re.fullmatch(r"\d+T+", m.group(1), re.I)
                 and not re.search(r"ART|[a-záéíóú]", limpiar(m.group(2)))}
        # "ARTÍCULO 1o." es el artículo 1: la `o` es el ordinal, no un sufijo.
        encabezados |= {re.sub(r"(?<=\d)[OºO°]$", "", m.group(1).upper()) for m in
                        re.finditer(r"(?im)^ART[IÍ]CULO\s+(\d+[A-Za-z]?)", limpiar(doc))}
    return (nums - subtitulos) or encabezados


def indice_gestor(url, enteros=False):
    """El Gestor no trae selector: el índice son los encabezados en línea propia."""
    from ingesta_senado import limpiar
    from ingesta_gestor import NUM_DUR, SUFIJO
    doc = re.sub(r"<style.*?</style>|<script.*?</script>", "", bajar(url, enc="utf-8"),
                 flags=re.S | re.I)
    d = re.search(r"(?<![a-záéíóú])DECRETA\b", doc)   # como ingesta_gestor.articulos
    doc = doc[d.end():] if d else doc
    ms = list(re.finditer(r"^[ \t]*((?-i:ART[IÍí]CULO|Art[íi]culo))(?:[ \t]*\.[ \t]*|\s+)(%s%s)(.*)" % (NUM_DUR, SUFIJO), limpiar(doc), re.I | re.M))
    hs, previo = [], None
    for m in ms:
        n = re.sub(r"\s", "", m.group(2)).upper()
        # «Artículo 1°. El artículo 8° de la Ley 65 de 1993 quedará así:» — lo que sigue hasta el
        # siguiente propio es transcrito (Decreto 2636/2004). Solo en numeración entera.
        if previo and "." not in n and re.search(r":\s*$", previo[1]) and \
                re.match(r"\d+", n) and int(re.match(r"\d+", n).group()) != previo[0] + 1:
            continue
        hs.append((m.group(1), n))
        if "." not in n and re.match(r"\d+", n):
            previo = (int(re.match(r"\d+", n).group()), m.group(3))
    # Ley con encabezados mayormente en mayúscula («ARTICULO 4º»): los «Artículo 88.» en minúscula son
    # los del código que transcribe al reformarlo (Ley 62/1988 → Código Electoral).
    if sum(c.isupper() for c, n in hs if "." not in n) > sum(not c.isupper() for c, n in hs if "." not in n):
        hs = [(c, n) for c, n in hs if c.isupper() or "." in n]
    nums = {n for _, n in hs}
    # En un DUR, un «ARTÍCULO 2.» entero es el del decreto que lo reformó, que la
    # fuente transcribe: no es artículo del DUR (ingesta_gestor.partir tampoco lo toma).
    # Al revés en un decreto que reforma un DUR (ingesta_gestor --enteros): los
    # decimales son los artículos del DUR que transcribe.
    if enteros:
        nums = {n for n in nums if "." not in n}
    elif sum("." in n for n in nums) > len(nums) / 2:
        nums = {n for n in nums if "." in n}
    return nums


def revisar(ruta):
    texto = open(ruta, encoding="utf-8").read()
    fuente = re.search(r"^fuente: (\S+)", texto, re.M)
    if not fuente:
        return None
    propios = {n.upper() for n in re.findall(r"^## art:(\S+)", texto, re.M)}
    # Los normogramas de DIAN, CREG, Cancillería, Colpensiones, JEP y SENA los publica el
    # mismo proveedor que senado (Avance Jurídico): mismo selector, mismo formato.
    if re.search(r"secretariasenado|normograma\.dian|creg\.gov|cancilleria\.gov|colpensiones\.gov"
                 r"|jurinfo\.jep|normograma\.sena", fuente.group(1)):
        fuente_nums = indice_fuente(fuente.group(1))
    elif "suin-juriscol" in fuente.group(1):
        # SUIN encierra cada artículo en un `<div id="toggle_N">` (y nada más): se cuentan esos
        # bloques, sin pasar por el parser; faltan/sobran se reportan como números.
        doc = bajar(fuente.group(1))
        n = len(set(re.findall(r'<div id="toggle_(\d+)">', doc)))
        print("%-46s %4d arts · bloques %4d · faltan %d" % (os.path.basename(ruta), len(propios), n,
                                                          max(0, n - len(propios))))
        return max(0, n - len(propios))
    elif "funcionpublica" in fuente.group(1):
        fuente_nums = indice_gestor(fuente.group(1), propios and not any("." in n for n in propios))
    else:
        return None
    faltan = sorted(fuente_nums - propios, key=lambda s: (len(s), s))
    sobran = sorted(propios - fuente_nums, key=lambda s: (len(s), s))
    # Ley aprobatoria con solo los artículos de la ley (los de tras el último DECRETA): el resto del índice
    # es texto del tratado, o de la Ley 424/1998 que las aprobatorias transcriben. No son artículos de la ley.
    if faltan and re.search(r"^titulo: .*\bapru[eé]ba", texto, re.M | re.I) and "secretariasenado" in fuente.group(1):
        ley = {a[0].upper() for a in articulos_tras_decreta(fuente.group(1))}
        if ley and ley == propios:
            print("%-46s %4d arts · índice %4d · faltan 0 (%d números del índice no son artículos de la ley sino del tratado o de otra norma transcrita: %s)" % (
                os.path.basename(ruta), len(propios), len(fuente_nums), len(faltan), ", ".join(faltan[:8])))
            return 0
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
