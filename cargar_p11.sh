#!/bin/bash
# P11: siguientes normas origen más citadas (build.py -v tras P10).
cd "$(dirname "$0")" || exit 1
B=http://www.secretariasenado.gov.co/senado/basedoc

run() { echo "== $1"; python3 ingesta_senado.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 5; }
gestor() { echo "== $1"; python3 ingesta_gestor.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; }

run $B/ley_0782_2002.html --minimo 20 --id co:ley:782:2002 --tipo ley \
    --titulo "Ley 782 de 2002 - Prorroga la vigencia de la Ley 418 de 1997 y modifica algunas de sus disposiciones" \
    --ramas "penal, victimas, administrativo" --salida normativa/co-ley-782-2002.md
run $B/ley_1421_2010.html --minimo 5 --id co:ley:1421:2010 --tipo ley \
    --titulo "Ley 1421 de 2010 - Prorroga la Ley 418 de 1997, prorrogada y modificada por las Leyes 548 de 1999, 782 de 2002 y 1106 de 2006" \
    --ramas "penal, victimas, administrativo" --salida normativa/co-ley-1421-2010.md
run $B/ley_1395_2010.html --minimo 50 --id co:ley:1395:2010 --tipo ley \
    --titulo "Ley 1395 de 2010 - Medidas en materia de descongestión judicial" \
    --ramas "procesal, civil, penal, laboral" --salida normativa/co-ley-1395-2010.md
run $B/ley_1285_2009.html --minimo 20 --id co:ley:1285:2009 --tipo ley \
    --titulo "Ley 1285 de 2009 - Reforma la Ley 270 de 1996, Estatutaria de la Administración de Justicia" \
    --ramas "constitucional, procesal" --salida normativa/co-ley-1285-2009.md
run $B/ley_0200_1995.html --minimo 100 --id co:ley:200:1995 --tipo ley --estado derogada \
    --titulo "Ley 200 de 1995 - Código Disciplinario Único (derogado por la Ley 734 de 2002)" \
    --ramas "disciplinario, administrativo" --salida normativa/co-ley-200-1995.md
run $B/ley_2200_2022.html --minimo 100 --id co:ley:2200:2022 --tipo ley \
    --titulo "Ley 2200 de 2022 - Organización y funcionamiento de los departamentos" \
    --ramas "territorial, administrativo" --salida normativa/co-ley-2200-2022.md
run $B/ley_1382_2010.html --minimo 20 --id co:ley:1382:2010 --tipo ley \
    --titulo "Ley 1382 de 2010 - Modifica la Ley 685 de 2001, Código de Minas" \
    --ramas "minero-energetico, ambiental" --salida normativa/co-ley-1382-2010.md
run $B/ley_1617_2013.html --minimo 50 --id co:ley:1617:2013 --tipo ley \
    --titulo "Ley 1617 de 2013 - Régimen para los Distritos Especiales" \
    --ramas "territorial, administrativo" --salida normativa/co-ley-1617-2013.md

# --- Gestor --------------------------------------------------------------------------
gestor 83596 --id co:decreto:2351:1965 --tipo decreto-ley --minimo 40 \
    --titulo "Decreto 2351 de 1965 - Reformas al Código Sustantivo del Trabajo" \
    --ramas "laboral" --salida normativa/co-decreto-2351-1965.md
gestor 80962 --id co:decreto:2820:1974 --tipo decreto-ley --minimo 60 \
    --titulo "Decreto 2820 de 1974 - Igualdad de derechos y obligaciones de mujeres y varones (reforma al Código Civil)" \
    --ramas "civil, familia" --salida normativa/co-decreto-2820-1974.md
gestor 171603 --enteros --id co:decreto:1142:2021 --tipo decreto --minimo 10 \
    --titulo "Decreto 1142 de 2021 - Adiciona y modifica el Decreto 1821 de 2020 (DUR Sistema General de Regalías)" \
    --ramas "territorial, minero-energetico" --salida normativa/co-decreto-1142-2021.md
gestor 166993 --enteros --id co:decreto:804:2021 --tipo decreto --minimo 1 \
    --titulo "Decreto 804 de 2021 - Adiciona el Decreto 1821 de 2020 (Sistema de Seguimiento, Evaluación y Control del SGR)" \
    --ramas "territorial, administrativo" --salida normativa/co-decreto-804-2021.md
gestor 256236 --enteros --id co:decreto:1381:2024 --tipo decreto --minimo 2 \
    --titulo "Decreto 1381 de 2024 - Modifica el Decreto 1077 de 2015 (servicio público de aseo, aprovechamiento y recicladores de oficio)" \
    --ramas "servicios-publicos, ambiental" --salida normativa/co-decreto-1381-2024.md
gestor 165219 --enteros --id co:decreto:739:2021 --tipo decreto --minimo 10 \
    --titulo "Decreto 739 de 2021 - Modifica el Decreto 1077 de 2015 (subsidio familiar de vivienda)" \
    --ramas "administrativo, urbanistico" --salida normativa/co-decreto-739-2021.md
gestor 170046 --enteros --id co:decreto:1033:2021 --tipo decreto --minimo 1 \
    --titulo "Decreto 1033 de 2021 - Adiciona el Decreto 1066 de 2015 (Esquemas Asociativos Territoriales)" \
    --ramas "territorial, administrativo" --salida normativa/co-decreto-1033-2021.md
gestor 173589 --enteros --id co:decreto:1494:2021 --tipo decreto --minimo 5 \
    --titulo "Decreto 1494 de 2021 - Modifica la Parte 7 del Libro 2 del Decreto 1068 de 2015 (monopolio de juegos de suerte y azar)" \
    --ramas "administrativo, tributario" --salida normativa/co-decreto-1494-2021.md
gestor 256297 --enteros --id co:decreto:149:2024 --tipo decreto --minimo 2 \
    --titulo "Decreto 149 de 2024 - Reglamenta el depósito legal; modifica el Decreto 1080 de 2015 y deroga artículos del Decreto 1066 de 2015" \
    --ramas "cultura, administrativo" --salida normativa/co-decreto-149-2024.md

# --- Normograma DIAN -----------------------------------------------------------------
run https://normograma.dian.gov.co/dian/compilacion/docs/decreto_2229_2023.htm --minimo 1 \
    --id co:decreto:2229:2023 --tipo decreto \
    --titulo "Decreto 2229 de 2023 - Reglamenta artículos del Estatuto Tributario y modifica el Decreto 1625 de 2016 (plazos 2024)" \
    --ramas "tributario" --salida normativa/co-decreto-2229-2023.md
