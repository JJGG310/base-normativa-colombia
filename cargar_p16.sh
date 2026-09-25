#!/bin/bash
# P16: leyes origen con 10-19 aristas de vigencia (build.py). Título = epígrafe de la fuente.
cd "$(dirname "$0")" || exit 1
run() { echo "== $1"; python3 ingesta_senado.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 3; }

run http://www.secretariasenado.gov.co/senado/basedoc/ley_2447_2025.html --minimo 1 --id co:ley:2447:2025 --tipo ley \
    --titulo "Ley 2447 de 2025 - Por medio del cual se eliminan todas las formas de uniones tempranas en las cuales uno o ambos contrayentes o compañeros permanentes sean menores de 18 años y se fortalece la Política Pública Nacional de Infancia y Adolescencia mediante la creación del programa nacional de proyectos de vida para niños, niñas y adolescentes" \
    --ramas "familia" --salida normativa/co-ley-2447-2025.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1864_2017.html --minimo 1 --id co:ley:1864:2017 --tipo ley \
    --titulo "Ley 1864 de 2017 - Mediante la cual se modifica la Ley 599 de 2000 y se dictan otras disposiciones para proteger los mecanismos de participación democrática" \
    --ramas "penal, electoral" --salida normativa/co-ley-1864-2017.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1121_2006.html --minimo 1 --id co:ley:1121:2006 --tipo ley \
    --titulo "Ley 1121 de 2006 - Por la cual se dictan normas para la prevención, detección, investigación y sanción de la financiación del terrorismo y otras disposiciones" \
    --ramas "penal, financiero" --salida normativa/co-ley-1121-2006.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1060_2006.html --minimo 1 --id co:ley:1060:2006 --tipo ley \
    --titulo "Ley 1060 de 2006 - Por la cual se modifican las normas que regulan la impugnación de la paternidad y la maternidad" \
    --ramas "familia, civil" --salida normativa/co-ley-1060-2006.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0575_2000.html --minimo 1 --id co:ley:575:2000 --tipo ley \
    --titulo "Ley 575 de 2000 - Por medio de la cual se reforma parcialmente la Ley 294 de 1996" \
    --ramas "familia" --salida normativa/co-ley-575-2000.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1719_2014.html --minimo 1 --id co:ley:1719:2014 --tipo ley \
    --titulo "Ley 1719 de 2014 - Por la cual se modifican algunos artículos de las Leyes 599 de 2000, 906 de 2004 y se adoptan medidas para garantizar el acceso a la justicia de las víctimas de violencia sexual, en especial la violencia sexual con ocasión del conflicto armado, y se dictan otras disposiciones" \
    --ramas "penal, procesal, victimas" --salida normativa/co-ley-1719-2014.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2474_2025.html --minimo 1 --id co:ley:2474:2025 --tipo ley \
    --titulo "Ley 2474 de 2025 - Por la cual se adopta la política nacional de gestión del riesgo de desastres y se establece el Sistema Nacional de Gestión del Riesgo de Desastres y se dictan otras disposiciones' con el propósito de incluir a los animales como sujetos destinatarios de las medidas de atención y prevención en el marco de esta política" \
    --ramas "administrativo, ambiental" --salida normativa/co-ley-2474-2025.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0791_2002.html --minimo 1 --id co:ley:791:2002 --tipo ley \
    --titulo "Ley 791 de 2002 - Por medio de la cual se reducen los términos de prescripción en materia civil" \
    --ramas "civil" --salida normativa/co-ley-791-2002.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1878_2018.html --minimo 1 --id co:ley:1878:2018 --tipo ley \
    --titulo "Ley 1878 de 2018 - Por medio de la cual se modifican algunos artículos de la Ley 1098 de 2006, por la cual se expide el Código de la Infancia y la Adolescencia, y se dictan otras disposiciones" \
    --ramas "familia, penal" --salida normativa/co-ley-1878-2018.md
