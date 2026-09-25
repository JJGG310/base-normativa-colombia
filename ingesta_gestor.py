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
import argparse, html, os, re, sys
from datetime import date

from ingesta_senado import bajar, limpiar, fecha_de, guardar_relaciones, MESES, TIPO_NORMA

RAIZ = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=%s"
ANCLA = re.compile(r'<a\s+[^>]*name="([\d.]+)"[^>]*>', re.I)
# Número de artículo de DUR tal como lo escribe el texto: con letra intercalada
# (2.2.7B.1.1.1) o con un espacio perdido (2.2.1.2. 7.16).
# Tras el primer punto, el espacio solo vale si sigue otro decimal («2. 1.11.10»): en
# «ARTÍCULO 11. 1. Los salarios…» es el artículo 11 con su numeral 1.
NUM_DUR = r"\d+(?-i:[A-Z])?(?:\.(?:\s(?=\d+\.\d))?\d+(?-i:[A-Z])?(?:\.\s?\d+(?-i:[A-Z])?)*)?"

ACCION = {"modificado": "modifica", "adicionado": "adiciona", "derogado": "deroga",
          "sustituido": "subroga", "subrogado": "subroga"}
# El formato real trae artículo definido y contracción:
# "(Modificado por el Art. 1 del Decreto 124 de 2021)".
RE_AFECTA = re.compile(
    r"(%s)\s+por\s+(?:el\s+)?(?:art[íi]?c?u?l?o?s?\.?\s*([\d\.]+)\s*,?\s*d?e?l?\s*)?"
    r"(Decreto|Ley|Resoluci[óo]n)\s+([\d\.]+)\s+de\s+(\d{4})" % "|".join(ACCION), re.I)

RE_PARTE = re.compile(r"(?:inciso|numeral|literal|par[áa]grafo|aparte|expresi[óo]n|ordinal|subrayad|tachad"
                      r"|frase|palabra|parcialmente)[^.;()\n]*$", re.I)

# EOSF: «6. Delegaciones para ordenar gastos. Derogado por el art. 123, Ley 510 de 1999».
RE_NUMERAL = re.compile(r"(?:^|\n|\.\s)\s*\d+[a-z]?\.\s+[^.\n]{2,120}\.\s*$")


def fecha_norma(doc):
    """El Gestor no publica la línea del Diario Oficial, pero sí la fecha junto al
    número: «DECRETO 1069 DE 2015 (Mayo 26)». Sale de la fuente, no de memoria.

    El «DE» no siempre está: el DUR 1076 se titula «DECRETO 1076 2015 (Mayo 26)»."""
    t = limpiar(re.sub(r"<style.*?</style>|<script.*?</script>", "", doc, flags=re.S | re.I))
    # Entre el año y la fecha puede haber paréntesis de reformas: el DUR 1073 trae
    # «DECRETO 1073 DE 2015 (Adicionado por…) (Adicionado por…) (Mayo 26)».
    m = re.search(r"\b(?:DECRETO|LEY)\s+(?:N[ÚU]MERO\s+)?[\d\.]+\s+(?:DE\s+)?(\d{4})\s*(?:\([^)]*\)\s*)*"
                  r"\(\s*(%s)\s+(\d{1,2})\s*\)" % "|".join(MESES), t, re.I)
    return "%s-%02d-%02d" % (m.group(1), MESES[m.group(2).lower()], int(m.group(3))) if m else ""


