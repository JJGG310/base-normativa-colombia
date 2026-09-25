#!/bin/bash
# P21: normas sin otra fuente, desde capturas de SUIN-Juriscol en archive.org (esquema.md §8,
# fuente 10; `verificado` = fecha de la captura). Fecha = publicación en el Diario Oficial.
cd "$(dirname "$0")" || exit 1
python3 ingesta_suin.py Decretos/1731310 --id co:decreto:982:1996 --tipo decreto --fecha 1996-06-04 \
    --titulo "Decreto 982 de 1996 - por el cual se modifica el Decreto 2664 de 1994" \
    --ramas "agrario, administrativo" --minimo 13 --salida normativa/co-decreto-982-1996.md
python3 ingesta_suin.py 30031743 --id co:decreto:939:2017 --tipo decreto --fecha 2017-06-05 \
    --titulo "Decreto 939 de 2017 - por el cual se corrigen los yerros de los artículos 89, 99, 111, 123, 165, 180, 281, 289, 305, 317 y 319 de la Ley 1819 de 2016" \
    --ramas "tributario" --minimo 12 --salida normativa/co-decreto-939-2017.md
# Senado y la Cancillería publican solo el epígrafe; SUIN trae el articulado (DO 43.662, 10-ago-1999).
python3 ingesta_suin.py 30019388 --id co:acto-legislativo:1:1999 --tipo acto-legislativo --fecha 1999-08-10 \
    --titulo "Acto Legislativo 1 de 1999 - por el cual se reforma el artículo 58 de la Constitución Política" \
    --ramas "constitucional" --minimo 2 --salida normativa/co-acto-legislativo-1-1999.md
