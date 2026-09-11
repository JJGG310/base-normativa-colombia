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
ANCLA = re.compile(r'<a class="bookmarkaj" name="([^"]+)"\s*>(.*?)</a>', re.I | re.S)
CAJA = re.compile(r'href="javascript:insRow(\d+)\(\)">([^<]+)</a>', re.I)
MESES = dict(zip("enero febrero marzo abril mayo junio julio agosto septiembre "
                 "octubre noviembre diciembre".split(), range(1, 13)))

ACCION = {"modificado": "modifica", "adicionado": "adiciona", "derogado": "deroga",
          "subrogado": "subroga", "sustituido": "subroga", "suprimido": "deroga", "corregido": "modifica"}   # los yerros se corrigen por decreto y cambian el texto
TIPO_NORMA = {"acto legislativo": "acto-legislativo", "ley": "ley",
              "decreto ley": "decreto-ley", "decreto": "decreto"}

RE_ACCION = re.compile(
    r"(?:Art[íi]culo|Par[áa]grafo|Inciso|Numeral|Literal|Aparte)(?:\s+\S+){0,3}?\s+(%s)\s+por"
    % "|".join(ACCION), re.I)
RE_ORIGEN = re.compile(
    r"(?:el\s+art[íi]culo\s+(?P<art>[\dA-Za-z]+)[o°º]?\.?\s+d[el]{1,2}\s+)?"
    r"(?P<tipo>Acto\s+Legislativo|Ley|Decreto\s+Ley|Decreto)\s+(?:N[o°º]\.?\s*)?(?P<num>[\d\.]+)\s+de\s+(?:\d{1,2}\s+de\s+\w+\s+de\s+)?(?P<anio>\d{4})", re.I)
RE_FECHA = re.compile(r"\bde\s+(\d{1,2})\s+de\s+(%s)\s+de\s+(\d{4})" % "|".join(MESES), re.I)
RE_SENTENCIA = re.compile(r"\b(C|T|SU)-(\d+)-(\d{2})\b")
RE_HISTORICA = re.compile(
    r"(?:Notas?|Texto)\s+correspondiente[s]?\s+al\s+art[íi]culo\s+[\dA-Za-z]+\s+antes\s+de\s+su", re.I)


CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuentes", "cache")


def bajar(url, obligatorio=True):
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
                doc = r.read().decode("iso-8859-1", "replace")
            if len(doc) > 500:
                with open(ruta, "w", encoding="utf-8") as fh:
                    fh.write(doc)
                return doc
            ultimo = "respuesta de %d bytes" % len(doc)
        except Exception as e:
            ultimo = e
        time.sleep(2 * (intento + 1))
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
    f = re.sub(r"<a [^>]*title=\"Ir al inicio\".*?</a>", "", f, flags=re.S)
    f = re.sub(r"<img[^>]*>", "", f)
    f = re.sub(r"</p\s*>|<br\s*/?>", "\n", f, flags=re.I)
    f = re.sub(r"<[^>]+>", "", f)
    f = html.unescape(f)
    f = re.sub(r"[ \t\xa0]+", " ", f)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", f).strip()


def descripciones(js):
    """`insRowNN(){ description[0] = "…" }` -> {NN: texto plano}."""
    salida = {}
    for num, cuerpo in re.findall(r"insRow(\d+)\(\)\s*\{(.*?)\n\}", js, re.S):
        trozos = re.findall(r'description\[\d+\]\s*=\s*"(.*?)";', cuerpo, re.S)
        txt = limpiar(" ".join(trozos).replace('\\"', '"'))
        if txt:
            salida[num] = " ".join(txt.split())
    return salida


def procesar(url):
    """Devuelve (artículos, cajas). Un solo recorrido: el texto y sus notas salen juntos."""
    arts, cajas, huerfanas = [], [], []
    titulo = capitulo = ""
    vistos = set()
    for u, doc in paginas(url):
        desc = descripciones(bajar(u.replace("/basedoc/", "/basedoc/js/").replace(".html", ".js"),
                                  obligatorio=False))
        anclas = list(ANCLA.finditer(doc))
        for k, m in enumerate(anclas):
            nombre = m.group(1).strip()
            encabezado = limpiar(m.group(2))
            fin = anclas[k + 1].start() if k + 1 < len(anclas) else len(doc)

            if re.match(r"^\s*T[IÍ]TULO", encabezado, re.I):
                titulo = " ".join((encabezado + " " + limpiar(doc[m.end():fin])[:120]).split())
                capitulo = ""
                continue
            if re.match(r"^\s*CAP[IÍ]TULO", encabezado, re.I):
                capitulo = " ".join((encabezado + " " + limpiar(doc[m.end():fin])[:120]).split())
                continue
            if re.match(r"^\d", nombre):
                num = nombre.lower()
            elif "TRANSITORIO" in nombre.upper():
                # Los transitorios de los Actos Legislativos (JEP, curules de paz)
                # son derecho vigente; el nombre del ancla dice cuál AL los agregó.
                crudo = re.sub(r"[^a-z0-9\-]+", "-", nombre.lower()).strip("-")
                num = "transitorio-" + re.sub(r"^transitorio-?", "", crudo)
            else:
                continue

            span = doc[m.end():fin]
            cuerpo = limpiar(span)
            if num in vistos or not cuerpo:
                continue
            epi = re.sub(r"^ART[IÍ]CULO\s*(TRANSITORIO)?\s*[\dA-Za-z\-]*[o°º]?\.?\s*",
                         "", encabezado, flags=re.I).strip(" .:-")
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
        if n and int(n.group(1)) > tope:
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
            salida.append((m.group(1).lower(), e, ubicacion, cuerpo))
    return salida