def articulos(doc, enteros=False):
    """Corta por las anclas `name="2.2.1.1.1"`, que es la numeración real del DUR."""
    # El CSS del pie de página quedaba pegado al último artículo de cada decreto.
    doc = re.sub(r"<style.*?</style>|<script.*?</script>", "", doc, flags=re.S | re.I)
    doc = re.split(r"<a[^>]*javascript:history\.back", doc)[0]   # «Volver Atrás» y el pie del sitio
    # Los considerandos transcriben artículos de otras normas («Artículo 28. Grupo empresarial»
    # de la Ley 222 en el Decreto 1457/2020): el articulado propio empieza tras «DECRETA».
    d = re.search(r"(?<![a-záéíóú])DECRETA\b", doc)
    doc = doc[d.end():] if d else doc
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
    decimal = sum("." in a.group(1) for a in anclas) > len(anclas) / 2   # la primera puede ser «1»
    # Un decreto que reforma un DUR transcribe sus artículos («quedará así: ARTÍCULO
    # 2.2.18.1.1…»): son mayoría, pero los propios son los enteros (--enteros).
    decimal = decimal and not enteros
    salida += [a for a in partir("", "", limpiar(doc[:anclas[0].start()]), decimal)
               if a[0] and ("." in a[0]) == decimal]
    for k, m in enumerate(anclas):
        num = m.group(1).strip(".")
        fin = anclas[k + 1].start() if k + 1 < len(anclas) else len(doc)
        # La fuente pone el ancla DESPUÉS de la palabra: «ARTÍCULO<a name=…> 1.1.2.1»,
        # así que cada span termina con el «ARTÍCULO» del siguiente.
        cuerpo = re.sub(r"\s*ART[IÍ]CULO\s*$", "", limpiar(doc[m.end():fin]))
        # Las leyes cierran con «Dada en Bogotá…» y las firmas: fuera del último artículo.
        cuerpo = re.split(r"(?m)^\s*Dada en ", cuerpo)[0].strip()
        if not cuerpo:
            continue
        # Si el ancla es la de un encabezado («ARTÍCULO<a name…> 1.1.2.4.», o el ancla
        # justo antes de «ARTÍCULO …»), manda el número del texto: el nombre del ancla
        # falla (el 1066 repite `1.1.2.3` para el 1.1.2.4; el 1076 escribe
        # «2.2.1.2. 7.16» y «2.2.7B.1.1.1»). Sin «ARTÍCULO» es un numeral de lista.
        es_art = (re.match(r"ART[IÍ]CULO\s", cuerpo)
                  or re.search(r"ART[IÍ]CULO\s*$", limpiar(doc[max(0, m.start() - 200):m.start()])))
        propio = re.match(r"(?:ART[IÍ]CULO\s+)?(%s)" % NUM_DUR, cuerpo)
        if es_art and propio:
            num = re.sub(r"\s", "", propio.group(1)).lower()
        # La fuente también le pone ancla a los numerales de una lista dentro del
        # artículo ("6. Entrenamiento."), con un name que parece numeración de DUR.
        # Solo es artículo si el texto arranca con el número completo del ancla; si
        # no, es la continuación del anterior y se le devuelve, no se parte en dos.
        # En un DUR, un ancla entera es de una tabla o del artículo del decreto
        # reformador que la fuente transcribe («ARTÍCULO 2. Vigencia»): tampoco.
        if (decimal != ("." in num)
                or not es_art and not re.match(r"(?:ART[IÍ]CULO\s+)?%s\b" % re.escape(num), cuerpo, re.I)):
            if salida:
                salida[-1] = salida[-1][:2] + (salida[-1][2] + "\n\n" + cuerpo,)
            continue
        # "ARTÍCULO 2.2.1.1.1. Concurrencias de las Misiones. <texto>" — algunos DUR
        # publican el mismo encabezado sin la palabra ARTÍCULO.
        enc = re.match(r"(?:ART[IÍ]CULO\s+)?(?:%s)\s*\.?\s*(.{3,120}?)\.(?:\s+|$)" % NUM_DUR, cuerpo)
        epi, texto = ("", cuerpo)
        # Los del libro 1 de los DUR son solo un epígrafe («Fondo de Protección de
        # Justicia»): el encabezado ES el contenido, no se deja vacío.
        if enc and cuerpo[enc.end():].strip():
            epi, texto = enc.group(1).strip(), cuerpo[enc.end():].strip()
        elif not enc:   # sin epígrafe, el número repetido («1. A partir…») no es texto
            texto = re.sub(r"^(?:ART[IÍ]CULO\s+)?%s\s*[.oº°-]*\s+" % re.escape(num), "", cuerpo, flags=re.I)
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
# «artículo 991 ibídem» en minúscula al inicio de una línea partida es una remisión, no un encabezado.
RE_ART_INLINE = re.compile(r"(?m)^[ \t]*(?-i:ART[IÍí]CULO|Art[íi]culo)\.?\s+(" + NUM_DUR + r"(?:\s?(?-i:[A-Z])(?=[\s.\-]))?)"
                           r"(?:[ºo°](?=[\s.\-]))?\s*[-.]?\s*", re.I)


