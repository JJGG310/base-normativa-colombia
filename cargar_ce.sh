#!/bin/bash
# Consejo de Estado con texto: CENDOJ WebRelatoria (esquema.md §8, fuente 8). El buscador exige
# término: esto es lo que alcanzan los temas, no «todo el Consejo de Estado». --limite es la perilla.
cd "$(dirname "$0")" || exit 1
for t in "NULIDAD SIMPLE" "NULIDAD POR INCONSTITUCIONALIDAD" "CONTROL INMEDIATO DE LEGALIDAD" \
         "NULIDAD ELECTORAL" "PÉRDIDA DE INVESTIDURA" "REPARACIÓN DIRECTA" "CONTRATO ESTATAL" \
         "NULIDAD Y RESTABLECIMIENTO DEL DERECHO" "RESPONSABILIDAD MÉDICA" "ACCIÓN POPULAR" \
         "IMPUESTO SOBRE LA RENTA" "SUSPENSIÓN PROVISIONAL" "PENSIÓN" "CARRERA ADMINISTRATIVA"; do
  echo "== $t"
  python3 ingesta_webrelatoria.py "$t" --limite 400 2>&1 | grep -v '^\s*$' | tail -15
done
