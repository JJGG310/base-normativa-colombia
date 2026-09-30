#!/bin/bash
# P23: decretos y decretos-ley origen con 8+ aristas que faltaban (los ids `i=` del Gestor salen de los
# enlaces de las páginas del propio Gestor ya en caché o de buscador web, y se verificaron contra el <title>
# de cada página: tipo, número y año). Título = epígrafe de la fuente; ramas = las dos más comunes entre las
# normas que el decreto afecta. Cada carga pasa por verificar.py (faltan 0). Muertes de la norma entera según
# el encabezado del Gestor, anotadas a mano en relaciones.csv (`manual:`): Decreto 141/2011 (INEXEQUIBLE,
# C-276/2011) y Decreto 934/2021 (derogado por el Decreto 821/2022). El Decreto 219/2000 («derogado
# parcialmente, con excepción de…») NO se registra. El Decreto 1934/2015 (i=63522) NO se carga: la
# página del Gestor está truncada (arts. 1-3 de 17, sin firma); sus 9 aristas de origen (art. 17) quedan sin resolver.
cd "$(dirname "$0")" || exit 1
gestor() { echo "== $3"; python3 ingesta_gestor.py "$@" 2>&1 | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error|notas no";
    python3 verificar.py "${@: -1}" 2>&1 | grep -E "faltan"; sleep 2; }

gestor 40618 --id co:decreto:262:2000 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 262 de 2000 - Por el cual se modifican la estructura y la organización de la Procuraduría General de la Nación y del Instituto de Estudios del Ministerio Público; el régimen de competencias interno de la Procuraduría General; se dictan normas para su funcionamiento; se modifica el régimen de carrera de la Procuraduría General de la Nación, el de inhabilidades e incompatibilidades de sus servidores y se regulan las diversas situaciones administrativas a las que se encuentren sujetos' \
    --ramas constitucional --salida normativa/co-decreto-262-2000.md
gestor 68758 --id co:decreto:16:2014 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 16 de 2014 - Por el cual se modifica y define la estructura orgánica y funcional de la Fiscalía General de la Nación' \
    --ramas constitucional --salida normativa/co-decreto-16-2014.md
gestor 69485 --id co:decreto:20:2014 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 20 de 2014 - Por el cual se clasifican los empleos y se expide el régimen de carrera especial de la Fiscalía General de la Nación y de sus entidades adscritas' \
    --ramas constitucional --salida normativa/co-decreto-20-2014.md
gestor 68763 --id co:decreto:25:2014 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 25 de 2014 - Por el cual se modifica la estructura orgánica y se establece la organización y funcionamiento de la Defensoría del Pueblo' \
    --ramas 'constitucional, administrativo' --salida normativa/co-decreto-25-2014.md
gestor 81854 --id co:decreto-ley:885:2017 --tipo decreto-ley --minimo 1 --enteros \
    --titulo 'Decreto Ley 885 de 2017 - Por medio del cual se modifica la Ley 434 de 1998 y se crea el Consejo Nacional de Paz, Reconciliación y Convivencia' \
    --ramas constitucional --salida normativa/co-decreto-ley-885-2017.md
gestor 135490 --id co:decreto:1054:2020 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1054 de 2020 - Por el cual se reglamentan los artículos 18-1, 23-1, 368-1 y el literal h del artículo 793 del Estatuto Tributario y el artículo 66 de la Ley 2010 de 2019 y se sustituyen unos artículos de la Parte 2 del Libro 1 del Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria' \
    --ramas tributario --salida normativa/co-decreto-1054-2020.md
gestor 170646 --id co:decreto:1079:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1079 de 2021 - Por medio del cual se reglamenta el artículo 25 de la Ley 2069 de 2020, se modifica y adiciona el Capítulo 3 del Título 1 de la Parte 2 del Libro 2 del Decreto 1074 de 2015, Decreto Único Reglamentario del Sector Comercio, Industria y Turismo' \
    --ramas 'comercial, societario' --salida normativa/co-decreto-1079-2021.md
