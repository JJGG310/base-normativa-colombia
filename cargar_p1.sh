#!/bin/bash
# Carga los códigos troncales de P1 que viven en secretariasenado.
# Reejecutable: cada corrida reescribe el .md y sus aristas en relaciones.csv.
cd "$(dirname "$0")" || exit 1
B=http://www.secretariasenado.gov.co/senado/basedoc

run() { echo "== $1"; python3 ingesta_senado.py "$B/$1.html" "${@:2}" 2>&1 | grep -E "artículos ->|aristas ->|sin ancla|no reconocidas"; }

run constitucion_politica_1991 --minimo 455 --id co:constitucion:1991 --tipo constitucion \
    --titulo "Constitución Política de Colombia" --corto "CP" \
    --fecha 1991-07-04 --ramas "constitucional" --salida normativa/co-constitucion-1991.md

run ley_1564_2012 --minimo 625 --id co:ley:1564:2012 --tipo ley \
    --titulo "Ley 1564 de 2012 - Código General del Proceso" --corto "CGP" \
    --fecha 2012-07-12 --ramas "procesal, civil, comercial, familia" --salida normativa/co-ley-1564-2012.md

run codigo_civil --minimo 2670 --id co:ley:84:1873 --tipo ley \
    --titulo "Ley 84 de 1873 - Código Civil" --corto "CC" \
    --fecha 1873-05-26 --ramas "civil, familia" --salida normativa/co-ley-84-1873.md

run ley_0599_2000 --minimo 550 --id co:ley:599:2000 --tipo ley \
    --titulo "Ley 599 de 2000 - Código Penal" \
    --fecha 2000-07-24 --ramas "penal" --salida normativa/co-ley-599-2000.md

run ley_0906_2004 --minimo 550 --id co:ley:906:2004 --tipo ley \
    --titulo "Ley 906 de 2004 - Código de Procedimiento Penal" --corto "CPP" \
    --fecha 2004-08-31 --ramas "penal, procesal" --salida normativa/co-ley-906-2004.md

run codigo_comercio --minimo 2035 --id co:decreto:410:1971 --tipo decreto \
    --titulo "Decreto 410 de 1971 - Código de Comercio" --corto "C.Co." \
    --fecha 1971-03-27 --ramas "comercial" --salida normativa/co-decreto-410-1971.md

run ley_1437_2011 --minimo 305 --id co:ley:1437:2011 --tipo ley \
    --titulo "Ley 1437 de 2011 - Código de Procedimiento Administrativo y de lo Contencioso Administrativo" --corto "CPACA" \
    --fecha 2011-01-18 --ramas "administrativo, contencioso-administrativo, procesal" --salida normativa/co-ley-1437-2011.md

run codigo_sustantivo_trabajo --minimo 490 --id co:decreto-ley:2663:1950 --tipo decreto-ley \
    --titulo "Decreto Ley 2663 de 1950 - Código Sustantivo del Trabajo" --corto "CST" \
    --fecha 1950-08-05 --ramas "laboral, seguridad-social" --salida normativa/co-decreto-ley-2663-1950.md

echo "== reconstruyendo"
python3 build.py && python3 export.py
