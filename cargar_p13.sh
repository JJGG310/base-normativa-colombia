#!/bin/bash
# P13: leyes origen con ≥20 aristas (build.py -v tras P11). Título = epígrafe de la fuente.
cd "$(dirname "$0")" || exit 1
run() { echo "== $1"; python3 ingesta_senado.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 3; }
gestor() { echo "== $1"; python3 ingesta_gestor.py "$1" "${@:2}" 2>&1 | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; }

run http://www.secretariasenado.gov.co/senado/basedoc/ley_1757_2015.html --minimo 1 --id co:ley-estatutaria:1757:2015 --tipo ley-estatutaria \
    --titulo "Ley 1757 de 2015 - Por la cual se dictan disposiciones en materia de promoción y protección del derecho a la participación democrática" \
    --ramas "constitucional, electoral" --salida normativa/co-ley-estatutaria-1757-2015.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0130_1994.html --minimo 1 --id co:ley-estatutaria:130:1994 --tipo ley-estatutaria \
    --titulo "Ley 130 de 1994 - Por la cual se dicta el Estatuto Básico de los partidos y movimientos políticos, se dictan normas sobre su financiación y la de las campañas electorales y se dictan otras disposiciones" \
    --ramas "electoral, constitucional" --salida normativa/co-ley-estatutaria-130-1994.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2155_2021.html --minimo 1 --id co:ley:2155:2021 --tipo ley \
    --titulo "Ley 2155 de 2021 - Por medio de la cual se expide la Ley de Inversión Social y se dictan otras disposiciones" \
    --ramas "tributario" --salida normativa/co-ley-2155-2021.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1383_2010.html --minimo 1 --id co:ley:1383:2010 --tipo ley \
    --titulo "Ley 1383 de 2010 - Por la cual se reforma la Ley 769 de 2002 - Código Nacional de Tránsito, y se dictan otras disposiciones" \
    --ramas "transporte, administrativo" --salida normativa/co-ley-1383-2010.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2056_2020.html --minimo 1 --id co:ley:2056:2020 --tipo ley \
    --titulo "Ley 2056 de 2020 - Por la cual se regula la organización y el funcionamiento del Sistema General de Regalías" \
    --ramas "territorial, minero-energetico" --salida normativa/co-ley-2056-2020.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2098_2021.html --minimo 1 --id co:ley:2098:2021 --tipo ley \
    --titulo "Ley 2098 de 2021 - Por medio de la cual se reglamenta la prisión perpetua revisable y se reforma el Código Penal (Ley 599 de 2000), el Código de Procedimiento Penal (Ley 906 de 2004), el Código Penitenciario y Carcelario (Ley 65 de 1993) y se dictan otras disposiciones, Ley Gilma Jiménez" \
    --ramas "penal, procesal" --salida normativa/co-ley-2098-2021.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2079_2021.html --minimo 1 --id co:ley:2079:2021 --tipo ley \
    --titulo "Ley 2079 de 2021 - Por medio de la cual se dictan disposiciones en materia de vivienda y hábitat" \
    --ramas "urbanistico, administrativo" --salida normativa/co-ley-2079-2021.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2099_2021.html --minimo 1 --id co:ley:2099:2021 --tipo ley \
    --titulo "Ley 2099 de 2021 - Por medio de la cual se dictan disposiciones para la transición energética, la dinamización del mercado energético, la reactivación económica del país y se dictan otras disposiciones" \
    --ramas "minero-energetico, ambiental" --salida normativa/co-ley-2099-2021.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0190_1995.html --minimo 1 --id co:ley:190:1995 --tipo ley \
    --titulo "Ley 190 de 1995 - Por la cual se dictan normas tendientes a preservar la moralidad en la administración pública y se fijan disposiciones con el fin de erradicar la corrupción administrativa" \
    --ramas "administrativo, disciplinario, penal" --salida normativa/co-ley-190-1995.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0454_1998.html --minimo 1 --id co:ley:454:1998 --tipo ley \
    --titulo "Ley 454 de 1998 - Por la cual se determina el marco conceptual que regula la economía solidaria, se transforma el Departamento Administrativo Nacional de Cooperativas en el Departamento Administrativo Nacional de la Economía Solidaria y se crea la Superintendencia de la Economía Solidaria" \
    --ramas "comercial, societario" --salida normativa/co-ley-454-1998.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1934_2018.html --minimo 1 --id co:ley:1934:2018 --tipo ley \
    --titulo "Ley 1934 de 2018 - Por medio de la cual se reforma y adiciona el Código Civil" \
    --ramas "civil, familia" --salida normativa/co-ley-1934-2018.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0689_2001.html --minimo 1 --id co:ley:689:2001 --tipo ley --fecha 2001-08-28 \
    --titulo "Ley 689 de 2001 - por la cual se modifica parcialmente la Ley 142 de 1994" \
    --ramas "servicios-publicos" --salida normativa/co-ley-689-2001.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0584_2000.html --minimo 1 --id co:ley:584:2000 --tipo ley \
    --titulo "Ley 584 de 2000 - Por la cual se derogan y se modifican algunas disposiciones del Código Sustantivo del Trabajo" \
    --ramas "laboral" --salida normativa/co-ley-584-2000.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0819_2003.html --minimo 1 --id co:ley:819:2003 --tipo ley \
    --titulo "Ley 819 de 2003 - Por la cual se dictan normas orgánicas en materia de presupuesto, responsabilidad y transparencia fiscal y se dictan otras disposiciones" \
    --ramas "administrativo, territorial" --salida normativa/co-ley-819-2003.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1909_2018.html --minimo 1 --id co:ley-estatutaria:1909:2018 --tipo ley-estatutaria \
    --titulo "Ley 1909 de 2018 - Por medio de la cual se adoptan el Estatuto de la Oposición Política y algunos derechos a las organizaciones políticas independientes" \
    --ramas "electoral, constitucional" --salida normativa/co-ley-estatutaria-1909-2018.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0712_2001.html --minimo 1 --id co:ley:712:2001 --tipo ley \
    --titulo "Ley 712 de 2001 - Por la cual se reforma el Código Procesal del Trabajo" \
    --ramas "procesal, laboral" --salida normativa/co-ley-712-2001.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0003_1992.html --minimo 1 --id co:ley:3:1992 --tipo ley \
    --titulo "Ley 3 de 1992 - Por la cual se expiden normas sobre las Comisiones del Congreso de Colombia y se dictan otras disposiciones" \
    --ramas "constitucional" --salida normativa/co-ley-3-1992.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0042_1993.html --minimo 1 --id co:ley:42:1993 --tipo ley \
    --titulo "Ley 42 de 1993 - Sobre la organización del sistema de control fiscal financiero y los organismos que lo ejercen" \
    --ramas "administrativo" --salida normativa/co-ley-42-1993.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1185_2008.html --minimo 1 --id co:ley:1185:2008 --tipo ley \
    --titulo "Ley 1185 de 2008 - Por la cual se modifica y adiciona la Ley 397 de 1997 –Ley General de Cultura– y se dictan otras disposiciones" \
    --ramas "cultura" --salida normativa/co-ley-1185-2008.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1236_2008.html --minimo 1 --id co:ley:1236:2008 --tipo ley \
    --titulo "Ley 1236 de 2008 - Por medio de la cual se modifican algunos artículos del Código Penal relativos a delitos de abuso sexual" \
    --ramas "penal" --salida normativa/co-ley-1236-2008.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0300_1996.html --minimo 1 --id co:ley:300:1996 --tipo ley \
    --titulo "Ley 300 de 1996 - Por la cual se expide la Ley General de Turismo y se dictan otras disposiciones" \
    --ramas "comercial, administrativo" --salida normativa/co-ley-300-1996.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0590_2000.html --minimo 1 --id co:ley:590:2000 --tipo ley \
    --titulo "Ley 590 de 2000 - Por la cual se dictan disposiciones para promover el desarrollo de las micro, pequeñas y medianas empresa" \
    --ramas "comercial" --salida normativa/co-ley-590-2000.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1106_2006.html --minimo 1 --id co:ley:1106:2006 --tipo ley \
    --titulo "Ley 1106 de 2006 - Por medio de la cual se prorroga la vigencia de la Ley 418 de 1997 prorrogada y modificada por las Leyes 548 de 1999 y 782 de 2002 y se modifican algunas de sus disposiciones" \
    --ramas "penal, victimas" --salida normativa/co-ley-1106-2006.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1393_2010.html --minimo 1 --id co:ley:1393:2010 --tipo ley \
    --titulo "Ley 1393 de 2010 - Por la cual se definen rentas de destinación específica para la salud, se adoptan medidas para promover actividades generadoras de recursos para la salud, para evitar la evasión y la elusión de aportes a la salud, se redireccionan recursos al interior del sistema de salud y se dictan otras disposiciones" \
    --ramas "salud, tributario" --salida normativa/co-ley-1393-2010.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1765_2015.html --minimo 1 --id co:ley:1765:2015 --tipo ley \
    --titulo "Ley 1765 de 2015 - Por la cual se reestructura la Justicia Penal Militar y Policial, se establecen requisitos para el desempeño de sus cargos, se implementa su Fiscalía General Penal Militar y Policial y se organiza su cuerpo técnico de investigación" \
    --ramas "penal-militar, penal" --salida normativa/co-ley-1765-2015.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2116_2021.html --minimo 1 --id co:ley:2116:2021 --tipo ley \
    --titulo "Ley 2116 de 2021 - Por medio de la cual se modifica el Decreto-ley número 1421 de 1,993, referente al Estatuto Orgánico de Bogotá" \
    --ramas "territorial, administrativo" --salida normativa/co-ley-2116-2021.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2387_2024.html --minimo 1 --id co:ley:2387:2024 --tipo ley \
    --titulo "Ley 2387 de 2024 - Por medio del cual se modifica el Procedimiento Sancionatorio Ambiental, Ley 1333 de 2009, con el propósito de otorgar herramientas efectivas para prevenir y sancionar a los infractores y se dictan otras disposiciones" \
    --ramas "ambiental, administrativo" --salida normativa/co-ley-2387-2024.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0446_1998.html --minimo 1 --id co:ley:446:1998 --tipo ley \
    --titulo "Ley 446 de 1998 - Por la cual se adoptan como legislación permanente algunas normas del Decreto 2651 de 1991, se modifican algunas del Código de Procedimiento Civil, se derogan otras de la Ley 23 de 1991 y del Decreto 2279 de 1989, se modifican y expiden normas del Código Contencioso Administrativo" \
    --ramas "procesal, civil, contencioso-administrativo, arbitraje" --salida normativa/co-ley-446-1998.md
