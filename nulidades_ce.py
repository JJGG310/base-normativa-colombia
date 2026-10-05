#!/usr/bin/env python3
"""Nulidades del Consejo de Estado leídas en la parte resolutiva de las fichas (esquema.md §6.1).

    python3 nulidades_ce.py            # lista candidatas en CSV (cargado,origen,tipo,destino,fecha,nota,fuente); no escribe
    python3 nulidades_ce.py --aplicar  # además añade las de destino cargado vía anadir_aristas.py
    python3 nulidades_ce.py --check    # autotest

Regla estricta (propuestas/nulidades-ce/informe.md §2.3): un numeral del `## resuelve` que EMPIEZA por
«declarar[se] la nulidad…» / «declárase nulo…» y nombra un decreto con número y año sin otro acto de por
medio. Total (`declara_nulo`) solo si no nombra sub-parte; si no, `declara_nulo_parcial`. Se descartan las
resolutivas de más de 3.500 caracteres, las de segunda instancia y los nombramientos/elecciones. En un DUR
el fallo puede citar el decreto que introdujo el artículo: el destino es el artículo del DUR que ese decreto
adicionó/modificó/subrogó según relaciones.csv, si es uno solo. Lee cada extracto antes de --aplicar.
"""
import csv, glob, os, re, subprocess, sys, tempfile
import build

RAIZ = os.path.dirname(os.path.abspath(__file__))
ORDINAL = re.compile(r"\b(?:PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[ÉE]PTIMO|OCTAVO|NOVENO|D[ÉE]CIMO)\b\s*(?:\.\s*-|[.:\-–])")
VERBO = re.compile(r"\W*DECL[AÁ]R(?:AR|ESE|ASE|ANSE|ENSE)\s+(?:LA\s+)?(?:NULIDAD|NUL[OA]S?)\b", re.I)
DECRETO = re.compile(r"\bDecreto(?:\s+(?:reglamentario|legislativo|nacional|ley|n[úu]mero|No\.?))*\s+(\d{1,5})\b"
                     r"[^.;]{0,60}?\b((?:18|19|20)\d\d)\b", re.I)
OTRO = re.compile(r"actuaci[óo]n|sentencia|providencia|\bauto\b|resoluci[óo]n|circular|acuerdo|ordenanza|\bley\b|contrato"
                  r"|\bacto\b|oficio|concepto|modificad|adicionad|subrogad", re.I)
SUBPARTE = re.compile(r"expresi[óo]n|apartes?\b|frases?\b|numeral|inciso|par[áa]grafo|literal|ordinal|palabra|parcial"
                      r"|segmento|vocablo", re.I)
NOMBRA = re.compile(r"nombr[óoa]|nombramiento|elecci[óo]n|eleg[ií]|design[óa]", re.I)
SEGUNDA = re.compile(r"\b(?:CONFIRM|REVOC|MODIFIC)[A-ZÁÉÍÓÚ]*\b[^.]{0,80}\bsentencia|quedar[áa] as[íi]", re.I)
EFECTOS = re.compile(r"hacia (?:el )?futuro|sin perjuicio de las situaciones|ex nunc|ex tunc|efectos? (?:de la|de esta) (?:presente )?"
                     r"(?:providencia|sentencia|decisi[óo]n)", re.I)


def candidatas():
    cargados = set()
    for ruta in glob.glob(os.path.join(RAIZ, "normativa", "*.md")):
        meta, cuerpo = build.frontmatter(open(ruta, encoding="utf-8").read())
        if meta.get("id"):
            cargados.add(meta["id"])
            cargados.update(meta["id"] + ":" + f[0] for f in build.fragmentos(cuerpo))
    reformas = [r for r in csv.DictReader(open(os.path.join(RAIZ, "relaciones.csv"), encoding="utf-8"))
                if r["tipo"] in ("adiciona", "modifica", "subroga")]

    def cargado(d):  # con el alias decreto / decreto-ley de build.py
        p = d.split(":")
        for t in (p[1],) + build.ALIAS.get(p[1], ()):
            if ":".join([p[0], t] + p[2:]) in cargados:
                return ":".join([p[0], t] + p[2:])

    for ruta in sorted(glob.glob(os.path.join(RAIZ, "jurisprudencia", "co-ce-*.md"))):
        meta, cuerpo = build.frontmatter(open(ruta, encoding="utf-8").read())
        res = next((t for c, _, _, t in build.fragmentos(cuerpo) if c == "resuelve"), "")
        if not res or len(res) > 3500 or SEGUNDA.search(res):
            continue
        ciego = re.sub(r"“[^”]*”|\"[^\"]*\"|‘[^’]*’", lambda m: "x" * len(m.group()), res)  # sin lo citado
        cortes = [m.end() for m in ORDINAL.finditer(ciego)] or [0]
        numerales = [(ciego[a:b], res[a:b]) for a, b in zip(cortes, [m.start() for m in ORDINAL.finditer(ciego)][1:] + [len(res)])]
        efectos = " ".join(o.strip()[:200] for c, o in numerales if EFECTOS.search(c))
        for c, o in numerales:
            v, d = VERBO.match(c), DECRETO.search(c)
            if not (v and d) or NOMBRA.search(c):
                continue
            objeto = c[v.end():d.start()]
            if OTRO.search(objeto):
                continue
            parcial = bool(SUBPARTE.search(objeto))  # «artículos 2.2.3.5.2.2.1.1. (literal f) y…» es parcial
            objeto = re.sub(r"\([^()]*\)", " ", objeto)
            base = "co:decreto:%s:%s" % d.groups()
            k = re.search(r"art[íi]culos?\b", objeto, re.I)
            arts = re.findall(r"\d+(?:\.\d+)*", objeto[k.end():]) if k else []
            if (k and not arts) or (parcial and not arts):
                continue  # «artículo segundo» o parte del decreto sin artículo: no se ubica
            nota = "manual: nulidad %s — %s" % ("parcial" if parcial else "total", re.sub(r"\s+", " ", o).strip()[:300])
            nota += ("; efectos: " + efectos) if efectos else ""  # sin « | »: separa condiciones en la vista
            for a in arts or [None]:
                dest = base + (":art:" + a if a else "")
                real, como = cargado(dest), ""
                if not real and a:  # DUR: el fallo cita el decreto que adicionó/modificó/subrogó el artículo
                    dur = {r["destino"] for r in reformas if r["destino"].endswith(":art:" + a)
                           and (r["origen"] == base or r["origen"].startswith(base + ":"))}
                    if len(dur) == 1:
                        real, como = cargado(dur.pop()), " (numeración del DUR; el fallo cita el Decreto %s de %s)" % d.groups()
                yield ("si" if real else "no", meta["id"], "declara_nulo_parcial" if parcial else "declara_nulo",
                       real or dest, meta.get("fecha", ""), nota + como, meta.get("fuente", ""))