gestor 250076 --id co:decreto:1104:2024 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1104 de 2024 - Por el cual se modifican los artículos 2.2.3.8.1.2, 2.2.3.8.2.1, 2.2.3.8.2.4, 2.2.3.8.3.1, 2.2.3.8.3.2, 2.2.3.8.3.3, 2.2.3.8.3.4, 2.2.3.8.4.2 y 2.2.3.8.4.3 del Decreto 1074 de 2015, Decreto Único Reglamentario del Sector Comercio, Industria Turismo' \
    --ramas 'comercial, societario' --salida normativa/co-decreto-1104-2024.md
gestor 82478 --id co:decreto:117:2017 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 117 de 2017 - Por el cual se adiciona el Decreto Único Reglamentario del Sector Hacienda y Crédito Público' \
    --ramas 'educacion, administrativo' --salida normativa/co-decreto-117-2017.md
gestor 87362 --id co:decreto:1181:2018 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1181 de 2018 - Por medio del cual se modifican parcialmente las disposiciones de que tratan los artículos 2.2.1.1.1., 2.2.1.2.1.17, 2.2.1.2.4.6, 2.2.1.2.4.9., 2.2.1.2.4.12. y se adicionan los artículos 2.2.1.2.4.18 y 2.2.1.2.4.19 al Decreto 1067 de 2015 "Por medio del cual se expide el Decreto único Reglamentario del Sector Administrativo de Relaciones Exteriores' \
    --ramas 'migratorio, internacional-publico' --salida normativa/co-decreto-1181-2018.md
gestor 172992 --id co:decreto:1357:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1357 de 2021 - Por el cual se reglamentan los literales a), b), c), d) y e) del numeral 2 del artículo 260-7 del Estatuto Tributario y se adiciona el Capítulo 6 al Título 2 de la Parte 2 del Libro 1 del Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria' \
    --ramas tributario --salida normativa/co-decreto-1357-2021.md
gestor 173647 --id co:decreto:1495:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1495 de 2021 - Por medio del cual se sustituye el Capítulo 23 del Título 1 Parte 6 del Libro 1 del Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria' \
    --ramas tributario --salida normativa/co-decreto-1495-2021.md
gestor 83538 --id co:decreto:1544:2017 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1544 de 2017 - Por el cual se modifica el Decreto 1082 de 2015, en lo relacionado al ciclo de los proyectos de inversión susceptibles de ser financiados con recursos del Sistema General de Regalías' \
    --ramas 'contratacion-estatal, administrativo' --salida normativa/co-decreto-1544-2017.md
gestor 175249 --id co:decreto:1843:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1843 de 2021 - Por el cual se reglamentan los artículos 44 y parcialmente el 65 de la Ley 2155 de 2021 y se modifican y adicionan unos artículos del Capítulo 22 del Título 1 de la Parte 2 del Libro 1 del Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria' \
    --ramas tributario --salida normativa/co-decreto-1843-2021.md
# gestor 63522 --id co:decreto:1934:2015 --tipo decreto --minimo 1 --enteros \
#     --titulo 'Decreto 1934 de 2015 - Por medio del cual se modifica el Decreto 1071 de 2015, Decreto Único Reglamentario del Sector Administrativo Agropecuario, Pesquero y de Desarrollo Rural, en lo relacionado con la reglamentación y valor del Subsidio Familiar de Vivienda de Interés Social Rural -VISR-' \
#     --ramas 'agrario, administrativo' --salida normativa/co-decreto-1934-2015.md
gestor 66059 --id co:decreto:1956:2015 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1956 de 2015 - Por el que se efectúan unas precisiones al Decreto 1076 de 2015, Por medio del cual se expide el Decreto Único Reglamentario del Sector Ambiente y Desarrollo Sostenible' \
    --ramas 'ambiental, administrativo' --salida normativa/co-decreto-1956-2015.md
gestor 101752 --id co:decreto:1973:2019 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1973 de 2019 - Por el cual se reglamentan los artículos 18-1, 23-1 y 368-1 del Estatuto Tributario y el artículo 58 de la Ley 1943 de 2018 y se adicionan y sustituyen unos artículos a la Parte 2 del Libro 1 del Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria' \
    --ramas tributario --salida normativa/co-decreto-1973-2019.md
