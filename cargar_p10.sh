#!/bin/bash
# P10: siguientes normas origen más citadas (build.py -v).
cd "$(dirname "$0")" || exit 1
B=http://www.secretariasenado.gov.co/senado/basedoc

run() { echo "== $1"; python3 ingesta_senado.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 5; }
gestor() { echo "== $1"; python3 ingesta_gestor.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; }

run $B/ley_0241_1995.html --minimo 10 --id co:ley:241:1995 --tipo ley \
    --titulo "Ley 241 de 1995 - Prorroga la vigencia, modifica y adiciona la Ley 104 de 1993" \
    --ramas "penal, administrativo" --salida normativa/co-ley-241-1995.md
run $B/ley_0418_1997.html --minimo 10 --id co:ley:418:1997 --tipo ley \
    --titulo "Ley 418 de 1997 - Instrumentos para la búsqueda de la convivencia y la eficacia de la justicia" \
    --ramas "penal, victimas, administrativo" --salida normativa/co-ley-418-1997.md
run $B/ley_1849_2017.html --minimo 10 --id co:ley:1849:2017 --tipo ley \
    --titulo "Ley 1849 de 2017 - Modifica y adiciona la Ley 1708 de 2014 (Código de Extinción de Dominio)" \
    --ramas "penal, procesal" --salida normativa/co-ley-1849-2017.md
run $B/ley_1739_2014.html --minimo 10 --id co:ley:1739:2014 --tipo ley \
    --titulo "Ley 1739 de 2014 - Modifica el Estatuto Tributario y la Ley 1607 de 2012; mecanismos contra la evasión" \
    --ramas "tributario" --salida normativa/co-ley-1739-2014.md
run $B/ley_1592_2012.html --minimo 10 --id co:ley:1592:2012 --tipo ley \
    --titulo "Ley 1592 de 2012 - Modificaciones a la Ley 975 de 2005 (Justicia y Paz)" \
    --ramas "penal, transicional, victimas" --salida normativa/co-ley-1592-2012.md
run $B/ley_0982_2005.html --minimo 10 --id co:ley:982:2005 --tipo ley \
    --titulo "Ley 982 de 2005 - Equiparación de oportunidades para las personas sordas y sordociegas" \
    --ramas "social, administrativo" --salida normativa/co-ley-982-2005.md
run $B/ley_1430_2010.html --minimo 10 --id co:ley:1430:2010 --tipo ley \
    --titulo "Ley 1430 de 2010 - Normas tributarias de control y para la competitividad" \
    --ramas "tributario" --salida normativa/co-ley-1430-2010.md
run $B/ley_1152_2007.html --minimo 10 --id co:ley:1152:2007 --tipo ley \
    --titulo "Ley 1152 de 2007 - Estatuto de Desarrollo Rural; reforma el Incoder" \
    --ramas "agrario, administrativo" --salida normativa/co-ley-1152-2007.md
run $B/ley_0383_1997.html --minimo 10 --id co:ley:383:1997 --tipo ley \
    --titulo "Ley 383 de 1997 - Normas para fortalecer la lucha contra la evasión y el contrabando" \
    --ramas "tributario, aduanero" --salida normativa/co-ley-383-1997.md
run $B/ley_0134_1994.html --minimo 10 --id co:ley-estatutaria:134:1994 --tipo ley-estatutaria --fecha 1994-05-31 \
    --titulo "Ley 134 de 1994 - Mecanismos de participación ciudadana" \
    --ramas "constitucional, electoral" --salida normativa/co-ley-estatutaria-134-1994.md

# --- Decretos reformadores de DUR (Gestor, numeración entera) -----------------------
gestor 257816 --enteros --id co:decreto:104:2025 --tipo decreto --minimo 2 \
    --titulo "Decreto 104 de 2025 - Modifica y adiciona el Decreto 1069 de 2015 (Sistema de Defensa Jurídica del Estado)" \
    --ramas "administrativo, procesal" --salida normativa/co-decreto-104-2025.md
