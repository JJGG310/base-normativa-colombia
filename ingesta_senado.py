#!/usr/bin/env python3
"""Extrae normativa de secretariasenado.gov.co: texto + grafo de afectaciones.

    python3 ingesta_senado.py <url> --id co:constitucion:1991 --tipo constitucion \\
        --titulo "Constitución Política de Colombia" --corto CP \\
        --fecha 1991-07-04 --ramas constitucional --salida normativa/co-constitucion-1991.md

La extracción es MECÁNICA a propósito: el texto pasa de la fuente al archivo sin
pasar por el modelo. Un modelo que "recuerda" el artículo 1502 del Código Civil
escribe algo plausible y equivocado; un script no puede inventar.

Las notas de vigencia no están en el HTML: la página las carga desde un .js hermano
(`js/<pagina>.js`) con funciones `insRowNN()`. De ahí sale `relaciones.csv`. Solo se
emite una arista cuando el patrón se reconoce sin ambigüedad — lo que no se entiende
se cuenta y se reporta, nunca se adivina. Una arista `deroga` inventada es peor que
una faltante: mata un artículo que está vivo.
"""
import argparse, csv, html, os, re, sys, time, urllib.request
from datetime import date

UA = {"User-Agent": "Mozilla/5.0"}
# Muchos artículos no llevan la clase `bookmarkaj` sino un `<A name="63">` pelado (y
# por eso tampoco salen en el selector de la fuente). Leer solo las `bookmarkaj`
# dejaba esos artículos tragados en el span anterior: si ese era un TÍTULO o
# CAPÍTULO, el artículo acababa dentro de la línea `ubicacion:` y desaparecía.
ANCLA = re.compile(r'<a (?:class="bookmarkaj" )?name="([^"]+)"\s*>(.*?)</a>', re.I | re.S)
# Fin de la ley: lo que sigue a las firmas (anexos, la sentencia de revisión del
# proyecto en las estatutarias) no es texto del último artículo.
RE_FIRMAS = re.compile(r"(?im)^\s*El Presidente del? (?:honorable |H\. )?Senado")
CAJA = re.compile(r'href="javascript:insRow(\d+)\(\)">([^<]+)</a>', re.I)
MESES = dict(zip("enero febrero marzo abril mayo junio julio agosto septiembre "
                 "octubre noviembre diciembre".split(), range(1, 13)))

ACCION = {"modificado": "modifica", "adicionado": "adiciona", "derogado": "deroga",
          "subrogado": "subroga", "sustituido": "subroga", "suprimido": "deroga", "corregido": "modifica"}   # los yerros se corrigen por decreto y cambian el texto
TIPO_NORMA = {"acto legislativo": "acto-legislativo", "ley": "ley",
              "decreto ley": "decreto-ley", "decreto": "decreto"}

# El grupo 1 es el alcance: solo «Artículo» afecta al artículo entero. «Parágrafo 4
# derogado» (o la errata «Parágarfo») convertido en `deroga` mataba artículos vivos.
RE_ACCION = re.compile(
    r"(Art[íi]culo|Par[áa]g\w*|Inciso|Numeral|Literal|Aparte|Ordinal|Expresi[óo]n)(?:\s+\S+){0,3}?\s+(%s)\s+por"
    % "|".join(ACCION), re.I)
# Marcador de muerte del artículo entero al inicio de su propio texto en la fuente.
RE_MUERTE_TEXTO = re.compile(r"derogad|suprimid|INEXEQUIBLE|\bNULO\b|^\s*DEROGADO", re.I)
RE_NO_TOTAL = re.compile(r"^\s*(?:Inciso|Numeral|Literal|Par[áa]g|Aparte|Ordinal|Expresi|Texto|El art|Ver )"
                         r"|reviv|en lo |en cuanto|parcial|salvo|excep|CONDICIONAL", re.I)


def muerto_en_texto(texto):
    """¿El texto publicado del artículo abre con un marcador de muerte total?

    La fuente siempre encabeza el artículo derogado con «<Artículo derogado…>». Si no
    lo hace, la nota «Artículo derogado» de la caja es de otro momento: el artículo
    fue re-adicionado (ET 882-916, derogados en 1991 y re-creados en 2016), revivido
    (ET 38, Ley 2010 de 2019) o la nota es de un inciso."""
    m = re.search(r"<([^<>]{0,400})>?", texto[:300])
    s = m.group(1) if m and m.start() < 150 else texto[:60]
    return bool(RE_MUERTE_TEXTO.search(s)) and not RE_NO_TOTAL.search(s)


RE_ORIGEN = re.compile(
    r"(?:el\s+art[íi]culo\s+(?P<art>[\dA-Za-z]+)[o°º]?\.?\s+d[el]{1,2}\s+)?"
    r"(?P<tipo>Acto\s+Legislativo|Ley|Decreto\s+Ley|Decreto)\s+(?:N[o°º]\.?\s*)?(?P<num>[\d\.]+)\s+de\s+(?:\d{1,2}\s+de\s+\w+\s+de\s+)?(?P<anio>\d{4})", re.I)