gestor 66617 --id co:decreto:2411:2015 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 2411 de 2015 - Por el cual se modifican algunas disposiciones del Decreto 1077 de 2015 en lo relacionado con los Programas de Vivienda Gratuita y de Vivienda de Interés Prioritario para Ahorradores VIPA, y se dictan otras disposiciones' \
    --ramas 'urbanistico, servicios-publicos' --salida normativa/co-decreto-2411-2015.md
gestor 89961 --id co:decreto:2413:2018 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 2413 de 2018 - Por el cual se adiciona el capítulo 6 al título 1 de la parte 1 del libro 2 del Decreto 1077 de 2015 en relación con la implementación del Programa de Arrendamiento y Arrendamiento con opción de compra "Semillero de Propietarios" y se dictan otras disposiciones' \
    --ramas 'urbanistico, servicios-publicos' --salida normativa/co-decreto-2413-2018.md
gestor 204603 --id co:decreto:347:2023 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 347 de 2023 - Por el cual se adicionan los artículos 2.18.1.8, 2.18.1.9, 2.18.1.10, 2.18.1.11, 2.18.1.12, 2.18.1.13, 2.18.1.14 y 2.18.1.15 al Título 1 de la Parte 18 del Libro 2 del Decreto 1068 de 2015, Decreto Único Reglamentario del Sector Hacienda y Crédito Público, en lo relacionado con las garantías para bonos hipotecarios para financiar cartera hipotecaria, leasing habitacional y para títulos emitidos en procesos de titularización de cartera hipotecaria y leasing habitacional' \
    --ramas 'tributario, financiero' --salida normativa/co-decreto-347-2023.md
gestor 259536 --id co:decreto:406:2025 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 406 de 2025 - Por el cual se adiciona el Título 9, a la Parte 3, del Libro 2 del Decreto 1077 de 2015, en lo relacionado con los proyectos y programas de agua potable y saneamiento básico cuyos recursos serán administrados y/o ejecutados por el Fondo Nacional de Vivienda – FONVIVIENDA' \
    --ramas 'urbanistico, servicios-publicos' --salida normativa/co-decreto-406-2025.md
gestor 164066 --id co:decreto:507:2017 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 507 de 2017 - Por el cual se crea la beca Jóvenes Ciudadanos de Paz' \
    --ramas 'educacion, administrativo' --salida normativa/co-decreto-507-2017.md
gestor 164615 --id co:decreto:654:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 654 de 2021 - Por el cual se adiciona la Sección 6 al Capítulo 2 del Título 6 de la Parte 2 del Libro 2 del Decreto 1072 de 2015, Decreto Único Reglamentario del Sector Trabajo, y se adopta la Clasificación Única de Ocupaciones para Colombia - CUOC y se dictan otras disposiciones' \
    --ramas 'laboral, seguridad-social' --salida normativa/co-decreto-654-2021.md
gestor 260496 --id co:decreto:670:2025 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 670 de 2025 - Por el cual se adiciona el Capítulo 8 del Título 2, de la Parte 3, del Libro 2, del Decreto 1077 de 2015, se reglamenta el artículo 227 de la Ley 2294 de 2023 referente al Programa Basura Cero, y por el cual se efectúan adiciones a los artículos 2.2.2.3.2.3 y 2.2.2.3.7.1 del Capítulo 3, Título 2, Parte 2, Libro 2 del Decreto 1076 de 2015 y se dictan otras disposiciones"' \
    --ramas 'administrativo, urbanistico' --salida normativa/co-decreto-670-2025.md
gestor 85982 --id co:decreto:710:2018 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 710 de 2018 - Por el cual se modifican unos artículos del Título 12 de la Parte 8 del Libro 2 del Decreto 780 de 2016, Único Reglamentario del Sector Salud y Protección Social en relación con la evaluación de tecnologías para propósitos de control de precios de medicamentos nuevos ·' \
    --ramas 'salud, seguridad-social' --salida normativa/co-decreto-710-2018.md
