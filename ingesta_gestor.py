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

from ingesta_senado import bajar, limpiar, fecha_de, guardar_relaciones, MESES, TIPO_NORMA

RAIZ = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=%s"
ANCLA = re.compile(r'<a\s+[^>]*name="([\d.]+)"[^>]*>', re.I)

ACCION = {"modificado": "modifica", "adicionado": "adiciona", "derogado": "deroga",
          "sustituido": "subroga", "subrogado": "subroga"}
# El formato real trae artículo definido y contracción:
# "(Modificado por el Art. 1 del Decreto 124 de 2021)".
RE_AFECTA = re.compile(
    r"(%s)\s+por\s+(?:el\s+)?(?:art[íi]?c?u?l?o?s?\.?\s*([\d\.]+)\s*,?\s*d?e?l?\s*)?"
    r"(Decreto|Ley|Resoluci[óo]n)\s+([\d\.]+)\s+de\s+(\d{4})" % "|".join(ACCION), re.I)


def fecha_norma(doc):
    """El Gestor no publica la línea del Diario Oficial, pero sí la fecha junto al
    número: «DECRETO 1069 DE 2015 (Mayo 26)». Sale de la fuente, no de memoria.

    El «DE» no siempre está: el DUR 1076 se titula «DECRETO 1076 2015 (Mayo 26)»."""
    t = limpiar(re.sub(r"<style.*?</style>|<script.*?</script>", "", doc, flags=re.S | re.I))
    # Entre el año y la fecha puede haber paréntesis de reformas: el DUR 1073 trae
    # «DECRETO 1073 DE 2015 (Adicionado por…) (Adicionado por…) (Mayo 26)».
    m = re.search(r"\b(?:DECRETO|LEY)\s+[\d\.]+\s+(?:DE\s+)?(\d{4})\s*(?:\([^)]*\)\s*)*"
                  r"\(\s*(%s)\s+(\d{1,2})\s*\)" % "|".join(MESES), t, re.I)
    return "%s-%02d-%02d" % (m.group(1), MESES[m.group(2).lower()], int(m.group(3))) if m else ""


def articulos(doc):
    """Corta por las anclas `name="2.2.1.1.1"`, que es la numeración real del DUR."""
    anclas = list(ANCLA.finditer(doc))
    salida, vistos = [], set()
    # Las normas anteriores a los DUR no traen anclas: solo el encabezado en el texto.
    if not anclas:
        return [a for a in partir("", "", limpiar(doc)) if a[0]]
    # Los primeros artículos suelen ir antes de la primera ancla, donde el corte por
    # anclas ni los mira (163 de la Ley 23 de 1982, el libro 1 de varios DUR). Se
    # exige que el número siga el estilo de numeración de la norma — decimal en los
    # DUR, entero en las viejas — para no confundir un artículo con la remisión del
    # preámbulo ("artículo 189 de la Constitución Política").
    decimal = "." in anclas[0].group(1)
    salida += [a for a in partir("", "", limpiar(doc[:anclas[0].start()]))
               if a[0] and ("." in a[0]) == decimal]
    for k, m in enumerate(anclas):
        num = m.group(1).strip(".")
        fin = anclas[k + 1].start() if k + 1 < len(anclas) else len(doc)
        cuerpo = limpiar(doc[m.end():fin])
        if not cuerpo:
            continue
        # La fuente también le pone ancla a los numerales de una lista dentro del
        # artículo ("6. Entrenamiento."), con un name que parece numeración de DUR.
        # Solo es artículo si el texto arranca con el número completo del ancla; si
        # no, es la continuación del anterior y se le devuelve, no se parte en dos.
        if not re.match(r"(?:ART[IÍ]CULO\s+)?%s\b" % re.escape(num), cuerpo, re.I):
            if salida:
                salida[-1] = salida[-1][:2] + (salida[-1][2] + "\n\n" + cuerpo,)
            continue
        # "ARTÍCULO 2.2.1.1.1. Concurrencias de las Misiones. <texto>" — algunos DUR
        # publican el mismo encabezado sin la palabra ARTÍCULO.
        enc = re.match(r"(?:ART[IÍ]CULO\s+)?[\d\.]+\s*\.?\s*(.{3,120}?)\.\s+", cuerpo)
        epi, texto = ("", cuerpo)
        if enc:
            epi, texto = enc.group(1).strip(), cuerpo[enc.end():].strip()
        salida.append((num, " ".join(epi.split()), texto))

    # La numeración se repite en la fuente (el 1078 trae dos anclas 2.2.9.1.4.2 con
    # artículos distintos). Descartar el ancla repetida entera se llevaba por delante
    # los 10 artículos que venían detrás: primero se parte, después se descarta.
    partes = []
    for art in salida:
        for a in partir(*art):
            if a[0] in vistos or not a[2]:
                continue
            vistos.add(a[0])
            partes.append(a)
    return partes