# «de 27 de diciembre 2019» (sin «de») existe: sin admitirlo se tomaba la fecha
# siguiente de la nota, que suele ser la de una reforma anterior.
RE_FECHA = re.compile(r"\bde\s+(\d{1,2})o?\.?\s+de\s+(%s)\s+(?:del?\s+)?(\d{4})" % "|".join(MESES), re.I)
RE_SENTENCIA = re.compile(r"\b(C|T|SU)-(\d+)-(\d{2})\b")
# La propia fuente lo dice en el epígrafe o el cuerpo del artículo vigente
# ("...anteriormente era el artículo 263-A"): no hace falta adivinar la
# renumeración a partir de las notas de vigencia históricas (ambiguas).
RE_RENUMERA = re.compile(r"anteriormente\s+era\s+el\s+art[íi]culo\s+([\dA-Za-z\-]+)", re.I)
RE_CONCORDANCIA = re.compile(
    r"href=['\"](?P<tipo>ley|decreto|acto_legislativo)_(?P<num>\d+)_(?P<anio>\d{4})"
    r"(?:_pr\d+)?\.html#(?P<anchor>\w+)['\"]", re.I)
# La norma se remite a sí misma con su propio nombre de archivo, sin número
# ("constitucion_politica_1991", "codigo_civil"): sin componente `num`.
RE_CONCORDANCIA_PROPIA = re.compile(
    r"href=['\"]constitucion_politica_(?P<anio>\d{4})(?:_pr\d+)?\.html#(?P<anchor>\w+)['\"]", re.I)
TIPO_CONC = {"ley": "ley", "decreto": "decreto", "acto_legislativo": "acto-legislativo"}
RE_HISTORICA = re.compile(
    r"(?:Notas?|Texto)\s+correspondiente[s]?\s+al\s+art[íi]culo\s+[\dA-Za-z]+\s+antes\s+de\s+su", re.I)


CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuentes", "cache")


def bajar(url, obligatorio=True, enc="iso-8859-1"):
    """Descarga con caché en disco y reintentos.

    Antes esto se tragaba los fallos y devolvía "": una página que no bajaba producía
    un código truncado que parecía completo (el Código Civil salió con 1.810 de 2.682
    artículos sin una sola señal de error). Ahora, si algo es obligatorio y no baja,
    revienta: mejor sin archivo que con un archivo al que le faltan 872 artículos.
    """
    os.makedirs(CACHE, exist_ok=True)
    ruta = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9_.-]", "_", url)[-180:])
    if os.path.exists(ruta) and os.path.getsize(ruta) > 500:
        with open(ruta, encoding="utf-8") as fh:
            return fh.read()
    ultimo = None
    for intento in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                doc = r.read().decode(enc, "replace")
            if len(doc) > 500:
                with open(ruta, "w", encoding="utf-8") as fh:
                    fh.write(doc)
                return doc
            ultimo = "respuesta de %d bytes" % len(doc)
        except urllib.error.HTTPError as e:
            ultimo = e
            if e.code == 404:          # respuesta definitiva: reintentar solo gasta minutos
                break
        except Exception as e:
            ultimo = e
        # La fuente corta la red (ENETUNREACH) tras muchas descargas seguidas y tarda
        # en soltar: esperar 2s no alcanzaba y tumbaba el resto de la tanda.
        time.sleep(20 * (intento + 1))
    if obligatorio:
        raise RuntimeError("no se pudo bajar %s tras 4 intentos: %s" % (url, ultimo))
    print("  sin notas de vigencia para %s: %s" % (url, ultimo), file=sys.stderr)
    return ""


def paginas(url):
    """La fuente pagina como _pr001, _pr002… Se sigue la cadena y se ordena: la
    ubicación (TÍTULO/CAPÍTULO) es estado que cruza páginas."""
    vistas, cola, salida = set(), [url], []
    base = url.rsplit("/", 1)[0] + "/"
    while cola:
        u = cola.pop(0)
        if u in vistas:
            continue
        vistas.add(u)
        doc = bajar(u)
        if not doc:
            continue
        salida.append((u, doc))
        for href in re.findall(r'href="([^"]*_pr\d+\.html)"', doc):
            full = href if href.startswith("http") else base + href.lstrip("./")
            if full not in vistas:
                cola.append(full)
    orden = lambda par: int((re.search(r"_pr(\d+)\.html", par[0]) or [0, 0])[1])
    return sorted(salida, key=orden)


def limpiar(fragmento):
    """Quita los widgets de navegación (tablas vacías que llena el JS) y el marcado."""
    f = re.sub(r'<div><a class="caja_vja_encabezado".*?</table>', "", fragmento, flags=re.S)
    # Cajas editoriales incrustadas («Reglas Jurisprudenciales», «Legislación
    # Anterior», «Nota Aclaratoria»): no son texto del artículo.
    f = re.sub(r'<div class="caja_vja">.*?</div>', "", f, flags=re.S)
    f = re.sub(r"<a [^>]*title=\"Ir al inicio\".*?</a>", "", f, flags=re.S)
    f = re.sub(r"<img[^>]*>", "", f)
    f = re.sub(r"<a class=antsig[^>]*>[^<]*</a>(?:\s*\|\s*<a class=antsig[^>]*>[^<]*</a>)?", "", f)
    # La fuente tacha (<S>) el texto que ya no rige: inexequible, nulo o derogado (el
    # marcador que lo precede dice cuál). Sin marca viajaría como texto vigente.
    f = re.sub(r"<S>(.*?)</S>", r"[TACHADO: \1]", f, flags=re.S | re.I)
    f = re.sub(r"</p\s*>|<br\s*/?>", "\n", f, flags=re.I)
    f = re.sub(r"<[^>]+>", "", f)
    f = html.unescape(f)
    f = re.sub(r"<Ver (?:Notas?|Jurisprudencia)[^<>]{0,80}>", "", f)   # remite a cajas que no viajan
    f = re.sub(r"[ \t\xa0]+", " ", f)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", f).strip()


