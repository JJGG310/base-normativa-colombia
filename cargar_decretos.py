#!/usr/bin/env python3
"""Carga desde el Gestor de Función Pública los decretos y decretos-ley origen que el grafo cita y
aún no están (la parte decreto de `origenes_sin_cargar`), de los más citados a los menos.

    python3 cargar_decretos.py --minimo-aristas 3 --maximo-aristas 7 --limite 10
    python3 cargar_decretos.py --check

El Gestor se busca por `i=`, no por número, y su buscador no sirve: el `i=` sale de los enlaces
`norma.php?i=` de las páginas del Gestor (y de las sentencias) que ya están en fuentes/cache — las
normas que el decreto modifica lo enlazan. Un `i=` solo se usa si el <title> de su página dice el mismo
número y año (y un tipo compatible) y la página está completa (firma al final): nunca se adivina.

El título es «Decreto N de AAAA - <epígrafe de la fuente>»; las ramas, las dos más comunes entre las
normas que el decreto afecta. Cada carga pasa por verificar.py (faltan 0). Lo que no se puede cargar
sin criterio va a `decretos_revisar.txt` con el motivo (como origenes_revisar.txt): sin `i=`, título que
no coincide, página truncada, fecha o epígrafe ilegibles, `faltan` > 0, o una muerte del decreto entero que
no es total y expresa (esas NO se cargan: un decreto muerto cargado como vigente es el peor error posible).
Si el encabezado dice «(Derogado por el Decreto X de AAAA)» o «Declarado INEXEQUIBLE … Sentencia C-N de
AAAA» sin salvedad, y las «Vigencias» del Gestor lo confirman, se carga con `estado_general` y se registra la
arista `manual:`; si es parcial se carga y se lista; tácita, gradual, con salvedad o ambigua: no se carga.
"""
import argparse, csv, html, os, re, shutil, sqlite3, subprocess, sys, tempfile, time

from cargar_origenes import ramas
from ingesta_gestor import BASE, fecha_norma
from ingesta_senado import MESES as MESES_N
from ingesta_senado import bajar, limpiar

RAIZ = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(RAIZ, "fuentes", "cache")
ENLACE = re.compile(r'<a\s[^>]*?href="(?:https?://www\.funcionpublica\.gov\.co/eva/gestornormativo/)?norma\.php\?i=(\d+)[^"]*"[^>]*>(.*?)</a>', re.I | re.S)
DECRETO = re.compile(r"\b(Decreto(?:[\s-]+(?:Ley|Legislativo))?)\s+(?:N[°ºo.]*\s*)?(\d[\d.]*)\s+(?:de|del)\s+(\d{4})", re.I)
# El <title> puede traer la entidad: «Decreto 1098 de 2025 Ministerio de Educación - Gestor Normativo».
TITULO = re.compile(r"<title>\s*(Decreto(?:\s+(?:Ley|Legislativo))?)\s+(\d[\d.]*)\s+de\s+(\d{4})\b[^<]*?-\s*Gestor Normativo", re.I)
# Cierre del decreto: la fórmula de promulgación o «Dado en …» (en línea propia) y, tras ella, una línea de firma
# («(FDO.) IVÁN DUQUE MÁRQUEZ» o un nombre en mayúsculas que no sea un cargo «EL PRESIDENTE…» ni «DADO EN…»).
CIERRE = re.compile(r"(?m)^[ \t]*(?i:publ[ií]quese|com[uú]n[ií]quese|c[uú]mplase|dad[oa]\s*(?:en\b|,))[^\n]*\n(?:.*\n)*?[ \t]*"
                    r"(?:\(FDO\.?\)|(?!(?:EL|LA|LOS|LAS|DAD[OA])\b)[A-ZÁÉÍÓÚÑ]{3,}\s+[A-ZÁÉÍÓÚÑ]{3,})")
NOMBRE = {"decreto": "Decreto", "decreto-ley": "Decreto Ley"}
MESES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre"


def normal(n):
    return n.replace(".", "").lstrip("0")


def pendientes(con, minimo, maximo):
    filas = con.execute("""
        WITH f AS (SELECT CASE WHEN instr(origen, ':art:') > 0 THEN substr(origen, 1, instr(origen, ':art:') - 1)
                               ELSE origen END n FROM relaciones
                   WHERE origen NOT IN (SELECT id FROM fragmentos) AND origen NOT IN (SELECT id FROM documentos))
        SELECT n, count(*) FROM f WHERE (n LIKE 'co:decreto:%' OR n LIKE 'co:decreto-ley:%')
          AND n NOT IN (SELECT id FROM documentos)
        GROUP BY n HAVING count(*) BETWEEN ? AND ? ORDER BY 2 DESC, 1""", (minimo, maximo)).fetchall()
    return [(n, c) for n, c in filas if len(n.split(":")) == 4]


