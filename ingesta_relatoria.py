#!/usr/bin/env python3
"""Extrae fichas de sentencias de la relatoría de la Corte Constitucional.

    python3 ingesta_relatoria.py co:cc:c-443:2019 co:cc:c-284:2015
    python3 ingesta_relatoria.py --del-grafo --limite 50   # las que ya cita relaciones.csv
    python3 ingesta_relatoria.py --check

Cada sentencia son ~260.000 caracteres: pasarlas por el modelo es inviable y además
innecesario. El texto abre con los **descriptores y restrictores** que escribe la
propia relatoría de la Corte — el resumen oficial, corto y citable — y cierra con el
RESUELVE. Con eso se arma la ficha entera de forma mecánica, sin que nada dependa de
lo que el modelo crea recordar.

La `subregla` redactada (esquema.md §4) NO la produce este script: eso exige leer la
sentencia y se reserva para las marcadas `hito`.
"""
import argparse, html, os, re, sqlite3, sys, time, urllib.error, urllib.request
from datetime import date

RAIZ = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(RAIZ, "fuentes", "cache")
UA = {"User-Agent": "Mozilla/5.0"}
PAUSA = 2.0   # segundos entre peticiones a corteconstitucional.gov.co (--pausa)
BASE = "https://www.corteconstitucional.gov.co/relatoria/%s/%s-%s-%s.htm"

MESES = dict(zip("enero febrero marzo abril mayo junio julio agosto septiembre "
                 "octubre noviembre diciembre".split(), range(1, 13)))
RE_ID = re.compile(r"^co:cc:(c|t|su)-(\d+):(\d{4})$", re.I)


def url_de(sid):
    m = RE_ID.match(sid)
    if not m:
        raise ValueError("id de sentencia no reconocido: %s" % sid)
    # La relatoría rellena el número a tres cifras: C-41 de 2000 vive en C-041-00.htm
    # y sin el relleno devuelve una página de error de 8 KB que parece una sentencia.
    serie, num, anio = m.group(1).upper(), m.group(2).zfill(3), m.group(3)
    # Las SU van sin guion entre serie y número (SU214-16.htm); con guion, el sitio
    # devuelve el cascarón JS de 8 KB con HTTP 200.
    if serie == "SU":
        return BASE.replace("%s-%s-%s", "%s%s-%s") % (anio, serie, num, anio[2:])
    return BASE % (anio, serie, num, anio[2:])


def indice(sid):
    """Hits del índice Elastic de la relatoría para el ID: [(rutahtml, fecha_sentencia)].

    Vacío = la Corte no la tiene publicada (2025-2026 aún sin texto) o la cita está errada
    (C-311/92 no existe). Sin esta consulta, la URL construida devolvía el cascarón SPA de
    8,6 KB con HTTP 200 y quedaba cacheado como si fuera la sentencia."""
    import json, urllib.parse
    m = RE_ID.match(sid)
    q = "%s-%s/%s" % (m.group(1).upper(), m.group(2).zfill(3), m.group(3)[2:])
    u = ("https://www.corteconstitucional.gov.co/relatoria/buscador_new/?accion=search&tipo=json"
         "&searchOption=prov_sentencia&buscar_por=%s&fini=1992-01-01&ffin=2030-12-31&maxprov=5"
         % urllib.parse.quote(q))
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90) as r:
        hits = json.load(r)["data"]["hits"]["hits"]
    # El buscador es difuso («C-99/13» también trae C-990/13): se exige el mismo número y año.
    return [(h["_source"]["rutahtml"], h["_source"].get("prov_f_sentencia") or "") for h in hits
            if h["_source"].get("rutahtml") and re.sub(r"\W", "", h["_source"].get("prov_sentencia", "")).lower()
            == re.sub(r"\W", "", q).lower()]


def bajar(url):
    """Con caché y reintentos, por lo mismo que en ingesta_senado: una descarga que
    falla en silencio produce una ficha vacía que parece una ficha."""
    os.makedirs(CACHE, exist_ok=True)
    ruta = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9_.-]", "_", url)[-180:])
    if os.path.exists(ruta) and os.path.getsize(ruta) > 2000:
        with open(ruta, encoding="utf-8") as fh:
            return fh.read()
    ultimo = None
    for intento in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                doc = r.read().decode("iso-8859-1", "replace")   # la relatoría no es UTF-8
            if "eval(function(p,a,c,k" in doc[:400]:   # desafío anti-bot de 2,4 KB: reintentar
                raise RuntimeError("desafío anti-bot")
            if "data-beasties-container" in doc[:300]:   # cascarón SPA: no es la sentencia
                raise RuntimeError("%s: la Corte devuelve el cascarón SPA (no publicada)" % url)
            if len(doc) > 2000:
                with open(ruta, "w", encoding="utf-8") as fh:
                    fh.write(doc)
                return doc
            ultimo = "respuesta de %d bytes" % len(doc)
        except urllib.error.HTTPError as e:
            # Un 404 no mejora reintentando: la sentencia no está en esa URL.
            if e.code in (404, 410):
                raise RuntimeError("%s: no existe (HTTP %d)" % (url, e.code))
            ultimo = e
        except Exception as e:
            ultimo = e
        time.sleep(2 * (intento + 1))
    raise RuntimeError("no se pudo bajar %s: %s" % (url, ultimo))