run http://www.secretariasenado.gov.co/senado/basedoc/decreto_0071_2020.html --minimo 1 --id co:decreto-ley:71:2020 --tipo decreto-ley \
    --titulo "Decreto Ley 71 de 2020 - Por el cual se establece y regula el Sistema Específico de Carrera de los empleados públicos de la Unidad Administrativa Especial Dirección de Impuestos y Aduanas Nacionales, y se expiden normas relacionadas con la administración y gestión del talento humano de la DIAN" \
    --ramas "administrativo, laboral" --salida normativa/co-decreto-ley-71-2020.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1558_2012.html --minimo 1 --id co:ley:1558:2012 --tipo ley \
    --titulo "Ley 1558 de 2012 - Por la cual se modifica la Ley 300 de 1996 -Ley General de Turismo, la Ley 1101 de 2006 y se dictan otras disposiciones" \
    --ramas "comercial, administrativo" --salida normativa/co-ley-1558-2012.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2390_2024.html --minimo 1 --id co:ley:2390:2024 --tipo ley \
    --titulo "Ley 2390 de 2024 - Por medio del cual se modifica la Ley 5ª de 1992 con el fin de implementar medios y/o herramientas tecnológicas o digitales en los procesos legislativos del Congreso y se dictan otras disposiciones" \
    --ramas "constitucional" --salida normativa/co-ley-2390-2024.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0974_2005.html --minimo 1 --id co:ley:974:2005 --tipo ley \
    --titulo "Ley 974 de 2005 - Por la cual se reglamenta la actuación en bancadas de los miembros de las corporaciones públicas y se adecua el Reglamento del Congreso al Régimen de Bancadas" \
    --ramas "constitucional, electoral" --salida normativa/co-ley-974-2005.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2292_2023.html --minimo 1 --id co:ley:2292:2023 --tipo ley \
    --titulo "Ley 2292 de 2023 - Por medio de la cual se adoptan acciones afirmativas para mujeres Cabeza de Familia en materias de política criminal y penitenciaria, se modifica y adiciona el Código Penal, la Ley 750 de 2002 y el Código de Procedimiento Penal y se dictan otras disposiciones" \
    --ramas "penal" --salida normativa/co-ley-2292-2023.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1370_2009.html --minimo 1 --id co:ley:1370:2009 --tipo ley \
    --titulo "Ley 1370 de 2009 - Por la cual se adiciona parcialmente el estatuto tributario" \
    --ramas "tributario" --salida normativa/co-ley-1370-2009.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0733_2002.html --minimo 1 --id co:ley:733:2002 --tipo ley \
    --titulo "Ley 733 de 2002 - Por medio de la cual se dictan medidas tendientes a erradicar los delitos de secuestro, terrorismo y extorsión, y se expiden otras disposiciones" \
    --ramas "penal" --salida normativa/co-ley-733-2002.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0365_1997.html --minimo 1 --id co:ley:365:1997 --tipo ley \
    --titulo "Ley 365 de 1997 - Por la cual se establecen normas tendientes a combatir la delincuencia organizada y se dictan otras disposiciones" \
    --ramas "penal" --salida normativa/co-ley-365-1997.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1176_2007.html --minimo 1 --id co:ley:1176:2007 --tipo ley \
    --titulo "Ley 1176 de 2007 - Por la cual se desarrollan los artículos 356 y 357 de la Constitución Política y se dictan otras disposiciones" \
    --ramas "territorial, administrativo" --salida normativa/co-ley-1176-2007.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2251_2022.html --minimo 1 --id co:ley:2251:2022 --tipo ley \
    --titulo "Ley 2251 de 2022 - Por la cual se dictan normas para el diseño e implementación de la política de seguridad vial con enfoque de sistema seguro y se dictan otras disposiciones Ley Julián Esteban" \
    --ramas "transporte" --salida normativa/co-ley-2251-2022.md

# No están en senado: Gestor Normativo.
gestor() { echo "== $1"; python3 ingesta_gestor.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; }
gestor 256 --id co:ley:29:1982 --tipo ley --minimo 5 \
    --titulo "Ley 29 de 1982 - Por la cual se otorga igualdad de derechos herenciales a los hijos legítimos, extramatrimoniales y adoptivos y se hacen los correspondientes ajustes a los diversos órdenes hereditarios" \
    --ramas "civil, familia" --salida normativa/co-ley-29-1982.md
gestor 6547 --id co:ley:62:1988 --tipo ley --minimo 5 \
    --titulo "Ley 62 de 1988 - Por la cual se modifica la Ley 96 de 1985 y el Decreto número 2241 de 1986 (Código Electoral)" \
    --ramas "electoral" --salida normativa/co-ley-62-1988.md