def enlaces(doc):
    """(i, número, año) por cada enlace norma.php?i= cuyo texto nombra un decreto: «Decreto 124 de 2021»."""
    for m in ENLACE.finditer(doc):
        texto = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", m.group(2))).split())
        for k in DECRETO.finditer(texto):
            yield m.group(1), normal(k.group(2)), k.group(3)


def indice_enlaces():
    """{(número, año): {i: veces}} con lo que dicen los enlaces del Gestor en la caché (páginas del Gestor y
    sentencias de la Corte Constitucional que lo citan)."""
    idx = {}
    for f in os.listdir(CACHE):
        ruta = os.path.join(CACHE, f)
        if os.path.getsize(ruta) < 500:
            continue
        with open(ruta, encoding="utf-8", errors="replace") as fh:
            doc = fh.read()
        for i, num, anio in enlaces(doc):
            d = idx.setdefault((num, anio), {})
            d[i] = d.get(i, 0) + 1
    return idx


def titulo_coincide(doc, id_norma):
    """El <title> del Gestor («Decreto Ley 262 de 2000 - Gestor Normativo…») dice el mismo número y año, y un
    tipo compatible: un co:decreto-ley exige «Decreto Ley/Legislativo»; un co:decreto admite los tres."""
    m = TITULO.search(doc)
    _, tipo, num, anio = id_norma.split(":")
    if not m:
        return False
    t = m.group(1).lower()
    return normal(m.group(2)) == num and m.group(3) == anio and (tipo == "decreto" or t != "decreto")


def texto_sin_pie(doc):
    doc = re.sub(r"<style.*?</style>|<script.*?</script>", "", doc, flags=re.S | re.I)
    return limpiar(re.split(r"<a[^>]*javascript:history\.back", doc)[0])


def completo(doc):
    """Falta el cierre (promulgación, «Dado en…», firma) si la fuente cortó la página (Decreto 1934/2015:
    arts. 1-3 de 17 y termina en medio de una fórmula)."""
    t = texto_sin_pie(doc)
    d = re.search(r"(?<![a-záéíóú])DECRETA\b", t)
    return bool(CIERRE.search(t[d.end():] if d else t))


def sin_cargar(doc, arts):
    """Los «ARTÍCULO N» (N entero) de la serie 1..k de la fuente que el .md no tiene. Un encabezado con errata
    («ARTÌCULO 6º», «ARTICULO.6») se funde con el artículo anterior sin que verificar.py lo note, porque el índice
    de la fuente tampoco lo ve. Si la serie la rompe un artículo transcrito de otra norma, es un falso aviso."""
    t = texto_sin_pie(doc)
    d = re.search(r"(?<![a-záéíóú])DECRETA\b", t)
    t = t[d.end():] if d else t
    nums = {int(n) for n in re.findall(r"(?mi)^[ \t\"“]*ART\S{0,3}CULO\s*\.?\s*(\d+)(?![\d.\-])", t)}
    k = 0
    while k + 1 in nums:
        k += 1
    return [n for n in range(1, k + 1) if str(n) not in arts]