def plano(doc):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", doc, flags=re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", t)).split())


# El descriptor es una corrida de MAYÚSCULAS que termina en `-`. No sirve partir por
# `/`: los descriptores consecutivos van pegados, sin separador entre ellos.
# El guion separador aparece de las dos formas: "CONCEPTO- restrictor" y
# "CONCEPTO -restrictor". Exigir solo una perdía un tercio de las fichas.
RE_DESCRIPTOR = re.compile(
    r"(?:^|\s|/)([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ0-9]*(?:\s+[A-ZÁÉÍÓÚÑÜ0-9,.()]+){0,9})\s*-\s*(?=[A-Za-zÁÉÍÓÚÑáéíóúñ])")


def descriptores(txt):
    """El bloque de apertura: `CONCEPTO EN MAYÚSCULAS- restrictor`, uno tras otro."""
    # "Referencia" a veces va ANTES de los descriptores (C-707/05 la trae en la
    # posición 9): solo sirve de frontera si aparece lo bastante adelante.
    corte = txt.find("Referencia")
    cabeza = txt[:corte if 400 < corte < 6000 else 6000]
    marcas = list(RE_DESCRIPTOR.finditer(cabeza))
    salida = []
    for k, m in enumerate(marcas):
        fin = marcas[k + 1].start() if k + 1 < len(marcas) else len(cabeza)
        # La carátula («REPÚBLICA DE COLOMBIA CORTE CONSTITUCIONAL -Sala Plena- SENTENCIA…») cierra
        # el bloque de descriptores; no es un descriptor ni parte del último restrictor.
        restrictor = " ".join(re.split(r"(?i)REPÚBLICA DE COLOMBIA\s+CORTE CONSTITUCIONAL",
                                       cabeza[m.end():fin])[0].strip(" /").split())
        if len(restrictor) > 240:                 # la fuente le pega extractos del cuerpo
            restrictor = restrictor[:240].rsplit(" ", 1)[0] + "…"
        etiqueta = " ".join(m.group(1).split())
        # Encabezados de la propia página, no descriptores de la sentencia.
        if etiqueta in ("TEMAS", "SUBTEMAS", "TEMAS-SUBTEMAS") or restrictor.startswith("SUBTEMAS") \
                or etiqueta.startswith("REPÚBLICA DE COLOMBIA"):
            continue
        if len(restrictor) >= 5:
            salida.append("%s — %s" % (etiqueta, restrictor))
    return salida


def resuelve(txt):
    """La parte resolutiva es la última aparición de RESUELVE **en mayúsculas**.

    No sirve buscar sin distinguir caso: el cuerpo de las providencias dice cosas
    como "resuelve un recurso de casación", y esa prosa se colaba como si fuera la
    decisión (pasó con C-284/15).
    """
    # Las providencias viejas espacian las letras: "R E S U E L V E".
    # Las tutelas de 1992 cierran con «…en nombre del pueblo y por mandato de la Constitución, FALLA:»;
    # el Consejo de Estado, con «FALLA PRIMERO: …» sin dos puntos.
    marcas = [m for m in re.finditer(r"\bR\s?E\s?S\s?U\s?E\s?L\s?V\s?E\b|\bF\s?A\s?L\s?L\s?A\s*:|\bF\s?A\s?L\s?L\s?A\s+(?=PRIMERO|[ÚU]NICO)|\bDECIDE\s*:", txt)]
    if not marcas:
        marcas = [m for m in re.finditer(r"(?i)\bresuelve\b\s*:?\s*(?=PRIMERO|[ÚU]NICO)", txt)]
    if not marcas:
        return ""
    # Tras el fallo suelen venir autos de corrección o de seguimiento con su propio
    # RESUELVE (T-025/04, T-051/10). El del fallo va precedido de la fórmula
    # «administrando justicia en nombre del pueblo»: si está, manda esa.
    formula = [m for m in marcas if "administrando justicia" in txt[max(0, m.start() - 300):m.start()]]
    marca = (formula or marcas)[-1]
    cuerpo = txt[marca.end():]
    # La fórmula de cierre viene también en mayúsculas («CÓPIESE, NOTIFÍQUESE»), y a
    # veces falta: entonces el corte es el primer salvamento/aclaración, cuyo texto
    # («…debió declararse INEXEQUIBLE») no es la decisión de la Sala.
    fin = re.search(r"(?i:Notif[ií]quese|C[óo]piese|C[úu]mplase|Comun[ií]quese)|"
                    r"SALVAMENTO|ACLARACI[OÓ]N DE VOTO|(?:\b[A-ZÁÉÍÓÚÑ]{2,}\s+)*\b[A-ZÁÉÍÓÚÑ]{3,} President[ae]\b", cuerpo)
    return cuerpo[:fin.start() if fin else 4000].strip(" .:-")


