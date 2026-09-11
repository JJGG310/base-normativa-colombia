#!/bin/bash
# P4: las sectoriales que quedaban fuera después de P3 (salud, educación, minas,
# TIC, penitenciario, tributarias, gestión del riesgo…). Mismo mecanismo de siempre.
cd "$(dirname "$0")" || exit 1
B=http://www.secretariasenado.gov.co/senado/basedoc

run() { echo "== $1"; python3 ingesta_senado.py "$B/$1.html" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|sin ancla|ABORTA|fecha|Error"; }

# --- Salud ---------------------------------------------------------------------
run ley_1751_2015 --minimo 20 --id co:ley-estatutaria:1751:2015 --tipo ley-estatutaria \
    --titulo "Ley 1751 de 2015 - Estatutaria de salud" \
    --ramas "salud, constitucional" --salida normativa/co-ley-estatutaria-1751-2015.md

run ley_1438_2011 --minimo 100 --id co:ley:1438:2011 --tipo ley \
    --titulo "Ley 1438 de 2011 - Reforma del Sistema General de Seguridad Social en Salud" \
    --ramas "salud, seguridad-social" --salida normativa/co-ley-1438-2011.md

run ley_1122_2007 --minimo 25 --id co:ley:1122:2007 --tipo ley \
    --titulo "Ley 1122 de 2007 - Modificaciones al Sistema General de Seguridad Social en Salud" \
    --ramas "salud, seguridad-social" --salida normativa/co-ley-1122-2007.md

run ley_0009_1979 --minimo 300 --id co:ley:9:1979 --tipo ley \
    --titulo "Ley 9 de 1979 - Código Sanitario Nacional" \
    --ramas "salud, ambiental, administrativo" --salida normativa/co-ley-9-1979.md

# --- Educación y cultura --------------------------------------------------------
run ley_0030_1992 --minimo 100 --id co:ley:30:1992 --tipo ley \
    --titulo "Ley 30 de 1992 - Educación Superior" \
    --ramas "educacion, administrativo" --salida normativa/co-ley-30-1992.md

run ley_0115_1994 --minimo 150 --id co:ley:115:1994 --tipo ley \
    --titulo "Ley 115 de 1994 - Ley General de Educación" \
    --ramas "educacion, administrativo" --salida normativa/co-ley-115-1994.md

run ley_0397_1997 --minimo 50 --id co:ley:397:1997 --tipo ley \
    --titulo "Ley 397 de 1997 - Ley General de Cultura" \
    --ramas "cultura, administrativo" --salida normativa/co-ley-397-1997.md

# --- Minero-energético, TIC y servicios -----------------------------------------
run ley_0685_2001 --minimo 250 --id co:ley:685:2001 --tipo ley \
    --titulo "Ley 685 de 2001 - Código de Minas" --corto "C. Minas" \
    --ramas "minero-energetico, administrativo" --salida normativa/co-ley-685-2001.md

run ley_0143_1994 --minimo 60 --id co:ley:143:1994 --tipo ley \
    --titulo "Ley 143 de 1994 - Régimen de generación y distribución de energía eléctrica" \
    --ramas "minero-energetico, servicios-publicos" --salida normativa/co-ley-143-1994.md

run ley_1341_2009 --minimo 50 --id co:ley:1341:2009 --tipo ley \
    --titulo "Ley 1341 de 2009 - Principios y conceptos de la sociedad de la información y las TIC" \
    --ramas "tic, administrativo" --salida normativa/co-ley-1341-2009.md

# --- Territorial y gestión del riesgo -------------------------------------------
run ley_1454_2011 --minimo 20 --id co:ley-organica:1454:2011 --tipo ley-organica \
    --titulo "Ley 1454 de 2011 - Ley Orgánica de Ordenamiento Territorial" --corto "LOOT" \
    --ramas "territorial, administrativo" --salida normativa/co-ley-organica-1454-2011.md

run ley_1523_2012 --minimo 40 --id co:ley:1523:2012 --tipo ley \
    --titulo "Ley 1523 de 2012 - Política Nacional de Gestión del Riesgo de Desastres" \
    --ramas "administrativo, ambiental" --salida normativa/co-ley-1523-2012.md

# --- Penal, penitenciario y seguridad -------------------------------------------
run ley_0065_1993 --minimo 150 --id co:ley:65:1993 --tipo ley \
    --titulo "Ley 65 de 1993 - Código Penitenciario y Carcelario" \
    --ramas "penal, administrativo" --salida normativa/co-ley-65-1993.md

run ley_1709_2014 --minimo 70 --id co:ley:1709:2014 --tipo ley \
    --titulo "Ley 1709 de 2014 - Reforma del Código Penitenciario y Carcelario" \
    --ramas "penal, administrativo" --salida normativa/co-ley-1709-2014.md

run ley_1826_2017 --minimo 30 --id co:ley:1826:2017 --tipo ley \
    --titulo "Ley 1826 de 2017 - Procedimiento penal especial abreviado y acusador privado" \
    --ramas "penal, procesal" --salida normativa/co-ley-1826-2017.md

run ley_2197_2022 --minimo 40 --id co:ley:2197:2022 --tipo ley \
    --titulo "Ley 2197 de 2022 - Seguridad ciudadana" \
    --ramas "penal, policivo" --salida normativa/co-ley-2197-2022.md

# --- Tributario y administrativo reciente ---------------------------------------
run ley_1819_2016 --minimo 200 --id co:ley:1819:2016 --tipo ley \
    --titulo "Ley 1819 de 2016 - Reforma tributaria estructural" \
    --ramas "tributario" --salida normativa/co-ley-1819-2016.md

# senado publica 61 artículos de esta ley: el resto quedó absorbido en el ET
run ley_2010_2019 --minimo 55 --id co:ley:2010:2019 --tipo ley \
    --titulo "Ley 2010 de 2019 - Normas para la promoción del crecimiento económico (reforma tributaria)" \
    --ramas "tributario" --salida normativa/co-ley-2010-2019.md

run ley_2277_2022 --minimo 50 --id co:ley:2277:2022 --tipo ley \
    --titulo "Ley 2277 de 2022 - Reforma tributaria para la igualdad y la justicia social" \
    --ramas "tributario" --salida normativa/co-ley-2277-2022.md

run ley_2080_2021 --minimo 50 --id co:ley:2080:2021 --tipo ley \
    --titulo "Ley 2080 de 2021 - Reforma del CPACA" \
    --ramas "contencioso-administrativo, procesal" --salida normativa/co-ley-2080-2021.md

run ley_2195_2022 --minimo 50 --id co:ley:2195:2022 --tipo ley \
    --titulo "Ley 2195 de 2022 - Transparencia, prevención y lucha contra la corrupción" \
    --ramas "administrativo, penal, disciplinario" --salida normativa/co-ley-2195-2022.md

run ley_2069_2020 --minimo 40 --id co:ley:2069:2020 --tipo ley \
    --titulo "Ley 2069 de 2020 - Impulso al emprendimiento" \
    --ramas "comercial, societario, contratacion-estatal" --salida normativa/co-ley-2069-2020.md

# la ley entera son dos artículos en la fuente: sustituye el título II del CPACA
run ley_1755_2015 --minimo 2 --id co:ley-estatutaria:1755:2015 --tipo ley-estatutaria \
    --titulo "Ley 1755 de 2015 - Derecho fundamental de petición" \
    --ramas "administrativo, constitucional" --salida normativa/co-ley-estatutaria-1755-2015.md