def descripciones(js):
    """`insRowNN(){ description[0] = "…" }` -> {NN: (texto_limpio, html_crudo)}.

    Se guarda también el HTML crudo porque las cajas "Concordancias" solo traen
    remisiones como `<A href='ley_0388_1997.html#1'>`; limpiar() los reduce a
    texto y el link se pierde.
    """
    salida = {}
    for num, cuerpo in re.findall(r"insRow(\d+)\(\)\s*\{(.*?)\n\}", js, re.S):
        trozos = re.findall(r'description\[\d+\]\s*=\s*"(.*?)";', cuerpo, re.S)
        crudo = " ".join(trozos).replace('\\"', '"')
        txt = limpiar(crudo)
        if txt:
            salida[num] = (" ".join(txt.split()), crudo)
    return salida


def clave(num):
    """Número de artículo como lo pide esquema.md §2: `82a` para el 82A (la fuente
    escribe «82-A», «82 A» o «82A» según la página) y `82-1` para el 82-1."""
    return re.sub(r"-(?=[a-zñ]+$)", "", re.sub(r"\s+", "", html.unescape(num).lower()))


def num_ancla(nombre, encabezado):
    """Número del artículo. Manda el que dice el encabezado: la fuente a veces repite
    un `name` ajeno (el art. 264 del C.C. lleva `name="6"`), y por el nombre el
    artículo chocaba con el 6 y se descartaba como repetido."""
    m = re.match(r"\s*ART[IÍ]CULO\s+(\d+[A-Za-zÑñ\-]*?)[o°º]?\s*\.", encabezado, re.I)
    return clave(m.group(1) if m else nombre)


def procesar(url):
    """Devuelve (artículos, cajas). Un solo recorrido: el texto y sus notas salen juntos."""
    arts, cajas, huerfanas = [], [], []
    titulo = capitulo = ""
    vistos = set()
    for u, doc in paginas(url):
        # Las notas viven en `js/` junto a la página: senado `basedoc/js/x.js`,
        # normograma DIAN `docs/js/x.js` (misma plataforma, extensión .htm).
        desc = descripciones(bajar(re.sub(r"/([^/]+)\.html?$", r"/js/\1.js", u),
                                  obligatorio=False))
        doc = doc.split("<!--Fin documento-->")[0]
        # Las anclas sin clase solo cuentan si son artículos: las hay de índice
        # ("LIBRO I", "TITULO I.") incrustadas a mitad de un artículo. Las `1f`…`6f`
        # del C.Co. son la Ley 1 de 1980 que el editor transcribe: otra norma.
        # Un `bookmarkaj` vacío con nombre de índice («TÍTULO I» a mitad del art. 2 de la Ley
        # 1429/2010, 56 en el PND 2294/2023) no abre nada: contarlo cortaba el artículo ahí.
        anclas = [m for m in ANCLA.finditer(doc)
                  if not re.fullmatch(r"\d+f", m.group(1)) and (
                      ("bookmarkaj" in m.group(0) and (limpiar(m.group(2)).strip() or re.match(r"\d", m.group(1))))
                      or re.match(r"\s*ART", limpiar(m.group(2)), re.I))]
        for k, m in enumerate(anclas):
            nombre = m.group(1).strip()
            encabezado = limpiar(m.group(2))
            fin = anclas[k + 1].start() if k + 1 < len(anclas) else len(doc)
            # `<a name="868">A</a>RTICULO 868.`: el ancla abarca solo la «A». Sin
            # juntarlas, el epígrafe salía «A» y el cuerpo «RTÍCULO…».
            partido = re.match(r"\s*RT[IÍ]CULO\s+[^.]{0,20}\.", limpiar(doc[m.end():fin])) \
                if encabezado == "A" else None
            if partido:
                encabezado = "A" + partido.group(0).strip()

            cuerpo = None
            if re.match(r"^\s*(T[IÍ]TULO|CAP[IÍ]TULO)", encabezado, re.I):
                # Un artículo sin ancla alguna justo tras el encabezado (art. 5 del
                # Código de Policía) no es parte de la ubicación: se rescata.
                resto = limpiar(doc[m.end():fin])
                art = RE_INLINE_LINEA.search(resto)
                fin_cab = re.search(r"(?m)^\s*<?ART[IÍ]CULO", resto)
                cab = " ".join((encabezado + " " + resto[:fin_cab.start() if fin_cab else None][:120]).split())
                if re.match(r"^\s*T[IÍ]TULO", encabezado, re.I):
                    titulo, capitulo = cab, ""
                else:
                    capitulo = cab
                if not art:
                    continue
                num, epi, cuerpo = clave(art.group(1)), "", RE_FIRMAS.split(resto[art.end():])[0].strip()
            elif re.fullmatch(r"(\d+)(?:_T|-A)", nombre, re.I) and not re.match(
                    r"\s*ART[IÍ]CULO\s+<?\d+\s*-?\s*A\b", encabezado, re.I):
                # Disposiciones transitorias con numeración propia: `1_T` (Ley 600),
                # `5-A` bajo «PARTE FINAL. DISPOSICIONES TRANSITORIAS» (Ley 5/1992),
                # con encabezado «ARTÍCULO 5o.». Por el encabezado chocaban con el
                # artículo 5 permanente y se descartaban.
                num = "transitorio-" + re.match(r"\d+", nombre).group(0)
            # Un ancla con nombre ajeno («Nivel001», «TITULO PRE») y encabezado de
            # artículo es un artículo (ET 19-5 y 580-1, C.Co. 508, Ley 142 art. 82).
            elif re.match(r"^\d", nombre) or re.match(r"\s*ART[IÍ]CULO\s+\d", encabezado, re.I):
                # Los planes de desarrollo numeran secciones («2.6 VIVIENDA Y
                # CIUDADES AMABLES», name="2.6-IIIII") con ancla de artículo.
                if re.match(r"\s*\d+(\.\d+)+\s+[^\d\s.]", encabezado):
                    continue
                num = num_ancla(nombre, encabezado) if re.match(r"^\d", nombre) else clave(re.match(
                    r"\s*ART[IÍ]CULO\s+(\d+(?:-\d+)?[A-Za-z]?)(?<![oO])", encabezado, re.I).group(1))
            elif "TRANSITORIO" in nombre.upper():
                # Los transitorios de los Actos Legislativos (JEP, curules de paz)
                # son derecho vigente; el nombre del ancla dice cuál AL los agregó.
                crudo = re.sub(r"[^a-z0-9\-]+", "-", nombre.lower()).strip("-")
                num = ("transitorio-" + re.sub(r"^transitorio-?", "", crudo)).rstrip("-")
            else:
                continue

            span = doc[m.end():fin]
            if cuerpo is None:
                cuerpo = RE_FIRMAS.split(limpiar(span))[0].strip()
                if partido:
                    cuerpo = cuerpo[len(partido.group(0).strip()):].strip()
                epi = re.sub(r"^ART[IÍ]CULO\s*(TRANSITORIO)?\s*[\dA-Za-z\-]*[o°º]?\.?\s*",
                             "", encabezado, flags=re.I).strip(" .:-")
            # Algunos artículos los resuelve la fuente en el propio encabezado
            # ("ARTÍCULO 10. DECLARADO INEXEQUIBLE.") y el cuerpo queda vacío. Sin
            # esto se perdían 22 artículos de la Ley 270 sin una sola señal de error.
            if not cuerpo:
                cuerpo = epi
            trozos = partir_inline(num, epi, " > ".join(x for x in (titulo, capitulo) if x), cuerpo)
            for a in trozos:
                if a[0] in vistos or not a[3]:
                    continue
                vistos.add(a[0])
                arts.append(a)
            if len(trozos) > 1:
                # El span traía varios artículos sin ancla propia. Las cajas van
                # intercaladas y no hay forma fiable de saber a cuál pertenece cada
                # una, así que no se atribuyen: una nota de vigencia en el artículo
                # equivocado es peor que una nota ausente.
                huerfanas.extend(a[0] for a in trozos)
                continue
            for rid, etiqueta in CAJA.findall(span):
                if rid in desc:
                    cajas.append((num, html.unescape(etiqueta).strip(), desc[rid]))
    return arts, cajas, huerfanas