RE_TRANSCRIBE = re.compile(r"quedar[áa]n? así|en los siguientes términos|el siguiente texto", re.I)


def orden(num):
    return [int(x) for x in re.findall(r"\d+", num)]


def partir(num, epi, texto, decimal=None):
    """Varios artículos pueden colgar de una sola ancla: el Gestor no le pone `name`
    a todos. El encabezado en línea propia los delimita — sin esto se perdían 287
    artículos del DUR 1072, tragados dentro del anterior."""
    # Con el estilo de numeración de la norma: un «ARTÍCULO 2.» entero dentro de un DUR
    # es el decreto reformador transcrito. En las de numeración entera, además, solo
    # hacia adelante y tras «…quedará así:» solo el número siguiente (el art. 152 del CPTSS reproduce los
    # arts. 13, 18 y 19 del D.L. 528/64); una letra (54 A) avanza sobre el 54. En los
    # DUR no: la fuente trae erratas de numeración y el orden cortaría artículos
    # legítimos, y un artículo puede acabar en «…así:» antes del siguiente.
    # Sin número (lo previo a la primera ancla) el estilo lo da quien llama.
    cortes, tope, ult = [], orden(num), num
    decimal = "." in num if decimal is None else decimal
    ini = 0
    for m in RE_ART_INLINE.finditer(texto):
        n = re.sub(r"\s", "", m.group(1).strip(".")).lower()
        k = orden(n)
        # El artículo en curso transcribe otros («…los cuales quedarán así:», y entre medio
        # títulos de capítulo): lo que salte lejos del siguiente propio es transcrito, no solo
        # el primero (Decreto 198/2013 transcribe los arts. 23-29 del Decreto 171/2001).
        # Solo saltos grandes: la numeración propia también tiene huecos legítimos (D.L. 2158/1948).
        citando = texto[:m.start()].rstrip(" \n\"“«").endswith(":") or (
            tope and k[0] > tope[0] + 5 and RE_TRANSCRIBE.search(texto, ini, m.start()))
        if n == ult or decimal != ("." in n) or (not decimal and (
                k < tope or (k == tope and n[-1].isdigit())
                or (citando and tope and k != [tope[0] + 1]))):   # sin tope: «DECRETA:» antes del 1
            continue
        cortes.append(m)
        tope, ult, ini = k, n, m.end()
    if not cortes:
        return [(num, epi, texto)]
    salida = [(num, epi, texto[:cortes[0].start()].strip())]
    for k, m in enumerate(cortes):
        fin = cortes[k + 1].start() if k + 1 < len(cortes) else len(texto)
        cuerpo = texto[m.end():fin].strip()
        # "Modificado por el art. 1, Ley 712 de 2001." no es el epígrafe del artículo:
        # arrancarlo como tal le corta el principio al texto.
        e = re.match(r"(?!Modificad|Adicionad|Derogad|Reglamentad|Ver\b)(.{3,120}?)\.\s+", cuerpo)
        salida.append((re.sub(r"\s", "", m.group(1).strip(".")).lower(), " ".join(e.group(1).split()) if e else "",
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
            tipo_a = ACCION[accion.lower()]
            # «Texto subrayado, derogado por…», «Numeral 3 derogado por…»: cae una parte, no
            # el artículo (EOSF art. 75). Mismo criterio que senado: modifica + nota.
            if tipo_a == "deroga" and (RE_PARTE.search(texto, max(0, m.start() - 120), m.start())
                                       or RE_NUMERAL.search(texto[max(0, m.start() - 200):m.start()])):
                tipo_a, nota = "modifica", "; ".join(x for x in (nota, "derogación parcial: " + " ".join(
                    texto[max(0, m.start() - 60):m.end()].split())) if x)
            filas.append((origen, tipo_a, destino, f, nota, fuente))
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
    f, _ = aristas([("75", "", "1. Regla. No podrán pertenecer. Texto subrayado, derogado por el art. 123, "
                          "Ley 510 de 1999. Otro. (Derogado por el art. 2, Ley 9 de 2000)\n6. Delegaciones. Derogado por "
                          "el art. 123, Ley 511 de 1999. El Ministerio")], "co:decreto:663:1993", "x")
    assert [x[1] for x in f] == ["modifica", "deroga", "modifica"] and "parcial" in f[0][4], f

    # Transcripción de artículos de otra norma dentro de uno propio (CPTSS art. 152).
    r = partir("", "", "ARTICULO 152. Conflictos. D.L. 528/64\nARTICULO 13. Corresponde a...\n"
                       "ARTICULO 54 A. Valor probatorio. Texto.")
    assert [x[0] for x in r] == ["152"], r
    r = partir("", "", "ARTICULO 54. Pruebas. Texto.\nARTICULO 54 A. Valor probatorio. Texto.")
    assert [x[0] for x in r] == ["54", "54a"], r

    # El ancla va después de «ARTÍCULO»: no puede quedar colgando del anterior, y el
    # pie del sitio no es texto.
    pie = articulos('<p>ARTÍCULO<a name="1.1.2.1"></a> 1.1.2.1 Fondo uno.</p>'
                     '<p>ARTÍCULO<a name="1.1.2.1"></a> 1.1.2.2. Fondo dos. Texto.</p>'
                     '<a href="javascript:history.back(1)">Volver Atrás</a> MinTIC')
    assert [(a[0], a[2]) for a in pie] == [("1.1.2.1", "1.1.2.1 Fondo uno."),
                                           ("1.1.2.2", "Texto.")], pie

    filas, _ = aristas(arts, "co:decreto:1067:2015", "x")
    assert ("co:decreto:1407:2024:art:1", "modifica",
            "co:decreto:1067:2015:art:2.2.1.1.1") == filas[0][:3], filas[0]
    assert ("co:decreto:484:2026", "deroga",
            "co:decreto:1067:2015:art:2.2.1.1.2") == filas[1][:3], filas[1]
    t = ("Artículo 3°. Modifícase el capítulo II del Decreto 171 de 2001, los cuales quedarán así:\n"
         "CAPÍTULO II\nArtículo 23. Permiso. Uno.\nArtículo 24. Otorgamiento. Dos.\n"
         "Artículo 4°. Modifícase el artículo 43. Tres.\nArtículo 5°. Vigencia. Cuatro.\n")
    assert [a[0] for a in partir("2", "", "Dos.\n" + t, False)] == ["2", "3", "4", "5"], \
        "los artículos transcritos tras «quedarán así:» no son propios"
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
    # La Ley 54 de 1990 (i=30896) marca algunos artículos con `<a id="1">` en vez de
    # `name=`. No se acepta `id=` siempre: los DUR traen cientos sin `name` y cambia su corte.
    p.add_argument("--anclas-id", action="store_true")
    p.add_argument("--enteros", action="store_true", help="decreto que reforma un DUR: los artículos decimales son texto transcrito")
    a = p.parse_args()

    url = BASE % a.i
    doc = bajar(url, enc="utf-8")          # el meta miente: dice ISO-8859-1, es UTF-8
    if a.anclas_id:
        doc = re.sub(r'<a\s+id="([\d.]+)"', r'<a name="\1"', doc, flags=re.I)
    fecha = a.fecha or fecha_norma(doc)
    if not fecha:
        sys.exit("no se pudo leer la fecha en la fuente: pasarla con --fecha")
    arts = articulos(doc, a.enteros)
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
    # «DECRETO 126 DE 2010 (Enero 21) Declarado INEXEQUIBLE…»: la norma entera murió y los
    # artículos no lo dicen. No se adivina la arista: se avisa para ponerla a mano (manual:).
    cab = re.search(r"(?:LEY|DECRETO)[^<]{0,40}?\d+\s+DE\s+\d{4}(.{0,400}?)[\"“]?\s*[Pp]or (?:el|la|medio)\b",
                    " ".join(html.unescape(re.sub(r"<[^>]+>", " ", doc)).split()))
    if cab and re.search(r"derogad|inexequible", cab.group(1), re.I):
        print("Error: el encabezado marca la norma entera:", cab.group(1).strip()[:200],
              "— agregar la arista a nivel de norma (manual:) en relaciones.csv")


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