def encabezado(doc):
    """(epígrafe, notas): lo que hay entre «DECRETO N DE AAAA (Mes D)» y el primer párrafo del epígrafe
    «Por el cual…», con las notas de vigencia entre paréntesis («(Derogado por el Decreto 821 de 2022)»).
    El título del Gestor escribe a veces «DECETO», «2231 2231» o sin el año: del encabezado solo se exige DEC + número."""
    t = texto_sin_pie(doc)
    t = t[max(0, t.find("actualización de los contenidos.")):]   # tras el aviso del sitio: el título de la página lo repite
    h = re.search(r"(?m)^\s*DEC\w*\s+(?:LEY\s+|LEGISLATIVO\s+)?(?:N[ÚU]MERO\s+)?\d[\d.]*[^\n]*\n", t, re.I)
    if not h:
        return "", ""
    notas, epi = [], ""
    alto = r"(?i)(?:EL |LA )?(?:PRESIDENTE|MINISTR[OA]|DIRECTOR)|DECRETA|CONSIDERANDO|ART[IÍ]CULO"
    for bloque in re.split(r"\n\s*\n", t[h.end():h.end() + 3000]):   # el epígrafe puede venir partido en líneas (Decreto 133/2018)
        lineas = [" ".join(l.split()) for l in bloque.split("\n") if l.strip()]
        if not lineas:
            continue
        p = lineas[0]
        if re.fullmatch(r"\(\s*(?:%s)\s+\d{1,2}\s*\)" % MESES, p, re.I):   # «(Octubre 17)»: la fecha
            continue
        if re.match(r"(?i)[\"“«<\s]*Por\b", p):
            texto = []
            for l in lineas:
                if texto and re.match(alto, l):
                    break
                texto.append(l)
            p = " ".join(texto)
            # Las comillas (o «< <…>>») que encierran todo el epígrafe se quitan; la de un nombre entre comillas al final, no.
            fuera = re.match(r"[\"“«<\s]+", p)
            epi = re.sub(r"[\s.\"”»>]+$", "", p[fuera.end():]) if fuera else p.rstrip(" .")
            break
        if re.match(alto, p):
            break
        notas.append(" ".join(lineas))
    return epi, " ".join(notas)


MUERTE = r"Derogad[oa]|Inexequib|Anulad[oa]|\bNul[oa]\b|Suspendid[oa]|Perdi[óo]|Compilad[oa]|Subrogad[oa]|Sustituid[oa]|Insubsistent|t[áa]cit"
# Una entrada de «Vigencias» que habla de la muerte de ESTA norma («Derogado por …», «Declarado inexequible …»).
ENTRADA = re.compile(r"Derogad\w+(?:\s+parcialmente)?\s+por\b|Declarad\w+\s+(?:inexequible|nul[oa]\w*)|Inexequible|Anulad\w+|Suspendid\w+"
                     r"|Compilad\w+|(?:Subrogad|Sustituid)\w+\s+por\b|Perdi\w+", re.I)
DEROGA = re.compile(r"Derogad[oa]\s+por\s+(?:el\s+|la\s+)?(?:art(?:[íi]culo|\.)\s*([\d.]+)\s+(?:del?\s+)?)?(Decreto(?:\s+Ley)?|Ley)\s+(\d[\d.]*)\s+de\s+(\d{4})", re.I)
INEXEQUIBLE = re.compile(r"Declarad[oa]\s+INEXEQUIBLE\s+por\s+la\s+Corte\s+Constitucional\s+(?:mediante|en)\s+(?:la\s+)?Sentencia\s+C-(\d+)\s+de\s+(\d{4})"
                         r"(?:,\s+como\s+consecuencia\s+de\s+la\s+declaratoria\s+de\s+inexequibilidad\s+del\s+[^()]*)?", re.I)
TIPO_ID = {"decreto": "decreto", "decreto ley": "decreto-ley", "ley": "ley"}


def muerte(notas, vigencias):
    """(muerte, aviso). La muerte del decreto entero solo se registra si el encabezado trae UNA nota que dice,
    sin salvedad, «Derogado por <Decreto|Ley N de AAAA>» o «Declarado INEXEQUIBLE … Sentencia C-N de AAAA», y las
    «Vigencias» del Gestor dicen lo mismo. Cualquier otra mención (parcial, tácita, «salvo», gradual, compilado,
    nulo…) es un aviso: se lista y no se registra. muerte = (estado, tipo de arista, origen, texto de la nota)."""
    notas_muerte, otras = [], []
    for p in re.split(r"\)\s*\(", notas):   # «(Modificado por …) (Derogado por …)»; hay paréntesis sueltos dentro de una nota
        p = " ".join(p.strip("() ").split())
        if re.search(MUERTE, p, re.I):
            notas_muerte.append(p)
        elif p:
            otras.append(p)
    fuera = len(ENTRADA.findall(vigencias))
    if not notas_muerte:
        return None, ("«Vigencias» del Gestor menciona una muerte que el encabezado no: " + vigencias[:200]) if fuera else None
    n = notas_muerte[0]
    d, c = DEROGA.fullmatch(n), INEXEQUIBLE.fullmatch(n)
    if len(notas_muerte) > 1 or not (d or c) or fuera != 1:
        return None, "encabezado: " + " | ".join(notas_muerte)[:300] + (" — Vigencias: " + vigencias[:150] if fuera != 1 else "")
    if d:
        art, tipo, num, anio = d.groups()
        origen = "co:%s:%s:%s" % (TIPO_ID[re.sub(r"\s+", " ", tipo.lower())], normal(num), anio) + (":art:" + art.strip(".") if art else "")
        if not re.search(r"Derogad[oa]\s+por\s+(?:.{0,40}?\b)?%s\s+%s\s+de\s+%s" % (re.escape(tipo), re.escape(num), anio), vigencias, re.I):
            return None, "encabezado dice «%s» pero «Vigencias» no: %s" % (n, vigencias[:200])
        return ("derogada", "deroga", origen, n), None
    if not re.search(r"C-0*%s\b" % c.group(1), vigencias, re.I):
        return None, "encabezado dice «%s» pero «Vigencias» no: %s" % (n, vigencias[:200])
    return ("inexequible", "declara_inexequible", "co:cc:c-%s:%s" % (c.group(1), c.group(2)), n), None