# Un encabezado de artículo sin ancla se reconoce por lo que lo SIGUE, no por dónde
# está: siempre trae su epígrafe en mayúsculas o una nota `<...>`. Exigir principio
# de línea perdía los que la fuente deja a mitad de párrafo (art. 63 del C. Penal).
RE_INLINE_LINEA = re.compile(
    r"(?m)^\.?\s*ART[IÍ]CULO\s+(\d+[A-Za-z\-]*?)[o°º]?\s*\.\s*")
RE_INLINE_PARRAFO = re.compile(
    r"\.\s+ART[IÍ]CULO\s+(\d+[A-Za-z\-]*?)[o°º]?\s*\.\s*"
    r"(?=<|[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ0-9 ,;()/\-]{3,})")


def cortes_inline(texto):
    """Une los dos patrones y descarta solapes, de izquierda a derecha."""
    todos = sorted(list(RE_INLINE_LINEA.finditer(texto)) + list(RE_INLINE_PARRAFO.finditer(texto)),
                   key=lambda m: m.start())
    salida = []
    for m in todos:
        if not salida or m.start() >= salida[-1].end():
            salida.append(m)
    return salida


def separar_epigrafe(cuerpo):
    """El epígrafe suele venir como `<TÍTULO DEL ARTÍCULO>.` al inicio del cuerpo.

    Solo se separa si queda texto detrás. Un artículo derogado dice únicamente
    `<DEROGADO>`: ahí el marcador ES el contenido, y arrancarlo deja el artículo
    vacío, que aguas abajo equivale a borrarlo del corpus.
    """
    for patron in (r"<([^>]{2,120})>\.?\s*",
                   r"([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ0-9 ,;()/\-]{3,110})\.\s+"):
        m = re.match(patron, cuerpo)
        # «<Artículo derogado por…>» detrás del epígrafe es la nota de vigencia, no
        # un epígrafe: arrancarla dejaba vivo un artículo muerto (Ley 1306, 39 arts).
        if m and re.search(r"[a-z]{3}(?:ad|id)[oa]s?\b|INEXEQUIBLE|EXEQUIBLE|\bNULO\b|\bVer\b", m.group(1)):
            break
        if m and cuerpo[m.end():].strip():
            return m.group(1).strip(), cuerpo[m.end():].strip()
    return "", cuerpo