gestor 166886 --id co:decreto:790:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 790 de 2021 - Por el cual se modifican los artículos 2.2.2.1.8., 2.2.16.1.3., 2.2.16.1.24., 2.2.16.3.8., 2.2.16.6.1., 2.2.16.6.5., 2.2.16.7.8., 2.2.16.7.10., 2.2.16.7.17 del Decreto 1833 de 2016 compilatorio de las normas del Sistema General de Pensiones, en lo relacionado con normas sobre bonos pensionales' \
    --ramas 'seguridad-social, administrativo' --salida normativa/co-decreto-790-2021.md
gestor 187747 --id co:decreto:1007:2022 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1007 de 2022 - Por medio del cual se adicionan los capítulos 11 al 17 al Título 8 de la Parte 2 del Libro 2 del Decreto 1070 de 2015, “Decreto Único Reglamentario del Sector Administrativo de Defensa” y se modifica el Decreto 1066 de 2015, “Decreto Único Reglamentario del Sector Administrativo del Interior”, para reglamentar parcialmente el Código Nacional de Seguridad y Convivencia Ciudadana",' \
    --ramas 'administrativo, defensa' --salida normativa/co-decreto-1007-2022.md
gestor 74494 --id co:decreto:1272:2016 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1272 de 2016 - Por el cual se adiciona un capítulo al Título 9 de' \
    --ramas 'ambiental, administrativo' --salida normativa/co-decreto-1272-2016.md
gestor 87623 --id co:decreto:1272:2018 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1272 de 2018 - Por el cual se modifica el Decreto 1075 de 2015 -Único Reglamentario del Sector Educación-, se reglamenta el reconocimiento y pago de Prestaciones Económicas a cargo del Fondo Nacional de Prestaciones Sociales del Magisterio y se dictan otras disposiciones' \
    --ramas 'educacion, administrativo' --salida normativa/co-decreto-1272-2018.md
gestor 75235 --id co:decreto:1325:2016 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1325 de 2016 - Por medio del cual se modifican parcialmente y se derogan algunas disposiciones generales de Control, Vigilancia y Verificación Migratoria, de que trata la sección 2 del capítulo 11 del título 1 de la parte 2 del libro 2 del Decreto 1067 de 2015' \
    --ramas 'migratorio, internacional-publico' --salida normativa/co-decreto-1325-2016.md
gestor 143007 --id co:decreto:1331:2020 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1331 de 2020 - Por el cual se realiza una depuración del Decreto 1074 de 2015, Decreto Único Reglamentario del sector Comercio, Industria y Turismo' \
    --ramas 'comercial, societario' --salida normativa/co-decreto-1331-2020.md
gestor 255976 --id co:decreto:1368:2024 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1368 de 2024 - Por el cual se adiciona el capítulo III al título I Parte VIII del Libro II del Decreto Único Reglamentario 1080 de 2015, y se corrige un yerro' \
    --ramas 'cultura, administrativo' --salida normativa/co-decreto-1368-2024.md
gestor 67534 --id co:decreto:13:2016 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 13 de 2016 - Por el cual se adiciona y modifica el Decreto Único del Sector Administrativo Agropecuario, Pesquero y de Desarrollo Rural, reglamentando el parágrafo tercero del artículo 106 de la Ley 1753 de 2015' \
    --ramas 'agrario, administrativo' --salida normativa/co-decreto-13-2016.md
gestor 41361 --id co:decreto:141:2011 --tipo decreto --minimo 1 --enteros --estado inexequible \
    --titulo 'Decreto 141 de 2011 - Por el cual se modifican los artículos 24, 26, 27, 28, 29, 31, 33, 37, 41, 44, 45, 65 y 66 de la Ley 99 de 1993, y se adoptan otras determinaciones"' \
    --ramas 'ambiental, administrativo' --salida normativa/co-decreto-141-2011.md
