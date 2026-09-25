#!/bin/bash
# P20: normas bloqueadas sin fuente en senado ni el Gestor, desde normogramas de otras entidades
# (Avance Jurídico, mismo formato que senado; admitidos en esquema.md §8 el 2026-09-25).
cd "$(dirname "$0")" || exit 1
run() { echo "== $1"; python3 ingesta_senado.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 3; }
CREG=https://gestornormativo.creg.gov.co/gestor/entorno/docs
CAN=https://www.cancilleria.gov.co/sites/default/files/Normograma/docs
COL=https://normativa.colpensiones.gov.co/colpens/docs

run $CREG/ley_0057_1887.htm --minimo 300 --id co:ley:57:1887 --tipo ley \
    --titulo "Ley 57 de 1887 - Sobre adopción de códigos y unificación de la legislación nacional" \
    --ramas "civil, constitucional" --salida normativa/co-ley-57-1887.md
run $CREG/decreto_1655_1991.htm --minimo 1 --id co:decreto:1655:1991 --tipo decreto \
    --titulo "Decreto 1655 de 1991 - Por el cual se armonizan con la nomenclatura nandina del actual arancel de aduanas, los bienes gravados y excluidos del impuesto sobre las ventas mencionados expresamente con su clasificación arancelaria en el Estatuto Tributario bajo la nomenclatura nabandina" \
    --ramas "tributario, aduanero" --salida normativa/co-decreto-1655-1991.md
run $CAN/ley_0011_1984.htm --minimo 1 --id co:ley:11:1984 --tipo ley \
    --titulo "Ley 11 de 1984 - Por la cual se reforman algunas normas de los Códigos Sustantivo y Procesal del Trabajo" \
    --ramas "laboral, procesal" --salida normativa/co-ley-11-1984.md
run $CAN/ley_0039_1985.htm --minimo 1 --id co:ley:39:1985 --tipo ley \
    --titulo "Ley 39 de 1985 - Por la cual se modifican los términos para el proceso de negociaciones colectivas de trabajo" \
    --ramas "laboral" --salida normativa/co-ley-39-1985.md
run $COL/ley_0028_1932.htm --minimo 1 --id co:ley:28:1932 --tipo ley \
    --titulo "Ley 28 de 1932 - Sobre reformas civiles (régimen patrimonial en el matrimonio)" \
    --ramas "civil, familia" --salida normativa/co-ley-28-1932.md
run $COL/ley_0045_1936.htm --minimo 1 --id co:ley:45:1936 --tipo ley \
    --titulo "Ley 45 de 1936 - Sobre reformas civiles (filiación natural)" \
    --ramas "civil, familia" --salida normativa/co-ley-45-1936.md
run $COL/decreto_0617_1954.htm --minimo 1 --id co:decreto:617:1954 --tipo decreto \
    --titulo "Decreto 617 de 1954 - por el cual se modifica el Código Sustantivo del Trabajo" \
    --ramas "laboral" --salida normativa/co-decreto-617-1954.md
