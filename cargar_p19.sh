#!/bin/bash
# P19: decretos origen con 10+ aristas que faltaban (IDs del Gestor hallados por buscador web y
# verificados contra el encabezado de cada página) y la norma que deroga al 777/1992.
cd "$(dirname "$0")" || exit 1
python3 ingesta_gestor.py 1454 --id co:decreto:777:1992 --titulo "Decreto 777 de 1992 - Por el cuál se reglamentan la celebración de los contratos a que refiere el inciso segundo del artículo 355 de la Constitución Política" --ramas "contratacion-estatal, administrativo" --estado derogada --salida normativa/co-decreto-777-1992.md
python3 ingesta_gestor.py 172113 --id co:decreto:1207:2021 --titulo "Decreto 1207 de 2021 - Por el cual se adoptan disposiciones para la elección de los representantes a la Cámara por las 16 Circunscripciones Transitorias Especiales de Paz para los periodos 2022-2026 y 2026-2030, en desarrollo del Acto Legislativo 02 del 25 de agosto de 2021" --ramas "electoral, victimas" --salida normativa/co-decreto-1207-2021.md
python3 ingesta_gestor.py 78935 --id co:decreto:92:2017 --titulo "Decreto 92 de 2017 - Por el cual se reglamenta la contratación con entidades privadas sin ánimo de lucro a la que hace referencia el inciso segundo del artículo 355 de la Constitución Política" --ramas "contratacion-estatal, administrativo" --salida normativa/co-decreto-92-2017.md
