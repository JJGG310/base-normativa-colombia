#!/bin/bash
# P12: actos legislativos citados como origen en el grafo (reformas a la Constitución).
# Título = epígrafe de la propia fuente.
cd "$(dirname "$0")" || exit 1
run() { echo "== $1"; python3 ingesta_senado.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 3; }

run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2017.html --minimo 1 --id co:acto-legislativo:1:2017 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2017 - Por medio del cual se crea un título de disposiciones transitorias de la Constitución para la terminación del conflicto armado y la construcción de una paz estable y duradera y se dictan otras disposiciones" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2017.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2015.html --minimo 1 --id co:acto-legislativo:2:2015 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2015 - Por medio del cual se adopta una reforma de equilibrio de poderes y reajuste institucional y se dictan otras disposiciones" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2015.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2003.html --minimo 1 --id co:acto-legislativo:1:2003 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2003 - Por el cual se adopta una Reforma Política Constitucional y se dictan otras disposiciones" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2003.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2009.html --minimo 1 --id co:acto-legislativo:1:2009 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2009 - Por el cual se modifican y adicionan unos artículos de la Constitución Política de Colombia" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2009.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2021.html --minimo 1 --id co:acto-legislativo:2:2021 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2021 - Por medio del cual se crean 16 Circunscripciones Transitorias Especiales de Paz para la Cámara de Representantes en los períodos 2022-2026 y 2026-2030" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2021.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2002.html --minimo 1 --id co:acto-legislativo:2:2002 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2002 - Por el cual se modifica el período de los gobernadores, diputados, alcaldes, concejales y ediles" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2002.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2016.html --minimo 1 --id co:acto-legislativo:1:2016 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2016 - Por medio del cual se establecen instrumentos jurídicos para facilitar y asegurar la implementación y el desarrollo normativo del acuerdo final para la terminación del conflicto y la construcción de una paz estable y duradera" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2016.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2007.html --minimo 1 --id co:acto-legislativo:1:2007 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2007 - Por medio del cual se modifican los numerales 8 y 9 del artículo 135 , se modifican los artículos 299 y 312 , y se adicionan dos numerales a los artículos 300 y 313 de la Constitución Política de Colombia" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2007.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2004.html --minimo 1 --id co:acto-legislativo:2:2004 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2004 - Por el cual se reforman algunos artículos de la Constitución Política de Colombia y se dictan otras disposiciones" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2004.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2011.html --minimo 1 --id co:acto-legislativo:2:2011 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2011 - Por el cual se deroga el artículo 76 y se modifica el artículo 77 de la Constitución Política de Colombia" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2011.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2012.html --minimo 1 --id co:acto-legislativo:2:2012 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2012 - Por el cual se reforman los artículos 116 , 152 y 221 de la Constitución Política de Colombia" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2012.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_03_2011.html --minimo 1 --id co:acto-legislativo:3:2011 --tipo acto-legislativo \
    --titulo "Acto Legislativo 3 de 2011 - Por el cual se establece el principio de la sostenibilidad fiscal" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-3-2011.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_04_2019.html --minimo 1 --id co:acto-legislativo:4:2019 --tipo acto-legislativo \
    --titulo "Acto Legislativo 4 de 2019 - Por medio del cual se reforma el Régimen de Control Fiscal" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-4-2019.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2012.html --minimo 1 --id co:acto-legislativo:1:2012 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2012 - Por medio del cual se establecen instrumentos jurídicos de justicia transicional en el marco del artículo 22 de la Constitución Política y se dictan otras disposiciones" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2012.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2003.html --minimo 1 --id co:acto-legislativo:2:2003 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2003 - Por medio del cual se modifican los artículos 15 , 24 , 28 y 250 de la Constitución Política de Colombia para enfrentar el terrorismo" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2003.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_03_2002.html --minimo 1 --id co:acto-legislativo:3:2002 --tipo acto-legislativo \
    --titulo "Acto Legislativo 3 de 2002 - Por el cual se reforma la Constitución Nacional" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-3-2002.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_03_2017.html --minimo 1 --id co:acto-legislativo:3:2017 --tipo acto-legislativo \
    --titulo "Acto Legislativo 3 de 2017 - Por medio del cual se regula parcialmente el componente de reincorporación política del Acuerdo Final para la Terminación del Conflicto y la Construcción de una Paz Estable y Duradera" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-3-2017.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_03_2023.html --minimo 1 --id co:acto-legislativo:3:2023 --tipo acto-legislativo \
    --titulo "Acto Legislativo 3 de 2023 - Por medio del cual se modifica la Constitución Política de Colombia y se establece la Jurisdicción Agraria y Rural" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-3-2023.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2001.html --minimo 1 --id co:acto-legislativo:1:2001 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2001 - Por medio del cual se modifican algunos artículos de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2001.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2018.html --minimo 1 --id co:acto-legislativo:1:2018 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2018 - Por medio del cual se modifican los artículos 186 , 234 y 235 de la Constitución Política y se implementan el derecho a la doble instancia y a impugnar la primera sentencia condenatoria" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2018.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2021.html --minimo 1 --id co:acto-legislativo:1:2021 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2021 - Por el cual se otorga la calidad de Distrito Especial de Ciencia, Tecnología e Innovación a la ciudad de Medellín y se dictan otras disposiciones" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2021.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_04_2011.html --minimo 1 --id co:acto-legislativo:4:2011 --tipo acto-legislativo \
    --titulo "Acto Legislativo 4 de 2011 - Por medio del cual se incorpora un artículo transitorio a la Constitución Política de Colombia" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-4-2011.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_06_2011.html --minimo 1 --id co:acto-legislativo:6:2011 --tipo acto-legislativo \
    --titulo "Acto Legislativo 6 de 2011 - Por el cual se reforma el numeral 4 del artículo 235 , el artículo 250 y el numeral 1 del artículo 251 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-6-2011.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_1996.html --minimo 1 --id co:acto-legislativo:1:1996 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 1996 - Por el cual se modifican los artículos 299 y 300 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-1996.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_1999.html --minimo 1 --id co:acto-legislativo:1:1999 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 1999 - Por el cual se reforma el artículo 58 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-1999.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2007.html --minimo 1 --id co:acto-legislativo:2:2007 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2007 - Por medio del cual se modifican los artículos 328 y 356 de la Constitución Política de Colombia" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2007.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2017.html --minimo 1 --id co:acto-legislativo:2:2017 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2017 - Por medio del cual se adiciona un artículo transitorio a la Constitución con el propósito de dar estabilidad y seguridad jurídica al acuerdo final para la terminación del conflicto y la construcción de una Paz Estable y Duradera" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2017.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2018.html --minimo 1 --id co:acto-legislativo:2:2018 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2018 - Por medio del cual se modifican los artículos 328 y 356 de la Constitución Política de Colombia" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2018.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_03_1993.html --minimo 1 --id co:acto-legislativo:3:1993 --tipo acto-legislativo \
    --titulo "Acto Legislativo 3 de 1993 - Por el cual se adicionan los artículos 134 y 261 de la Constitución Política de Colombia" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-3-1993.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_03_2005.html --minimo 1 --id co:acto-legislativo:3:2005 --tipo acto-legislativo \
    --titulo "Acto Legislativo 3 de 2005 - Por el cual se modifica el artículo 176 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-3-2005.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_03_2024.html --minimo 1 --id co:acto-legislativo:3:2024 --tipo acto-legislativo \
    --titulo "Acto Legislativo 3 de 2024 - Por el cual se fortalece la autonomía de los departamentos, distritos y municipios, se modifica el artículo 356 y 357 de la Constitución Política y se dictan otras disposiciones - Segunda Vuelta Bogotá, D" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-3-2024.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_04_2007.html --minimo 1 --id co:acto-legislativo:4:2007 --tipo acto-legislativo \
    --titulo "Acto Legislativo 4 de 2007 - Por el cual se reforman los artículos 356 y 357 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-4-2007.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_05_2011.html --minimo 1 --id co:acto-legislativo:5:2011 --tipo acto-legislativo \
    --titulo "Acto Legislativo 5 de 2011 - Por el cual se constituye el Sistema General de Regalías, se modifican los artículos 360 y 361 de la Constitución Política y se dictan otras disposiciones sobre el Régimen de Regalías y Compensaciones" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-5-2011.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_1993.html --minimo 1 --id co:acto-legislativo:1:1993 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 1993 - Por medio del cual se elige a la ciudad de Barranquilla, Capital del Departamento del Atlántico, en Distrito Especial, Industrial y Portuario" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-1993.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_1995.html --minimo 1 --id co:acto-legislativo:1:1995 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 1995 - Por el cual se adiciona el artículo 357 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-1995.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2002.html --minimo 1 --id co:acto-legislativo:1:2002 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2002 - Por medio de la cual se reforma el artículo 96 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2002.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2005.html --minimo 1 --id co:acto-legislativo:1:2005 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2005 - Por el cual se adiciona el artículo 48 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2005.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2008.html --minimo 1 --id co:acto-legislativo:1:2008 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2008 - Por medio del cual se adiciona el artículo 125 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2008.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2013.html --minimo 1 --id co:acto-legislativo:1:2013 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2013 - Por el cual se modifica el artículo 176 de la Constitución Política, para fortalecer la representación en" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2013.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2015.html --minimo 1 --id co:acto-legislativo:1:2015 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2015 - Por el cual se reforma el artículo 221 de la Constitución Política de Colombia" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2015.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2019.html --minimo 1 --id co:acto-legislativo:1:2019 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2019 - Por el cual se otorga la Categoría de Distrito Especial Portuario, Biodiverso, Industrial y Turístico al municipio de Barrancabermeja en el departamento de Santander" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2019.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2020.html --minimo 1 --id co:acto-legislativo:1:2020 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2020 - Por medio del cual se modifica el artículo 34 de la Constitución Política, suprimiendo la prohibición de la Pena de Prisión Perpetua y estableciendo la prisión perpetua revisable" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2020.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2023.html --minimo 1 --id co:acto-legislativo:1:2023 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2023 - Por medio del cual se reconoce al Campesinado como sujeto de Especial Protección Constitucional" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2023.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2024.html --minimo 1 --id co:acto-legislativo:1:2024 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2024 - Por medio del cual se modifica el artículo 48 de la Constitución Política, se reconoce la mesada catorce para la fuerza pública y se dictan otras disposiciones" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2024.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2025.html --minimo 1 --id co:acto-legislativo:1:2025 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2025 - Por el cual se modifica el artículo 65 de la Constitución Política de Colombia.- Segunda Vuelta" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2025.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_1993.html --minimo 1 --id co:acto-legislativo:2:1993 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 1993 - Por el cual se adoptan medidas Transitorias" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-1993.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2005.html --minimo 1 --id co:acto-legislativo:2:2005 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2005 - Por el cual se modifica el artículo 176 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2005.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2009.html --minimo 1 --id co:acto-legislativo:2:2009 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2009 - Por el cual se reforma el artículo 49 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2009.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2019.html --minimo 1 --id co:acto-legislativo:2:2019 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2019 - Por medio del cual se adiciona un inciso y un parágrafo al numeral 17 del artículo 150 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2019.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2020.html --minimo 1 --id co:acto-legislativo:2:2020 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2020 - Por el cual se modifica el artículo 325 de la Constitución Política de Colombia y se dictan otras disposiciones" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2020.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2023.html --minimo 1 --id co:acto-legislativo:2:2023 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2023 - Por medio del cual se modifica el artículo 138 de la Constitución Política de Colombia de 1991" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2023.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2024.html --minimo 1 --id co:acto-legislativo:2:2024 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2024 - Por el cual se modifica el inciso 1 del artículo 217 de la Constitución Política de Colombia, se cambia el nombre de la Fuerza Aérea por Fuerza Aeroespacial y se dictan otras disposiciones (Segunda vuelta)" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2024.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_03_2007.html --minimo 1 --id co:acto-legislativo:3:2007 --tipo acto-legislativo \
    --titulo "Acto Legislativo 3 de 2007 - Por medio del cual se modifica el artículo 323 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-3-2007.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_03_2019.html --minimo 1 --id co:acto-legislativo:3:2019 --tipo acto-legislativo \
    --titulo "Acto Legislativo 3 de 2019 - Por el cual se modifica el artículo 323 de la Constitución Política de Colombia y se establece la segunda vuelta para la Elección de Alcalde Mayor de Bogotá, Distrito Capital, Segunda Vuelta" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-3-2019.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_05_2017.html --minimo 1 --id co:acto-legislativo:5:2017 --tipo acto-legislativo \
    --titulo "Acto Legislativo 5 de 2017 - Por medio del cual se dictan disposiciones para asegurar el monopolio legítimo de la fuerza y del uso de las armas por parte del Estado" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-5-2017.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_05_2019.html --minimo 1 --id co:acto-legislativo:5:2019 --tipo acto-legislativo \
    --titulo "Acto Legislativo 5 de 2019 - Por el cual se modifica el artículo 361 de la Constitución Política y se dictan otras disposiciones sobre el Régimen de Regalías y Compensaciones" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-5-2019.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_1997.html --minimo 1 --id co:acto-legislativo:1:1997 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 1997 - Por medio del cual se modifica el artículo 35 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-1997.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2000.html --minimo 1 --id co:acto-legislativo:1:2000 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2000 - Por el cual se modifica el inciso 1o. del artículo 322 de la Constitución Política de Colombia" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2000.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_1995.html --minimo 1 --id co:acto-legislativo:2:1995 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 1995 - Por medio del cual se adiciona el artículo 221 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-1995.md
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_02_2000.html --minimo 1 --id co:acto-legislativo:2:2000 --tipo acto-legislativo \
    --titulo "Acto Legislativo 2 de 2000 - Por el cual se modifica el artículo 52 de la Constitución Política de Colombia" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-2-2000.md
# Sin epígrafe en la fuente: el título sale del encabezado de su único artículo.
run http://www.secretariasenado.gov.co/senado/basedoc/acto_legislativo_01_2004.html --minimo 1 --id co:acto-legislativo:1:2004 --tipo acto-legislativo \
    --titulo "Acto Legislativo 1 de 2004 - Pérdida de derechos políticos (inciso quinto del artículo 122 de la Constitución)" \
    --ramas "constitucional" --salida normativa/co-acto-legislativo-1-2004.md