# Verbos de la Sala en infinitivo. «que resolvió negar…» describe la instancia, no el fallo.
_NO_INST = r"(?<!resolvió )(?<!decidió )"
# ORDENAR a una parte también es conceder (T-881/02 concede así, sin decir «conceder»);
# «ordenar que se remita…» u ordenarle algo a la Secretaría es trámite, no amparo.
RE_CONCEDE = re.compile(_NO_INST + r"\b(conceder|tutelar|amparar|ordenar(?=\s+al?\s)(?!\s+a\s+la\s+secretar|\s+al\s+secretari))\b"
                        r"|\bse\s+(?:conceden?|tutelan?|amparan?)\b")
RE_NIEGA = re.compile(_NO_INST + r"\b(negar|denegar)\b|\bdeclarar\s+(?:la\s+)?improcedente")
# CONFIRMAR hereda el sentido del fallo confirmado, dicho en la misma frase.
# CONFIRMAR PARCIALMENTE no: la parte revocada puede ir en el otro sentido.
RE_CONF_NIEGA = re.compile(r"\bconfirmar\b(?!\s+parcialmente)[^.]{0,500}?\b(negó|denegó|declaró\s+improcedente|rechaz|improcedente)")
RE_CONF_CONCEDE = re.compile(r"\bconfirmar\b(?!\s+parcialmente)[^.]{0,500}?\b(concedió|amparó|tuteló|accedió|acceder a la tutela)")


def decision_tutela(res):
    """tutela-concede / tutela-niega. Si el RESUELVE trae las dos señales (varios
    expedientes, confirma y a la vez concede otro derecho) o ninguna (carencia de
    objeto, remisiones), devuelve "": ambiguo no se adivina."""
    t = " ".join(res.lower().split())
    concede = RE_CONCEDE.search(t) or RE_CONF_CONCEDE.search(t)
    niega = RE_NIEGA.search(t) or RE_CONF_NIEGA.search(t)
    if concede and not niega:
        return "tutela-concede"
    if niega and not concede:
        return "tutela-niega"
    return ""


def decision_de(res, serie="c"):
    if serie.lower() in ("t", "su"):
        return decision_tutela(res)
    alto = res.upper().translate(str.maketrans("ÁÉÍÓÚ", "AEIOU"))
    # Lo citado entre comillas es el texto de la norma juzgada, no la decisión: un
    # «siempre que» dentro de la expresión demandada no condiciona nada.
    alto = re.sub(r'"[^"]{0,400}"|«[^»]{0,400}»|“[^”]{0,400}”', " ", alto)
    alto = re.sub(r"\bIN\s+EXEQ", "INEXEQ", alto)       # «IN EXEQUIBLE» (C-296/19)
    # «Estarse a lo resuelto en la C-1056/03, que declaró inexequible…» cuenta lo que
    # hizo OTRA sentencia, no esta: el pretérito siempre es una sentencia anterior.
    alto = re.sub(r"\bDECLAR(?:O|ARON)\b(?:(?!EN CONSECUENCIA)[^.;])*", " ", alto)
    # Los decretos legislativos y las objeciones se fallan con «(IN)CONSTITUCIONAL».
    consti = r"(?:DECLAR\w*|ES|SON)\s+(?:LA\s+|SU\s+)?"
    inex = re.search(r"INEXEQ|" + consti + r"INCONSTITUCIONAL", alto) is not None
    # "EXEQUIBLE" es subcadena de "INEXEQUIBLE": sin el lookbehind, un fallo que
    # declara exequible se clasificaba como inexequible (pasó con C-951/14).
    exeq = re.search(r"(?<!IN)EXEQ|" + consti + r"CONSTITUCIONAL", alto) is not None
    # «siempre que» también puede ser parte de la expresión juzgada cuando la fuente no
    # la entrecomilla (C-019/04, C-576/04): solo cuenta tras EXEQUIBLE, sin que medie
    # «la expresión…», y tras coma o tras la cita de la norma; o si dice «se entienda».
    cond = re.search(r"CONDICIONAD|CONDICIONAMIENTO(?![^.;]{0,60}SENTENCIA C)|SE CONDICIONA|EL ENTENDIDO|ES ENTENDIDO QUE|"
                     r"SIEMPRE (?:Y CUANDO|QUE) SE ENTIENDA|"
                     r"(?<!IN)EXEQ(?:(?!EXPRESI|FRASE)[^.;]){0,300}?(?:,|DE \d{4}|LEY \d+)\s*SIEMPRE (?:Y CUANDO|QUE)",
                     alto) is not None
    if inex and (cond or exeq):
        return "inexequible-parcial"
    if inex:
        return "inexequible"
    if cond:
        return "exequible-condicionado"
    if exeq:
        return "exequible"
    if "INHIBIRSE" in alto or "INHIBIDA" in alto:
        return "inhibitoria"
    if re.search(r"EST(?:ESE|ARSE)\s+A\s+LO\s+(?:RESUELTO|DECIDIDO|DISPUESTO)", alto):
        return "estese-a-lo-resuelto"
    return ""