def partir_inline(num, epi, ubicacion, texto):
    """Rescata artículos que la fuente dejó sin ancla `bookmarkaj` y quedaron tragados
    dentro del anterior (pasa con el art. 2 del CPACA y 14 del Código Civil). Solo se
    acepta el corte si el número es mayor que el del artículo contenedor: así una
    remisión a un artículo anterior no se confunde con el encabezado de uno nuevo."""
    cortes = cortes_inline(texto)
    base = re.match(r"^(\d+)", num)
    if not cortes or not base:
        e, cuerpo = separar_epigrafe(texto)
        return [(num, epi or e, ubicacion, cuerpo)]

    validos, tope = [], int(base.group(1))
    for m in cortes:
        n = re.match(r"^(\d+)", m.group(1))
        # Solo el número siguiente, y nunca detrás de «…quedará así:»: un salto o unos
        # dos puntos delatan la transcripción de otra norma (la Ley 222 reescribiendo
        # el art. 100 del C.Co.), no un artículo propio sin ancla.
        previo = texto[:m.start()].rstrip(" \n\"“«")
        if n and int(n.group(1)) == tope + 1 and not previo.endswith(":"):
            validos.append(m)
            tope = int(n.group(1))
    if not validos:
        e, cuerpo = separar_epigrafe(texto)
        return [(num, epi or e, ubicacion, cuerpo)]

    e, cuerpo = separar_epigrafe(texto[:validos[0].start()].strip())
    salida = [(num, epi or e, ubicacion, cuerpo)]
    for k, m in enumerate(validos):
        fin = validos[k + 1].start() if k + 1 < len(validos) else len(texto)
        e, cuerpo = separar_epigrafe(texto[m.end():fin].strip())
        if cuerpo:
            salida.append((clave(m.group(1)), e, ubicacion, cuerpo))
    return salida


def fecha_norma(url):
    """La fecha de expedición sale de la línea del Diario Oficial de la propia fuente.

    Escribirla de memoria sería exactamente lo que este proyecto no hace: es un dato
    verificable y la fuente lo trae. Si no está, el llamador debe pasarla a mano.
    """
    # Sin quitar el CSS, el encabezado de la norma cae más allá del corte en las
    # páginas largas y la fecha se daba por inexistente.
    doc = re.sub(r"<style.*?</style>|<script.*?</script>", "", bajar(url), flags=re.S | re.I)
    t = limpiar(doc)
    # El índice de artículos empuja el encabezado lejos del inicio en las normas
    # largas: se ancla en el título de la norma y se mira solo lo que sigue.
    # El `<LEY>` de "DECRETO <LEY> 2241 DE 1986" sobrevive a limpiar: viene escapado
    # en la fuente y se desescapa después de quitar el marcado.
    h = re.search(r"\b(?:LEY|DECRETO|ACTO LEGISLATIVO)\s*(?:<[^>]*>)?\s+\d+\s+DE\s+\d{4}\b", t)
    t = t[h.start():h.start() + 1500] if h else t[:15000]
    # La fuente escribe la fecha de cuatro maneras: "de 6 de agosto de 1998",
    # "No. 44.097 de 24 de julio del 2000", "de 26 de agosto 2019", "de 1o. de agosto".
    m = re.search(r"Diario\s+Oficial\s+No\.?\s*[\d\.]+\s*,?\s*del?\s*(\d{1,2})o?\.?\s*del?\s*(%s)\s*"
                  r"(?:del?\s*)?(\d{4})" % "|".join(MESES), t, re.I)
    if m:
        return "%s-%02d-%02d" % (m.group(3), MESES[m.group(2).lower()], int(m.group(1)))
    return ""


def fecha_de(texto, anio):
    """Primera fecha de la nota que no sea anterior al año de la norma origen: una
    reforma no surte efecto antes de expedirse."""
    m = next((x for x in RE_FECHA.finditer(texto) if int(x.group(3)) >= int(anio)), None)
    if m:
        return "%s-%02d-%02d" % (m.group(3), MESES[m.group(2).lower()], int(m.group(1))), ""
    return "%s-12-31" % anio, "fecha aproximada: la fuente solo da el año"


def id_sentencia(m):
    """C-076-18 -> co:cc:c-076:2018. La Corte arrancó en 1992, así que 92-99 es siglo XX."""
    serie, num, aa = m.group(1).lower(), m.group(2), int(m.group(3))
    return "co:cc:%s-%s:%d" % (serie, num, 1900 + aa if aa >= 90 else 2000 + aa)


