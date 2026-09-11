#!/bin/bash
# Decretos Únicos Reglamentarios, vía Gestor Normativo (senado no los publica).
# El `i=` sale del índice de DUR del propio Gestor (norma.php?i=62255).
# La fecha ya no se pasa a mano: sale del «(Mayo 26)» del encabezado de la fuente.
cd "$(dirname "$0")" || exit 1

run() { echo "== $2"; python3 ingesta_gestor.py "$1" "${@:3}" 2>&1 \
    | grep -E "artículos ->|aristas ->|no reconocidas|ABORTA|fecha"; }

run 74174 1069 --minimo 150 --id co:decreto:1069:2015 \
    --titulo "Decreto 1069 de 2015 - DUR del Sector Justicia y del Derecho" \
    --ramas "justicia, administrativo, procesal" --salida normativa/co-decreto-1069-2015.md

run 72173 1072 --minimo 150 --id co:decreto:1072:2015 \
    --titulo "Decreto 1072 de 2015 - DUR del Sector Trabajo" \
    --ramas "laboral, seguridad-social, administrativo" --salida normativa/co-decreto-1072-2015.md

run 76608 1074 --minimo 150 --id co:decreto:1074:2015 \
    --titulo "Decreto 1074 de 2015 - DUR del Sector Comercio, Industria y Turismo" \
    --ramas "comercial, societario, consumo, administrativo" --salida normativa/co-decreto-1074-2015.md

run 78153 1076 --minimo 150 --id co:decreto:1076:2015 \
    --titulo "Decreto 1076 de 2015 - DUR del Sector Ambiente y Desarrollo Sostenible" \
    --ramas "ambiental, administrativo" --salida normativa/co-decreto-1076-2015.md

run 77216 1077 --minimo 150 --id co:decreto:1077:2015 \
    --titulo "Decreto 1077 de 2015 - DUR del Sector Vivienda, Ciudad y Territorio" \
    --ramas "urbanistico, servicios-publicos, administrativo" --salida normativa/co-decreto-1077-2015.md

run 77653 1082 --minimo 150 --id co:decreto:1082:2015 \
    --titulo "Decreto 1082 de 2015 - DUR del Sector Administrativo de Planeación Nacional" \
    --ramas "contratacion-estatal, administrativo" --salida normativa/co-decreto-1082-2015.md

run 62866 1083 --minimo 150 --id co:decreto:1083:2015 \
    --titulo "Decreto 1083 de 2015 - DUR del Sector de Función Pública" \
    --ramas "administrativo, laboral" --salida normativa/co-decreto-1083-2015.md
