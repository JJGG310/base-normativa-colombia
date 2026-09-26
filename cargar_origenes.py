#!/usr/bin/env python3
"""Carga desde senado las leyes, estatutarias y actos legislativos origen que el grafo cita y
aún no están (lo que lista `build.py -v`), de la más citada a la menos.

    python3 cargar_origenes.py --minimo-aristas 2 --limite 500
    python3 cargar_origenes.py --check

El título es «Ley N de AAAA - <epígrafe de la fuente>»; las ramas, las dos más comunes entre
las normas que esa ley afecta (no se eligen a ojo). Cada ingesta pasa por verificar.py. Lo que no
se puede cargar sin criterio humano va a `origenes_revisar.txt` y NO se adivina: 404 en senado,
`faltan` > 0, o una nota de muerte de la norma entera en el encabezado (hay que poner a mano la
arista `manual:` a nivel de norma, como en P17/P18).
"""
import argparse, collections, html, os, re, sqlite3, subprocess, sys, time

from ingesta_senado import bajar, limpiar

RAIZ = os.path.dirname(os.path.abspath(__file__))
B = "http://www.secretariasenado.gov.co/senado/basedoc/"
PAGINA = {"ley": "ley_%04d_%s.html", "ley-estatutaria": "ley_%04d_%s.html", "ley-organica": "ley_%04d_%s.html",
          "acto-legislativo": "acto_legislativo_%02d_%s.html"}
NOMBRE = {"ley": "Ley", "ley-estatutaria": "Ley", "ley-organica": "Ley", "acto-legislativo": "Acto Legislativo"}


def pendientes(con, minimo):
    filas = con.execute("""
        WITH f AS (SELECT CASE WHEN instr(origen, ':art:') > 0 THEN substr(origen, 1, instr(origen, ':art:') - 1)
                               ELSE origen END n, destino FROM relaciones
                   WHERE origen NOT IN (SELECT id FROM fragmentos) AND origen NOT IN (SELECT id FROM documentos))
        SELECT n, count(*) FROM f GROUP BY n HAVING count(*) >= ? ORDER BY 2 DESC""", (minimo,)).fetchall()
    return [(n, c) for n, c in filas if n.split(":")[1] in PAGINA and len(n.split(":")) == 4]


def ramas(con, id_norma):
    c = collections.Counter()
    for (r,) in con.execute("""SELECT d.ramas FROM relaciones r JOIN documentos d
            ON r.destino = d.id OR r.destino LIKE d.id || ':art:%'
            WHERE r.origen = ? OR r.origen LIKE ? || ':art:%'""", (id_norma, id_norma)):
        c.update(x.strip() for x in re.sub(r"[\[\]]", "", r or "").split(",") if x.strip())
    return ", ".join(x for x, _ in c.most_common(2)) or "general"


def epigrafe(doc):
    """El primer párrafo con minúsculas entre el encabezado de la norma y «EL CONGRESO…/DECRETA»."""
    t = html.unescape(limpiar(re.sub(r"<style.*?</style>|<script.*?</script>", "", doc, flags=re.S | re.I)))
    h = re.search(r"\b(?:LEY|ACTO LEGISLATIVO)\s+(?:N[o°º]\.?\s*)?\d+\s+DE\s+\d{4}\b", t, re.I)
    if not h:
        return ""
    for p in t[h.end():h.end() + 4000].split("\n"):
        p = " ".join(p.split())
        if re.match(r"(?i)(EL CONGRESO|DECRETA|Resumen de Notas|ART[IÍ]CULO)", p):
            break
        if (re.search(r"[a-záéíóúñ]{3}", p) and not p.startswith(("(", "<", "Diario Oficial"))
                and not re.match(r"(?i)diario oficial", p)):
            return p.rstrip(" .")
    return ""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--minimo-aristas", type=int, default=2)
    p.add_argument("--limite", type=int, default=100)
    a = p.parse_args()
    con = sqlite3.connect(os.path.join(RAIZ, "index.db"))
    revisar = open(os.path.join(RAIZ, "origenes_revisar.txt"), "a", encoding="utf-8")
    hechas = 0
    # Todo lo que sale de index.db se lee al inicio: build.py lo regenera y puede correr en paralelo.
    lote = [(i, n, ramas(con, i)) for i, n in pendientes(con, a.minimo_aristas)[:a.limite]]
    con.close()
    for id_norma, n, ramas_norma in lote:
        _, tipo, num, anio = id_norma.split(":")
        url = B + PAGINA[tipo] % (int(num), anio)
        try:
            doc = bajar(url)
        except Exception as e:
            revisar.write("%s\t%d aristas\tsin fuente en senado: %s\n" % (id_norma, n, e))
            continue
        epi = epigrafe(doc)
        titulo = "%s %s de %s" % (NOMBRE[tipo], num, anio) + (" - " + epi if epi else "")
        salida = "normativa/%s.md" % id_norma.replace(":", "-")
        r = subprocess.run([sys.executable, "ingesta_senado.py", url, "--minimo", "1", "--id", id_norma,
                            "--tipo", tipo, "--titulo", titulo, "--ramas", ramas_norma,
                            "--salida", salida], cwd=RAIZ, capture_output=True, text=True)
        salida_txt = r.stdout + r.stderr
        if r.returncode or not os.path.exists(os.path.join(RAIZ, salida)):
            revisar.write("%s\t%d aristas\tingesta falló: %s\n" % (id_norma, n, " ".join(salida_txt.split())[-300:]))
            continue
        v = subprocess.run([sys.executable, "verificar.py", salida], cwd=RAIZ, capture_output=True, text=True).stdout
        faltan = re.search(r"faltan (\d+)", v)
        if faltan and int(faltan.group(1)):
            revisar.write("%s\t%d aristas\tverificar: %s\n" % (id_norma, n, " ".join(v.split())[:300]))
        for linea in salida_txt.splitlines():
            if linea.startswith("Error: nota de vigencia de la norma entera"):
                revisar.write("%s\t%d aristas\t%s\n" % (id_norma, n, linea[:400]))
        hechas += 1
        print("%s (%d aristas): %s" % (id_norma, n, " | ".join(l for l in salida_txt.splitlines() if "->" in l)), flush=True)
        time.sleep(2)
    print("%d normas cargadas" % hechas)


def check():
    doc = ("<p>LEY 105 DE 1993</p><p>(diciembre 30)</p><p>Diario Oficial No. 41.158, de 30 de diciembre de 1993</p>"
           "<p>CONGRESO DE COLOMBIA</p><p>&lt;NOTA: Esta norma no incluye análisis&gt;</p>"
           "<p>Por la cual se dictan disposiciones básicas sobre el transporte.</p><p>EL CONGRESO DE COLOMBIA,</p>")
    assert epigrafe(doc) == "Por la cual se dictan disposiciones básicas sobre el transporte", epigrafe(doc)
    assert epigrafe("<p>LEY 1 DE 2000</p><p>EL CONGRESO</p><p>Por la cual x</p>") == ""
    assert epigrafe("<p>[LEY_0335_1996]</p><p>LEY 335 de 1996</p><p>por la cual se modifica.</p>") == "por la cual se modifica"
    print("check OK")


if __name__ == "__main__":
    check() if "--check" in sys.argv else main()