def aristas(cajas, id_norma, fuente):
    """Cajas -> filas de relaciones.csv. Conservador: lo dudoso se descarta y se cuenta."""
    filas, sin_parsear = [], []
    for num_art, etiqueta, (texto, crudo) in cajas:
        destino = "%s:art:%s" % (id_norma, num_art)

        if etiqueta == "Concordancias":
            # Estas cajas no traen prosa, son puros links a otras normas: se leen
            # del HTML crudo, no del texto limpio (limpiar() ya tiró los <A href>).
            vistas = 0
            for m in RE_CONCORDANCIA.finditer(crudo):
                if m.group("anchor") == "0":
                    continue
                origen = "co:%s:%s:%s:art:%s" % (
                    TIPO_CONC[m.group("tipo").lower()],
                    m.group("num").lstrip("0") or "0",
                    m.group("anio"), m.group("anchor").lower())
                filas.append((origen, "concordancia", destino, "", "", fuente))
                vistas += 1
            for m in RE_CONCORDANCIA_PROPIA.finditer(crudo):
                if m.group("anchor") == "0":
                    continue
                origen = "co:constitucion:%s:art:%s" % (m.group("anio"), m.group("anchor").lower())
                if origen != destino:
                    filas.append((origen, "concordancia", destino, "", "", fuente))
                vistas += 1
            if not vistas and texto:
                sin_parsear.append((destino, etiqueta, texto[:110]))
            continue

        if etiqueta == "Notas de Vigencia":
            # La fuente mete, en la misma caja, el historial del artículo que ANTES
            # llevaba este número (renumeraciones). Esas notas son de otro artículo,
            # hoy muerto: atribuírselas al vigente le inventa reformas que no tuvo.
            if RE_HISTORICA.search(texto):
                sin_parsear.append((destino, etiqueta + " (histórica, ignorada)", texto[:110]))
                continue
            for trozo in re.split(r"(?=- (?:Art[íi]culo|Par[áa]g\w*|Inciso|Numeral|Literal|Aparte|Ordinal|Texto)\s)", texto):
                # «Texto vigente antes de la derogatoria … revivido por …»: no es
                # una reforma, es la resurrección del texto; no produce arista.
                if re.search(r"\breviv", trozo, re.I):
                    continue
                acc = RE_ACCION.search(trozo)
                org = RE_ORIGEN.search(trozo[acc.end():]) if acc else None
                if not (acc and org):
                    if acc or "Art" in trozo[:40]:
                        sin_parsear.append((destino, etiqueta, trozo[:110]))
                    continue
                tipo_n = TIPO_NORMA[re.sub(r"\s+", " ", org.group("tipo").lower())]
                # Sin normalizar, "Acto Legislativo 01 de 1999" y "1 de 1999" serían
                # dos nodos distintos de la misma norma, y el grafo se parte en dos.
                num_n = org.group("num").replace(".", "").lstrip("0") or "0"
                origen = "co:%s:%s:%s" % (tipo_n, num_n, org.group("anio"))
                if org.group("art"):
                    origen += ":art:" + re.sub(r"[o°º]$", "", org.group("art").lower())
                f, nota = fecha_de(trozo, org.group("anio"))
                # La fuente marca cuando la norma reformadora fue tumbada: si la
                # reforma cayó, decir "modificado" a secas engañaría.
                if re.search(r"\bINEXEQUIBLE\b", trozo):
                    nota = (nota + "; " if nota else "") + "la fuente marca INEXEQUIBLE sobre esta reforma — verificar si surtió efecto"
                tipo = ACCION[acc.group(2).lower()]
                if tipo == "deroga" and not re.match(r"Art", acc.group(1), re.I):
                    tipo, nota = "modifica", "; ".join(x for x in (
                        nota, "derogación parcial: " + " ".join(trozo.split())[:200]) if x)
                filas.append((origen, tipo, destino, f, nota, fuente))

        elif etiqueta == "Jurisprudencia Vigencia":
            for trozo in re.split(r"(?=- (?:La Corte|Art[íi]culo|Aparte|Expresi))", texto):
                s = RE_SENTENCIA.search(trozo)
                if not s:
                    continue
                # Ninguna de estas afecta la vigencia: una remite a otro fallo, la
                # otra es una no-decisión por demanda mal formulada.
                if re.search(r"estarse a lo resuelto|INHIBIDA", trozo, re.I):
                    continue
                # Revisión previa de estatutarias: la fuente dice (IN)CONSTITUCIONAL, en
                # mayúsculas; sensible a mayúsculas para no confundirlo con «Corte Constitucional».
                alto = re.sub(r"\bCONSTITUCIONAL(ES)?\b", "EXEQUIBLE",
                              re.sub(r"\bINCONSTITUCIONAL(ES)?\b", "INEXEQUIBLE", trozo)).upper()
                if "INEXEQUIBLE" in alto:
                    tipo = ("declara_inexequible_parcial"
                            if re.search(r"\b(las? expresi|los apartes?|el aparte|parcialmente|salvo|excepto)", trozo, re.I)
                            else "declara_inexequible")
                elif "EXEQUIBLE" in alto:
                    tipo = ("declara_exequible_condicionado"
                            if re.search(r"en el entendido|CONDICIONA|bajo el entendido", trozo, re.I)
                            else "declara_exequible")
                else:
                    sin_parsear.append((destino, etiqueta, trozo[:110]))
                    continue
                f, _ = fecha_de(trozo, id_sentencia(s).rsplit(":", 1)[1])
                nota = " ".join(trozo.split())[:300] if tipo in (
                    "declara_exequible_condicionado", "declara_inexequible_parcial") else ""
                filas.append((id_sentencia(s), tipo, destino, f, nota, fuente))

        elif etiqueta in ("Jurisprudencia Concordante", "Jurisprudencia Unificación"):
            for s in RE_SENTENCIA.finditer(texto):
                filas.append((id_sentencia(s), "interpreta", destino, "", "", fuente))

    vistos, unicas = set(), []
    for f in filas:
        clave = (f[0], f[1], f[2])
        if clave not in vistos:
            vistos.add(clave)
            unicas.append(f)
    return unicas, sin_parsear


