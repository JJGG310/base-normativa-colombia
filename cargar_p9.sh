#!/bin/bash
# P9: normas origen más citadas que faltaban (build.py -v).
cd "$(dirname "$0")" || exit 1
B=http://www.secretariasenado.gov.co/senado/basedoc
D=https://normograma.dian.gov.co/dian/compilacion/docs

run() { echo "== $1"; python3 ingesta_senado.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 5; }

run $B/ley_0510_1999.html --minimo 90 --id co:ley:510:1999 --tipo ley \
    --titulo "Ley 510 de 1999 - Disposiciones sobre el sistema financiero y asegurador y el mercado público de valores" \
    --ramas "financiero, comercial" --salida normativa/co-ley-510-1999.md
run $B/ley_1142_2007.html --minimo 50 --id co:ley:1142:2007 --tipo ley \
    --titulo "Ley 1142 de 2007 - Reformas a las Leyes 906 de 2004, 599 y 600 de 2000 (convivencia y seguridad ciudadana)" \
    --ramas "penal, procesal" --salida normativa/co-ley-1142-2007.md
run $B/ley_0962_2005.html --minimo 70 --id co:ley:962:2005 --tipo ley \
    --titulo "Ley 962 de 2005 - Racionalización de trámites y procedimientos administrativos (antitrámites)" \
    --ramas "administrativo" --salida normativa/co-ley-962-2005.md
run $B/ley_0104_1993.html --minimo 100 --id co:ley:104:1993 --tipo ley \
    --titulo "Ley 104 de 1993 - Instrumentos para la búsqueda de la convivencia y la eficacia de la justicia" \
    --ramas "penal, defensa" --salida normativa/co-ley-104-1993.md
run $B/ley_2421_2024.html --minimo 30 --id co:ley:2421:2024 --tipo ley \
    --titulo "Ley 2421 de 2024 - Modifica la Ley 1448 de 2011 (víctimas y restitución de tierras)" \
    --ramas "victimas, agrario" --salida normativa/co-ley-2421-2024.md
run $B/decreto_2106_2019.html --minimo 130 --id co:decreto:2106:2019 --tipo decreto-ley \
    --titulo "Decreto Ley 2106 de 2019 - Simplificación, supresión y reforma de trámites innecesarios" \
    --ramas "administrativo" --salida normativa/co-decreto-2106-2019.md
run $D/decreto_0360_2021.htm --minimo 100 --id co:decreto:360:2021 --tipo decreto \
    --titulo "Decreto 360 de 2021 - Modifica el Decreto 1165 de 2019 (régimen aduanero)" \
    --ramas "aduanero, tributario" --salida normativa/co-decreto-360-2021.md
run $D/decreto_0659_2024.htm --minimo 40 --id co:decreto:659:2024 --tipo decreto \
    --titulo "Decreto 659 de 2024 - Modifica el Decreto 1165 de 2019 (régimen aduanero)" \
    --ramas "aduanero, tributario" --salida normativa/co-decreto-659-2024.md
run $D/decreto_1743_2015.htm --minimo 5 --id co:decreto:1743:2015 --tipo decreto \
    --titulo "Decreto 1743 de 2015" \
    --ramas "tributario" --salida normativa/co-decreto-1743-2015.md

# --- Decretos que modifican DUR: solo en el Gestor ------------------------------
gestor() { echo "== $1"; python3 ingesta_gestor.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|Error"; sleep 5; }
gestor 62959 --enteros --id co:decreto:1743:2015 --tipo decreto --minimo 2 \
    --titulo "Decreto 1743 de 2015 - Modifica el Decreto 1067 de 2015 (DUR Relaciones Exteriores)" \
    --ramas "administrativo, internacional-publico" --salida normativa/co-decreto-1743-2015.md
gestor 98270 --enteros --id co:decreto:1330:2019 --tipo decreto --minimo 2 \
    --titulo "Decreto 1330 de 2019 - Sustituye el Capítulo 2 del Título 3 del Decreto 1075 de 2015 (registro calificado)" \
    --ramas "educacion, administrativo" --salida normativa/co-decreto-1330-2019.md
gestor 64533 --enteros --id co:decreto:2029:2015 --tipo decreto --minimo 2 \
    --titulo "Decreto 2029 de 2015 - Modifica el Decreto 1075 de 2015 (DUR Educación)" \
    --ramas "educacion, administrativo" --salida normativa/co-decreto-2029-2015.md
gestor 66429 --enteros --id co:decreto:1851:2015 --tipo decreto --minimo 2 \
    --titulo "Decreto 1851 de 2015 - Modifica el Decreto 1075 de 2015 (DUR Educación)" \
    --ramas "educacion, administrativo" --salida normativa/co-decreto-1851-2015.md
gestor 188166 --id co:decreto:1042:2022 --tipo decreto --minimo 2 \
    --fecha 2022-06-21 --titulo "Decreto 1042 de 2022 - Depuración del Decreto 1082 de 2015 (DUR Planeación Nacional)" \
    --ramas "administrativo" --salida normativa/co-decreto-1042-2022.md
gestor 105072 --enteros --id co:decreto:65:2020 --tipo decreto --minimo 2 \
    --titulo "Decreto 65 de 2020 - Modifica el Decreto 1074 de 2015 (DUR Comercio, Industria y Turismo)" \
    --ramas "comercial, administrativo" --salida normativa/co-decreto-65-2020.md
gestor 175148 --enteros --id co:decreto:1835:2021 --tipo decreto --minimo 2 \
    --titulo "Decreto 1835 de 2021 - Modifica el Decreto 1071 de 2015 (DUR Agropecuario)" \
    --ramas "agrario, administrativo" --salida normativa/co-decreto-1835-2021.md
gestor 165926 --enteros --id co:decreto:770:2021 --tipo decreto --minimo 2 \
    --titulo "Decreto 770 de 2021 - Modifica el Decreto 1083 de 2015 (DUR Función Pública)" \
    --ramas "administrativo, laboral" --salida normativa/co-decreto-770-2021.md

# --- Otras compilaciones con la plataforma de senado ------------------------------
# Ley 50/1990: senado 404 y el Gestor la mezcla con el CST; la Cancillería la publica
# con el formato de senado (anclas bookmarkaj + js de notas).
run https://www.cancilleria.gov.co/normograma/compilacion/docs/ley_0050_1990.htm --minimo 100 \
    --id co:ley:50:1990 --tipo ley \
    --titulo "Ley 50 de 1990 - Reformas al Código Sustantivo del Trabajo" \
    --ramas "laboral, seguridad-social" --salida normativa/co-ley-50-1990.md
run $D/decreto_1643_1991.htm --minimo 30 --id co:decreto:1643:1991 --tipo decreto-ley \
    --titulo "Decreto 1643 de 1991 - Organización de la Dirección de Impuestos Nacionales" \
    --ramas "tributario, administrativo" --salida normativa/co-decreto-1643-1991.md
gestor 80915 --enteros --id co:decreto:648:2017 --tipo decreto --minimo 2 \
    --titulo "Decreto 648 de 2017 - Modifica y adiciona el Decreto 1083 de 2015 (DUR Función Pública)" \
    --ramas "administrativo, laboral" --salida normativa/co-decreto-648-2017.md
