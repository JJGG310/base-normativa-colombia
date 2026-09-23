#!/bin/bash
# Re-ingesta TODAS las normas de secretariasenado.gov.co que hay en normativa/, con los
# datos de su propio frontmatter (fuente, id, tipo, titulo, titulo_corto, fecha, ramas,
# estado_general), y corre verificar.py sobre cada una.
#   ./reingestar_senado.sh                 # todas
#   ./reingestar_senado.sh ley-1306 et     # solo los archivos cuyo nombre contenga eso
# --minimo = 98% de los artículos que ya tiene el archivo: si el parser pierde más, no
# se sobrescribe. Usa fuentes/cache/ (borrar el caché de una norma para re-bajarla).
cd "$(dirname "$0")" || exit 1
python3 - "$@" <<'EOF'
import glob, re, subprocess, sys
filtros = sys.argv[1:]
fallos = []
for ruta in sorted(glob.glob("normativa/*.md")):
    if filtros and not any(f in ruta for f in filtros):
        continue
    txt = open(ruta, encoding="utf-8").read()
    fm = dict(re.findall(r"^(\w+): (.*)$", txt.split("\n---\n", 1)[0], re.M))
    if "secretariasenado" not in fm.get("fuente", ""):
        continue
    n = len(re.findall(r"^## art:", txt, re.M))
    cmd = ["python3", "ingesta_senado.py", fm["fuente"], "--id", fm["id"], "--tipo", fm["tipo"],
           "--titulo", fm["titulo"], "--fecha", fm["fecha"], "--ramas", fm["ramas"].strip("[]"),
           "--estado", fm.get("estado_general", "vigente"), "--minimo", str(int(n * 0.98)),
           "--salida", ruta]
    if fm.get("titulo_corto"):
        cmd += ["--corto", fm["titulo_corto"]]
    print("==", ruta, flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("\n".join(l for l in (r.stdout + r.stderr).splitlines()
                    if re.search(r"artículos ->|aristas ->|ABORTA|Traceback|^\w*Error", l)), flush=True)
    v = subprocess.run(["python3", "verificar.py", ruta], capture_output=True, text=True).stdout
    print(v.strip(), flush=True)
    if r.returncode or not re.search(r"faltantes en total: 0\b", v):
        fallos.append(ruta)
print("\nCON PROBLEMAS (%d): %s" % (len(fallos), " ".join(fallos) or "ninguna"))
EOF
