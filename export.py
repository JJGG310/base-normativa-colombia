#!/usr/bin/env python3
"""Exporta el corpus como contexto autocontenido para cualquier IA.

    python3 export.py                 # todo -> contexto.jsonl
    python3 export.py familia penal   # solo esas ramas

Cada línea es un registro que se puede recuperar SOLO (RAG, o pegado en un prompt)
sin perder su estado: la vigencia va calculada y, si el artículo está muerto o
condicionado, la advertencia viaja dentro del registro. Es la única defensa contra
que una IA cite un artículo derogado — el chunk no siempre llega acompañado de su
norma, pero siempre llega acompañado de su advertencia.
"""
import datetime, json, re, sqlite3, sys, os
import build

RAIZ = os.path.dirname(os.path.abspath(__file__))

RE_PARTE = re.compile(r"<[^<>]{0,150}(?:INEXEQUIBLE|[Dd]erogad[oa])[^<>]{0,300}>")

ADVERTENCIA = {
    "MUERTO": "NO APLICAR. Este artículo fue derogado, declarado inexequible o declarado nulo. Se conserva solo por valor histórico y para resolver casos regidos por la ley anterior.",
    "SUSPENDIDO": "NO APLICAR SIN VERIFICAR. Artículo suspendido; confirmar si la suspensión sigue vigente.",
    "VIGENTE_CONDICIONADO": "APLICAR SOLO EN EL SENTIDO CONDICIONADO. La Corte lo declaró exequible bajo una interpretación específica; leerlo por fuera de ella es error.",
    "VIGENTE_REFORMADO": "VERIFICAR REDACCIÓN. El artículo fue modificado o adicionado; el texto aquí debe corresponder a la última versión.",
    "VIGENTE": None,
    "INEXEQUIBLE_PARCIAL": "NO APLICAR SIN VERIFICAR. Una sentencia declaró inexequible parte de este artículo y la base no registra qué apartes cayeron: el texto aquí puede incluir partes ya retiradas del ordenamiento. Consultar la sentencia (ver `condicionamiento`) antes de aplicar.",
    "NULIDAD_PARCIAL": "NO APLICAR SIN VERIFICAR. El Consejo de Estado declaró nula una parte de este artículo, o lo anuló con efectos diferidos o modulados (ver `condicionamiento`, `afectado_por` o la nota de la fuente en el texto): el texto aquí puede incluir apartes que ya no rigen. Consultar la providencia antes de aplicar.",
    "TACHADO": "El texto contiene apartes [TACHADO: …]: la fuente los publica tachados porque ya no rigen (inexequibles, nulos o derogados). Se conservan para que la cita sea completa; no aplicarlos.",
    "PARTE_MARCADA": "El texto incluye una parte marcada que ya no rige: la fuente la señala como derogada o inexequible («<Inciso INEXEQUIBLE>», «Texto subrayado, derogado por…», o una derogación parcial en `afectado_por`). El artículo sigue vigente, pero esa parte no se aplica.",
    "SIN_TEXTO_PROPIO": "SIN TEXTO PROPIO. La fuente no publica contenido para este artículo, solo la nota entre «<>» (sustituido o subrogado por otra norma, incorporado en un estatuto, desplazado por norma comunitaria…). No citarlo como regla: la disposición aplicable es la que la nota señala.",
    "COMPILADA": "COMPILADA EN UN DUR. Esta norma reglamentaria fue compilada en %s, cuya derogatoria integral (art. 3.1.1) deroga las disposiciones reglamentarias sobre las mismas materias, salvo las excepciones que enumera. Citar y aplicar el artículo equivalente del DUR, no este.",
    "SIN_TEXTO": "SOLO METADATOS, SIN TEXTO VERIFICADO. No se obtuvo el texto de la providencia; este registro no dice qué se decidió ni con qué razones. No citarlo como fundamento sin leerlo en la fuente.",
    "VERIFICADO_VIEJO": "VERIFICADO HACE MÁS DE 12 MESES (%s). La vigencia pudo cambiar desde entonces: confirmarla en la fuente antes de citarlo.",
    "VIGENCIA_NO_VERIFICADA": "VERIFICAR ANTES DE USAR. De esta norma todavía no se cargó el rastro de reformas y derogatorias, así que no consta que el artículo siga vigente ni que este sea su texto actual. La ausencia de afectaciones registradas no es prueba de vigencia.",
}


