#!/bin/bash
# CENDOJ WebRelatoria (esquema.md §8, fuente 8): Consejo de Estado y Corte Suprema, EN SERIE —
# en paralelo el servidor respondió 502 y se cayó (2026-09-25). Se puede relanzar: salta lo que ya
# está (LOG=archivo guarda la salida completa, con los «[!] NR …» de cada fallida). El buscador exige término: esto es lo que alcanzan los temas; --limite es la perilla.
cd "$(dirname "$0")" || exit 1
until [ "$(curl -s -o /dev/null -w '%{http_code}' -A Mozilla/5.0 --max-time 60 \
      https://jurisprudencia.ramajudicial.gov.co/WebRelatoria/consulta/index.xhtml)" = 200 ]; do
  echo "CENDOJ no responde; espero 10 min"; sleep 600
done
for t in "NULIDAD SIMPLE" "NULIDAD POR INCONSTITUCIONALIDAD" "CONTROL INMEDIATO DE LEGALIDAD" \
         "NULIDAD ELECTORAL" "PÉRDIDA DE INVESTIDURA" "REPARACIÓN DIRECTA" "CONTRATO ESTATAL" \
         "NULIDAD Y RESTABLECIMIENTO DEL DERECHO" "RESPONSABILIDAD MÉDICA" "ACCIÓN POPULAR" \
         "IMPUESTO SOBRE LA RENTA" "SUSPENSIÓN PROVISIONAL" "PENSIÓN" "CARRERA ADMINISTRATIVA"; do
  echo "== CE $t"; python3 ingesta_webrelatoria.py "$t" --corp CE --limite 400 --pausa 2 2>&1 | tee -a "${LOG:-/dev/null}" | tail -4
done
for t in "CONTRATO DE ARRENDAMIENTO" "RESPONSABILIDAD CIVIL EXTRACONTRACTUAL" "CONTRATO DE SEGURO" \
         "PRESCRIPCIÓN ADQUISITIVA" "UNIÓN MARITAL DE HECHO" "SUCESIÓN" "SIMULACIÓN" "RESPONSABILIDAD MÉDICA" \
         "PENSIÓN DE SOBREVIVIENTES" "PENSIÓN DE VEJEZ" "CONTRATO REALIDAD" "INDEMNIZACIÓN MORATORIA" \
         "ESTABILIDAD LABORAL REFORZADA" "HOMICIDIO" "ACCESO CARNAL" "CONCIERTO PARA DELINQUIR" \
         "PECULADO" "ESTAFA" "TRÁFICO DE ESTUPEFACIENTES" "PRINCIPIO DE CONGRUENCIA"; do
  echo "== CSJ $t"; python3 ingesta_webrelatoria.py "$t" --corp CSJ --limite 300 --pausa 2 2>&1 | tee -a "${LOG:-/dev/null}" | tail -4
done