gestor 191906 --id co:decreto:1564:2022 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1564 de 2022 - Por el cual se modifica el Decreto 1070 de 2015 "Decreto Único Reglamentario del Sector Administrativo de Defensa" en cuanto a la reglamentación de las Medallas Militares "Servicios'"'"' Distinguidos en Operaciones Especiales" y "Cruz de Plata en Operaciones Especiales' \
    --ramas 'defensa, administrativo' --salida normativa/co-decreto-1564-2022.md
gestor 154306 --id co:decreto:1806:2020 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1806 de 2020 - Por el cual se reglamenta el numeral v) de la letra ii del literal d del artículo 1 del Decreto Legislativo 816 de 2020 y se adiciona la Parte 23 al Libro 2 del Decreto 1068 de 2015, Único Reglamentario del Sector Hacienda y Crédito Público' \
    --ramas 'tributario, financiero' --salida normativa/co-decreto-1806-2020.md
gestor 175268 --id co:decreto:1838:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1838 de 2021 - Por el cual se adiciona la Sección 3 al Capítulo 3 del Título 1 de la Parte 2 del Libro 2 del Decreto 1074 de 2015, Decreto Único Reglamentario del Sector Comercio, Industria y Turismo, con el fin de reglamentar el artículo 46 de la Ley 2069 de 2020, en lo relacionado con la unificación de las fuentes de emprendimiento y desarrollo empresarial' \
    --ramas 'comercial, societario' --salida normativa/co-decreto-1838-2021.md
gestor 64532 --id co:decreto:1961:2015 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 1961 de 2015 - Por el cual se modifica la numeración del Capítulo 15 del Título 6 de la Parte 2 del Libro 2 del Decreto 1069 de 2015, Decreto Único Reglamentario del Sector Justicia y del Derecho, denominado Apertura de Matrícula Inmobiliaria de Bienes Baldíos' \
    --ramas 'administrativo, procesal' --salida normativa/co-decreto-1961-2015.md
gestor 75313 --id co:decreto:219:2000 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 219 de 2000 - Por el cual se modifica la estructura del Ministerio de Desarrollo Económico' \
    --ramas 'comercial, administrativo' --salida normativa/co-decreto-219-2000.md
gestor 110796 --id co:decreto:465:2020 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 465 de 2020 - Por el cual se adiciona el Decreto 1076 de 2015, Decreto Único Reglamentario del Sector Ambiente y Desarrollo Sostenible, en lo relacionado con la adopción de disposiciones transitorias en materia de concesiones de agua para la prestación del servicio público esencial de acueducto, y se toman otras determinaciones en el marco de la emergencia sanitaria declarada por el Gobierno nacional a causa de la Pandemia COVID-19' \
    --ramas 'ambiental, administrativo' --salida normativa/co-decreto-465-2020.md
gestor 205943 --id co:decreto:490:2023 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 490 de 2023 - Por el cual se modifica parcialmente el Decreto 1077 de 2015, en lo relacionado con las condiciones del programa de promoción de acceso a la vivienda de interés social "Mi Casa Ya" y se dictan otras disposiciones' \
    --ramas 'urbanistico, servicios-publicos' --salida normativa/co-decreto-490-2023.md
gestor 45240 --id co:decreto:4923:2011 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 4923 de 2011 - Por el cual se garantiza la operación del Sistema General de Regalías' \
    --ramas constitucional --salida normativa/co-decreto-4923-2011.md
gestor 163290 --id co:decreto:525:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 525 de 2021 - Por el cual se modifican los artículos 2.10.1.2, 2.10.1.4, 2.10.1.5, 2.10.1.6, 2.10.1.7, 2.10.1.8, 2.10.1.10 y 2.10.1.13 el Decreto 1080 dé 2015, Decreto Único Reglamentario del Sector Cultura' \
    --ramas 'cultura, administrativo' --salida normativa/co-decreto-525-2021.md
gestor 163291 --id co:decreto:526:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 526 de 2021 - Por el cual se adicionan unos artículos al capítulo 1 del Título 1, de la Parte 2 del libro 2 del Decreto 1072 de 2015, Decreto Único Reglamentario del Sector Trabajo, para regular la firma electrónica del contrato individual de trabajo' \
    --ramas 'laboral, seguridad-social' --salida normativa/co-decreto-526-2021.md
