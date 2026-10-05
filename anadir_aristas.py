#!/usr/bin/env python3
"""Añade aristas manuales a relaciones.csv bajo el candado de las ingestas (pueden estar corriendo).

    python3 anadir_aristas.py aristas.csv   # 6 columnas: origen,tipo,destino,fecha,nota,fuente; con o sin cabecera

Idempotente: salta las filas idénticas a una ya presente. La nota debe empezar por «manual:» para que
una re-ingesta no la borre (guardar_relaciones / guardar_aristas solo conservan esas y las CENDOJ).
"""
import csv, fcntl, os, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
nuevas = [r for r in csv.reader(open(sys.argv[1], encoding="utf-8", newline="")) if r and r[0] != "origen"]
assert all(len(r) == 6 for r in nuevas), "6 columnas: origen,tipo,destino,fecha,nota,fuente"
assert all(r[4].startswith("manual:") for r in nuevas), "la nota debe empezar por «manual:»"
with open(os.path.join(RAIZ, ".relaciones.lock"), "w") as candado:
    fcntl.flock(candado, fcntl.LOCK_EX)
    ruta = os.path.join(RAIZ, "relaciones.csv")
    with open(ruta, encoding="utf-8", newline="") as fh:
        previas = {tuple(r) for r in csv.reader(fh)}
    nuevas = [r for r in dict.fromkeys(map(tuple, nuevas)) if r not in previas]
    with open(ruta, "a", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerows(nuevas)
print(len(nuevas), "aristas añadidas")
