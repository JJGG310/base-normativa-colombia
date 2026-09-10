#!/usr/bin/env python3
"""Extrae normativa de secretariasenado.gov.co a un .md del esquema.

    python3 ingesta_senado.py <url> --id co:constitucion:1991 --tipo constitucion \\
        --titulo "Constitución Política de Colombia" --corto CP \\
        --fecha 1991-07-04 --ramas constitucional --salida normativa/co-constitucion-1991.md

La extracción es MECÁNICA a propósito: el texto pasa de la fuente al archivo sin
pasar por el modelo. Un modelo que "recuerda" el artículo 1502 del Código Civil
escribe algo plausible y equivocado; un script no puede inventar.

Ojo: esta fuente NO trae las notas de vigencia en el HTML (las carga por JS), así
que `relaciones.csv` no se llena desde aquí. Eso sale de SUIN-Juriscol.
"""
import argparse, html, os, re, sys, urllib.request

UA = {"User-Agent": "Mozilla/5.0"}
ANCLA = re.compile(r'<a class="bookmarkaj" name="([^"]+)"\s*>(.*?)</a>', re.I | re.S)


def bajar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("iso-8859-1", "replace")


def paginas(url):
    """La fuente pagina como _pr001, _pr002… Se sigue la cadena hasta que corte."""
    vistas, cola, salida = set(), [url], []
    base = url.rsplit("/", 1)[0] + "/"
    while cola:
        u = cola.pop(0)
        if u in vistas:
            continue
        vistas.add(u)
        try:
            doc = bajar(u)
        except Exception as e:
            print("  no se pudo bajar %s: %s" % (u, e), file=sys.stderr)
            continue
        salida.append((u, doc))
        for href in re.findall(r'href="([^"]*_pr\d+\.html)"', doc):
            full = href if href.startswith("http") else base + href.lstrip("./")
            if full not in vistas:
                cola.append(full)
    orden = lambda par: int((re.search(r"_pr(\d+)\.html", par[0]) or [0, 0])[1])
    return [doc for _, doc in sorted(salida, key=orden)]


def limpiar(fragmento):
    """Quita los widgets de navegación (tablas vacías que llena el JS) y el marcado."""
    f = re.sub(r'<div><a class="caja_vja_encabezado".*?</table>', "", fragmento, flags=re.S)
    f = re.sub(r"<a [^>]*title=\"Ir al inicio\".*?</a>", "", f, flags=re.S)
    f = re.sub(r"<img[^>]*>", "", f)
    f = re.sub(r"</p\s*>|<br\s*/?>", "\n", f, flags=re.I)
    f = re.sub(r"<[^>]+>", "", f)
    f = html.unescape(f)
    f = re.sub(r"[ \t\xa0]+", " ", f)
    f = re.sub(r"\n\s*\n\s*\n+", "\n\n", f)
    return f.strip()


def articulos(docs):
    """Corta por ancla `bookmarkaj`. Es el único marcador fiable: el texto del
    encabezado varía (ARTICULO 1o., ARTÍCULO 14., ARTICULO 82-1).

    Devuelve (num, epígrafe, ubicación, texto). La ubicación (TÍTULO > CAPÍTULO) va
    porque un artículo recuperado suelto la necesita: "art. 86" no dice nada, "Título
    II, Cap. 4 — De la protección de los derechos" sitúa al modelo que lo lea.
    """
    salida = []
    titulo = capitulo = ""
    for doc in docs:
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

            cuerpo = limpiar(doc[m.end():fin])
            epi = re.sub(r"^ART[IÍ]CULO\s*(TRANSITORIO)?\s*[\dA-Za-z\-]*[o°º]?\.?\s*",
                         "", encabezado, flags=re.I).strip(" .:-")
            salida.append((num, epi, " > ".join(x for x in (titulo, capitulo) if x), cuerpo))

    vistos, unicos = set(), []
    for fila in salida:
        if fila[0] in vistos or not fila[3]:
            continue
        vistos.add(fila[0])
        unicos.append(fila)
    return unicos


def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    for a in ("id", "tipo", "titulo", "fecha", "ramas", "salida"):
        p.add_argument("--" + a, required=True)
    p.add_argument("--corto", default="")
    p.add_argument("--estado", default="vigente")
    p.add_argument("--verificado", default=None)
    a = p.parse_args()

    docs = paginas(a.url)
    arts = articulos(docs)
    if not arts:
        sys.exit("no se extrajo ningún artículo — revisar el formato de la fuente")

    from datetime import date
    fm = ["---", "id: " + a.id, "tipo: " + a.tipo, "titulo: " + a.titulo]
    if a.corto:
        fm.append("titulo_corto: " + a.corto)
    fm += ["fecha: " + a.fecha,
           "ramas: [%s]" % a.ramas,
           "estado_general: " + a.estado,
           "fuente: " + a.url,
           "verificado: " + (a.verificado or date.today().isoformat()),
           "---", ""]

    partes = fm
    for num, epi, ubicacion, txt in arts:
        partes.append("## art:%s — %s" % (num, epi))
        if ubicacion:
            partes.append("ubicacion: " + ubicacion)
        partes.append("")
        partes.append(txt)
        partes.append("")

    destino = a.salida if os.path.isabs(a.salida) else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), a.salida)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(partes))
    print("%d páginas, %d artículos -> %s" % (len(docs), len(arts), a.salida))


if __name__ == "__main__":
    main()