def guardar_relaciones(raiz, id_norma, filas):
    """Idempotente: borra las aristas que apuntan a artículos de esta norma y
    reescribe. Las aristas a la norma entera (destino == id_norma) y las que tienen
    nota «manual: …» (sacadas a mano de otra fuente) se conservan. Con candado: varias ingestas pueden correr a la vez."""
    import fcntl
    ruta = os.path.join(raiz, "relaciones.csv")
    with open(os.path.join(raiz, ".relaciones.lock"), "w") as candado:
        fcntl.flock(candado, fcntl.LOCK_EX)
        previas = []
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as fh:
                previas = [f for f in csv.reader(fh)
                           if f and f[0] != "origen"
                       and (not f[2].startswith(id_norma + ":") or f[4].startswith("manual:"))]
        with open(ruta, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["origen", "tipo", "destino", "fecha", "nota", "fuente"])
            w.writerows(previas + filas)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    for a in ("id", "tipo", "titulo", "ramas", "salida"):
        p.add_argument("--" + a, required=True)
    p.add_argument("--fecha", default="", help="si se omite, se toma del Diario Oficial de la fuente")
    p.add_argument("--corto", default="")
    p.add_argument("--estado", default="vigente")
    p.add_argument("--minimo", type=int, default=0,
                   help="artículos mínimos esperados; por debajo NO se escribe el archivo")
    a = p.parse_args()
    raiz = os.path.dirname(os.path.abspath(__file__))

    fecha = a.fecha or fecha_norma(a.url)
    if not fecha:
        sys.exit("no se pudo leer la fecha en la fuente: pasarla con --fecha")
    arts, cajas, huerfanas = procesar(a.url)
    if not arts:
        sys.exit("no se extrajo ningún artículo — revisar el formato de la fuente")
    # Última defensa contra el truncamiento silencioso: un corpus legal incompleto
    # que parece completo es peor que no tener el archivo.
    if a.minimo and len(arts) < a.minimo:
        sys.exit("ABORTA: %d artículos, se esperaban al menos %d. No se escribe %s."
                 % (len(arts), a.minimo, a.salida))
    filas, sin_parsear = aristas(cajas, a.id, a.url)
    textos = {"%s:art:%s" % (a.id, x[0]): x[3] for x in arts}
    filas = [f if f[1] != "deroga" or muerto_en_texto(textos.get(f[2], "<derogado>")) else
             (f[0], "modifica", f[2], f[3], "; ".join(x for x in (f[4], (
                 "la nota de vigencia dice «derogado», pero la fuente publica el artículo sin "
                 "marcador de derogatoria (derogación parcial, re-adicionado o revivido)")) if x), f[5])
             for f in filas]
    for num, epi, _, txt in arts:
        m = RE_RENUMERA.search(epi + " " + txt)
        if m:
            viejo = "%s:art:%s" % (a.id, m.group(1).lower())
            filas.append((viejo, "renumera", "%s:art:%s" % (a.id, num), "", "", a.url))

    fm = ["---", "id: " + a.id, "tipo: " + a.tipo, "titulo: " + a.titulo]
    if a.corto:
        fm.append("titulo_corto: " + a.corto)
    fm += ["fecha: " + fecha, "ramas: [%s]" % a.ramas, "estado_general: " + a.estado,
           "afectaciones: " + ("cargadas" if filas else "pendiente"),
           "fuente: " + a.url, "verificado: " + date.today().isoformat(), "---", ""]
    for num, epi, ubicacion, txt in arts:
        fm.append("## art:%s — %s" % (num, epi))
        if ubicacion:
            fm.append("ubicacion: " + ubicacion)
        fm += ["", txt, ""]

    destino = a.salida if os.path.isabs(a.salida) else os.path.join(raiz, a.salida)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(fm))
    guardar_relaciones(raiz, a.id, filas)

    print("%d artículos -> %s" % (len(arts), a.salida))
    print("%d cajas leídas, %d aristas -> relaciones.csv" % (len(cajas), len(filas)))
    if huerfanas:
        print("%d artículos sin ancla propia en la fuente: rescatados del cuerpo del "
              "anterior, pero SIN sus notas de vigencia (no son atribuibles): %s"
              % (len(huerfanas), ", ".join(huerfanas[:12])))
    if sin_parsear:
        print("%d notas no reconocidas (NO se inventaron aristas):" % len(sin_parsear))
        for d, e, t in sin_parsear[:5]:
            print("   %s [%s] %s…" % (d, e, t))