gestor 175266 --enteros --id co:decreto:1836:2021 --tipo decreto --minimo 2 \
    --titulo "Decreto 1836 de 2021 - Modifica y adiciona el Decreto 1074 de 2015 (Registro Nacional de Turismo y plataformas digitales)" \
    --ramas "comercial, administrativo" --salida normativa/co-decreto-1836-2021.md
gestor 175086 --enteros --id co:decreto:1783:2021 --tipo decreto --minimo 2 \
    --titulo "Decreto 1783 de 2021 - Modifica el Decreto 1077 de 2015 (licencias urbanísticas)" \
    --ramas "urbanistico, administrativo" --salida normativa/co-decreto-1783-2021.md
gestor 249376 --enteros --id co:decreto:1063:2024 --tipo decreto --minimo 2 \
    --titulo "Decreto 1063 de 2024 - Modifica el Decreto 1070 de 2015 (Gente de Mar)" \
    --ramas "maritimo, defensa" --salida normativa/co-decreto-1063-2024.md
gestor 213970 --enteros --id co:decreto:1167:2023 --tipo decreto --minimo 2 \
    --titulo "Decreto 1167 de 2023 - Modifica el Decreto 1074 de 2015 (auxiliares de la justicia en insolvencia)" \
    --ramas "insolvencia, comercial" --salida normativa/co-decreto-1167-2023.md
gestor 172769 --enteros --id co:decreto:1338:2021 --tipo decreto --minimo 2 \
    --titulo "Decreto 1338 de 2021 - Adiciona el Decreto 1074 de 2015 (contribución parafiscal para el turismo)" \
    --ramas "tributario, comercial" --salida normativa/co-decreto-1338-2021.md
gestor 174036 --enteros --id co:decreto:1648:2021 --tipo decreto --minimo 1 \
    --titulo "Decreto 1648 de 2021 - Sustituye la Parte 12 del Decreto 1085 de 2015 (antidopaje)" \
    --ramas "deporte, administrativo" --salida normativa/co-decreto-1648-2021.md
gestor 173949 --enteros --id co:decreto:1650:2021 --tipo decreto --minimo 1 \
    --titulo "Decreto 1650 de 2021 - Adiciona el Decreto 1072 de 2015 (Subsistema de Formación para el Trabajo)" \
    --ramas "laboral, educacion" --salida normativa/co-decreto-1650-2021.md
gestor 66599 --enteros --id co:decreto:2348:2015 --tipo decreto --minimo 2 \
    --titulo "Decreto 2348 de 2015 - Modifica el Decreto 1067 de 2015 (concurrencias y circunscripciones consulares)" \
    --ramas "internacional-publico, administrativo" --salida normativa/co-decreto-2348-2015.md
# DUR del Sistema General de Regalías (numeración decimal propia)
gestor 154466 --id co:decreto:1821:2020 --tipo decreto --minimo 50 \
    --titulo "Decreto 1821 de 2020 - Decreto Único Reglamentario del Sistema General de Regalías" \
    --ramas "territorial, minero-energetico, administrativo" --salida normativa/co-decreto-1821-2020.md

# Ley 21/1991 (Convenio 169 OIT). Senado 404. Como la Ley 518/1999 (CISG): los artículos del
# tratado son art:N (así se citan: «art. 6 del Convenio 169»); los arts. 1-3 aprobatorios de
# la ley quedan en el texto del art. 44, después de la constancia de la Cancillería.
gestor 37032 --id co:ley:21:1991 --tipo ley --minimo 44 \
    --titulo "Ley 21 de 1991 - Aprueba el Convenio 169 de la OIT sobre pueblos indígenas y tribales en países independientes" \
    --ramas "etnico, internacional-publico, constitucional" --salida normativa/co-ley-21-1991.md

# Ley 2430/2024: recarga para leer las notas de la revisión previa C-134/2023
# («declara CONSTITUCIONAL / INCONSTITUCIONAL»), que aristas() antes no reconocía.
run $B/ley_2430_2024.html --minimo 50 --id co:ley-estatutaria:2430:2024 --tipo ley-estatutaria \
    --titulo "Ley 2430 de 2024 - Modifica la Ley 270 de 1996, Estatutaria de la Administración de Justicia" \
    --ramas "constitucional, procesal" --salida normativa/co-ley-estatutaria-2430-2024.md