# Una palabra de nombre propio (o una inicial «S.»), y las que cortan el nombre.
NOMBRE = r"[A-ZÁÉÍÓÚÑ]\.|[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñü]+"
MAYUS = r"[A-ZÁÉÍÓÚÑ]\.|[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑÜ]+(?![a-záéíóúñ])"
ALTO = (r"(?i:bogot|santa|sentencia|acta|aprobad|referencia|expediente|temas?\b|s[ií]ntesis|dra?\b|"
        r"doctor|me\b|en\b|aclar|salv|magistrad|cartagena)|Con\b|I\b|La\b")

def metadatos(txt, anio=""):
    meta = {}
    m = re.search(r"Expediente[s]?:?\s*([A-Z]{1,3}-[\d\.]+(?:\s*(?:y|,)\s*[A-Z]{0,3}-?[\d\.]+)*)", txt)
    if m:
        meta["expediente"] = " ".join(m.group(1).split())
    # El nombre puede venir precedido de "Dr."/"Dra.", cuyo punto cortaba la captura.
    m = re.search(r"Magistrad[oa]s?\s+(?:Ponente|Sustanciador[a]?)\s*:?\s*(?:Dra?\.?\s*)?"
                  r"([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{6,60}?)\s*(?:\.|,|Bogot|Santaf|La\s+Sala|SENTENCIA|I\.\s)", txt)
    # Si no: «Magistrada ponente (E): Dra. Carmenza Isaza de Gómez», nombres en
    # minúscula, «Doctor», «DR.», dos ponentes. Aquí sí se exige «:» — sin él, lo que
    # sigue suele ser la fila de firmas, donde el nombre vecino es de otro magistrado.
    m = m or re.search(
        r"Magistrad[oa]s?\s+(?:[Pp]onentes?|PONENTE|[Ss]ustanciador[a]?)\s*(?:\([Ee]\))?\s*:\s*"
        r"(?:(?:Doctor[a]?|D[Rr][Aa]?)\s*\.?\s*)?((?:%s)(?:\s+(?:(?:DE|DEL|Y|de|del|y)\s+)?(?!%s)(?:%s)){1,5}\b(?![a-záéíóúñ])"
        r"|(?:%s)(?:\s+(?:(?:de|del|y)\s+)?(?!%s)(?:%s)){1,5})"
        % ((MAYUS, ALTO, MAYUS, NOMBRE, ALTO, NOMBRE)), txt)
    if m:
        meta["ponente"] = re.sub(r" (De|Del|Y) ", lambda x: x.group().lower(),
                                 " ".join(m.group(1).split()).title())
    f = fecha_en(txt, anio)
    if f:
        meta["fecha"] = f
    meta["sala"] = "plena" if re.search(r"\bSala\s+Plena\b", txt) else (
        "revision" if re.search(r"Sala\s+\w+\s+de\s+Revisi", txt) else "plena")
    return meta


_UNI = ("uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince "
        "dieciseis diecisiete dieciocho diecinueve veinte veintiuno veintidos veintitres "
        "veinticuatro veinticinco veintiseis veintisiete veintiocho veintinueve").split()


def _anio_en_letras(a):
    a = int(a)
    if 1991 <= a <= 1999:
        return "mil novecientos noventa y " + _UNI[a - 1991]
    return "dos mil" + ("" if a == 2000 else " " + _UNI[a - 2001])


