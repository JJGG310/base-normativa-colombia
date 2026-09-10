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
import json, sqlite3, sys, os

RAIZ = os.path.dirname(os.path.abspath(__file__))

ADVERTENCIA = {
    "MUERTO": "NO APLICAR. Este artículo fue derogado o declarado inexequible. Se conserva solo por valor histórico y para resolver casos regidos por la ley anterior.",
    "SUSPENDIDO": "NO APLICAR SIN VERIFICAR. Artículo suspendido; confirmar si la suspensión sigue vigente.",
    "VIGENTE_CONDICIONADO": "APLICAR SOLO EN EL SENTIDO CONDICIONADO. La Corte lo declaró exequible bajo una interpretación específica; leerlo por fuera de ella es error.",
    "VIGENTE_REFORMADO": "VERIFICAR REDACCIÓN. El artículo fue modificado o adicionado; el texto aquí debe corresponder a la última versión.",
    "VIGENTE": None,
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
                "advertencia": ADVERTENCIA.get(estado),
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
            if estado == "VIGENTE_CONDICIONADO" and v and v["condicion"]:
                reg["condicionamiento"] = v["condicion"]
            if estado == "MUERTO" and v and v["mata"]:
                reg["derogado_por"] = v["mata"]
            fh.write(json.dumps(reg, ensure_ascii=False) + "\n")
            n += 1
    con.close()
    print("%d registros -> %s" % (n, os.path.relpath(salida, RAIZ)))
    return n


def check():
    """El registro de un artículo muerto DEBE salir con advertencia. Es el punto del archivo."""
    import build, tempfile, shutil
    tmp = tempfile.mkdtemp()
    os.makedirs(tmp + "/normativa"); os.makedirs(tmp + "/jurisprudencia")
    open(tmp + "/normativa/x.md", "w", encoding="utf-8").write(
        "---\nid: co:ley:1:2000\ntipo: ley\ntitulo: Ley Uno\nramas: [civil]\n"
        "fuente: http://x\nverificado: 2026-01-01\n---\n\n## art:1 — Uno\nTexto.\n")
    open(tmp + "/relaciones.csv", "w", encoding="utf-8").write(
        "origen,tipo,destino,fecha,nota,fuente\n"
        "co:ley:2:2001:art:9,deroga,co:ley:1:2000:art:1,2001-01-01,,x\n")
    build.construir(tmp + "/index.db", tmp)
    global RAIZ
    RAIZ = tmp
    exportar(salida=tmp + "/c.jsonl")
    reg = json.loads(open(tmp + "/c.jsonl", encoding="utf-8").readline())
    assert reg["estado"] == "MUERTO", reg["estado"]
    assert "NO APLICAR" in reg["advertencia"], "un artículo muerto debe salir advertido"
    assert reg["cita"] == "Art. 1, Ley Uno", reg["cita"]
    assert reg["afectado_por"][0]["tipo"] == "deroga"
    shutil.rmtree(tmp)
    print("check OK")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check() if "--check" in sys.argv else exportar(args)