run http://www.secretariasenado.gov.co/senado/basedoc/decreto_0902_2017.html --minimo 1 --id co:decreto:902:2017 --tipo decreto-ley \
    --titulo "Decreto 902 de 2017 - Por el cual se adoptan medidas para facilitar la implementación de la Reforma Rural Integral contemplada en el Acuerdo Final en materia de tierras, específicamente el procedimiento para el acceso y formalización y el Fondo de Tierras" \
    --ramas "agrario, transicional" --salida normativa/co-decreto-902-2017.md
run http://www.secretariasenado.gov.co/senado/basedoc/decreto_1122_1999.html --minimo 1 --id co:decreto:1122:1999 --tipo decreto-ley \
    --titulo "Decreto 1122 de 1999 - Por el cual se dictan normas para suprimir trámites, facilitar la actividad de los ciudadanos, contribuir a la eficiencia y eficacia de la Administración Pública y fortalecer el principio de la buena fe" \
    --ramas "administrativo" --salida normativa/co-decreto-1122-1999.md

# --- Gestor: leyes antiguas que senado no publica ----------------------------------
# Ley 57 de 1887: el Gestor (i=39535) responde «No disponible» y senado no la publica — bloqueada.
gestor 15805 --id co:ley:153:1887 --tipo ley --minimo 50 \
    --titulo "Ley 153 de 1887 - Por la cual se adiciona y reforma los códigos nacionales, la ley 61 de 1886 y la 57 de 1887" \
    --ramas "civil, constitucional" --salida normativa/co-ley-153-1887.md
gestor 9028 --id co:ley:6:1990 --tipo ley --minimo 10 \
    --titulo "Ley 6 de 1990 - Por la cual se reforma el Decreto 2241 de 1986 (Código Electoral) y se dictan otras disposiciones" \
    --ramas "electoral" --salida normativa/co-ley-6-1990.md
