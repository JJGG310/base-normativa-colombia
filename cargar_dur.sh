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

# --- Los doce DUR restantes. El título es el de la propia página del Gestor. ------
run 76835 1066 --minimo 150 --id co:decreto:1066:2015 \
    --titulo "Decreto 1066 de 2015 - DUR del Sector Administrativo del Interior" \
    --ramas "administrativo, policivo, constitucional" --salida normativa/co-decreto-1066-2015.md

run 72893 1068 --minimo 150 --id co:decreto:1068:2015 \
    --titulo "Decreto 1068 de 2015 - DUR del Sector Hacienda y Crédito Público" \
    --ramas "tributario, financiero, administrativo" --salida normativa/co-decreto-1068-2015.md

run 76837 1070 --minimo 150 --id co:decreto:1070:2015 \
    --titulo "Decreto 1070 de 2015 - DUR del Sector Administrativo de Defensa" \
    --ramas "defensa, administrativo" --salida normativa/co-decreto-1070-2015.md

run 76838 1071 --minimo 150 --id co:decreto:1071:2015 \
    --titulo "Decreto 1071 de 2015 - DUR del Sector Administrativo Agropecuario, Pesquero y de Desarrollo Rural" \
    --ramas "agrario, administrativo" --salida normativa/co-decreto-1071-2015.md

run 77887 1073 --minimo 150 --id co:decreto:1073:2015 \
    --titulo "Decreto 1073 de 2015 - DUR del Sector Administrativo de Minas y Energía" \
    --ramas "minero-energetico, administrativo" --salida normativa/co-decreto-1073-2015.md

run 77913 1075 --minimo 150 --id co:decreto:1075:2015 \
    --titulo "Decreto 1075 de 2015 - DUR del Sector Educación" \
    --ramas "educacion, administrativo" --salida normativa/co-decreto-1075-2015.md

run 77888 1078 --minimo 150 --id co:decreto:1078:2015 \
    --titulo "Decreto 1078 de 2015 - DUR del Sector de Tecnologías de la Información y las Comunicaciones" \
    --ramas "tic, administrativo" --salida normativa/co-decreto-1078-2015.md

run 77889 1079 --minimo 150 --id co:decreto:1079:2015 \
    --titulo "Decreto 1079 de 2015 - DUR del Sector Transporte" \
    --ramas "transporte, administrativo" --salida normativa/co-decreto-1079-2015.md

run 76833 1080 --minimo 150 --id co:decreto:1080:2015 \
    --titulo "Decreto 1080 de 2015 - DUR del Sector Cultura" \
    --ramas "cultura, administrativo" --salida normativa/co-decreto-1080-2015.md

run 73593 1081 --minimo 150 --id co:decreto:1081:2015 \
    --titulo "Decreto 1081 de 2015 - DUR del Sector Presidencia de la República" \
    --ramas "administrativo, constitucional" --salida normativa/co-decreto-1081-2015.md

run 77715 1084 --minimo 150 --id co:decreto:1084:2015 \
    --titulo "Decreto 1084 de 2015 - DUR del Sector de Inclusión Social y Reconciliación" \
    --ramas "social, victimas, administrativo" --salida normativa/co-decreto-1084-2015.md

run 77714 1085 --minimo 100 --id co:decreto:1085:2015 \
    --titulo "Decreto 1085 de 2015 - DUR del Sector Administrativo del Deporte" \
    --ramas "deporte, administrativo" --salida normativa/co-decreto-1085-2015.md

# --- Normas del Gestor que no son DUR (senado no las publica) --------------------
run 5259 2158 --minimo 100 --id co:decreto:2158:1948 --tipo decreto-ley \
    --titulo "Decreto 2158 de 1948 - Código Procesal del Trabajo y de la Seguridad Social" \
    --corto "CPTSS" --ramas "laboral, procesal, seguridad-social" \
    --salida normativa/co-decreto-ley-2158-1948.md

run 1348 663 --minimo 150 --id co:decreto:663:1993 \
    --titulo "Decreto 663 de 1993 - Estatuto Orgánico del Sistema Financiero" --corto "EOSF" \
    --ramas "financiero, comercial, administrativo" --salida normativa/co-decreto-663-1993.md

run 3431 23 --minimo 150 --tipo ley --id co:ley:23:1982 \
    --titulo "Ley 23 de 1982 - Derechos de autor" \
    --ramas "propiedad-intelectual, civil, comercial" --salida normativa/co-ley-23-1982.md

run 53646 1377 --minimo 20 --id co:decreto:1377:2013 \
    --titulo "Decreto 1377 de 2013 - Reglamento de protección de datos personales" \
    --ramas "datos-personales, administrativo" --salida normativa/co-decreto-1377-2013.md