def cita(doc, clave):
    """Cita como se escribe en un escrito jurídico colombiano."""
    corto = (" (%s)" % doc["titulo_corto"]) if doc["titulo_corto"] else ""
    if doc["clase"] == "jurisprudencia":
        return "%s, %s" % (doc["titulo"], doc["fecha"] or "")
    num = clave.split("art:")[-1]
    return "Art. %s, %s%s" % (num, doc["titulo"], corto)


def exportar(ramas=(), salida=None):
    con = sqlite3.connect(os.path.join(RAIZ, "index.db"))
    con.row_factory = sqlite3.Row
    viejo = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()  # CLAUDE.md, regla 3
    vig = {r["articulo"]: r for r in con.execute("SELECT * FROM vigencia")}
    # Decreto reglamentario compilado en un DUR (arista `compila` a la norma entera).
    compilada = dict(con.execute("SELECT destino, origen FROM relaciones WHERE tipo = 'compila' "
                                 "AND destino IN (SELECT id FROM documentos)").fetchall())
    salida = salida or os.path.join(RAIZ, "contexto.jsonl")
    n = 0
    with open(salida, "w", encoding="utf-8") as fh:
        for f in con.execute("""SELECT f.id, f.clave, f.texto, f.ubicacion, f.titulo AS epigrafe,
                                d.clase, d.tipo, d.titulo, d.titulo_corto, d.fecha,
                                d.ramas, d.fuente, d.verificado, d.afectaciones, d.corporacion, d.ponente, d.decision
                                FROM fragmentos f JOIN documentos d ON d.id = f.doc_id
                                ORDER BY f.doc_id, f.id"""):
            rama_lista = (f["ramas"] or "").split(",")
            if ramas and not set(ramas) & set(rama_lista):
                continue
            v = vig.get(f["id"])
            estado = v["estado"] if v else ("FICHA" if f["clase"] == "jurisprudencia" else "SIN_DATO")
            # Sin el rastro de afectaciones cargado, "VIGENTE" sería una afirmación
            # sin respaldo: la única salida honesta es decir que no se verificó.
            if estado == "VIGENTE" and (f["afectaciones"] or "pendiente") != "cargadas":
                estado = "VIGENCIA_NO_VERIFICADA"
            adv = ADVERTENCIA["INEXEQUIBLE_PARCIAL"] if v and estado != "MUERTO" \
                and build.PARCIAL in (v["condicion"] or "") else ADVERTENCIA.get(estado)
            if estado != "MUERTO" and (build.NULO_PARCIAL in ((v and v["condicion"]) or "") or (  # arista o nota de la fuente
                    f["clave"].startswith("art:") and build.nulidad(f["texto"], f["clave"][4:]))):
                # la advertencia de VIGENTE_CONDICIONADO habla de la Corte: sobra si solo hay nulidades
                solo = estado == "VIGENTE_CONDICIONADO" and all(build.NULO_PARCIAL in c for c in v["condicion"].split(" | "))
                adv = " ".join(filter(None, (None if solo else adv, ADVERTENCIA["NULIDAD_PARCIAL"])))
            if estado != "MUERTO" and "[TACHADO:" in f["texto"]:
                adv = " ".join(filter(None, (adv, ADVERTENCIA["TACHADO"])))
            if estado != "MUERTO" and (RE_PARTE.search(f["texto"]) or con.execute(  # Gestor: «Texto subrayado, derogado por…»
                    "SELECT 1 FROM relaciones WHERE destino = ? AND nota LIKE '%derogación parcial%'", (f["id"],)).fetchone()):
                adv = " ".join(filter(None, (adv, ADVERTENCIA["PARTE_MARCADA"])))
            if estado != "MUERTO" and f["clave"].startswith("art:") and len(re.sub(r"<[^<>]*>", "", f["texto"]).strip(" .\n")) < 3:
                adv = " ".join(filter(None, (ADVERTENCIA["SIN_TEXTO_PROPIO"], adv)))
            dur = compilada.get(f["id"].split(":art:")[0])
            if dur and estado != "MUERTO":
                adv = " ".join(filter(None, (ADVERTENCIA["COMPILADA"] % dur, adv)))
            if f["clase"] != "jurisprudencia" and estado != "MUERTO" and f["verificado"] and f["verificado"] < viejo:
                adv = " ".join(filter(None, (adv, ADVERTENCIA["VERIFICADO_VIEJO"] % f["verificado"])))
            if f["clase"] == "jurisprudencia" and ("No se pudo bajar el texto" in f["texto"] or "No se pudo extraer la parte resolutiva" in f["texto"]):
                adv = ADVERTENCIA["SIN_TEXTO"]  # fichas del Consejo de Estado sin texto (SAMAI 403)
            reg = {
                "id": f["id"],
                "cita": cita(f, f["clave"]),
                "clase": f["clase"],
                "norma": f["titulo"],
                "seccion": f["clave"],
                "epigrafe": f["epigrafe"] if f["clave"].startswith("art:") else None,
                "ubicacion": f["ubicacion"] or None,
                "ramas": rama_lista,
                "estado": estado,
                "advertencia": adv,
                "texto": f["texto"],
                "afectado_por": [dict(r) for r in con.execute(
                    # También las de la norma entera (derogada, compilada…): sin ellas el registro
                    # sale MUERTO o advertido sin decir por qué.
                    "SELECT tipo, origen, fecha, nota FROM relaciones WHERE destino IN (?, ?) ORDER BY fecha",
                    (f["id"], f["id"].split(":art:")[0]))],
                "interpretado_por": [r[0] for r in con.execute(
                    "SELECT origen FROM relaciones WHERE destino = ? AND tipo IN ('interpreta','declara_exequible_condicionado','declara_inexequible_parcial')",
                    (f["id"],))],
                "fuente": f["fuente"],
                "verificado": f["verificado"],
            }
            if f["clase"] == "jurisprudencia":
                reg.update(corporacion=f["corporacion"], ponente=f["ponente"], decision=f["decision"])
            if estado == "VIGENTE_CONDICIONADO" and v and v["condicion"]:
                reg["condicionamiento"] = v["condicion"]
            if estado == "MUERTO" and v and v["mata"]:
                reg["derogado_por"] = v["mata"]
            fh.write(json.dumps(reg, ensure_ascii=False) + "\n")
            n += 1
    con.close()
    print("%d registros -> %s" % (n, os.path.relpath(salida, RAIZ)))
    return n


