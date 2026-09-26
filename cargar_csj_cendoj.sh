#!/bin/bash
# Corte Suprema desde CENDOJ WebRelatoria: fichas nuevas con texto íntegro y, para todas (también
# las ya cargadas del portal de la Corte), aristas `cita` desde la FUENTE FORMAL de la relatoría.
cd "$(dirname "$0")" || exit 1
for t in "CONTRATO DE ARRENDAMIENTO" "RESPONSABILIDAD CIVIL EXTRACONTRACTUAL" "CONTRATO DE SEGURO" \
         "PRESCRIPCIÓN ADQUISITIVA" "UNIÓN MARITAL DE HECHO" "SUCESIÓN" "SIMULACIÓN" "RESPONSABILIDAD MÉDICA" \
         "PENSIÓN DE SOBREVIVIENTES" "PENSIÓN DE VEJEZ" "CONTRATO REALIDAD" "INDEMNIZACIÓN MORATORIA" \
         "ESTABILIDAD LABORAL REFORZADA" "HOMICIDIO" "ACCESO CARNAL" "CONCIERTO PARA DELINQUIR" \
         "PECULADO" "ESTAFA" "TRÁFICO DE ESTUPEFACIENTES" "PRINCIPIO DE CONGRUENCIA"; do
  echo "== $t"
  python3 ingesta_webrelatoria.py "$t" --corp CSJ --limite 300 2>&1 | grep -v '^\s*$' | tail -8
done
