#!/bin/bash
# P15: últimos orígenes con ≥20 aristas cargables (tras P12-P14).
cd "$(dirname "$0")" || exit 1
B=http://www.secretariasenado.gov.co/senado/basedoc
run() { echo "== $1"; python3 ingesta_senado.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 3; }

run $B/ley_0905_2004.html --minimo 20 --id co:ley:905:2004 --tipo ley \
    --titulo "Ley 905 de 2004 - Por medio de la cual se modifica la Ley 590 de 2000 sobre promoción del desarrollo de la micro, pequeña y mediana empresa colombiana y se dictan otras disposiciones" \
    --ramas "comercial" --salida normativa/co-ley-905-2004.md
run $B/ley_2068_2020.html --minimo 50 --id co:ley:2068:2020 --tipo ley \
    --titulo "Ley 2068 de 2020 - Por el cual se modifica la Ley General de Turismo y se dictan otras disposiciones" \
    --ramas "comercial, administrativo" --salida normativa/co-ley-2068-2020.md
# La fuente lo encabeza con «<NOTA DE VIGENCIA: Decreto declarado INEXEQUIBLE>».
run $B/decreto_0266_2000.html --minimo 50 --id co:decreto:266:2000 --tipo decreto-ley \
    --titulo "Decreto 266 de 2000 - Por el cual se dictan normas para suprimir y reformar las regulaciones, trámites y procedimientos (declarado INEXEQUIBLE)" \
    --ramas "administrativo" --salida normativa/co-decreto-266-2000.md