def violaciones(ruta):
    """Registros que contradicen su propio texto o salen sin advertencia debida."""
    malos = []
    for linea in open(ruta, encoding="utf-8"):
        r = json.loads(linea)
        if not r["seccion"].startswith("art:"):
            continue
        if build.marca(r["texto"], r["epigrafe"] or "", r["seccion"][4:]) and r["estado"] != "MUERTO":
            malos.append("texto dice derogado/inexequible/nulo y sale %s: %s" % (r["estado"], r["id"]))
        if r["estado"] != "MUERTO" and not r["advertencia"] and any(
                a["tipo"] == "declara_inexequible" for a in r["afectado_por"]):
            malos.append("inexequible parcial sin advertencia: " + r["id"])
        if r["estado"] != "MUERTO" and "nula una parte" not in (r["advertencia"] or "") and any(
                a["tipo"] == "declara_nulo_parcial" for a in r["afectado_por"]):
            malos.append("nulidad parcial sin advertencia: " + r["id"])
        if r["estado"] != "MUERTO" and "[TACHADO:" in r["texto"] and "TACHADO" not in (r["advertencia"] or ""):
            malos.append("texto tachado sin advertencia: " + r["id"])
    return malos


def check():
    """El registro de un artículo muerto DEBE salir con advertencia. Es el punto del archivo."""
    import build, tempfile, shutil
    tmp = tempfile.mkdtemp()
    os.makedirs(tmp + "/normativa"); os.makedirs(tmp + "/jurisprudencia")
    open(tmp + "/normativa/x.md", "w", encoding="utf-8").write(
        "---\nid: co:ley:1:2000\ntipo: ley\ntitulo: Ley Uno\nramas: [civil]\n"
        "fuente: http://x\nverificado: 2026-01-01\nafectaciones: cargadas\n---\n\n## art:1 — Uno\nTexto.\n"
        "\n## art:2 — Dos\n<Artículo INEXEQUIBLE>\n\n## art:3 — Tres\nTexto tres.\n"
        "\n## art:4 — Cuatro\nVive. <Aparte tachado INEXEQUIBLE> [TACHADO: cayó]\n"
        "\n## art:5 — Cinco\n<Artículo sustituido por los artículos 1o. a 23 del Decreto 919 de 1989>.\n"
        "\n## art:6 — Seis\nTexto seis con un numeral 2.\n\n## art:7 — Siete\nTexto siete.\n"
        "\n## art:8 — Ocho\nTexto.\n\n(Numeral 2 declarado NULO por el Consejo de Estado, Sección Cuarta.)\n"
        "\n## art:9 — Nueve\nTexto.\n\nArtículo declarado NULO por el Consejo de Estado, Expediente 1 de 2020.\n")
    open(tmp + "/normativa/y.md", "w", encoding="utf-8").write(
        "---\nid: co:ley:3:2003\ntipo: ley\ntitulo: Ley Tres\nramas: [civil]\n"
        "fuente: http://x\nverificado: 2020-01-01\nafectaciones: cargadas\n---\n\n## art:1 — Uno\nTexto.\n")
    open(tmp + "/jurisprudencia/s.md", "w", encoding="utf-8").write(
        "---\nid: co:ce:1:2022\ntipo: sentencia\ncorporacion: consejo-estado\nponente: P\nramas: [administrativo]\n"
        "fuente: http://x\nverificado: 2026-01-01\n---\n\n## ficha\nActor: X\n**No se pudo bajar el texto íntegro**.\n")
    open(tmp + "/relaciones.csv", "w", encoding="utf-8").write(
        "origen,tipo,destino,fecha,nota,fuente\n"
        "co:ley:2:2001:art:9,deroga,co:ley:1:2000:art:1,2001-01-01,,x\n"
        "co:cc:c-3:2010,declara_inexequible,co:ley:1:2000:art:3,2010-01-01,,x\n"
        "co:decreto:9:2015:art:3.1.1,compila,co:ley:1:2000,2015-01-01,,x\n"
        "co:ce:7:2020,declara_nulo_parcial,co:ley:1:2000:art:6,2020-01-01,numeral 2,x\n"
        "co:ce:8:2020,declara_nulo,co:ley:1:2000:art:7,2020-01-01,,x\n")
    build.construir(tmp + "/index.db", tmp)
    global RAIZ
    RAIZ = tmp
    exportar(salida=tmp + "/c.jsonl")
    regs = [json.loads(l) for l in open(tmp + "/c.jsonl", encoding="utf-8")]
    ficha, regs = regs[0], regs[1:]  # co:ce:… ordena antes que co:ley:…
    reg = regs[0]
    assert reg["estado"] == "MUERTO", reg["estado"]
    assert "NO APLICAR" in reg["advertencia"], "un artículo muerto debe salir advertido"
    assert reg["cita"] == "Art. 1, Ley Uno", reg["cita"]
    assert reg["afectado_por"][0]["tipo"] == "deroga"
    assert not violaciones(tmp + "/c.jsonl"), violaciones(tmp + "/c.jsonl")
    assert regs[1]["estado"] == "MUERTO", "marcador <Artículo INEXEQUIBLE> en el texto"
    assert "parte" in regs[2]["advertencia"], "inexequible parcial debe salir advertido"
    assert "TACHADO" in regs[3]["advertencia"], "texto tachado debe salir advertido"
    assert "parte marcada" in regs[3]["advertencia"], "marca <Aparte … INEXEQUIBLE> debe salir advertida"
    assert "co:decreto:9:2015:art:3.1.1" in regs[2]["advertencia"], "norma compilada en un DUR"
    assert "SIN TEXTO PROPIO" in regs[4]["advertencia"], "artículo que solo trae la nota de la fuente"
    assert "nula una parte" in regs[5]["advertencia"] and "NULIDAD PARCIAL — numeral 2" in regs[5]["condicionamiento"], "nulidad parcial (arista)"
    assert regs[6]["estado"] == "MUERTO" and "declarado nulo" in regs[6]["advertencia"], "nulidad total (arista)"
    assert regs[7]["estado"] == "VIGENTE" and "nula una parte" in regs[7]["advertencia"], "nulidad parcial (nota de la fuente)"
    assert regs[8]["estado"] == "MUERTO" and "Consejo de Estado" in regs[8]["derogado_por"], "nulidad total (nota de la fuente)"
    assert "12 MESES (2020-01-01)" in regs[-1]["advertencia"] and "12 MESES" not in (regs[0]["advertencia"] or ""), "regla 3: verificado viejo"
    assert "SOLO METADATOS" in ficha["advertencia"] and ficha["corporacion"] == "consejo-estado", ficha
    shutil.rmtree(tmp)
    RAIZ = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(RAIZ, "index.db")):  # la misma regla sobre el corpus real
        exportar(salida=tmp + ".jsonl")
        malos = violaciones(tmp + ".jsonl"); os.remove(tmp + ".jsonl")
        assert not malos, "%d violaciones, p. ej. %s" % (len(malos), malos[:5])
    print("check OK")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check() if "--check" in sys.argv else exportar(args)
