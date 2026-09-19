#!/bin/bash
# Corte Suprema: primera tanda. El portal exige término de búsqueda, así que esto no
# es «toda la Corte» — es lo que los términos amplios alcanzan, por sala y por año.
# Subir --limite o agregar años es la perilla para ampliar la cobertura.
cd "$(dirname "$0")" || exit 1
for sala in CIVIL LABORAL PENAL; do
  for anio in 2025 2024 2023 2022; do
    echo "== $sala $anio"
    python3 ingesta_cendoj.py "$sala" "$anio" --limite 80
  done
done
