#!/bin/bash
# P7: cobertura — nuevo CPT (Ley 2452/2025), familia/notarial, estatutarias,
# PND, tributarias reformadoras del ET, contratación y vivienda.
cd "$(dirname "$0")" || exit 1
B=http://www.secretariasenado.gov.co/senado/basedoc

run() { echo "== $1"; python3 ingesta_senado.py "$B/$1.html" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 5; }

# --- Laboral procesal -----------------------------------------------------------
run ley_2452_2025 --minimo 300 --id co:ley:2452:2025 --tipo ley \
    --titulo "Ley 2452 de 2025 - Código Procesal del Trabajo y de la Seguridad Social" \
    --corto "CPTSS 2025" --ramas "laboral, procesal, seguridad-social" \
    --salida normativa/co-ley-2452-2025.md

# --- Administrativo, notarial, familia -----------------------------------------
run decreto_0019_2012 --minimo 200 --id co:decreto:19:2012 --tipo decreto-ley \
    --titulo "Decreto Ley 19 de 2012 - Supresión y reforma de trámites innecesarios (antitrámites)" \
    --ramas "administrativo" --salida normativa/co-decreto-19-2012.md

run decreto_0960_1970 --minimo 180 --id co:decreto:960:1970 --tipo decreto-ley \
    --titulo "Decreto 960 de 1970 - Estatuto del Notariado" \
    --ramas "notarial-registral" --salida normativa/co-decreto-960-1970.md

run ley_0294_1996 --minimo 20 --id co:ley:294:1996 --tipo ley \
    --titulo "Ley 294 de 1996 - Prevención y sanción de la violencia intrafamiliar" \
    --ramas "familia, penal" --salida normativa/co-ley-294-1996.md

# --- Estatutarias ---------------------------------------------------------------
run ley_1095_2006 --minimo 8 --id co:ley:1095:2006 --tipo ley \
    --titulo "Ley 1095 de 2006 - Reglamenta el artículo 30 de la Constitución (hábeas corpus)" \
    --ramas "constitucional, penal, procesal" --salida normativa/co-ley-1095-2006.md

run ley_0137_1994 --minimo 50 --id co:ley-estatutaria:137:1994 --tipo ley-estatutaria \
    --titulo "Ley 137 de 1994 - Estados de excepción" \
    --ramas "constitucional" --salida normativa/co-ley-estatutaria-137-1994.md

# --- Planes de desarrollo ------------------------------------------------------
run ley_1955_2019 --minimo 250 --id co:ley:1955:2019 --tipo ley \
    --titulo "Ley 1955 de 2019 - Plan Nacional de Desarrollo 2018-2022" \
    --ramas "administrativo" --salida normativa/co-ley-1955-2019.md

run ley_2294_2023 --minimo 300 --id co:ley:2294:2023 --tipo ley \
    --titulo "Ley 2294 de 2023 - Plan Nacional de Desarrollo 2022-2026" \
    --ramas "administrativo" --salida normativa/co-ley-2294-2023.md

# --- Tributario y cartera pública ----------------------------------------------
run ley_1607_2012 --minimo 150 --id co:ley:1607:2012 --tipo ley \
    --titulo "Ley 1607 de 2012 - Reforma tributaria" \
    --ramas "tributario" --salida normativa/co-ley-1607-2012.md

run ley_1231_2008 --minimo 8 --id co:ley:1231:2008 --tipo ley \
    --titulo "Ley 1231 de 2008 - Factura como título valor" \
    --ramas "comercial" --salida normativa/co-ley-1231-2008.md

run ley_1066_2006 --minimo 15 --id co:ley:1066:2006 --tipo ley \
    --titulo "Ley 1066 de 2006 - Normalización de la cartera pública" \
    --ramas "administrativo, tributario" --salida normativa/co-ley-1066-2006.md

run decreto_0403_2020 --minimo 120 --id co:decreto-ley:403:2020 --tipo decreto-ley \
    --titulo "Decreto Ley 403 de 2020 - Implementación del Acto Legislativo 04 de 2019 y fortalecimiento del control fiscal" \
    --ramas "administrativo" --salida normativa/co-decreto-ley-403-2020.md

# --- Nacionalidad, insolvencia, vivienda, contratación --------------------------
run ley_0043_1993 --minimo 35 --id co:ley:43:1993 --tipo ley \
    --titulo "Ley 43 de 1993 - Adquisición, renuncia, pérdida y recuperación de la nacionalidad colombiana" \
    --ramas "constitucional, migratorio" --salida normativa/co-ley-43-1993.md

run ley_2445_2025 --minimo 20 --id co:ley:2445:2025 --tipo ley \
    --titulo "Ley 2445 de 2025 - Modifica el régimen de insolvencia de la persona natural no comerciante (CGP)" \
    --ramas "insolvencia, procesal, civil" --salida normativa/co-ley-2445-2025.md

run ley_0546_1999 --minimo 50 --id co:ley:546:1999 --tipo ley \
    --titulo "Ley 546 de 1999 - Ley de vivienda (sistema especializado de financiación)" \
    --ramas "financiero, civil, urbanistico" --salida normativa/co-ley-546-1999.md

run ley_1882_2018 --minimo 15 --id co:ley:1882:2018 --tipo ley \
    --titulo "Ley 1882 de 2018 - Fortalecimiento de la contratación pública e infraestructura" \
    --ramas "contratacion-estatal" --salida normativa/co-ley-1882-2018.md

# --- Reformadoras del Estatuto Tributario --------------------------------------
run ley_0223_1995 --minimo 250 --id co:ley:223:1995 --tipo ley \
    --titulo "Ley 223 de 1995 - Racionalización tributaria" \
    --ramas "tributario" --salida normativa/co-ley-223-1995.md

run ley_0006_1992 --minimo 100 --id co:ley:6:1992 --tipo ley \
    --titulo "Ley 6 de 1992 - Reforma tributaria" \
    --ramas "tributario" --salida normativa/co-ley-6-1992.md

run ley_1943_2018 --minimo 100 --id co:ley:1943:2018 --tipo ley \
    --titulo "Ley 1943 de 2018 - Ley de financiamiento" \
    --ramas "tributario" --salida normativa/co-ley-1943-2018.md

run ley_1753_2015 --minimo 200 --id co:ley:1753:2015 --tipo ley \
    --titulo "Ley 1753 de 2015 - Plan Nacional de Desarrollo 2014-2018" \
    --ramas "administrativo" --salida normativa/co-ley-1753-2015.md

run ley_0788_2002 --minimo 100 --id co:ley:788:2002 --tipo ley \
    --titulo "Ley 788 de 2002 - Reforma tributaria" \
    --ramas "tributario, penal" --salida normativa/co-ley-788-2002.md

# --- Gestor Normativo (senado no publica ley_0054_1990: 404) ---------------------
rung() { echo "== $2"; python3 ingesta_gestor.py "$1" "${@:3}" 2>&1 \
    | grep -E "artículos ->|aristas ->|no reconocidas|ABORTA|fecha"; sleep 5; }

# BLOQUEADA: 0 artículos — la página usa <a id="1"> y no <a name="1">; ver cola.md P7.
# rung 30896 54 --minimo 8 --id co:ley:54:1990 --tipo ley \
#     --titulo "Ley 54 de 1990 - Uniones maritales de hecho y régimen patrimonial entre compañeros permanentes" \
#     --ramas "familia, civil" --salida normativa/co-ley-54-1990.md
