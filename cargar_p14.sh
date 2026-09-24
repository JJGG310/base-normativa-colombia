#!/bin/bash
# P14: decretos origen con ≥20 aristas (reformadores de DUR). Títulos: epígrafe de la fuente.
cd "$(dirname "$0")" || exit 1
D=https://normograma.dian.gov.co/dian/compilacion/docs
run() { echo "== $1"; python3 ingesta_senado.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 3; }
g() { i=$1; id=$2; t=$3; r=$4; n=${id#co:decreto:}; echo "== $i $id"
      python3 ingesta_gestor.py "$i" --enteros --id "$id" --tipo decreto --minimo 1 --titulo "$t" \
        --ramas "$r" --salida "normativa/co-decreto-${n%%:*}-${n##*:}.md" 2>&1 \
        | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; }

g 100521 co:decreto:1760:2019 "Decreto 1760 de 2019 - Modifica y adiciona el Decreto 1068 de 2015 (administración de bienes del FRISCO)" "administrativo, penal"
g 171486 co:decreto:1139:2021 "Decreto 1139 de 2021 - Modifica el Decreto 1066 de 2015 (programas de prevención y protección de la UNP)" "administrativo, victimas"
g 200584 co:decreto:2642:2022 "Decreto 2642 de 2022 - Modifica el Decreto 2555 de 2010 y los DUR 1072, 1074, 1075 y 1079 de 2015 (valores en UVT)" "administrativo, financiero"
g 253216 co:decreto:1231:2024 "Decreto 1231 de 2024 - Adiciona el Decreto 1070 de 2015 (uso diferenciado y proporcional de la fuerza por la Policía Nacional)" "defensa, policivo"
g 163195 co:decreto:523:2021 "Decreto 523 de 2021 - Modifica el Decreto 1077 de 2015 (saneamiento predial y transferencia de bienes fiscales)" "administrativo, urbanistico"
g 169127 co:decreto:951:2021 "Decreto 951 de 2021 - Modifica el Decreto 1077 de 2015 (cobertura a la tasa de interés para vivienda de interés social)" "administrativo, financiero"
g 265256 co:decreto:1086:2025 "Decreto 1086 de 2025 - Sustituye el Título 6 de la Parte 4 del Libro 2 del Decreto 1070 de 2015 (seguridad y protección marítima)" "maritimo, defensa"
g 107874 co:decreto:328:2020 "Decreto 328 de 2020 - Lineamientos para los Proyectos Piloto de Investigación Integral sobre yacimientos no convencionales (fracturamiento hidráulico); adiciona el Decreto 1073 de 2015" "minero-energetico, ambiental"
g 163187 co:decreto:520:2021 "Decreto 520 de 2021 - Reglamenta la Ley 1946 de 2019 y sustituye la Parte 9 del Libro 2 del Decreto 1085 de 2015 (deporte de personas con discapacidad)" "deporte, social"
g 127789 co:decreto:826:2020 "Decreto 826 de 2020 - Adiciona y modifica el Decreto 1082 de 2015 (pago a destinatario final del Sistema General de Regalías)" "territorial, administrativo"
g 80076 co:decreto:431:2017 "Decreto 431 de 2017 - Modifica y adiciona el Decreto 1079 de 2015 (servicio público de transporte terrestre automotor especial)" "transporte, administrativo"
g 168248 co:decreto:880:2021 "Decreto 880 de 2021 - Adiciona el Decreto 1080 de 2015 y reglamenta parcialmente la Ley 2070 de 2020 (FONCULTURA)" "cultura, administrativo"
g 143189 co:decreto:1346:2020 "Decreto 1346 de 2020 - Reglamenta la Ley 1979 de 2019 (veteranos de la Fuerza Pública); modifica los DUR 1070, 1075 y 1072 de 2015" "defensa, administrativo"
g 173043 co:decreto:1347:2021 "Decreto 1347 de 2021 - Adiciona el Decreto 1072 de 2015 (Programa de Prevención de Accidentes Mayores)" "laboral, ambiental"
g 173879 co:decreto:1630:2021 "Decreto 1630 de 2021 - Adiciona el Decreto 1076 de 2015 (gestión integral de sustancias químicas de uso industrial)" "ambiental"
g 186366 co:decreto:625:2022 "Decreto 625 de 2022 - Modifica el Decreto 1821 de 2020 (DUR Sistema General de Regalías)" "territorial, minero-energetico"
g 173608 co:decreto:1510:2021 "Decreto 1510 de 2021 - Adiciona el Decreto 1068 de 2015 (gobierno corporativo de las empresas estatales)" "administrativo, societario"
g 104832 co:decreto:2358:2019 "Decreto 2358 de 2019 - Modifica y adiciona el Decreto 1080 de 2015 (patrimonio cultural material e inmaterial)" "cultura, administrativo"
g 179787 co:decreto:279:2022 "Decreto 279 de 2022 - Modifica y adiciona el Decreto 1071 de 2015 (Fondo Nacional de Adecuación de Tierras)" "agrario, administrativo"
g 261836 co:decreto:869:2025 "Decreto 869 de 2025 - Adiciona el Decreto 1071 de 2015 (Programa Especial de Acceso Integral a Tierras del pueblo Rrom)" "agrario, etnico"
g 264276 co:decreto:1017:2025 "Decreto 1017 de 2025 - Modifica, adiciona y deroga artículos del Decreto 1079 de 2015 (DUR Transporte)" "transporte, administrativo"
g 254016 co:decreto:1310:2024 "Decreto 1310 de 2024 - Modifica el Decreto 1073 de 2015 (almacenamiento estratégico de combustibles líquidos y GLP)" "minero-energetico"
g 99716 co:decreto:1533:2019 "Decreto 1533 de 2019 - Modifica el Decreto 1077 de 2015 (asignación del Subsidio Familiar de Vivienda)" "administrativo, urbanistico"
g 173957 co:decreto:1649:2021 "Decreto 1649 de 2021 - Adopta y reglamenta el Marco Nacional de Cualificaciones; adiciona la Parte 7 al Libro 2 del Decreto 1075 de 2015" "educacion, laboral"
g 162326 co:decreto:438:2021 "Decreto 438 de 2021 - Modifica el Decreto 1082 de 2015 (asociaciones público privadas)" "contratacion-estatal, administrativo"
g 249476 co:decreto:1079:2024 "Decreto 1079 de 2024 - Adiciona el Decreto 1083 de 2015 (Servicio Social para la Paz)" "administrativo, social"

# --- Normogramas con la plataforma de senado ----------------------------------------
run https://normograma.mintic.gov.co/mintic/compilacion/docs/decreto_2640_2022.htm --minimo 5 --id co:decreto:2640:2022 --tipo decreto \
    --titulo "Decreto 2640 de 2022 - Modifica los Decretos 1069, 1078 y 1080 de 2015 (DUR Justicia, TIC y Cultura)" \
    --ramas "administrativo, tic" --salida normativa/co-decreto-2640-2022.md
run https://normograma.com/keralty/compilacion/docs/decreto_1136_2025.htm --minimo 1 --id co:decreto:1136:2025 --tipo decreto \
    --titulo "Decreto 1136 de 2025 - Corrige yerros en la Ley 2445 de 2025 (insolvencia de la persona natural no comerciante)" \
    --ramas "procesal, insolvencia, civil" --salida normativa/co-decreto-1136-2025.md
run $D/decreto_1091_2020.htm --minimo 5 --id co:decreto:1091:2020 --tipo decreto \
    --titulo "Decreto 1091 de 2020 - Modifica el Decreto 1625 de 2016 y sustituye el capítulo 6 del título 4 de la parte 3 del libro 2 del Decreto 1068 de 2015" \
    --ramas "tributario" --salida normativa/co-decreto-1091-2020.md
run $D/decreto_1618_2023.htm --minimo 5 --id co:decreto:1618:2023 --tipo decreto \
    --titulo "Decreto 1618 de 2023 - Modifica artículos del Decreto 1625 de 2016 (DUR Tributario)" \
    --ramas "tributario" --salida normativa/co-decreto-1618-2023.md
run $D/decreto_2250_2017.htm --minimo 3 --id co:decreto:2250:2017 --tipo decreto \
    --titulo "Decreto 2250 de 2017 - Adiciona, modifica y sustituye artículos de los Títulos 1 y 4 de la Parte 2 del Libro 1 del Decreto 1625 de 2016" \
    --ramas "tributario" --salida normativa/co-decreto-2250-2017.md
run $D/decreto_1653_2021.htm --minimo 1 --id co:decreto:1653:2021 --tipo decreto \
    --titulo "Decreto 1653 de 2021 - Reglamenta los artículos 46, 47 y 48 de la Ley 2155 de 2021 y sustituye capítulos del Decreto 1625 de 2016" \
    --ramas "tributario" --salida normativa/co-decreto-1653-2021.md
run $D/decreto_1468_2019.htm --minimo 1 --id co:decreto:1468:2019 --tipo decreto \
    --titulo "Decreto 1468 de 2019 - Reglamenta los artículos 437, 555-2 y 903 al 916 del Estatuto Tributario (régimen simple) y modifica el Decreto 1625 de 2016" \
    --ramas "tributario" --salida normativa/co-decreto-1468-2019.md
run $D/decreto_1652_2021.htm --minimo 1 --id co:decreto:1652:2021 --tipo decreto \
    --titulo "Decreto 1652 de 2021 - Reglamenta el parágrafo 5 del artículo 240 del Estatuto Tributario, modificado por el artículo 41 de la Ley 2068 de 2020, y adiciona el Decreto 1625 de 2016" \
    --ramas "tributario" --salida normativa/co-decreto-1652-2021.md
run $D/decreto_0678_2022.htm --minimo 5 --id co:decreto:678:2022 --tipo decreto \
    --titulo "Decreto 678 de 2022 - Reglamenta los artículos 555-2, 631-6 y 903 del Estatuto Tributario y modifica el Decreto 1625 de 2016" \
    --ramas "tributario" --salida normativa/co-decreto-678-2022.md