def check():
    """Autotest del corte de artículos. Existe porque este parser ya perdió 823
    artículos en silencio: entregó archivos que se veían correctos, con los artículos
    derogados desaparecidos. Un extractor no falla ruidosamente, hay que interrogarlo."""
    # Un artículo derogado es solo su marcador: no puede quedar vacío ni perderse.
    for texto in ("<DEROGADO>.", "<ARTICULO DEROGADO>", "DEROGADO. "):
        r = partir_inline("30", "", "", texto)
        assert len(r) == 1 and r[0][3].strip(), "artículo derogado perdido: %r -> %r" % (texto, r)

    # Epígrafe sí se separa cuando hay cuerpo detrás.
    r = partir_inline("27", "", "", "<INTERPRETACION GRAMATICAL>. Cuando el sentido sea claro...")
    assert r[0][1] == "INTERPRETACION GRAMATICAL" and r[0][3].startswith("Cuando"), r

    # Artículo sin ancla propia, rescatado del cuerpo del anterior.
    r = partir_inline("1", "FINALIDAD", "", "Texto del uno.\n.ARTÍCULO 2o. ÁMBITO. Texto del dos.")
    assert [x[0] for x in r] == ["1", "2"], r
    assert r[1][1] == "ÁMBITO" and r[1][3] == "Texto del dos.", r

    # Una remisión a un artículo ANTERIOR no puede tomarse por un artículo nuevo.
    r = partir_inline("500", "", "", "Se aplicará lo previsto.\nARTÍCULO 12. no es un encabezado aquí.")
    assert len(r) == 1, "remisión hacia atrás tomada como artículo: %r" % (r,)

    # Una remisión hacia ADELANTE en prosa tampoco: no la sigue un epígrafe.
    r = partir_inline("60", "", "", "Se concederá conforme al artículo 68A de la Ley 599 de 2000, "
                                    "el juez de conocimiento concederá la medida.")
    assert len(r) == 1, "remisión en prosa tomada como artículo: %r" % (r,)

    # Encabezado sin ancla a mitad de párrafo (art. 63 del C. Penal): debe rescatarse.
    r = partir_inline("62", "", "", "Las circunstancias agravantes se comunican. "
                      "ARTÍCULO 63. SUSPENSIÓN DE LA EJECUCIÓN DE LA PENA. <Artículo modificado "
                      "por el artículo 29 de la Ley 1709 de 2014> La ejecución de la pena...")
    assert [x[0] for x in r] == ["62", "63"], r
    assert r[1][1] == "SUSPENSIÓN DE LA EJECUCIÓN DE LA PENA", r[1]

    # Vigencia: una nota estándar debe producir la arista correcta.
    filas, _ = aristas([("82", "Notas de Vigencia",
                         ("- Artículo modificado por el artículo 1 del Acto Legislativo 2 de 2003, "
                         "publicado en el Diario Oficial No. 45.406, de 19 de diciembre de 2003.",) * 2)],
                       "co:constitucion:1991", "x")
    assert filas[0][:4] == ("co:acto-legislativo:2:2003:art:1", "modifica",
                            "co:constitucion:1991:art:82", "2003-12-19"), filas
    # Y las notas del artículo que ANTES llevaba ese número no deben producir ninguna.
    filas, _ = aristas([("261", "Notas de Vigencia",
                         ("Notas correspondiente al artículo 261 antes de su derogatoria por el "
                         "Acto Legislativo 2 de 2015: - Artículo modificado por el artículo 10 "
                         "del Acto Legislativo 1 de 2009.",) * 2)], "co:constitucion:1991", "x")
    assert filas == [], "se atribuyeron reformas históricas al artículo vigente: %r" % (filas,)
    # Transcripción de un artículo de otra norma: no es artículo propio.
    r = partir_inline("1", "", "", "El artículo 100 del Código de Comercio quedará así:\n"
                                   "ARTICULO 100. Se tendrán como comerciales...")
    assert len(r) == 1, "transcripción tomada como artículo: %r" % (r,)
    r = partir_inline("1", "", "", "El artículo 2 de la Ley 5 quedará así:\nARTÍCULO 2. OBJETO. Texto.")
    assert len(r) == 1, "transcripción tomada como artículo: %r" % (r,)

    # Pie de navegación, remisiones a cajas y texto tachado.
    t = limpiar('<p>Texto. &lt;Ver Notas del Editor&gt; Sigue <S>esto cayó</S>.</p>'
                '<p style="x"><a class=antsig href="a.html">Anterior</a> | '
                '<a class=antsig href="b.html">Siguiente</a></p>')
    assert t == "Texto. Sigue [TACHADO: esto cayó].", repr(t)

    # Derogatoria de un inciso/parágrafo no mata el artículo; «revivido» no produce arista.
    filas, _ = aristas([("468", "Notas de Vigencia", (
        "- Parágarfo derogado por el artículo 160 de la Ley 2010 de 2019, publicada en el Diario "
        "Oficial No. 51.179 de 27 de diciembre 2019. - Texto vigente antes de la derogatoria por la "
        "Ley 1943 de 2018 revivido por el artículo 160 de la Ley 2010 de 2019.",) * 2)], "co:d:1:1", "x")
    assert [f[1] for f in filas] == ["modifica"] and "parcial" in filas[0][4], filas
    # El marcador de vigencia detrás del epígrafe se queda en el texto.
    r = partir_inline("2", "LOS SUJETOS", "", "<Artículo derogado por el artículo 61 de la Ley 1996 de 2019> Una persona")
    assert r[0][3].startswith("<Artículo derogado"), r
    assert muerto_en_texto(r[0][3]) and not muerto_en_texto("<Inciso derogado por la Ley 1> Texto")
    assert not muerto_en_texto("<Texto vigente antes de la derogatoria por la Ley 1943 revivido> T")
    assert clave("38-&Ntilde;") == "38ñ", clave("38-&Ntilde;")

    # Año de 2 dígitos de la sentencia: la fecha aproximada debe salir con 4.
    filas, _ = aristas([("9", "Jurisprudencia Vigencia",
                         ("- Artículo declarado EXEQUIBLE por la Corte Constitucional mediante "
                         "Sentencia C-651-97.",) * 2)], "co:ley:84:1873", "x")
    assert filas[0][3] == "1997-12-31", filas
    print("check OK")


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