def vigencias(doc):
    """El bloque «Vigencias(n)» del Gestor, antes del aviso del sitio."""
    t = " ".join(texto_sin_pie(doc).split())
    m = re.search(r"Vigencias\s*\(\d+\)(.*?)(?:X -->\s*)?Los datos publicados", t)
    return m.group(1).strip() if m else ""


def fecha_gestor(doc, anio):
    """La fecha del decreto según el Gestor: la del encabezado «(Mayo 26)» (la que lee ingesta_gestor, del texto de
    la norma) o, si el encabezado falla, el campo «Fecha de Expedición: 26 de mayo de 2017» (que a veces difiere
    del texto: Decreto 815/2018, 3 vs 8 de mayo). Solo vale una del año del decreto: el encabezado trae erratas
    («DECRETO 2231 2231» → 2231-12-22) o a veces otro formato («30 ENE 2024»)."""
    m = re.search(r"Fecha de Expedici[óo]n:\s*(\d{1,2}) de (%s) de (\d{4})" % MESES, texto_sin_pie(doc), re.I)
    campo = "%s-%02d-%02d" % (m.group(3), MESES_N[m.group(2).lower()], int(m.group(1))) if m else ""
    return next((f for f in (fecha_norma(doc), campo) if f[:4] == anio), "")


def registrar(raiz, id_norma, m, fecha_origen, fuente):
    """La arista de muerte a nivel de norma, por anadir_aristas.py (candado de relaciones.csv; nota «manual:»).
    La fecha es la del documento origen si está cargado; si no, el 31 de diciembre de su año (aproximada)."""
    nota = "manual: %sencabezado del Gestor: «%s» (y «Vigencias»); %s" % (
        "total — " if m[1] == "declara_inexequible" else "", m[3],
        "fecha del documento origen cargado" if fecha_origen else "fecha aproximada: la fuente solo da el año")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="", encoding="utf-8") as tmp:
        csv.writer(tmp).writerow([m[2], m[1], id_norma, fecha_origen or "%s-12-31" % m[2].split(":")[3], nota, fuente])
    subprocess.run([sys.executable, os.path.join(raiz, "anadir_aristas.py"), tmp.name], cwd=raiz, check=True, capture_output=True)
    os.unlink(tmp.name)