def fecha_en(txt, anio):
    """Fecha de la providencia: la que sigue a «Bogotá[, D.C.],» en el encabezado.

    Se exige el año del ID: la fecha de un fallo citado o de la sentencia de instancia
    («Tribunal de Bogotá, el 30 de noviembre de 2021») casi nunca coincide con él, y si
    ninguna ventana da ese año se devuelve "" — sin fecha es honesto, con la equivocada no.
    Formatos vistos: «veinte (20) de septiembre de dos mil veintitrés (2023)», «febrero
    catorce (14) del año dos mil uno (2001)», «Septiembre 30 de 1993», «29 de febrero de
    mil novecientos noventa y seis», «primero (1º) de febrero de ...».
    """
    if not anio:
        return ""
    plano_ = " ".join(txt.split())
    sin_tilde = plano_.lower().translate(str.maketrans("áéíóú", "aeiou"))
    # Encabezado sin año, «Sentencia C-008/10 (Enero 14; Bogotá D.C.)» o «(27 de
    # noviembre)»: si el número y el año corto son los del propio fallo, el año es el del ID.
    h = re.search(r"sentencia\s+[a-z]+-?\d+/(\d\d)\s*\(([^)]{3,40})\)", sin_tilde[:3000])
    if h and h.group(1) == str(anio)[2:] and not re.search(r"\d{4}", h.group(2)):
        m = re.search(r"(?:(\d{1,2})\s*(?:de\s+)?)?(%s)\s*(\d{1,2})?" % "|".join(MESES), h.group(2))
        dia = m and (m.group(1) or m.group(3))
        if dia and 1 <= int(dia) <= 31:
            return "%s-%02d-%02d" % (anio, MESES[m.group(2)], int(dia))
    # Hasta los ANTECEDENTES todo es encabezado: una fecha con otro año ahí (la de la
    # demanda o la del auto admisorio) no descarta la siguiente. Más abajo, sí.
    limite = sin_tilde.find("antecedentes") % (len(sin_tilde) + 1)
    dias = "|".join(sorted(_UNI + ["treinta y uno", "treinta"], key=len, reverse=True))
    # Ancla: «Bogotá[, D.C.],», el encabezado «Sentencia C-012/13 (23 de enero de 2013)»,
    # la ciudad tras el acta cuando la Sala sesiona fuera («Acta 16 Sincelejo, …»), o la
    # sesión que aprobó el fallo («acta número tres (3), … llevada a cabo el día …»).
    for b in re.finditer(r"bogot[aá]?\b|sentencia aprobada|sentencia [a-z]+-\d+/\d\d\s*\(|"
                         r"\bacta\s+(?:n\S*\s*)?\d+\s+[a-zñ ()]{3,60}\.?,|llevada a cabo|"
                         r"sesion (?:de la sala plena,? )?del dia|mediante acta del", sin_tilde):
        # «llevada a cabo el 21 de marzo, resolvió acumular» (C-107/18) es otra sesión: el
        # acta solo vale en el encabezado. Y «Tribunal … de Bogotá el 4 de febrero» es
        # la fecha del fallo de instancia (T-414/92), no la de este.
        if b.group()[0] in "lsm" and not b.group().startswith("sentencia") and b.start() > limite:
            continue
        if b.group().startswith("bogot") and re.search(r"(?:tribunal|juzgado|circuito|distrito)\b[^.,;:]{0,50}$",
                                                        sin_tilde[max(0, b.start() - 80):b.start()]):
            continue
        w = sin_tilde[b.end():b.end() + 200]
        m = re.search("|".join(MESES), w)
        if not m or m.start() > 110:
            continue
        antes, despues = w[:m.start()], w[m.end():]
        # Sin año a la vista («(Bogotá DC, febrero 25)») no es el encabezado: siguiente.
        if not re.match(r".{0,80}?\b\d{4}\b|.{0,40}\bmil\b", despues):
            continue
        # La primera ventana con día, mes y año decide: si no cuadra, no se busca otra
        # más abajo, porque las de más abajo son fechas citadas (la demanda, el decreto).
        d = re.search(r"(?:\(\s*(\d{1,2})\s*\.?\s*(?:er|[º°o])?\s*\)|\b(\d{1,2})\s*[º°]?|(primero)|\b(%s))\s*,?\s*"
                      r"(?:dias\s+)?(?:del mes\s+)?(?:de\s*)?$" % dias, antes)
        if not d:  # «febrero 25 de 2009», «febrero catorce (14) del año ...»
            d = re.match(r"\s*(?:[a-z ]{0,25}\()?(\d{1,2})\)?", despues)
            if d:
                despues = despues[d.end():]
        if not d:
            return ""
        g = next(x for x in d.groups() if x)
        dia = 1 if g == "primero" else int(g) if g.isdigit() else (_UNI + ["treinta", "treinta y uno"]).index(g) + 1
        dia = 30 if g == "treinta" else 31 if g == "treinta y uno" else dia
        # El año en letras o en cifras: basta uno. «dos mil veintitrés (2022)» (SP251-2023)
        # es errata de la cifra; el ID y las letras coinciden.
        y = re.match(r"[^\d]{0,70}?\b(\d{4})\b", despues)
        ok = (y is not None and y.group(1) == str(anio)) or re.match(
            r"[\s,]*(?:de[l]?\s+)?(?:a[ñn]o\s+)?(?:de\s+)?" + _anio_en_letras(anio) + r"\b", despues) is not None
        if not ok and b.start() < limite:
            continue
        return "%s-%02d-%02d" % (anio, MESES[m.group()], dia) if ok and 1 <= dia <= 31 else ""
    return ""


def ramas_de(sid, con):
    """La sentencia hereda las ramas de los artículos que toca. Sale del grafo, no
    de una opinión sobre de qué 'trata' el fallo."""
    if not con:
        return []
    # La ficha no depende de la base: si index.db está a medio construir, la sentencia
    # se guarda igual sin ramas. Perder 239 fichas por un build simultáneo no tiene
    # sentido: las ramas se recalculan en el siguiente build.
    try:
        filas = con.execute("""SELECT DISTINCT d.ramas FROM relaciones r
            JOIN fragmentos f ON f.id = r.destino JOIN documentos d ON d.id = f.doc_id
            WHERE r.origen = ?""", (sid,)).fetchall()
    except sqlite3.DatabaseError:
        return []
    ramas = sorted({x.strip() for (r,) in filas for x in (r or "").split(",") if x.strip()})
    return ramas


