#!/bin/bash
# P5: lo que se ve que falta al usar la base — conciliación, JEP, justicia y paz,
# garantías mobiliarias, comisarías de familia y demás normas que el litigio cita.
cd "$(dirname "$0")" || exit 1
B=http://www.secretariasenado.gov.co/senado/basedoc

run() { echo "== $1"; python3 ingesta_senado.py "$B/$1.html" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; }

# --- Conciliación y arbitraje ---------------------------------------------------
run ley_2220_2022 --minimo 80 --id co:ley:2220:2022 --tipo ley \
    --titulo "Ley 2220 de 2022 - Estatuto de Conciliación" \
    --ramas "procesal, civil, administrativo" --salida normativa/co-ley-2220-2022.md

run ley_0640_2001 --minimo 30 --id co:ley:640:2001 --tipo ley \
    --titulo "Ley 640 de 2001 - Normas relativas a la conciliación" \
    --ramas "procesal, civil" --salida normativa/co-ley-640-2001.md

# --- Justicia transicional ------------------------------------------------------
run ley_1957_2019 --minimo 100 --id co:ley-estatutaria:1957:2019 --tipo ley-estatutaria \
    --titulo "Ley 1957 de 2019 - Estatutaria de la Administración de Justicia en la JEP" \
    --ramas "transicional, penal, constitucional" --salida normativa/co-ley-estatutaria-1957-2019.md

run ley_1922_2018 --minimo 40 --id co:ley:1922:2018 --tipo ley \
    --titulo "Ley 1922 de 2018 - Reglas de procedimiento para la JEP" \
    --ramas "transicional, penal, procesal" --salida normativa/co-ley-1922-2018.md

run ley_0975_2005 --minimo 50 --id co:ley:975:2005 --tipo ley \
    --titulo "Ley 975 de 2005 - Justicia y Paz" \
    --ramas "transicional, penal" --salida normativa/co-ley-975-2005.md

# --- Comercial y financiero -----------------------------------------------------
run ley_1676_2013 --minimo 50 --id co:ley:1676:2013 --tipo ley \
    --titulo "Ley 1676 de 2013 - Garantías mobiliarias" \
    --ramas "comercial, civil, insolvencia" --salida normativa/co-ley-1676-2013.md

run ley_1314_2009 --minimo 10 --id co:ley:1314:2009 --tipo ley \
    --titulo "Ley 1314 de 2009 - Principios y normas de contabilidad e información financiera" \
    --ramas "comercial, contable" --salida normativa/co-ley-1314-2009.md

run ley_1727_2014 --minimo 20 --id co:ley:1727:2014 --tipo ley \
    --titulo "Ley 1727 de 2014 - Régimen de las cámaras de comercio" \
    --ramas "comercial, societario" --salida normativa/co-ley-1727-2014.md

run ley_1429_2010 --minimo 40 --id co:ley:1429:2010 --tipo ley \
    --titulo "Ley 1429 de 2010 - Formalización y generación de empleo" \
    --ramas "laboral, comercial, tributario" --salida normativa/co-ley-1429-2010.md

# --- Penal especial -------------------------------------------------------------
run ley_1908_2018 --minimo 30 --id co:ley:1908:2018 --tipo ley \
    --titulo "Ley 1908 de 2018 - Grupos delictivos organizados y grupos armados organizados" \
    --ramas "penal, procesal" --salida normativa/co-ley-1908-2018.md

run ley_1778_2016 --minimo 20 --id co:ley:1778:2016 --tipo ley \
    --titulo "Ley 1778 de 2016 - Responsabilidad por soborno transnacional" \
    --ramas "penal, administrativo, comercial" --salida normativa/co-ley-1778-2016.md

run ley_1273_2009 --minimo 3 --id co:ley:1273:2009 --tipo ley \
    --titulo "Ley 1273 de 2009 - Protección de la información y de los datos (delitos informáticos)" \
    --ramas "penal, tic" --salida normativa/co-ley-1273-2009.md

# --- Familia y capacidad --------------------------------------------------------
run ley_2126_2021 --minimo 20 --id co:ley:2126:2021 --tipo ley \
    --titulo "Ley 2126 de 2021 - Comisarías de Familia" \
    --ramas "familia, administrativo" --salida normativa/co-ley-2126-2021.md

run ley_1306_2009 --minimo 50 --id co:ley:1306:2009 --tipo ley \
    --titulo "Ley 1306 de 2009 - Protección de personas con discapacidad mental" \
    --ramas "civil, familia" --salida normativa/co-ley-1306-2009.md