def cargar(id_norma, n, ramas_norma, origenes, idx, fechas, a, revisar):
    """Devuelve (cargado, aristas que resuelven, muerte registrada)."""
    _, tipo, num, anio = id_norma.split(":")
    motivos, doc, elegido = [], None, None
    for i in sorted(idx.get((num, anio), {}), key=lambda k: -idx[(num, anio)][k]):
        try:
            t0 = time.time()
            d = bajar(BASE % i, enc="utf-8")
            if time.time() - t0 > 0.1:   # bajó de la red, no de la caché
                time.sleep(a.pausa)
        except Exception as e:
            motivos.append("i=%s no baja: %s" % (i, " ".join(str(e).split())[:100]))
            continue
        if not titulo_coincide(d, id_norma):
            motivos.append("i=%s: el <title> no es el decreto (%s)" % (i, (re.search(r"<title>[^<]*", d) or [""])[0][7:90]))
        elif not completo(d):
            motivos.append("i=%s: página truncada, sin firma ni cierre del decreto" % i)
        else:
            doc, elegido = d, i
            break

    def listar(motivo):
        revisar.write("%s\t%d aristas\t%s\n" % (id_norma, n, motivo))
        revisar.flush()
        return False, 0, False

    if not doc:
        return listar("; ".join(motivos) or "sin i= en los enlaces de la caché (el buscador del Gestor no sirve)")
    fecha = fecha_gestor(doc, anio)
    if not fecha:
        return listar("i=%s: ni el encabezado ni el campo «Fecha de Expedición» dan una fecha del año del decreto" % elegido)
    epi, notas = encabezado(doc)
    if not epi:
        return listar("i=%s: no se reconoce el epígrafe «Por el cual…» (encabezado raro u OCR): revisar a mano" % elegido)
    m, aviso = muerte(notas, vigencias(doc))
    if m and m[2].split(":")[3] < anio:
        m, aviso = None, "el instrumento que lo derogaría es de un año anterior: " + m[3]
    # Cargarlo como vigente cuando la fuente dice que murió (gradual, con salvedad, tácita…) es el error que este
    # proyecto no se permite: no se carga y un humano decide. Solo la derogación PARCIAL se carga (las notas por artículo la cubren).
    if aviso and not re.search(r"parcial", aviso, re.I):
        return listar("i=%s: NO cargado, la fuente dice que el decreto murió pero no de forma total y expresa (decidir a mano): %s" % (elegido, aviso))
    titulo = "%s %s de %s" % (NOMBRE[tipo], num, anio) + (" - " + epi if epi else "")
    salida = "normativa/%s.md" % id_norma.replace(":", "-")
    cmd = [sys.executable, "ingesta_gestor.py", elegido, "--id", id_norma, "--tipo", tipo, "--minimo", "1",
           "--titulo", titulo, "--ramas", ramas_norma, "--salida", salida, "--fecha", fecha]
    if not any("." in o.split(":art:")[1] for o in origenes if ":art:" in o):
        cmd.append("--enteros")   # un decreto que reforma un DUR: los artículos decimales son texto transcrito
    if m:
        cmd += ["--estado", m[0]]
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True)
    out = r.stdout + r.stderr
    if r.returncode or not os.path.exists(os.path.join(RAIZ, salida)):
        return listar("i=%s: ingesta falló: %s" % (elegido, " ".join(out.split())[-300:]))
    v = subprocess.run([sys.executable, "verificar.py", salida], cwd=RAIZ, capture_output=True, text=True).stdout
    faltan = re.search(r"faltan (\d+)", v)
    avisos = [] if faltan and not int(faltan.group(1)) else ["verificar: " + " ".join(v.split())[:300]]
    with open(os.path.join(RAIZ, salida), encoding="utf-8") as fh:
        arts = {x.lower() for x in re.findall(r"^## art:(\S+)", fh.read(), re.M)}
    perdidos = [] if "--enteros" not in cmd else sin_cargar(doc, arts)
    if perdidos:
        avisos.append("la fuente titula «ARTÍCULO %s» y el .md no lo tiene (¿errata en el encabezado?)" % ", ".join(map(str, perdidos)))
    sin = [o.split(":art:")[1] for o in origenes if ":art:" in o and o.split(":art:")[1].lower() not in arts]
    resuelven = len(origenes) - len(sin)
    if sin:
        avisos.append("%d de %d aristas de origen no resuelven: el .md no tiene el art. %s" % (len(sin), len(origenes), ", ".join(sorted(set(sin)))))
    for linea in out.splitlines():
        if linea.startswith("Error: el encabezado marca la norma entera") and not m and not aviso:
            aviso = linea[:300]
    if aviso:
        avisos.append("derogación parcial según el encabezado (no se registra a nivel de norma): " + aviso)
    if avisos:
        listar("cargado; " + "; ".join(avisos))
    if m:
        registrar(RAIZ, id_norma, m, fechas.get(":".join(m[2].split(":")[:4])), BASE % elegido)
    print("%s (%d aristas, resuelven %d): i=%s %s%s" % (id_norma, n, resuelven, elegido, " | ".join(l for l in out.splitlines() if "->" in l),
                                                      " | MUERTE: %s %s" % (m[1], m[2]) if m else ""), flush=True)
    return True, resuelven, bool(m)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--minimo-aristas", type=int, default=3)
    p.add_argument("--maximo-aristas", type=int, default=7)
    p.add_argument("--limite", type=int, default=100, help="cuántos decretos procesar (los más citados primero)")
    p.add_argument("--pausa", type=float, default=2, help="segundos entre descargas al Gestor (≥ 2)")
    a = p.parse_args()
    ruta_revisar = os.path.join(RAIZ, "decretos_revisar.txt")
    filas = open(ruta_revisar, encoding="utf-8").read().splitlines() if os.path.exists(ruta_revisar) else []
    # Los «sin i=» se reintentan en cada corrida (las páginas que bajó la anterior traen enlaces nuevos); los demás motivos esperan a un humano.
    ya = {f.split("\t")[0] for f in filas if "\tsin i=" not in f}
    # Todo lo que sale de index.db se lee al inicio: build.py lo regenera y puede correr en paralelo.
    con = sqlite3.connect("file:%s?mode=ro" % os.path.join(RAIZ, "index.db"), uri=True)
    fechas = dict(con.execute("SELECT id, fecha FROM documentos WHERE fecha <> ''"))
    lote = []
    for n, c in pendientes(con, a.minimo_aristas, a.maximo_aristas):
        if n in ya or os.path.exists(os.path.join(RAIZ, "normativa", n.replace(":", "-") + ".md")):
            continue
        origenes = [o for (o,) in con.execute("SELECT origen FROM relaciones WHERE origen = ? OR origen LIKE ? || ':art:%'", (n, n))]
        lote.append((n, c, ramas(con, n), origenes))
        if len(lote) == a.limite:
            break
    con.close()
    reintento = {x[0] for x in lote}
    with open(ruta_revisar, "w", encoding="utf-8") as fh:
        fh.write("".join(f + "\n" for f in filas if f.split("\t")[0] not in reintento))
    idx = indice_enlaces()
    tot = [0, 0, 0, 0]   # cargados, aristas que resuelven, aristas de los cargados, muertes registradas
    with open(ruta_revisar, "a", encoding="utf-8") as revisar:
        for id_norma, n, ramas_norma, origenes in lote:
            ok, res, muerta = cargar(id_norma, n, ramas_norma, origenes, idx, fechas, a, revisar)
            tot[0] += ok; tot[1] += res; tot[2] += n * ok; tot[3] += muerta
    print("%d de %d decretos cargados; resuelven %d de %d aristas de origen; %d muertes registradas; el resto en decretos_revisar.txt"
          % (tot[0], len(lote), tot[1], tot[2], tot[3]))