def ficha(sid, con=None):
    hits = indice(sid)
    if not hits:
        raise RuntimeError("no está en el índice de la Corte (no publicada o cita errada)")
    time.sleep(PAUSA)
    url = "https://www.corteconstitucional.gov.co/relatoria/" + hits[0][0]
    txt = plano(bajar(url))
    desc, res = descriptores(txt), resuelve(txt)
    if not desc and not res:
        raise RuntimeError("%s: ni descriptores ni parte resolutiva — revisar la fuente" % sid)
    meta = metadatos(txt, sid.rsplit(":", 1)[1])
    # Si el año de la fecha no coincide con el del ID, la página no es la sentencia
    # que se pidió (suele ser un auto de corrección posterior). Sin fecha es honesto;
    # con la fecha equivocada, no: C-105/94 quedó fechada en 1995 por esto.
    anio_id = sid.rsplit(":", 1)[1]
    if meta.get("fecha") and not meta["fecha"].startswith(anio_id):
        meta["aviso"] = "la fuente trae fecha %s, distinta del año del ID" % meta.pop("fecha")
    ramas = ramas_de(sid, con)
    serie = RE_ID.match(sid).group(1).lower()

    fm = ["---", "id: " + sid, "tipo: sentencia", "corporacion: corte-constitucional",
          # Las T las decide siempre una Sala de Revisión; «Sala Plena» en el texto
          # suele ser una cita (T-025/04 quedó como plena por eso).
          "sala: " + ("revision" if serie == "t" else meta.get("sala", "plena")),
          "titulo: Sentencia %s de %s" % (sid.split(":")[2].upper(), sid.split(":")[3])]
    for k in ("ponente", "fecha", "expediente"):
        if meta.get(k):
            fm.append("%s: %s" % (k, meta[k]))
    fm += ["ramas: [%s]" % ", ".join(ramas or ["constitucional"]),
           "decision: " + (decision_de(res, serie) or "sin-determinar"),
           "afectaciones: cargadas",
           "fuente: " + url, "verificado: " + date.today().isoformat(), "---", ""]
    if meta.get("aviso"):
        fm.insert(-2, "aviso: " + meta["aviso"])
    if desc:
        fm += ["## descriptores", "", "\n".join("- " + d for d in desc), ""]
    if res:
        fm += ["## resuelve", "", res, ""]
    return "\n".join(fm), meta, len(desc)


