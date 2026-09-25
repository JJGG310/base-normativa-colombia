#!/bin/bash
# Re-ingesta normas del Gestor Normativo (funcionpublica.gov.co) con los datos de su propio
# frontmatter, y corre verificar.py sobre cada una. Mismo contrato que reingestar_senado.sh.
#   ./reingestar_gestor.sh co-decreto-1073-2015 co-decreto-762-2018   # solo esos archivos
# --enteros si todas las claves actuales son enteras (decreto que reforma un DUR: lo decimal
# es transcrito). --minimo = 98% de los artículos actuales. Usa fuentes/cache/.
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
    if "gestornormativo" not in fm.get("fuente", ""):
        continue
    claves = re.findall(r"^## art:(\S+)", txt, re.M)
    cmd = ["python3", "ingesta_gestor.py", fm["fuente"].split("i=")[1], "--id", fm["id"],
           "--tipo", fm["tipo"], "--titulo", fm["titulo"], "--fecha", fm["fecha"],
           "--ramas", fm["ramas"].strip("[]"), "--estado", fm.get("estado_general", "vigente"),
           "--minimo", str(int(len(claves) * 0.98)), "--salida", ruta]
    if fm.get("titulo_corto"):
        cmd += ["--corto", fm["titulo_corto"]]
    if claves and not any("." in c for c in claves):
        cmd.append("--enteros")
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
