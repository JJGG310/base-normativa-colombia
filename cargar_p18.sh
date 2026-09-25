#!/bin/bash
# P18: leyes origen con 10-19 aristas (build.py). Título = epígrafe de la fuente.
cd "$(dirname "$0")" || exit 1
run() { echo "== $1"; python3 ingesta_senado.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; sleep 3; }

run http://www.secretariasenado.gov.co/senado/basedoc/ley_1004_2005.html --minimo 1 --id co:ley:1004:2005 --tipo ley \
    --titulo "Ley 1004 de 2005 - Por la cual se modifican <sic> un régimen especial para estimular la inversión y se dictan otras disposiciones" \
    --ramas "tributario, comercial" --salida normativa/co-ley-1004-2005.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1033_2006.html --minimo 1 --id co:ley:1033:2006 --tipo ley \
    --titulo "Ley 1033 de 2006 - Por la cual se establece la Carrera Administrativa Especial para los Empleados Públicos no uniformados al servicio del Ministerio de Defensa Nacional, de las Fuerzas Militares, de la Policía Nacional y de sus entidades descentralizadas, adscritas y vinculadas al sector Defensa, se derogan y modifican unas disposiciones de la Ley 909 de 2004 y se conceden unas facultades conforme al numeral 10 del artículo 150 de la Constitución Política" \
    --ramas "administrativo, defensa" --salida normativa/co-ley-1033-2006.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0105_1993.html --minimo 1 --id co:ley:105:1993 --tipo ley \
    --titulo "Ley 105 de 1993 - Por la cual se dictan disposiciones básicas sobre el transporte, se redistribuyen competencias y recursos entre la Nación y las Entidades Territoriales, se reglamenta la planeación en el sector transporte y se dictan otras disposiciones" \
    --ramas "transporte, territorial" --salida normativa/co-ley-105-1993.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0106_1993.html --minimo 1 --id co:ley:106:1993 --tipo ley \
    --titulo "Ley 106 de 1993 - Por la cual se dictan normas sobre organización y funcionamiento de la Contraloría General de la República, se establece su estructura orgánica, se determina la organización y funcionamiento de la Auditoría Externa, se organiza el Fondo de Bienestar Social, se determina el Sistema de Personal, se desarrolla la Carrera Administrativa Especial y se dictan otras disposiciones" \
    --ramas "administrativo, constitucional" --salida normativa/co-ley-106-1993.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1101_2006.html --minimo 1 --id co:ley:1101:2006 --tipo ley \
    --titulo "Ley 1101 de 2006 - Por la cual se modifica la Ley 300 de 1996 - Ley General de Turismo y se dictan otras disposiciones" \
    --ramas "comercial, administrativo" --salida normativa/co-ley-1101-2006.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1114_2006.html --minimo 1 --id co:ley:1114:2006 --tipo ley \
    --titulo "Ley 1114 de 2006 - Por la cual se modifica la Ley 546 de 1999, el numeral 7 del artículo 16 de la Ley 789 de 2002 y el artículo 6o de la Ley 973 de 2005 y se destinan recursos para la vivienda de interés social" \
    --ramas "financiero, seguridad-social" --salida normativa/co-ley-1114-2006.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1148_2007.html --minimo 1 --id co:ley:1148:2007 --tipo ley \
    --titulo "Ley 1148 de 2007 - Por medio de la cual se modifican las Leyes 136 de 1994 y 617 de 2000 y se dictan otras disposiciones" \
    --ramas "territorial, administrativo" --salida normativa/co-ley-1148-2007.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1149_2007.html --minimo 1 --id co:ley:1149:2007 --tipo ley \
    --titulo "Ley 1149 de 2007 - Por la cual se reforma el Código Procesal del Trabajo y de la Seguridad Social para hacer efectiva la oralidad en sus procesos" \
    --ramas "procesal, laboral" --salida normativa/co-ley-1149-2007.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1153_2007.html --minimo 1 --id co:ley:1153:2007 --tipo ley \
    --titulo "Ley 1153 de 2007 - Por medio de la cual se establece el tratamiento de las pequeñas causas en materia penal" \
    --ramas "penal, procesal" --salida normativa/co-ley-1153-2007.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0119_1994.html --minimo 1 --id co:ley:119:1994 --tipo ley \
    --titulo "Ley 119 de 1994 - Por la cual se reestructura el Servicio Nacional de Aprendizaje, SENA, se deroga el Decreto 2149 de 1992 y se dictan otras disposiciones" \
    --ramas "administrativo, educacion" --salida normativa/co-ley-119-1994.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0011_1992.html --minimo 1 --id co:ley:11:1992 --tipo ley \
    --titulo "Ley 11 de 1992 - Por medio de la cual se aprueba el Protocolo Adicional a los Convenios de Ginebra del 12 de agosto de 1949 relativo a la protección de las víctimas de los conflictos armados internacionales (Protocolo I), adoptado en Ginebra, el 8 de junio de 1977" \
    --ramas "internacional-publico" --salida normativa/co-ley-11-1992.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1210_2008.html --minimo 1 --id co:ley:1210:2008 --tipo ley \
    --titulo "Ley 1210 de 2008 - Por la cual se modifican parcialmente los artículos 448 numeral 4 y 451 del Código Sustantivo del Trabajo y 2 del Código Procesal del Trabajo y de la Seguridad Social y se crea el artículo 129A del Código Procesal del Trabajo y de la Seguridad Social y se dictan otras disposiciones" \
    --ramas "laboral, procesal" --salida normativa/co-ley-1210-2008.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1263_2008.html --minimo 1 --id co:ley:1263:2008 --tipo ley \
    --titulo "Ley 1263 de 2008 - Por medio de la cual se modifica parcialmente los artículos 26 y 28 de la Ley 99 de 1993" \
    --ramas "ambiental, administrativo" --salida normativa/co-ley-1263-2008.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1288_2009.html --minimo 1 --id co:ley:1288:2009 --tipo ley \
    --titulo "Ley 1288 de 2009 - Por medio del cual se expiden normas para fortalecer el marco legal que permite a los organismos, que llevan a cabo actividades de inteligencia y contrainteligencia, cumplir con su misión constitucional y legal, y se dictan otras disposiciones" \
    --ramas "defensa, constitucional" --salida normativa/co-ley-1288-2009.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0128_1994.html --minimo 1 --id co:ley:128:1994 --tipo ley \
    --titulo "Ley 128 de 1994 - Por la cual se expide la Ley Orgánica de las Areas Metropolitanas" \
    --ramas "territorial, administrativo" --salida normativa/co-ley-128-1994.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1309_2009.html --minimo 1 --id co:ley:1309:2009 --tipo ley \
    --titulo "Ley 1309 de 2009 - Por la cual se modifica la Ley 599 de 2000 relativa a las conductas punibles que atentan contra los bienes jurídicamente protegidos de los miembros de una organización sindical [TACHADO: legalmente reconocida]" \
    --ramas "penal" --salida normativa/co-ley-1309-2009.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0131_1994.html --minimo 1 --id co:ley-estatutaria:131:1994 --tipo ley-estatutaria \
    --titulo "Ley 131 de 1994 - Por la cual se reglamenta el voto programático y se dictan otras disposiciones" \
    --ramas "electoral, constitucional" --salida normativa/co-ley-estatutaria-131-1994.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0133_1994.html --minimo 1 --id co:ley-estatutaria:133:1994 --tipo ley-estatutaria \
    --titulo "Ley 133 de 1994 - Por la cual se desarrolla el Derecho de Libertad Religiosa y de Cultos, reconocido en el artículo 19 de la Constitución Política" \
    --ramas "constitucional" --salida normativa/co-ley-estatutaria-133-1994.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1357_2009.html --minimo 1 --id co:ley:1357:2009 --tipo ley \
    --titulo "Ley 1357 de 2009 - Por la cual se modifica el Código Penal" \
    --ramas "penal" --salida normativa/co-ley-1357-2009.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1381_2010.html --minimo 1 --id co:ley:1381:2010 --tipo ley \
    --titulo "Ley 1381 de 2010 - Por la cual se desarrollan los artículos 7o, 8o, 10 y 70 de la Constitución Política, y los artículos 4o, 5o y 28 de la Ley 21 de 1991 (que aprueba el Convenio 169 de la OIT sobre pueblos indígenas y tribales), y se dictan normas sobre reconocimiento, fomento, protección, uso, preservación y fortalecimiento de las lenguas de los grupos étnicos de Colombia y sobre sus derechos lingüísticos y los de sus hablantes" \
    --ramas "etnico, cultura" --salida normativa/co-ley-1381-2010.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1418_2010.html --minimo 1 --id co:ley:1418:2010 --tipo ley \
    --titulo "Ley 1418 de 2010 - Por medio de la cual se aprueba la “Convención Internacional para la Protección de todas las Personas contra las Desapariciones Forzadas”, adoptada en Nueva York el 20 de diciembre de 2006" \
    --ramas "internacional-publico, penal" --salida normativa/co-ley-1418-2010.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1426_2010.html --minimo 1 --id co:ley:1426:2010 --tipo ley \
    --titulo "Ley 1426 de 2010 - Por la cual se modifica la Ley 599 de 2000, relativa a las conductas punibles que atentan contra los bienes jurídicamente protegidos de los defensores de derechos humanos y periodistas" \
    --ramas "penal" --salida normativa/co-ley-1426-2010.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1434_2011.html --minimo 1 --id co:ley:1434:2011 --tipo ley \
    --titulo "Ley 1434 de 2011 - Por la cual se modifica y adiciona la Ley 5ª de 1992, se crea la Comisión Legal para la Equidad de la Mujer del Congreso de la República de Colombia y se dictan otras disposiciones" \
    --ramas "constitucional, administrativo" --salida normativa/co-ley-1434-2011.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1469_2011.html --minimo 1 --id co:ley:1469:2011 --tipo ley \
    --titulo "Ley 1469 de 2011 - Por la cual se adoptan medidas para promover la oferta de suelo urbanizable y se adoptan otras disposiciones para promover el acceso a la vivienda" \
    --ramas "urbanistico" --salida normativa/co-ley-1469-2011.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1482_2011.html --minimo 1 --id co:ley:1482:2011 --tipo ley \
    --titulo "Ley 1482 de 2011 - Por medio de la cual se modifica el Código Penal y se establecen otras disposiciones" \
    --ramas "penal" --salida normativa/co-ley-1482-2011.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1537_2012.html --minimo 1 --id co:ley:1537:2012 --tipo ley \
    --titulo "Ley 1537 de 2012 - Por la cual se dictan normas tendientes a facilitar y promover el desarrollo urbano y el acceso a la vivienda y se dictan otras disposiciones" \
    --ramas "urbanistico, administrativo" --salida normativa/co-ley-1537-2012.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0163_1994.html --minimo 1 --id co:ley:163:1994 --tipo ley \
    --titulo "Ley 163 de 1994 - Por la cual se expiden algunas disposiciones en materia electoral" \
    --ramas "electoral" --salida normativa/co-ley-163-1994.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1682_2013.html --minimo 1 --id co:ley:1682:2013 --tipo ley \
    --titulo "Ley 1682 de 2013 - Por la cual se adoptan medidas y disposiciones para los proyectos de infraestructura de transporte y se conceden facultades extraordinarias" \
    --ramas "transporte, administrativo" --salida normativa/co-ley-1682-2013.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1738_2014.html --minimo 1 --id co:ley:1738:2014 --tipo ley \
    --titulo "Ley 1738 de 2014 - Por medio de la cual se prorroga la Ley 418 de 1997, prorrogada y modificada por las Leyes 548 de 1999, 782 de 2002, 1106 de 2006 y 1421 de 2010" \
    --ramas "victimas, defensa" --salida normativa/co-ley-1738-2014.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0174_1994.html --minimo 1 --id co:ley:174:1994 --tipo ley \
    --titulo "Ley 174 de 1994 - Por la cual se expiden normas en materia de saneamiento aduanero y se dictan otras disposiciones en materia tributaria" \
    --ramas "aduanero, tributario" --salida normativa/co-ley-174-1994.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1752_2015.html --minimo 1 --id co:ley:1752:2015 --tipo ley \
    --titulo "Ley 1752 de 2015 - Por medio de la cual se modifica la Ley 1482 de 2011, para sancionar penalmente la discriminación contra las personas con discapacidad" \
    --ramas "penal" --salida normativa/co-ley-1752-2015.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0177_1994.html --minimo 1 --id co:ley:177:1994 --tipo ley \
    --titulo "Ley 177 de 1994 - Por la cual se modifica la Ley 136 de 1994 y se dictan otras disposiciones" \
    --ramas "territorial" --salida normativa/co-ley-177-1994.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0179_1994.html --minimo 1 --id co:ley:179:1994 --tipo ley \
    --titulo "Ley 179 de 1994 - Por la cual se introducen algunas modificaciones a la Ley 38 de 1989, Orgánica de Presupuesto" \
    --ramas "administrativo, territorial" --salida normativa/co-ley-179-1994.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1811_2016.html --minimo 1 --id co:ley:1811:2016 --tipo ley \
    --titulo "Ley 1811 de 2016 - Por la cual se otorgan incentivos para promover el uso de la bicicleta en el territorio nacional y se modifica el Código Nacional de Tránsito" \
    --ramas "transporte" --salida normativa/co-ley-1811-2016.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1816_2016.html --minimo 1 --id co:ley:1816:2016 --tipo ley \
    --titulo "Ley 1816 de 2016 - Por la cual se fija el régimen propio del monopolio rentístico de licores destilados, se modifica el impuesto al consumo de licores, vinos, aperitivos y similares, y se dictan otras disposiciones" \
    --ramas "tributario, territorial" --salida normativa/co-ley-1816-2016.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0181_1995.html --minimo 1 --id co:ley:181:1995 --tipo ley \
    --titulo "Ley 181 de 1995 - Por la cual se dictan disposiciones para el fomento del deporte, la recreación, el aprovechamiento del tiempo libre y la Educación Física y se crea el Sistema Nacional del Deporte" \
    --ramas "administrativo, educacion" --salida normativa/co-ley-181-1995.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1828_2017.html --minimo 1 --id co:ley:1828:2017 --tipo ley \
    --titulo "Ley 1828 de 2017 - Por medio de la cual se expide el Código de Ética y Disciplinario del Congresista y se dictan otras disposiciones" \
    --ramas "disciplinario, constitucional" --salida normativa/co-ley-1828-2017.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0182_1995.html --minimo 1 --id co:ley:182:1995 --tipo ley \
    --titulo "Ley 182 de 1995 - por la cual se reglamenta el servicio de televisión y se formulan políticas para su desarrollo, se democratiza el acceso a éste, se conforma la Comisión Nacional de Televisión, se promueven la industria y actividades de televisión, se establecen normas para contratación de los servicios, se reestreucturan <sic> entidades del sector y se dictan otras disposiciones en materia de telecomunicaciones" \
    --ramas "tic, administrativo" --salida normativa/co-ley-182-1995.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0191_1995.html --minimo 1 --id co:ley:191:1995 --tipo ley --fecha 1995-06-23 \
    --titulo "Ley 191 de 1995 - Por medio de la cual se dictan disposiciones sobre Zonas de Frontera" \
    --ramas "territorial, tributario" --salida normativa/co-ley-191-1995.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_1949_2019.html --minimo 1 --id co:ley:1949:2019 --tipo ley \
    --titulo "Ley 1949 de 2019 - Por la cual se adicionan y modifican algunos artículos de las leyes 1122 de 2007 y 1438 de 2011, y se dictan otras disposiciones" \
    --ramas "salud, seguridad-social" --salida normativa/co-ley-1949-2019.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2014_2019.html --minimo 1 --id co:ley:2014:2019 --tipo ley \
    --titulo "Ley 2014 de 2019 - Por medio de la cual se regulan las sanciones para condenados por corrupción y delitos contra la Administración pública, así como la cesión unilateral administrativa del contrato por actos de corrupción y se dictan otras disposiciones" \
    --ramas "penal, contratacion-estatal" --salida normativa/co-ley-2014-2019.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2078_2021.html --minimo 1 --id co:ley:2078:2021 --tipo ley \
    --titulo "Ley 2078 de 2021 - Por medio de la cual se modifica la Ley 1448 de 2011 y los Decretos-ley Étnicos 4633 de 2011, 4634 de 2011 y 4635 de 2011, prorrogando por 10 años su vigencia" \
    --ramas "victimas, transicional" --salida normativa/co-ley-2078-2021.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2108_2021.html --minimo 1 --id co:ley:2108:2021 --tipo ley \
    --titulo "Ley 2108 de 2021 - “Ley de Internet como servicio público esencial y universal” o por medio de la cual se modifica la Ley 1341 de 2009 y se dictan otras disposiciones" \
    --ramas "tic, servicios-publicos" --salida normativa/co-ley-2108-2021.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2157_2021.html --minimo 1 --id co:ley-estatutaria:2157:2021 --tipo ley-estatutaria \
    --titulo "Ley 2157 de 2021 - Por medio de la cual se modifica y adiciona la Ley Estatutaria 1266 de 2008, y se dictan disposiciones generales del Hábeas Data con relación a la información financiera, crediticia, comercial, de servicios y la proveniente de terceros países y se dictan otras disposiciones" \
    --ramas "constitucional, financiero" --salida normativa/co-ley-estatutaria-2157-2021.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2160_2021.html --minimo 1 --id co:ley:2160:2021 --tipo ley \
    --titulo "Ley 2160 de 2021 - Por medio de la cual se modifica la Ley 80 de 1993 y la Ley 1150 de 2007" \
    --ramas "contratacion-estatal" --salida normativa/co-ley-2160-2021.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2272_2022.html --minimo 1 --id co:ley:2272:2022 --tipo ley \
    --titulo "Ley 2272 de 2022 - Por medio de la cual se modifica adiciona y prorroga la ley 418 de 1997, prorrogada, modificada y adicionada por las Leyes 548 de 1999, 782 de 2002, 1106 de 2006, 1421 de 2010, 1738 de 2014 y 1941 de 2018, se define la política de paz de Estado, se crea el servicio social para la paz, y se dictan otras disposiciones" \
    --ramas "victimas, defensa" --salida normativa/co-ley-2272-2022.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2455_2025.html --minimo 1 --id co:ley:2455:2025 --tipo ley \
    --titulo "Ley 2455 de 2025 - Por la cual se fortalece la lucha contra el maltrato animal y se actualiza el Estatuto Nacional de Protección de los Animales Ley 84 de 1989 - Ley Ángel" \
    --ramas "penal, ambiental" --salida normativa/co-ley-2455-2025.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_2477_2025.html --minimo 1 --id co:ley:2477:2025 --tipo ley \
    --titulo "Ley 2477 de 2025 - Por medio de la cual se modifican las Leyes 599 de 2000, 906 de 2004 y 1121 de 2006, en relación con la figura de la reparación integral, la concesión de beneficios por allanamientos y preacuerdos, y la aplicación del principio de oportunidad, entre otras reformas orientadas a garantizar una administración de justicia penal pronta y eficaz" \
    --ramas "penal, procesal" --salida normativa/co-ley-2477-2025.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0024_1992.html --minimo 1 --id co:ley:24:1992 --tipo ley \
    --titulo "Ley 24 de 1992 - Por la cual se establecen la organización y funcionamiento de la Defensoría del Pueblo y se dictan otras disposiciones en desarrollo del artículo 283 de la Constitución Política de Colombia" \
    --ramas "constitucional, administrativo" --salida normativa/co-ley-24-1992.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0025_1992.html --minimo 1 --id co:ley:25:1992 --tipo ley \
    --titulo "Ley 25 de 1992 - Por la cual se desarrollan los incisos 9, 10, 11, 12 y 13 del artículo 42 de la Constitución Política" \
    --ramas "familia, civil" --salida normativa/co-ley-25-1992.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0319_1996.html --minimo 1 --id co:ley:319:1996 --tipo ley \
    --titulo "Ley 319 de 1996 - Por medio de la cual se aprueba el Protocolo Adicional a la Convención Americana sobre Derechos Humanos en Materia de Derechos Económicos, Sociales y Culturales \"Protocolo de San Salvador\", suscrito en San Salvador el 17 de noviembre de 1988" \
    --ramas "internacional-publico, constitucional" --salida normativa/co-ley-319-1996.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0031_1992.html --minimo 1 --id co:ley:31:1992 --tipo ley \
    --titulo "Ley 31 de 1992 - Por la cual se dictan las normas a las que deberá sujetarse el Banco de la" \
    --ramas "financiero, constitucional" --salida normativa/co-ley-31-1992.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0336_1996.html --minimo 1 --id co:ley:336:1996 --tipo ley \
    --titulo "Ley 336 de 1996 - Estatuto General de Transporte" \
    --ramas "transporte" --salida normativa/co-ley-336-1996.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0344_1996.html --minimo 1 --id co:ley:344:1996 --tipo ley \
    --titulo "Ley 344 de 1996 - Por la cual se dictan normas tendientes a la racionalización del gasto público, se conceden unas facultades extraordinarias y se expiden otras disposiciones" \
    --ramas "administrativo" --salida normativa/co-ley-344-1996.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0387_1997.html --minimo 1 --id co:ley:387:1997 --tipo ley \
    --titulo "Ley 387 de 1997 - Por la cual se adoptan medidas para la prevención del desplazamiento forzado; la atención, protección, consolidación y estabilización socioeconómica de los desplazados internos por la violencia en la República de Colombia" \
    --ramas "victimas, administrativo" --salida normativa/co-ley-387-1997.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0443_1998.html --minimo 1 --id co:ley:443:1998 --tipo ley \
    --titulo "Ley 443 de 1998 - Por la cual se expiden normas sobre carrera administrativa y se dictan otras disposiciones" \
    --ramas "administrativo" --salida normativa/co-ley-443-1998.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0522_1999.html --minimo 1 --id co:ley:522:1999 --tipo ley \
    --titulo "Ley 522 de 1999 - Por medio de la cual se expide el Código Penal Militar" \
    --ramas "penal, defensa" --salida normativa/co-ley-522-1999.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0550_1999.html --minimo 1 --id co:ley:550:1999 --tipo ley \
    --titulo "Ley 550 de 1999 - Por la cual se establece un régimen que promueva y facilite la reactivación empresarial y la reestructuración de los entes territoriales para asegurar la función social de las empresas y lograr el desarrollo armónico de las regiones y se dictan disposiciones para armonizar el régimen legal vigente con las normas de esta ley" \
    --ramas "insolvencia, comercial" --salida normativa/co-ley-550-1999.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0594_2000.html --minimo 1 --id co:ley:594:2000 --tipo ley \
    --titulo "Ley 594 de 2000 - Por medio de la cual se dicta la Ley General de Archivos y se dictan otras disposiciones" \
    --ramas "administrativo, cultura" --salida normativa/co-ley-594-2000.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0060_1993.html --minimo 1 --id co:ley:60:1993 --tipo ley \
    --titulo "Ley 60 de 1993 - Por la cual se dictan normas orgánicas sobre la distribución de competencias de conformidad con los artículos 151 y 288 de la Constitución Política y se distribuyen recursos según los artículos 356 y 357 de la Constitución Política y se dictan otras disposiciones" \
    --ramas "territorial, educacion, salud" --salida normativa/co-ley-60-1993.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0619_2000.html --minimo 1 --id co:ley:619:2000 --tipo ley \
    --titulo "Ley 619 de 2000 - Por la cual se modifica la Ley 141 de 1994, se establecen criterios de distribución y se dictan otras disposiciones" \
    --ramas "minero-energetico, territorial" --salida normativa/co-ley-619-2000.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0677_2001.html --minimo 1 --id co:ley:677:2001 --tipo ley \
    --titulo "Ley 677 de 2001 - Por medio de la cual se expiden normas sobre tratamientos excepcionales para regímenes territoriales" \
    --ramas "territorial, tributario" --salida normativa/co-ley-677-2001.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0681_2001.html --minimo 1 --id co:ley:681:2001 --tipo ley \
    --titulo "Ley 681 de 2001 - Por la cual se modifica el régimen de concesiones de combustibles en las zonas de frontera y se establecen otras disposiciones en materia tributaria para combustibles" \
    --ramas "tributario, minero-energetico" --salida normativa/co-ley-681-2001.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0716_2001.html --minimo 1 --id co:ley:716:2001 --tipo ley \
    --titulo "Ley 716 de 2001 - Por la cual se expiden normas para el saneamiento de la información contable en el sector público y se dictan disposiciones en materia tributaria y otras disposiciones" \
    --ramas "tributario, administrativo" --salida normativa/co-ley-716-2001.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0814_2003.html --minimo 1 --id co:ley:814:2003 --tipo ley \
    --titulo "Ley 814 de 2003 - Por la cual se dictan normas para el fomento de la actividad cinematográfica en Colombia" \
    --ramas "cultura, tributario" --salida normativa/co-ley-814-2003.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0082_1993.html --minimo 1 --id co:ley:82:1993 --tipo ley \
    --titulo "Ley 82 de 1993 - Por la cual se expiden normas para apoyar de manera especial a la mujer cabeza de familia" \
    --ramas "familia, social" --salida normativa/co-ley-82-1993.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0971_2005.html --minimo 1 --id co:ley:971:2005 --tipo ley \
    --titulo "Ley 971 de 2005 - Por medio de la cual se reglamenta el mecanismo de búsqueda urgente y se dictan otras disposiciones" \
    --ramas "penal, victimas" --salida normativa/co-ley-971-2005.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0987_2005.html --minimo 1 --id co:ley:987:2005 --tipo ley \
    --titulo "Ley 987 de 2005 - Por medio de la cual se modifican los Decretos 1211 de 1990, 1790 y 1793 de 2000 relacionados con el régimen salarial y prestacional del personal de oficiales, suboficiales y soldados de las Fuerzas Militares; los Decretos 1091 de 1995, 1212 y 1213 de 1990 y 1791 de 2000, relacionados con el régimen salarial y prestacional de oficiales, suboficiales, personal del nivel ejecutivo y agentes de la Policía Nacional y el Decreto 1214 de 1990 relacionado con el régimen prestacional civil del Ministerio de Defensa y Policía Nacional" \
    --ramas "defensa, laboral" --salida normativa/co-ley-987-2005.md
run http://www.secretariasenado.gov.co/senado/basedoc/ley_0996_2005.html --minimo 1 --id co:ley:996:2005 --tipo ley \
    --titulo "Ley 996 de 2005 - Por medio de la cual se reglamenta la elección de Presidente de la República, de conformidad con el artículo 152 literal f) de la Constitución Política de Colombia, y de acuerdo con lo establecido en el Acto Legislativo 02 de 2004, y se dictan otras disposiciones" \
    --ramas "electoral, constitucional" --salida normativa/co-ley-996-2005.md