def fecha_de(texto, anio):
    m = RE_FECHA.search(texto)
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
    for num_art, etiqueta, texto in cajas:
        destino = "%s:art:%s" % (id_norma, num_art)

        if etiqueta == "Notas de Vigencia":
            # La fuente mete, en la misma caja, el historial del artículo que ANTES
            # llevaba este número (renumeraciones). Esas notas son de otro artículo,
            # hoy muerto: atribuírselas al vigente le inventa reformas que no tuvo.
            if RE_HISTORICA.search(texto):
                sin_parsear.append((destino, etiqueta + " (histórica, ignorada)", texto[:110]))
                continue
            for trozo in re.split(r"(?=- Art[íi]culo\s)", texto):
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
                filas.append((origen, ACCION[acc.group(1).lower()], destino, f, nota, fuente))

        elif etiqueta == "Jurisprudencia Vigencia":
            for trozo in re.split(r"(?=- (?:La Corte|Art[íi]culo|Aparte|Expresi))", texto):
                s = RE_SENTENCIA.search(trozo)
                if not s:
                    continue
                # Ninguna de estas afecta la vigencia: una remite a otro fallo, la
                # otra es una no-decisión por demanda mal formulada.
                if re.search(r"estarse a lo resuelto|INHIBIDA", trozo, re.I):
                    continue
                alto = trozo.upper()
                if "INEXEQUIBLE" in alto:
                    tipo = ("declara_inexequible_parcial"
                            if re.search(r"\b(la expresi|los apartes?|el aparte|parcialmente)", trozo, re.I)
                            else "declara_inexequible")
                elif "EXEQUIBLE" in alto:
                    tipo = ("declara_exequible_condicionado"
                            if re.search(r"en el entendido|CONDICIONAL|bajo el entendido", trozo, re.I)
                            else "declara_exequible")
                else:
                    sin_parsear.append((destino, etiqueta, trozo[:110]))
                    continue
                f, _ = fecha_de(trozo, s.group(3))
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
    """Idempotente: borra las aristas que apuntan a esta norma y reescribe."""
    ruta = os.path.join(raiz, "relaciones.csv")
    previas = []
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as fh:
            previas = [f for f in csv.reader(fh)
                       if f and f[0] != "origen" and not f[2].startswith(id_norma)]
    with open(ruta, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["origen", "tipo", "destino", "fecha", "nota", "fuente"])
        w.writerows(previas + filas)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    for a in ("id", "tipo", "titulo", "fecha", "ramas", "salida"):
        p.add_argument("--" + a, required=True)
    p.add_argument("--corto", default="")
    p.add_argument("--estado", default="vigente")
    p.add_argument("--minimo", type=int, default=0,
                   help="artículos mínimos esperados; por debajo NO se escribe el archivo")
    a = p.parse_args()
    raiz = os.path.dirname(os.path.abspath(__file__))

    arts, cajas, huerfanas = procesar(a.url)
    if not arts:
        sys.exit("no se extrajo ningún artículo — revisar el formato de la fuente")
    # Última defensa contra el truncamiento silencioso: un corpus legal incompleto
    # que parece completo es peor que no tener el archivo.
    if a.minimo and len(arts) < a.minimo:
        sys.exit("ABORTA: %d artículos, se esperaban al menos %d. No se escribe %s."
                 % (len(arts), a.minimo, a.salida))
    filas, sin_parsear = aristas(cajas, a.id, a.url)

    fm = ["---", "id: " + a.id, "tipo: " + a.tipo, "titulo: " + a.titulo]
    if a.corto:
        fm.append("titulo_corto: " + a.corto)
    fm += ["fecha: " + a.fecha, "ramas: [%s]" % a.ramas, "estado_general: " + a.estado,
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
                         "- Artículo modificado por el artículo 1 del Acto Legislativo 2 de 2003, "
                         "publicado en el Diario Oficial No. 45.406, de 19 de diciembre de 2003.")],
                       "co:constitucion:1991", "x")
    assert filas[0][:4] == ("co:acto-legislativo:2:2003:art:1", "modifica",
                            "co:constitucion:1991:art:82", "2003-12-19"), filas
    # Y las notas del artículo que ANTES llevaba ese número no deben producir ninguna.
    filas, _ = aristas([("261", "Notas de Vigencia",
                         "Notas correspondiente al artículo 261 antes de su derogatoria por el "
                         "Acto Legislativo 2 de 2015: - Artículo modificado por el artículo 10 "
                         "del Acto Legislativo 1 de 2009.")], "co:constitucion:1991", "x")
    assert filas == [], "se atribuyeron reformas históricas al artículo vigente: %r" % (filas,)
    print("check OK")


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