def check():
    """Verifica el parseo sobre texto fijo: sin red, sin depender de la Corte."""
    txt = ("C-443-19 Sentencia C-443/19 DEMANDA DE INCONSTITUCIONALIDAD- Competencia de la "
           "Corte Constitucional ACCESO A LA ADMINISTRACION DE JUSTICIA- Garantía del plazo "
           "razonable para adelantar etapas/ LEGISLADOR- Amplio margen de configuración "
           "Referencia: Expediente D-12981 Demanda de inconstitucionalidad contra el artículo "
           "121 (parcial) del Código General del Proceso Actor: Eulin Abreo Magistrado "
           "Sustanciador: LUIS GUILLERMO GUERRERO PÉREZ Bogotá D. C., veinticinco (25) de "
           "septiembre de dos mil diecinueve (2019) La Sala Plena resolvió. RESUELVE se cita "
           "aquí en el cuerpo. Luego mas texto. RESUELVE PRIMERO.- DECLARAR LA INEXEQUIBILIDAD "
           "de la expresión de pleno derecho, y la EXEQUIBILIDAD CONDICIONADA del resto, en el "
           "entendido de que la nulidad debe alegarse. Notifíquese y cúmplase")
    d = descriptores(txt)
    assert len(d) >= 3, d
    # La otra forma del separador, y "Referencia" antes de los descriptores.
    otra = ("C-050-24 TEMAS-SUBTEMAS Sentencia C-050/24 PRINCIPIO DE IGUALDAD EN MATERIA PENAL "
            "-No se vulnera en norma que establece rebaja punitiva DEBIDO PROCESO -Alcance")
    d2 = descriptores(otra)
    assert any(x.startswith("PRINCIPIO DE IGUALDAD EN MATERIA PENAL —") for x in d2), d2
    assert d[0].startswith("DEMANDA DE INCONSTITUCIONALIDAD —"), d[0]
    assert descriptores("C-017-26 TEMAS-SUBTEMAS Sentencia C-017/26 PRINCIPIO PRO PERSONA -Aplicación REPÚBLICA DE "
                        "COLOMBIA CORTE CONSTITUCIONAL Sala Plena SENTENCIA C-017 de 2026") == ["PRINCIPIO PRO PERSONA — Aplicación"]
    assert not descriptores("C-117-26 REPÚBLICA DE COLOMBIA CORTE CONSTITUCIONAL -Sala Plena- SENTENCIA C-117 "
                            "DE 2026 Referencia: Expediente D-16.917. Asunto: Demanda de inconstitucionalidad"), "membrete"

    r = resuelve(txt)
    assert r.startswith("PRIMERO.- DECLARAR LA INEXEQUIBILIDAD"), r[:80]
    assert "Notifíquese" not in r, "la fórmula de cierre no va en la parte resolutiva"
    assert resuelve("RESUELVE PRIMERO.- Declarar EXEQUIBLE el art. 5 del Código Civil. JORGE IVÁN PALACIO "
                    "PALACIO Presidente Con aclaración") == "PRIMERO.- Declarar EXEQUIBLE el art. 5 del Código Civil"
    assert "se cita aquí en el cuerpo" not in r, "se tomó un RESUELVE del cuerpo, no el final"

    assert decision_de(r) == "inexequible-parcial", decision_de(r)
    assert decision_de("DECLARAR EXEQUIBLE el artículo") == "exequible"
    # "EXEQUIBLE" vive dentro de "INEXEQUIBLE": no puede confundirlos.
    assert decision_de("Declarar INEXEQUIBLE el artículo 5") == "inexequible"
    assert decision_de("Primero.- Declarar EXEQUIBLE el Proyecto de Ley Estatutaria") == "exequible"
    assert decision_de("PRIMERO. INEXEQUIBLE el inciso 2. SEGUNDO. EXEQUIBLE el resto") == "inexequible-parcial"
    # Errata de la fuente: "INEXEQIBLES" sin la U (C-990/06).
    assert decision_de("Declarar INEXEQIBLES las expresiones fijada por peritos") == "inexequible"

    # Fórmula resolutiva con letras espaciadas, propia de las providencias viejas.
    viejo = ("texto del cuerpo. R E S U E L V E : Declarar EXEQUIBLES los artículos 828 del "
             "Decreto 410 de 1971. Notifíquese")
    rv = resuelve(viejo)
    assert rv.startswith("Declarar EXEQUIBLES"), rv[:60]
    assert decision_de(rv) == "exequible", decision_de(rv)
    assert decision_de("INHIBIRSE de emitir pronunciamiento") == "inhibitoria"
    assert decision_de("Declarar EXEQUIBLE el artículo 4º, siempre y cuando se entienda que") == "exequible-condicionado"
    assert decision_de('Declarar EXEQUIBLE la expresión "siempre que el deudor pague"') == "exequible"
    assert decision_de("Declarar INEXEQUIBLE la expresión siempre que éste exceda de tres meses") == "inexequible"
    assert decision_de("Declárase CONSTITUCIONAL el Decreto 333 de 1992") == "exequible"
    assert decision_de("Declarar la INCONSTITUCIONALIDAD del Proyecto de Ley") == "inexequible"
    assert decision_de("Estése a lo decidido en la sentencia C-176 de 1993") == "estese-a-lo-resuelto"
    assert decision_de("Declarar IN EXEQUIBLE la expresión") == "inexequible"
    assert decision_de("ESTARSE A LO RESUELTO en la C-1056 de 2003, que declaró la inconstitucionalidad del art 18") == "estese-a-lo-resuelto"
    assert decision_de("ESTARSE A LO RESUELTO en la C-599 de 1992 que declaró exequibles los arts 19, y en consecuencia declarar EXEQUIBLES los arts 24") == "exequible"
    assert decision_de("Declarar EXEQUIBLE el literal b) del artículo 24 de la ley 1564 siempre y cuando la estructura") == "exequible-condicionado"
    assert decision_de("Declarar EXEQUIBLE la expresión 87.9 Las entidades podrán aportar bienes, siempre y cuando su valor") == "exequible"
    assert decision_de("Declarar EXEQUIBLE la expresión siempre que esté debidamente ejecutoriada") == "exequible"
    assert decision_de("Declarar la EXEQUIBILIDAD del artículo 2°, en los términos del condicionamiento precisado") == "exequible-condicionado"
    assert decision_de("Estarse a lo resuelto en la C-339 de 2002 mediante la cual se declaró exequible el inciso 1; se declaró exequible el inciso 2, en el entendido que X. SEGUNDO. Declarar exequible el artículo 34") == "exequible"
    assert decision_de("Declarar EXEQUIBLE el inciso final, en armonía con el condicionamiento efectuado en la Sentencia C-177/00") == "exequible"
    assert decision_de("NEGAR la solicitud de corrección de la Sentencia C-029") == ""

    # Tutelas: el sentido sale del verbo de la Sala, no de lo que hizo la instancia.
    assert decision_de("PRIMERO.- REVOCAR la decisión que negó por improcedente el amparo. "
                       "En su lugar, CONCEDER el amparo impetrado.", "t") == "tutela-concede"
    assert decision_de("Primero.- Confirmar la sentencia del Juzgado, mediante la cual "
                       "rechaza las pretensiones", "t") == "tutela-niega"
    assert decision_de("REVOCAR las sentencias. En su lugar, NEGAR el amparo", "t") == "tutela-niega"
    assert decision_de("CONFIRMAR el fallo que revocó el del a quo y amparó el derecho", "t") == "tutela-concede"
    assert decision_de("REVOCAR el fallo que resolvió negar por improcedente la tutela", "t") == ""
    assert decision_de("DECLARAR la carencia actual de objeto", "t") == ""
    assert decision_de("CONFIRMAR los fallos. Segundo. ORDENAR que se remita copia", "t") == ""
    assert decision_de("CONFIRMAR PARCIALMENTE la sentencia que negó el amparo", "t") == ""
    assert decision_de("CONDENAR a las IPS y médicos que negaron el procedimiento", "t") == ""
    # Varios expedientes, uno con orden y otro denegado: ambiguo, no se adivina.
    assert decision_de("Primero. Confirmar la sentencia en el sentido de ordenar a Electrocosta "
                       "abstenerse. Cuarto. Confirmar en el sentido de denegar la tutela", "t") == ""
    assert decision_de("Declarar EXEQUIBLE", "t") == "", "una T nunca es exequible"
    ra = resuelve("administrando justicia en nombre del pueblo, RESUELVE PRIMERO.- CONCEDER la "
                  "tutela. Notifíquese. " + "x " * 200 + "AUTO En mérito de lo expuesto RESUELVE Primero. CORREGIR la página 9")
    assert ra.startswith("PRIMERO.- CONCEDER"), ra

    assert fecha_en("Sentencia C-008/10 (Enero 14; Bogotá D.C.) PRINCIPIO", "2010") == "2010-01-14"
    assert fecha_en("Sentencia C-852/13 (27 de noviembre) FACULTADES", "2013") == "2013-11-27"
    assert fecha_en("acta número tres (3), correspondiente a la sesión de la Sala Plena, llevada a cabo el "
                    "día diez y seis (16) del mes de febrero de mil novecientos noventa y cinco (1995).", "1995") == "1995-02-16"
    assert fecha_en("Aprobada en Santafé de Bogotá, D.C., mediante acta del veintiuno de abril de mil "
                    "novecientos noventa y cuatro (1994). I. ANTECEDENTES", "1994") == "1994-04-21"
    assert fecha_en("Bogotá, D. C., el 12 de noviembre de 2003 Magistrado Ponente: X Bogotá D.C., ocho (8) "
                    "de marzo de dos mil seis (2006). I. ANTECEDENTES", "2006") == "2006-03-08"
    assert fecha_en("Bogot, D.C., veintiocho (28) de agosto de dos mil diecinueve (2019)", "2019") == "2019-08-28"
    assert fecha_en("Acta 027 Bogotá, D. C., primero (1.º) de agosto de dos mil veintitrés (2023).", "2023") == "2023-08-01"
    assert fecha_en("Acta 16 Sincelejo., catorce (14) de mayo de dos mil veinticinco (2025).", "2025") == "2025-05-14"
    assert fecha_en("Acta 36 Barranquilla Distrito Especial, Industrial y Portuario, tres (3) de octubre de "
                    "dos mil veinticuatro (2024)", "2024") == "2024-10-03"
    assert fecha_en("Acta No. 108 Bogotá D.C., siete (7) de junio de dos mil veintitrés (2022) VISTOS", "2023") == "2023-06-07"
    assert fecha_en("I. ANTECEDENTES la Sala, en sesión llevada a cabo el 21 de marzo de 2018, resolvió acumular", "2018") == ""
    assert fecha_en("confirmada por el Tribunal Superior de Bogotá el 4 de febrero de 1992. I. ANTECEDENTES", "1992") == ""
    assert fecha_en("I. ANTECEDENTES Bogotá el 12 de julio de 1973. Bogotá, 5 de marzo de 1993", "1993") == ""
    m = metadatos(txt, "2019")
    assert m["expediente"] == "D-12981", m
    assert m["fecha"] == "2019-09-25", m
    assert m["ponente"] == "Luis Guillermo Guerrero Pérez", m
    assert m["sala"] == "plena", m

    assert url_de("co:cc:c-443:2019").endswith("/relatoria/2019/C-443-19.htm"), url_de("co:cc:c-443:2019")
    assert url_de("co:cc:su-214:2016").endswith("/relatoria/2016/SU214-16.htm")
    assert url_de("co:cc:c-41:2000").endswith("/relatoria/2000/C-041-00.htm"), url_de("co:cc:c-41:2000")
    print("check OK")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ids", nargs="*")
    p.add_argument("--del-grafo", action="store_true",
                   help="toma las sentencias que relaciones.csv ya cita y aún no tienen ficha")
    p.add_argument("--limite", type=int, default=25)
    p.add_argument("--pausa", type=float, default=2.0, help="segundos entre peticiones (≥ 2)")
    p.add_argument("--todas", action="store_true",
                   help="no solo las que afectan vigencia: también las que solo interpretan")
    a = p.parse_args()
    global PAUSA
    PAUSA = a.pausa

    con = sqlite3.connect(os.path.join(RAIZ, "index.db")) if os.path.exists(
        os.path.join(RAIZ, "index.db")) else None
    ids = list(a.ids)
    if a.del_grafo and con:
        # Prioriza las que más artículos afectan: son las que más peso tienen.
        ids += [r[0] for r in con.execute("""SELECT origen, COUNT(*) n FROM relaciones
            WHERE origen LIKE 'co:cc:%' AND (tipo LIKE 'declara%' OR ?)
              AND origen NOT IN (SELECT id FROM documentos)
            GROUP BY origen ORDER BY n DESC""", (1 if a.todas else 0,)).fetchall()][:a.limite]

    ok = fallos = 0
    for sid in ids:
        time.sleep(PAUSA)
        destino = os.path.join(RAIZ, "jurisprudencia", sid.replace(":", "-") + ".md")
        try:
            texto, meta, nd = ficha(sid, con)
        except Exception as e:
            print("  [!] %s: %s" % (sid, e))
            fallos += 1
            continue
        with open(destino, "w", encoding="utf-8") as fh:
            fh.write(texto)
        ok += 1
        print("  %s  %s  %d descriptores" % (sid, meta.get("fecha", "sin fecha"), nd))
    print("%d fichas escritas, %d fallidas" % (ok, fallos))


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
