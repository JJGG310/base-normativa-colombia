#!/bin/bash
# P6: huecos que el uso deja ver — vivienda y registro, laboral/pensional reciente,
# seguridad ciudadana, fiscal, financiero y competencia, ambiental y étnico.
cd "$(dirname "$0")" || exit 1
B=http://www.secretariasenado.gov.co/senado/basedoc

run() { echo "== $1"; python3 ingesta_senado.py "$B/$1.html" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 5; }

# --- Vivienda y registro --------------------------------------------------------
run ley_0675_2001 --minimo 60 --id co:ley:675:2001 --tipo ley \
    --titulo "Ley 675 de 2001 - Régimen de propiedad horizontal" \
    --ramas "civil, urbanistico" --salida normativa/co-ley-675-2001.md

run ley_0820_2003 --minimo 30 --id co:ley:820:2003 --tipo ley \
    --titulo "Ley 820 de 2003 - Régimen de arrendamiento de vivienda urbana" \
    --ramas "civil, urbanistico" --salida normativa/co-ley-820-2003.md

run ley_1579_2012 --minimo 70 --id co:ley:1579:2012 --tipo ley \
    --titulo "Ley 1579 de 2012 - Estatuto de registro de instrumentos públicos" \
    --ramas "notarial-registral, civil" --salida normativa/co-ley-1579-2012.md

# --- Laboral y pensional --------------------------------------------------------
run ley_2381_2024 --minimo 60 --id co:ley:2381:2024 --tipo ley \
    --titulo "Ley 2381 de 2024 - Sistema de Protección Social Integral para la Vejez, Invalidez y Muerte (reforma pensional)" \
    --ramas "seguridad-social, laboral" --salida normativa/co-ley-2381-2024.md

run ley_0789_2002 --minimo 35 --id co:ley:789:2002 --tipo ley \
    --titulo "Ley 789 de 2002 - Normas para apoyar el empleo y ampliar la protección social" \
    --ramas "laboral, seguridad-social" --salida normativa/co-ley-789-2002.md

run ley_2101_2021 --minimo 3 --id co:ley:2101:2021 --tipo ley \
    --titulo "Ley 2101 de 2021 - Reducción de la jornada laboral semanal" \
    --ramas "laboral" --salida normativa/co-ley-2101-2021.md

run ley_2466_2025 --minimo 40 --id co:ley:2466:2025 --tipo ley \
    --titulo "Ley 2466 de 2025 - Reforma Laboral para el trabajo decente y digno" \
    --ramas "laboral, seguridad-social" --salida normativa/co-ley-2466-2025.md

# --- Penal ----------------------------------------------------------------------
run ley_1453_2011 --minimo 80 --id co:ley:1453:2011 --tipo ley \
    --titulo "Ley 1453 de 2011 - Seguridad ciudadana" \
    --ramas "penal, procesal, policivo" --salida normativa/co-ley-1453-2011.md

run ley_0890_2004 --minimo 12 --id co:ley:890:2004 --tipo ley \
    --titulo "Ley 890 de 2004 - Modificaciones y adiciones al Código Penal" \
    --ramas "penal" --salida normativa/co-ley-890-2004.md

# --- Fiscal ---------------------------------------------------------------------
run ley_0610_2000 --minimo 50 --id co:ley:610:2000 --tipo ley \
    --titulo "Ley 610 de 2000 - Trámite de los procesos de responsabilidad fiscal" \
    --ramas "administrativo, disciplinario" --salida normativa/co-ley-610-2000.md

# --- Financiero, electrónico y competencia --------------------------------------
run ley_1328_2009 --minimo 60 --id co:ley:1328:2009 --tipo ley \
    --titulo "Ley 1328 de 2009 - Régimen de protección al consumidor financiero" \
    --ramas "financiero, consumo, comercial" --salida normativa/co-ley-1328-2009.md

run ley_0964_2005 --minimo 50 --id co:ley:964:2005 --tipo ley \
    --titulo "Ley 964 de 2005 - Ley del mercado de valores" \
    --ramas "financiero, comercial" --salida normativa/co-ley-964-2005.md

run ley_0527_1999 --minimo 35 --id co:ley:527:1999 --tipo ley \
    --titulo "Ley 527 de 1999 - Comercio electrónico, mensajes de datos y firmas digitales" \
    --ramas "comercial, civil" --salida normativa/co-ley-527-1999.md

run ley_1340_2009 --minimo 25 --id co:ley:1340:2009 --tipo ley \
    --titulo "Ley 1340 de 2009 - Normas en materia de protección de la competencia" \
    --ramas "competencia, comercial" --salida normativa/co-ley-1340-2009.md

run ley_0256_1996 --minimo 25 --id co:ley:256:1996 --tipo ley \
    --titulo "Ley 256 de 1996 - Competencia desleal" \
    --ramas "competencia, comercial" --salida normativa/co-ley-256-1996.md

# --- Ambiental y étnico ---------------------------------------------------------
run ley_1333_2009 --minimo 45 --id co:ley:1333:2009 --tipo ley \
    --titulo "Ley 1333 de 2009 - Procedimiento sancionatorio ambiental" \
    --ramas "ambiental, administrativo" --salida normativa/co-ley-1333-2009.md

run ley_0070_1993 --minimo 45 --id co:ley:70:1993 --tipo ley \
    --titulo "Ley 70 de 1993 - Comunidades negras" \
    --ramas "etnico, agrario, constitucional" --salida normativa/co-ley-70-1993.md

# --- Plan de desarrollo ---------------------------------------------------------
run ley_1450_2011 --minimo 180 --id co:ley:1450:2011 --tipo ley \
    --titulo "Ley 1450 de 2011 - Plan Nacional de Desarrollo 2010-2014" \
    --ramas "administrativo" --salida normativa/co-ley-1450-2011.md

# --- DUR 2016 (Gestor Normativo; senado no los publica) --------------------------
rung() { echo "== $2"; python3 ingesta_gestor.py "$1" "${@:3}" 2>&1 \
    | grep -E "artículos ->|aristas ->|no reconocidas|ABORTA|fecha"; sleep 5; }

rung 85319 1833 --minimo 300 --id co:decreto:1833:2016 \
    --titulo "Decreto 1833 de 2016 - Compilación de normas del Sistema General de Pensiones" \
    --ramas "seguridad-social, administrativo" --salida normativa/co-decreto-1833-2016.md

rung 77813 780 --minimo 300 --id co:decreto:780:2016 \
    --titulo "Decreto 780 de 2016 - DUR del Sector Salud y Protección Social" \
    --ramas "salud, seguridad-social, administrativo" --salida normativa/co-decreto-780-2016.md

rung 83233 1625 --minimo 300 --id co:decreto:1625:2016 \
    --titulo "Decreto 1625 de 2016 - DUR en materia tributaria" \
    --ramas "tributario" --salida normativa/co-decreto-1625-2016.md
