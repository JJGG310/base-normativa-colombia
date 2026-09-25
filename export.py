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
import json, re, sqlite3, sys, os
import build

RAIZ = os.path.dirname(os.path.abspath(__file__))

RE_PARTE = re.compile(r"<[^<>]{0,150}(?:INEXEQUIBLE|[Dd]erogad[oa])[^<>]{0,300}>")

ADVERTENCIA = {
    "MUERTO": "NO APLICAR. Este artículo fue derogado o declarado inexequible. Se conserva solo por valor histórico y para resolver casos regidos por la ley anterior.",
    "SUSPENDIDO": "NO APLICAR SIN VERIFICAR. Artículo suspendido; confirmar si la suspensión sigue vigente.",
    "VIGENTE_CONDICIONADO": "APLICAR SOLO EN EL SENTIDO CONDICIONADO. La Corte lo declaró exequible bajo una interpretación específica; leerlo por fuera de ella es error.",
    "VIGENTE_REFORMADO": "VERIFICAR REDACCIÓN. El artículo fue modificado o adicionado; el texto aquí debe corresponder a la última versión.",
    "VIGENTE": None,
    "INEXEQUIBLE_PARCIAL": "NO APLICAR SIN VERIFICAR. Una sentencia declaró inexequible parte de este artículo y la base no registra qué apartes cayeron: el texto aquí puede incluir partes ya retiradas del ordenamiento. Consultar la sentencia (ver `condicionamiento`) antes de aplicar.",
    "TACHADO": "El texto contiene apartes [TACHADO: …]: la fuente los publica tachados porque ya no rigen (inexequibles, nulos o derogados). Se conservan para que la cita sea completa; no aplicarlos.",
    "PARTE_MARCADA": "El texto trae marcas de la fuente del tipo «<Inciso INEXEQUIBLE>» o «<Inciso derogado por…>»: la parte marcada ya no rige aunque el artículo siga vigente; no aplicarla.",
    "SIN_TEXTO": "SOLO METADATOS, SIN TEXTO VERIFICADO. No se obtuvo el texto de la providencia; este registro no dice qué se decidió ni con qué razones. No citarlo como fundamento sin leerlo en la fuente.",
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
    vig = {r["articulo"]: r for r in con.execute("SELECT * FROM vigencia")}
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
            if estado != "MUERTO" and "[TACHADO:" in f["texto"]:
                adv = " ".join(filter(None, (adv, ADVERTENCIA["TACHADO"])))
            if estado != "MUERTO" and RE_PARTE.search(f["texto"]):
                adv = " ".join(filter(None, (adv, ADVERTENCIA["PARTE_MARCADA"])))
            if f["clase"] == "jurisprudencia" and "No se pudo bajar el texto" in f["texto"]:
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
                    "SELECT tipo, origen, fecha, nota FROM relaciones WHERE destino = ? ORDER BY fecha",
                    (f["id"],))],
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
        if build.marca(r["texto"], r["epigrafe"] or "") and r["estado"] != "MUERTO":
            malos.append("texto dice derogado/inexequible y sale %s: %s" % (r["estado"], r["id"]))
        if r["estado"] != "MUERTO" and not r["advertencia"] and any(
                a["tipo"] == "declara_inexequible" for a in r["afectado_por"]):
            malos.append("inexequible parcial sin advertencia: " + r["id"])
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
        "\n## art:4 — Cuatro\nVive. <Aparte tachado INEXEQUIBLE> [TACHADO: cayó]\n")
    open(tmp + "/jurisprudencia/s.md", "w", encoding="utf-8").write(
        "---\nid: co:ce:1:2022\ntipo: sentencia\ncorporacion: consejo-estado\nponente: P\nramas: [administrativo]\n"
        "fuente: http://x\nverificado: 2026-01-01\n---\n\n## ficha\nActor: X\n**No se pudo bajar el texto íntegro**.\n")
    open(tmp + "/relaciones.csv", "w", encoding="utf-8").write(
        "origen,tipo,destino,fecha,nota,fuente\n"
        "co:ley:2:2001:art:9,deroga,co:ley:1:2000:art:1,2001-01-01,,x\n"
        "co:cc:c-3:2010,declara_inexequible,co:ley:1:2000:art:3,2010-01-01,,x\n")
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