gestor 186648 --id co:decreto:631:2022 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 631 de 2022 - Por el cual se reglamentan los artículos 11, 14, 15, 22, 26 y 28 de la Ley 1765 de 2015 y se modifica el Decreto 1070 de 2015, Decreto Único Reglamentario del Sector Defensa, en el sentido de establecer el procedimiento para la integración de las listas de candidatos a ocupar los cargos de Magistrados del Tribunal Superior Militar y Policial, Fiscal General Penal Militar y Policial y Fiscales Penales Militares y Policiales Delegados ante el Tribunal Superior Penal Militar y Policial' \
    --ramas 'defensa, administrativo' --salida normativa/co-decreto-631-2022.md
gestor 164607 --id co:decreto:647:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 647 de 2021 - Por medio del cual se adicionan unos artículos al Capítulo 11 Titulo 8 parte 2 del Libro 2 del Decreto 1070 de 2015, "Decreto Único Reglamentario del Sector Administrativo de Defensa", relacionados con la reglamentación del Consejo Nacional de Seguridad y Convivencia Ciudadana' \
    --ramas 'defensa, administrativo' --salida normativa/co-decreto-647-2021.md
gestor 167367 --id co:decreto:830:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 830 de 2021 - Por el cual se modifican y adicionan algunos artículos al Decreto 1081 de 2015, Único Reglamentario del Sector Presidencia de la República, en lo relacionado con el régimen de las Personas Expuestas Políticamente (PEP)' \
    --ramas 'administrativo, constitucional' --salida normativa/co-decreto-830-2021.md
gestor 262196 --id co:decreto:875:2025 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 875 de 2025 - Por el cual se adiciona la Sección 6 al Capítulo 1, Título V, Parte 2, Libro 2 del Decreto 1073 de 2015 Decreto Único Reglamentario del Sector Administrativo de Minas y Energía, en relación con la creación del Sistema Nacional de Seguridad Minera - SNSM contenido en el artículo 24 de la Ley 2250 de 2022' \
    --ramas 'minero-energetico, administrativo' --salida normativa/co-decreto-875-2025.md
gestor 168913 --id co:decreto:934:2021 --tipo decreto --minimo 1 --enteros --estado derogada \
    --titulo 'Decreto 934 de 2021 - Por el cual se adiciona el capítulo 7 al título 2 de la parte 2 del libro 2 del Decreto 1078 de 2015, Decreto Único Reglamentario del Sector de Tecnologías de la Información y las Comunicaciones, para reglamentarse el parágrafo 2 del artículo 11 de la Ley 1341 de 2009' \
    --ramas 'tic, administrativo' --salida normativa/co-decreto-934-2021.md
gestor 169006 --id co:decreto:952:2021 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 952 de 2021 - Por el cual se reglamenta el artículo 2 de la Ley 2039 del 2020 y se adiciona el capítulo 6 al título 5 de la parte 2 del libro 2 del Decreto 1083 del 2015, en lo relacionado con el reconocimiento de la experiencia previa como experiencia profesional válida para la inserción laboral de jóvenes en el sector público' \
    --ramas 'administrativo, laboral' --salida normativa/co-decreto-952-2021.md
gestor 188946 --id co:decreto:985:2022 --tipo decreto --minimo 1 --enteros \
    --titulo 'Decreto 985 de 2022 - Por medio del cual se reglamenta el artículo 257-1 del Estatuto Tributario, adicionado por el artículo 190 de la Ley 1955 de 2019 y se adicionan los artículos 1.6.2.5.5., 1.6.2.5.6., 1.6.2.5.7., 1.6.2.5.8., 1.6.2.5.9., 1.6.2.5.10., 1.6.2.5.11. y 1.6.2.5.12., al Capítulo 5 del Título 2 de la Parte 6 del Libro 1 del Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria y la Parte 14 del Libro 2 al Decreto 1085 de 2015 Único Reglamentario del Sector Administrativo del Deporte' \
    --ramas tributario --salida normativa/co-decreto-985-2022.md