def check():
    # Emparejamiento ID <-> título: número, año y tipo compatible; el <title> puede traer la entidad.
    t = lambda x: "<html><title>%s - Gestor Normativo - Función Pública</title>" % x
    assert titulo_coincide(t("Decreto 1098 de 2025 Ministerio de Educación"), "co:decreto:1098:2025")
    assert titulo_coincide(t("Decreto Ley 262 de 2000"), "co:decreto:262:2000")        # P23: co:decreto ↔ «Decreto Ley»
    assert titulo_coincide(t("Decreto Ley 885 de 2017"), "co:decreto-ley:885:2017")
    assert not titulo_coincide(t("Decreto 885 de 2017"), "co:decreto-ley:885:2017")    # un decreto-ley exige «Ley»
    assert not titulo_coincide(t("Decreto 1098 de 2024"), "co:decreto:1098:2025")      # otro año
    assert not titulo_coincide(t("Decreto 109 de 2025"), "co:decreto:1098:2025")       # otro número
    assert not titulo_coincide(t("Ley 1098 de 2025"), "co:decreto:1098:2025")          # otro tipo
    assert not titulo_coincide(t("No disponible"), "co:decreto:1098:2025")
    # Los enlaces: el texto del ancla nombra el decreto, el href da el i=.
    doc = ('<a href="norma.php?i=241076#">Modificado por Decreto 720 de 2024</a> '
           '<A href="https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=190935#2">Art. 3 Decreto 1.227 de 2022 Ministerio de Trabajo</A> '
           '<a href="norma.php?i=7#1">Sección 5</a> <a href="otro.php?i=9">Decreto 5 de 2000</a>')
    assert list(enlaces(doc)) == [("241076", "720", "2024"), ("190935", "1227", "2022")], list(enlaces(doc))
    # Páginas truncadas: el cierre (promulgación + firma) no está o se corta a medias (Decreto 1934/2015).
    firma = "ARTÍCULO 2. Vigencia. Rige.\n\nPUBLÍQUESE Y CÚMPLASE\n\nDado en Bogotá D.C., a 18 de agosto de 2021\n\nEL PRESIDENTE\n\n(FDO.) IVÁN DUQUE MÁRQUEZ\n"
    assert completo("<p>DECRETA:</p><p>ARTÍCULO 1. Algo.</p><p>" + firma.replace("\n", "</p><p>"))
    assert completo("<p>DECRETA</p><p>x</p><p>COMUNÍQUESE Y CÚMPLASE</p><p>Dado, a los 10 días del mes de octubre de 2024</p><p>EL PRESIDENTE</p><p>GUSTAVO PETRO URREGO</p>")
    assert completo("<p>DECRETA</p><p>ARTÍCULO 9. Rige.</p><p>Dado en Bogotá D.C., a los 20 días de enero de 2020</p><p>EL PRESIDENTE</p><p>(FDO.) IVAN DUQUE</p>")   # sin fórmula (Decreto 64/2020)
    assert not completo("<p>DECRETA:</p><p>ARTÍCULO 1. Algo.</p><p>Pli = Pl’</p>")
    assert not completo("<p>DECRETA:</p><p>ARTÍCULO 1. Se ha dado en Bogotá, así.</p><p>CAPÍTULO PRIMERO</p>")
    assert not completo("<p>DECRETA:</p><p>ARTÍCULO 1. Algo.</p><p>PUBLÍQUESE Y CÚMPLASE</p><p>Dado en Bogotá</p>")
    assert not completo("<p>Por el cual x. Dado en Bogotá, publíquese y cúmplase</p>")
    # Encabezado: epígrafe y notas de vigencia entre la fecha y «Por el cual».
    cab = lambda notas: ("<p>Los datos publicados … actualización de los contenidos.</p>\n<p>DECRETO 934 DE 2021</p>\n<p>(Agosto 18)</p>\n"
                         + notas + '\n<p>"Por el cual se adiciona el capítulo 7."</p>\n<p>EL PRESIDENTE</p>')
    assert encabezado(cab("")) == ("Por el cual se adiciona el capítulo 7", "")
    assert encabezado(cab("<p> (Derogado por el Decreto 821 de 2022)</p>"))[1] == "(Derogado por el Decreto 821 de 2022)"
    vig = "Derogado por Decreto 821 de 2022Adiciona Decreto 1078 de 2015"
    assert muerte("(Derogado por el Decreto 821 de 2022)", vig) == (("derogada", "deroga", "co:decreto:821:2022", "Derogado por el Decreto 821 de 2022"), None)
    assert muerte("(Derogado por el artículo 5 del Decreto Ley 10 de 2020)", "Derogado por Decreto Ley 10 de 2020")[0][2] == "co:decreto-ley:10:2020:art:5"
    assert muerte("(Derogado por el Art. 2 del Decreto 1764 de 2020)", "Derogado por Decreto 1764 de 2020Modifica Decreto 1066 de 2015")[0][2:] == ("co:decreto:1764:2020:art:2", "Derogado por el Art. 2 del Decreto 1764 de 2020")
    assert muerte("(Derogado parcialmente por el Decreto 821 de 2022)", vig)[0] is None      # parcial: se lista
    assert muerte("(Derogado por el Decreto 821 de 2022, salvo el artículo 3)", vig)[0] is None
    assert muerte("(Derogado por el Decreto 821 de 2022)", "Derogado por Decreto 822 de 2022")[0] is None   # Vigencias discrepa
    assert muerte("(Derogado por el Decreto 821 de 2022)", "")[0] is None
    assert muerte("(Derogado por el artículo 5 del Decreto 10 de 2020)", "Derogado por art. 5 de Decreto 10 de 2020")[0][2] == "co:decreto:10:2020:art:5"
    assert muerte("(Modifica parcialmente el Decreto 1083 de 2015, Deroga el Decreto 455 de 2020)", "") == (None, None)   # lo que ESTE decreto hace
    assert muerte("(Modificado por el Decreto 5 de 2020)", "")[0] is None
    assert muerte("", "Derogado por Decreto 5 de 2020")[1], "Vigencias dice muerte y el encabezado no: aviso"
    assert muerte("", "Derogado parcialmente Decreto 1082 de 2015 Sector Planeación") == (None, None)   # efecto de ESTE decreto, no su muerte
    assert muerte("", "Declarado exequible Sentencia C-5 de 2020") == (None, None)
    inex = ("Declarado INEXEQUIBLE por la Corte Constitucional mediante la Sentencia C-276 de 2011, como consecuencia de la "
            "declaratoria de inexequibilidad del Decreto Legislativo 020 de 2011")
    assert muerte("(%s)" % inex, "Declarado inexequible Sentencia C-276 de 2011")[0][:3] == ("inexequible", "declara_inexequible", "co:cc:c-276:2011")
    assert muerte("(Declarado INEXEQUIBLE por la Corte Constitucional mediante la Sentencia C-276 de 2011, con efectos diferidos)", "C-276")[0] is None
    assert muerte("(Declarado NULO por el Consejo de Estado)", "Nulo")[0] is None
    assert muerte("(Declarado EXEQUIBLE por la Sentencia de la Corte Constitucional C-160 de 2020)", "") == (None, None)   # no es una muerte
    assert muerte("(Compilado en el Decreto 1083 de 2015)", "")[0] is None
    assert fecha_gestor("<p>DECRETO 45 DE 2024</p><p>30 ENE 2024</p> Fecha de Expedición: 30 de enero de 2024 ", "2024") == "2024-01-30"
    assert fecha_gestor("<p>DECRETO 45 DE 2024 (Enero 30)</p>", "2024") == "2024-01-30"
    assert fecha_gestor("<p>DECRETO 2231 2231 (Diciembre 22)</p> Fecha de Expedición: 22 de diciembre de 2023", "2023") == "2023-12-22"   # errata de la fuente
    assert fecha_gestor("<p>DECRETO 45 DE 2024 (Enero 30)</p> Fecha de Expedición: 31 de enero de 2024", "2024") == "2024-01-30"   # manda el texto
    assert fecha_gestor("<p>DECRETO 45 DE 2024 (Enero 30)</p>", "2023") == ""
    assert encabezado("<p>actualización de los contenidos.</p>\n<p>DECETO 1252 DE 2021</p>\n<p>(Octubre 12)</p>\n<p>\"Por el cual se modifica.\"</p>")[0] == "Por el cual se modifica"
    assert encabezado('<p>actualización de los contenidos.</p>\n<p>DECRETO 1 DE 2020</p>\n<p>"Por el cual x".</p>')[0] == "Por el cual x"
    assert encabezado('<p>actualización de los contenidos.</p>\n<p>DECRETO 1 DE 2020</p>\n<p>Por el cual se crea la Medalla "Bicentenario"</p>')[0] == 'Por el cual se crea la Medalla "Bicentenario"'
    assert encabezado("<p>actualización de los contenidos.</p>\n<p>DECRETO 133 DE 2018</p>\n<p>(Enero 19)</p>\n<p>Por el cual se modifican\nalgunas disposiciones del\nDecreto 1077 de 2015.</p>\n<p>EL PRESIDENTE</p>")[0] == "Por el cual se modifican algunas disposiciones del Decreto 1077 de 2015"
    assert encabezado("<p>actualización de los contenidos.</p>\n<p>DECRETO 133 DE 2018</p>\n<p>Por el cual x\nEL PRESIDENTE DE LA REPÚBLICA</p>")[0] == "Por el cual x"
    assert encabezado("<p>actualización de los contenidos.</p>\n<p>MINISTERIO DE HACIENDA</p>\n<p>DECRETO 0435</p>\n<p>(24 ABR)</p>\n<p>Por el cual x</p>")[0] == "Por el cual x"
    assert encabezado("<p>actualización de los contenidos.</p>\n<p>DECRETO 1421 DE 2017</p>\n<p>(Agosto 29)</p>\n<p> &lt; &lt; Por el cual se reglamenta&gt;&gt;</p>")[0] == "Por el cual se reglamenta"
    assert muerte("(Derogado por el literal c), art. 626, Ley 1564 de 2012) (Ver otro)", "Derogado por art. 626 de Ley 1564 de 2012")[0] is None   # CPC: gradual
    assert muerte("(Modificado por el Decreto 5 de 2020) (Derogado por el Decreto 821 de 2022)", vig)[0][2] == "co:decreto:821:2022"
    # La muerte registrada: una fila con nota «manual:» en relaciones.csv (en una copia, no en el real).
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(os.path.join(RAIZ, "anadir_aristas.py"), d)
        with open(os.path.join(d, "relaciones.csv"), "w", encoding="utf-8", newline="") as fh:
            fh.write("origen,tipo,destino,fecha,nota,fuente\n")
        m = muerte("(Derogado por el Decreto 821 de 2022)", vig)[0]
        registrar(d, "co:decreto:934:2021", m, None, "https://x/norma.php?i=1")
        registrar(d, "co:decreto:934:2021", m, None, "https://x/norma.php?i=1")   # idempotente
        filas = list(csv.reader(open(os.path.join(d, "relaciones.csv"), encoding="utf-8")))[1:]
        assert len(filas) == 1 and filas[0][:4] == ["co:decreto:821:2022", "deroga", "co:decreto:934:2021", "2022-12-31"], filas
        assert filas[0][4].startswith("manual: encabezado del Gestor: «Derogado por el Decreto 821 de 2022»"), filas
    print("check OK")


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