# El ordinal («ARTICULO 1º- …», «ARTICULO 1o. …») solo se consume si lo sigue un
# signo: con re.I, una `o` suelta se comía la primera letra del epígrafe ("Otro").
RE_ART_INLINE = re.compile(r"(?m)^ART[IÍ]CULO\s+([\d][\d\.]*)(?:[ºo°](?=[\s.\-]))?\s*[-.]?\s*", re.I)


def partir(num, epi, texto):
    """Varios artículos pueden colgar de una sola ancla: el Gestor no le pone `name`
    a todos. El encabezado en línea propia los delimita — sin esto se perdían 287
    artículos del DUR 1072, tragados dentro del anterior."""
    cortes = [m for m in RE_ART_INLINE.finditer(texto) if m.group(1).strip(".") != num]
    if not cortes:
        return [(num, epi, texto)]
    salida = [(num, epi, texto[:cortes[0].start()].strip())]
    for k, m in enumerate(cortes):
        fin = cortes[k + 1].start() if k + 1 < len(cortes) else len(texto)
        cuerpo = texto[m.end():fin].strip()
        # "Modificado por el art. 1, Ley 712 de 2001." no es el epígrafe del artículo:
        # arrancarlo como tal le corta el principio al texto.
        e = re.match(r"(?!Modificad|Adicionad|Derogad|Reglamentad|Ver\b)(.{3,120}?)\.\s+", cuerpo)
        salida.append((m.group(1).strip("."), " ".join(e.group(1).split()) if e else "",
                       cuerpo[e.end():].strip() if e else cuerpo))
    return [a for a in salida if a[2]]


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

    # Un artículo sin ancla propia, tragado dentro del anterior, se rescata.
    r = partir("2.2.1.1.1", "Epígrafe", "Texto del primero.\nARTÍCULO 2.2.1.1.9. Otro. Texto del otro.")
    assert [x[0] for x in r] == ["2.2.1.1.1", "2.2.1.1.9"], r
    assert r[1][1] == "Otro" and r[1][2] == "Texto del otro.", r[1]

    # Un numeral de lista con ancla propia no es un artículo: vuelve al anterior.
    lista = doc + '<a name="2.2.1.1.2.6"></a><p>6. Entrenamiento.</p>'
    arts = articulos(lista)
    assert [a[0] for a in arts] == ["2.2.1.1.1", "2.2.1.1.2"], arts
    assert arts[1][2].endswith("6. Entrenamiento."), arts[1][2]

    # Las normas viejas del Gestor citan con coma: "Modificado por el art. 1, Ley 712 de 2001".
    f, _ = aristas([("1", "", "Modificado por el art. 1, Ley 712 de 2001. Aplicación.")],
                   "co:decreto:2158:1948", "x")
    assert f[0][:3] == ("co:ley:712:2001:art:1", "modifica", "co:decreto:2158:1948:art:1"), f

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
    p.add_argument("--fecha", default="")   # si se omite, sale del «(Mayo 26)» de la fuente
    p.add_argument("--corto", default="")
    p.add_argument("--tipo", default="decreto")
    p.add_argument("--minimo", type=int, default=0)
    a = p.parse_args()

    url = BASE % a.i
    doc = bajar(url, enc="utf-8")          # el meta miente: dice ISO-8859-1, es UTF-8
    fecha = a.fecha or fecha_norma(doc)
    if not fecha:
        sys.exit("no se pudo leer la fecha en la fuente: pasarla con --fecha")
    arts = articulos(doc)
    if a.minimo and len(arts) < a.minimo:
        sys.exit("ABORTA: %d artículos, se esperaban al menos %d" % (len(arts), a.minimo))
    if not arts:
        sys.exit("no se extrajo ningún artículo — revisar el formato de la fuente")
    filas, sin_parsear = aristas(arts, a.id, url)

    fm = ["---", "id: " + a.id, "tipo: " + a.tipo, "titulo: " + a.titulo]
    if a.corto:
        fm.append("titulo_corto: " + a.corto)
    fm += ["fecha: " + fecha, "ramas: [%s]" % a.ramas, "estado_general: vigente",
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