def check():
    v = VERBO.match
    assert v("DECLÁRASE la nulidad de") and v(" Declarar la nulidad del") and v("DECLÁRANSE NULOS los")
    assert not v("DECLARAR que los efectos de la declaratoria de nulidad") and not v("NEGAR la nulidad")
    d = DECRETO.search("del Decreto reglamentario 1814 de 14 de septiembre de 2015 expedido")
    assert d.groups() == ("1814", "2015") and DECRETO.search("Decreto 4994 expedido el 24 de diciembre de 2009").groups() == ("4994", "2009")
    assert SUBPARTE.search("de la expresión “x” contenida en el artículo 2.2.6.1.7 del ") and not SUBPARTE.search("la integridad del artículo 44 del ")
    assert OTRO.search("de la actuación surtida en el") and NOMBRA.search("mediante el cual se nombró a X")
    import shutil  # extremo a extremo sobre una raíz temporal
    tmp = tempfile.mkdtemp()
    os.makedirs(tmp + "/normativa"); os.makedirs(tmp + "/jurisprudencia")
    open(tmp + "/normativa/d.md", "w", encoding="utf-8").write(
        "---\nid: co:decreto:1073:2015\n---\n\n## art:2.2.3.1 —\nT.\n\n## art:2.2.3.4 —\nT.\n\n## art:2.2.6.1.7 —\nT.\n")
    open(tmp + "/relaciones.csv", "w", encoding="utf-8").write(
        "origen,tipo,destino,fecha,nota,fuente\nco:decreto:1814:2015:art:1,adiciona,co:decreto:1073:2015:art:2.2.6.1.7,2015-09-14,,x\n")
    for n, res in enumerate((
            "PRIMERO: DECLARAR la nulidad de los artículos 2.2.3.1. (literal f) y 2.2.3.4. (literal a) del Decreto 1073 de 2015. "
            "SEGUNDO: Declarar la nulidad de la expresión “x”, contenida en el artículo 2.2.6.1.7 del Decreto reglamentario 1814 "
            "de 14 de septiembre de 2015. TERCERO: DECLÁRESE la nulidad de la integridad del artículo 44 del Decreto 2474 de 2008. "
            "CUARTO: Los efectos de la presente providencia rigen hacia futuro.",
            "PRIMERO: CONFIRMAR la sentencia que declaró la nulidad del Decreto 1 de 2001.",
            "PRIMERO: DECLARAR LA NULIDAD del Decreto 1555 del 5 de agosto de 2022, mediante el cual se nombró a X.",
            "PRIMERO: DECLARAR la nulidad de la actuación surtida a partir del auto. SEGUNDO: NEGAR la nulidad del Decreto 2 de 2002.")):
        open(tmp + "/jurisprudencia/co-ce-%d.md" % n, "w", encoding="utf-8").write(
            "---\nid: co:ce:%d:2020\nfecha: 2020-01-0%d\nfuente: http://x\n---\n\n## resuelve\n%s\n" % (n, n + 1, res))
    global RAIZ
    RAIZ, viejo = tmp, RAIZ
    f = list(candidatas())
    RAIZ = viejo
    shutil.rmtree(tmp)
    assert [(c, t, d) for c, _, t, d, *_ in f] == [
        ("si", "declara_nulo_parcial", "co:decreto:1073:2015:art:2.2.3.1"),
        ("si", "declara_nulo_parcial", "co:decreto:1073:2015:art:2.2.3.4"),
        ("si", "declara_nulo_parcial", "co:decreto:1073:2015:art:2.2.6.1.7"),
        ("no", "declara_nulo", "co:decreto:2474:2008:art:44")], f
    assert f[0][5].startswith("manual: nulidad parcial — ") and "hacia futuro" in f[0][5] and "numeración del DUR" in f[2][5]
    print("check OK")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check(); sys.exit()
    filas = list(candidatas())
    w = csv.writer(sys.stdout)
    w.writerow(("cargado", "origen", "tipo", "destino", "fecha", "nota", "fuente"))
    w.writerows(filas)
    if "--aplicar" in sys.argv:
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerows(f[1:] for f in filas if f[0] == "si")
        subprocess.run([sys.executable, os.path.join(RAIZ, "anadir_aristas.py"), fh.name], check=True)
        os.remove(fh.name)
