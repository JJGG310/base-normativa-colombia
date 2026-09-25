#!/bin/bash
# P17: decretos origen con 10-19 aristas de vigencia (reformadores de DUR y otros), del Gestor.
# IDs del Gestor verificados contra el encabezado de la página; título = epígrafe de la fuente.
cd "$(dirname "$0")" || exit 1
gestor() { echo "== $1"; python3 ingesta_gestor.py "$1" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|ABORTA|fecha|Error"; }

gestor 86900 --id co:decreto:991:2018 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 991 de 2018 - Por el cual se modifica parcialmente el Decreto Único Reglamentario 1074 de 2015 en diversas materias relacionadas con los procesos concursales" \
    --ramas "comercial,societario,consumo,administrativo" --salida normativa/co-decreto-991-2018.md
gestor 174448 --id co:decreto:1731:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1731 de 2021 - Por medio del cual se modifica y adiciona al Decreto 1071 de 2015, Único Reglamentario del Sector Administrativo Agropecuario, Pesquero y de Desarrollo Rural, lo relacionado con el Fondo de Fomento para las Mujeres Rurales (FOMMUR)" \
    --ramas "agrario,administrativo" --salida normativa/co-decreto-1731-2021.md
gestor 173808 --id co:decreto:1588:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1588 de 2021 - Por el cual se adiciona la Sección 12 al Capítulo 1 del Título 1 de la Parte 6 del Libro 2 del Decreto 1070 de 2015 'Por el cual se expide el Decreto Único Reglamentario del Sector Administrativo de Defensa', reglamentando el Seguro de Vida Colectivo que ampara al Personal Operativo de los […]" \
    --ramas "defensa,administrativo" --salida normativa/co-decreto-1588-2021.md
gestor 162993 --id co:decreto:478:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 478 de 2021 - Por el cual se modifica y adiciona el Capítulo 6 del Título 1 de la Parte 2 del Libro 2 del Decreto 1079 de 2015, Único Reglamentario del Sector Transporte" \
    --ramas "transporte,administrativo" --salida normativa/co-decreto-478-2021.md
gestor 174573 --id co:decreto:1732:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1732 de 2021 - Por el cual se reglamenta el artículo 5 de la Ley 2069 de 2020, en relación con los mecanismos exploratorios de regulación para modelos de negocio innovadores en industrias reguladas y los ambientes especiales de vigilancia y control o sandbox regulatorio, y se adiciona el Capítulo 19 al Título 1 […]" \
    --ramas "comercial,societario,consumo,administrativo" --salida normativa/co-decreto-1732-2021.md
gestor 105033 --id co:decreto:46:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 46 de 2020 - Por el cual se modifican disposiciones del Decreto 1077 de 2015 en relación con los precios máximos de la Vivienda de Interés Social y la Vivienda de Interés Prioritario" \
    --ramas "urbanistico,servicios-publicos,administrativo" --salida normativa/co-decreto-46-2020.md
gestor 84673 --id co:decreto:2105:2017 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 2105 de 2017 - Por el cual se modifica parcialmente el Decreto 1075 de 2015, Único Reglamentario del Sector Educación, en relación con la jornada única escolar, los tipos de cargos del sistema especial de carrera docente y su forma de provisión, los concursos docentes y la actividad laboral docente en el servicio […]" \
    --ramas "educacion,administrativo" --salida normativa/co-decreto-2105-2017.md
gestor 60437 --id co:decreto:1333:2007 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1333 de 2007 - Por el cual se modifica el Decreto 4299 de 2005 y se establecen otras disposiciones" \
    --ramas "minero-energetico,administrativo" --salida normativa/co-decreto-1333-2007.md
gestor 145418 --id co:decreto:1457:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1457 de 2020 - Por el cual se reglamentan los artículos 242, 242-1, 245, 246-1 y 895 del Estatuto Tributario y se modifican, adicionan y sustituyen artículos del Capítulo 10 del Título 1 de la Parte 2 del Libro 1, del Capítulo 7 del Título 4 de la Parte 2 del Libro 1, del Capítulo 21 del Título 1 de la Parte 6 […]" \
    --ramas "tributario" --salida normativa/co-decreto-1457-2020.md
gestor 85084 --id co:decreto:50:2018 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 50 de 2018 - Por el cual se modifica parcialmente el Decreto 1076 de 2015, Decreto único Reglamentario del Sector Ambiente y Desarrollo Sostenible en relación con los Consejos Ambientales Regionales de la Macrocuencas (CARMAC), el Ordenamiento del Recurso Hídrico y Vertimientos y se dictan otras disposiciones" \
    --ramas "ambiental,administrativo" --salida normativa/co-decreto-50-2018.md
gestor 190146 --id co:decreto:1247:2022 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1247 de 2022 - Por el cual se adiciona una sección al Capítulo 1 del Título 10 de la parte 1 del Libro 2 del Decreto 1077 de 2015 en relación con las Cajas de Compensación Familiar dentro de la Política Pública de Vivienda de Interés Social Rural y se dictan otras disposiciones" \
    --ramas "urbanistico,servicios-publicos,administrativo" --salida normativa/co-decreto-1247-2022.md
gestor 67433 --id co:decreto:36:2016 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 36 de 2016 - Por el cual se modifican los artículos 2.2.2.1.16 al 2.2.2.1.23 y se adicionan los artículos 2.2.2.1.24 al 2.2.2.1.32 del capítulo 1 del título 2 de la parte 2 del libro 2 del Decreto 1072 de 2015, Decreto Único Reglamentario del Sector Trabajo, y se reglamentan los artículos 482, 483 y 484 del […]" \
    --ramas "laboral,seguridad-social,administrativo" --salida normativa/co-decreto-36-2016.md
gestor 154447 --id co:decreto:1823:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1823 de 2020 - Por el cual se modifica parcialmente el Título 6 sección 2 del Decreto 1072 de 2015" \
    --ramas "laboral,seguridad-social,administrativo" --salida normativa/co-decreto-1823-2020.md
gestor 84474 --id co:decreto:1949:2017 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1949 de 2017 - Por el cual se modifica y adiciona el Decreto Único Reglamentario No 1073 de 2015, en cuanto se reglamentan los mecanismos para el trabajo bajo el amparo de un título en la pequeña minería y se toman otras determinaciones" \
    --ramas "minero-energetico,administrativo" --salida normativa/co-decreto-1949-2017.md
gestor 104912 --id co:decreto:2371:2019 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 2371 de 2019 - Por el cual se reglamentan los artículos 242, 242-1, 245 y 246-1 del Estatuto Tributario y se modifica y adiciona el Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria" \
    --ramas "tributario" --salida normativa/co-decreto-2371-2019.md
gestor 177047 --id co:decreto:204:2022 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 204 de 2022 - Por el cual se modifican y adicionan unos Artículos del Decreto Único Reglamentario del Sector Cultura 1080 de 2015, sobre Patrimonio Cultural Sumergido" \
    --ramas "cultura,administrativo" --salida normativa/co-decreto-204-2022.md
gestor 175106 --id co:decreto:1785:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1785 de 2021 - Por medio del cual se adiciona al Libro 2, Título 2, Capitulo 1 del Decreto 1076 de 2015, Decreto Único Reglamentario del Sector de Ambiente y Desarrollo Sostenible, una nueva sección relacionada con las medidas tendientes a dinamizar procesos de saneamiento al interior de las áreas del Sistema de […]" \
    --ramas "ambiental,administrativo" --salida normativa/co-decreto-1785-2021.md
gestor 174048 --id co:decreto:1667:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1667 de 2021 - Por el cual se adiciona la Sección 5 al Capítulo 3, Título 3, Parte 5, Libro 2, y la Sección 6 al Capítulo 3, Título 3, Parte 5, Libro 2, del Decreto 1075 de 2015 Único Reglamentario del Sector Educación, para reglamentar el artículo 27 de la Ley 2155 de 2021" \
    --ramas "educacion,administrativo" --salida normativa/co-decreto-1667-2021.md
gestor 191426 --id co:decreto:1493:2022 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1493 de 2022 - Por el cual se modifican y subrogan unos artículos del Decreto Único Reglamentario del Sector Trabajo 1072 de 2015, relacionados con las prestaciones económicas a la población cesante reconocidas por el Fondo de Solidaridad de Fomento al Empleo y Protección al Cesante - FOSFEC - y sobre el ahorro […]" \
    --ramas "laboral,seguridad-social,administrativo" --salida normativa/co-decreto-1493-2022.md
gestor 95470 --id co:decreto:1120:2019 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1120 de 2019 - Por el cual se modifican unos artículos de la Sección 7 del Capítulo 7 del Título 1 de la Parte 2 del Libro 2 del Decreto 1079 de 2015 Único Reglamentario del Sector Transporte»" \
    --ramas "transporte,administrativo" --salida normativa/co-decreto-1120-2019.md
gestor 205703 --id co:decreto:442:2023 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 442 de 2023 - Por el cual se reglamentan parcialmente los artículos 511 , 615 , 616-1 modificado por el artículo 13 de la Ley 2155 de 2021, 617 , 618 y 771-2 del Estatuto Tributario, y se modifican los numerales 3, 5, 8 y 11 del artículo 1.6.1.4.1. , el parágrafo 1 del artículo 1.6.1.4.3. , el inciso 1 y el […]" \
    --ramas "tributario" --salida normativa/co-decreto-442-2023.md
gestor 268436 --id co:decreto:1138:2025 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1138 de 2025 - Por medio del cual se modifica parcialmente el Título 11 de la Parte 8 del Libro 2 del Decreto 780 de 2016, Único Reglamentario del Sector Salud y Protección Social, en relación con el acceso seguro e informado al uso del cannabis y de la planta de cannabis" \
    --ramas "salud,seguridad-social,administrativo" --salida normativa/co-decreto-1138-2025.md
gestor 48893 --id co:decreto:1736:2012 --tipo decreto --minimo 1 --fecha 2012-08-17 \
    --titulo "Decreto 1736 de 2012 - Por el que se corrigen unos yerros en la Ley 1564 del 12 de julio de 2012, 'por medio de la cual se expide el Código General del Proceso y se dictan otras disposiciones" \
    --ramas "procesal,civil,comercial,familia" --salida normativa/co-decreto-1736-2012.md
gestor 80775 --id co:decreto:555:2017 --tipo decreto --minimo 1 \
    --titulo "Decreto 555 de 2017 - Por el cual se corrigen unos yerros en la Ley 1801 de 2016 “Por la cual se expide el Código Nacional de Policía y Convivencia" \
    --ramas "policivo,administrativo" --salida normativa/co-decreto-555-2017.md
gestor 62991 --id co:decreto:1814:2015 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1814 de 2015 - Por el cual se reglamenta el Decreto 1772 de 2015 'Por medio del cual se establecen disposiciones excepcionales para garantizar la reunificación familiar de los nacionales colombianos deportados, expulsados o retomados como consecuencia de la declaratoria del Estado de Excepción efectuada en la […]" \
    --ramas "migratorio,internacional-publico,administrativo" --salida normativa/co-decreto-1814-2015.md
gestor 164895 --id co:decreto:696:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 696 de 2021 - Por medio del cual se corrige un yerro en la numeración del Decreto 1690 de 2020" \
    --ramas "social,victimas,administrativo" --salida normativa/co-decreto-696-2021.md
gestor 31645 --id co:decreto:1474:1997 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1474 de 1997 - por el cual se derogan, modifican y/o adicionan algunos artículos del Decreto reglamentario 1748 de 1995 y se dictan otras disposiciones" \
    --ramas "seguridad-social,administrativo" --salida normativa/co-decreto-1474-1997.md
gestor 31644 --id co:decreto:1513:1998 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1513 de 1998 - por el cual se modifican y/o adicionan algunos artículos de los Decretos Reglamentarios 1748 de 1995 y 1474 de 1997 y se dictan otras disposiciones" \
    --ramas "seguridad-social,administrativo" --salida normativa/co-decreto-1513-1998.md
gestor 173293 --id co:decreto:1417:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1417 de 2021 - Por el cual se adicionan unos artículos al Libro 2, Parte 2, Título 4, Capítulo 3 del Decreto 1070 de 2015 Decreto Único Reglamentario del Sector Administrativo de Defensa sobre la clasificación y reglamentación de la tenencia y el porte de las armas traumáticas" \
    --ramas "defensa,administrativo" --salida normativa/co-decreto-1417-2021.md
gestor 173333 --id co:decreto:1429:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1429 de 2021 - Por el cual se adicionan las secciones 2 y 6 del Capítulo 3, del Título 1, de la Parte 3, del libro 2 del Decreto 1070 de 2015 'Por el cual se expide el Decreto Único Reglamentario del Sector Administrativo de Defensa' en lo que respecta a la creación de las Medallas Militares 'Corazón Azul', 'Alma […]" \
    --ramas "defensa,administrativo" --salida normativa/co-decreto-1429-2021.md
gestor 190935 --id co:decreto:1227:2022 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1227 de 2022 - Por el cual se modifican los artículos 2.2.1.5.3, 2.2.1.5.5, 2.2.1.5.8 y 2.2.1.5.9. y se adicionan los artículos 2.2.1.5.15 al 2.2.1.5.25 al Decreto 1072 de 2015, Único Reglamentario del Sector Trabajo, relacionados con el Teletrabajo" \
    --ramas "laboral,seguridad-social,administrativo" --salida normativa/co-decreto-1227-2022.md
gestor 144983 --id co:decreto:1435:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1435 de 2020 - Por el cual se reglamentan los artículos 27 , 46 , 55 , 119 , 206 , 206-1 , 235-2 , literal e) del parágrafo 5 del artículo 240, 330 , 331 , 332 , 333 , 335 y 336 del Estatuto Tributario y se modifica el Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria" \
    --ramas "tributario" --salida normativa/co-decreto-1435-2020.md
gestor 128721 --id co:decreto:849:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 849 de 2020 - Por el cual se reglamentan los numerales 2 del artículo 235-2 y 24 del artículo 476 del Estatuto Tributario, se adicionan unos artículos al Capítulo 22 del Título 1 de la Parte 2 del Libro 1 y el artículo 1.3.1.13.17. al Capítulo 13 del Título 1 de la Parte 3 del Libro 1 del Decreto 1625 de 2016, […]" \
    --ramas "tributario" --salida normativa/co-decreto-849-2020.md
gestor 191728 --id co:decreto:1575:2022 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1575 de 2022 - Por el cual se modifica el Título 1 de la Parle 2 del Libro 2 del Decreto 1068 de 2015 - 'Decreto Único Reglamentario del Sector Hacienda y Crédito Público' en lo relacionado con operaciones de crédito público, asimiladas, de manejo de la deuda y conexas" \
    --ramas "tributario,financiero,administrativo" --salida normativa/co-decreto-1575-2022.md
gestor 145419 --id co:decreto:1468:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1468 de 2020 - Por el cual se modifican parcialmente las Secciones 2, 5 y 6 del Capítulo 7 del Título 1 de la Parte 2 del Libro 2 del Decreto 1074 de 2015, Único Reglamentario del Sector Comercio, Industria y Turismo, en lo relativo a la aplicación del análisis de impacto normativo en los reglamentos técnicos" \
    --ramas "comercial,societario,consumo,administrativo" --salida normativa/co-decreto-1468-2020.md
gestor 164893 --id co:decreto:690:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 690 de 2021 - Por el cual se adiciona y modifica el Decreto Único Reglamentario 1076 de 2015, del sector de Ambiente y Desarrollo Sostenible, en lo relacionado con el manejo sostenible de la flora silvestre y los productos forestales no maderables, y se adoptan otras determinaciones" \
    --ramas "ambiental,administrativo" --salida normativa/co-decreto-690-2021.md
gestor 47260 --id co:decreto:900:2012 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 900 de 2012 - Por el cual se modifican parcialmente los Decretos número 2675 de 2005 y 1160 de 2010 y se dictan otras disposiciones en relación con el Subsidio Familiar de Vivienda de Interés Social Rural" \
    --ramas "agrario,administrativo" --salida normativa/co-decreto-900-2012.md
gestor 260396 --id co:decreto:638:2025 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 638 de 2025 - Por el cual se adiciona el Capítulo 8 al Título 1 de la Parte 4 del Libro 2 del Decreto 1066 de 2015, Único Reglamentario del Sector Administrativo del Interior, en lo relacionado con la reglamentación del Programa de Protección Integral de que trata el artículo 12 del Decreto Ley 895 de 2017" \
    --ramas "administrativo,policivo,constitucional" --salida normativa/co-decreto-638-2025.md
gestor 85479 --id co:decreto:412:2018 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 412 de 2018 - Por el cual se modifica parcialmente el Decreto 1068 de 2015 en el Libro 2 Régimen reglamentario del sector hacienda y crédito público, Parte 8 del Régimen Presupuestal, Parte 9 Sistema Integrado de Información Financiera - SIIF NACIÓN y se establecen otras disposiciones" \
    --ramas "tributario,financiero,administrativo" --salida normativa/co-decreto-412-2018.md
gestor 107614 --id co:decreto:277:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 277 de 2020 - Por el cual se modifican unos artículos de la Parte 19 del Libro 2 del Decreto 1068 de 2015, Decreto Único Reglamentario del Sector Hacienda y Crédito Público, en lo relacionado con el Fondo Nacional para el Desarrollo de la Infraestructura" \
    --ramas "tributario,financiero,administrativo" --salida normativa/co-decreto-277-2020.md
gestor 175187 --id co:decreto:1860:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1860 de 2021 - Por el cual se modifica y adiciona el Decreto 1082 de 2015, Único Reglamentario del Sector Administrativo de Planeación Nacional, con el fin reglamentar los artículos 30 , 31 , 32 , 34 y 35 de la Ley 2069 de 2020, en lo relativo al sistema de compras públicas y se dictan otras disposiciones" \
    --ramas "contratacion-estatal,administrativo" --salida normativa/co-decreto-1860-2021.md
gestor 175267 --id co:decreto:1837:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1837 de 2021 - Por el cual se reglamenta el artículo 63 de la Ley 2069 de 2020, respecto del funcionamiento, las condiciones, destinaciones y requisitos de los Fondos Territoriales Temporales para el desarrollo integral y reactivación económica de las empresas y emprendimientos" \
    --ramas "comercial,societario,consumo,administrativo" --salida normativa/co-decreto-1837-2021.md
gestor 175406 --id co:decreto:1885:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1885 de 2021 - Por medio del cual se modifican los Artículos 2.2.4.2.6.1.1., 2.2.4.2.6.1.4., 2.2.4.2.6.2.1., 2.2.4.2.6.2.2., 2.2.4.2.6.2.3., 2.2.4.2.6.2.5., 2.2.4.2.9.6., 2.2.4.4.7.2., 2.2.6.13.2.1.1., 2.2.6.13.2.2.4., 2.2.6.13.2.2.6., 2.2.6.13.3.1.1. y 2.2.6.13.3.2.1. del Decreto 1069 de 2015, Decreto único […]" \
    --ramas "administrativo,procesal" --salida normativa/co-decreto-1885-2021.md
gestor 66480 --id co:decreto:4222:2006 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 4222 de 2006 - Por el cual se modifica parcialmente la estructura del Ministerio de Defensa Nacional" \
    --ramas "defensa,administrativo" --salida normativa/co-decreto-4222-2006.md
gestor 99909 --id co:decreto:1562:2019 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1562 de 2019 - Por el cual se adicionan tres parágrafos al artículo 2.2.1.3.3 . y se adicionan los artículos 2.2.1.3.15 . a 2.2.1.3.26 . al Decreto 1072 de 2015, referentes al retiro de cesantías" \
    --ramas "laboral,seguridad-social,administrativo" --salida normativa/co-decreto-1562-2019.md
gestor 92070 --id co:decreto:632:2019 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 632 de 2019 - Por el cual se modifica, adiciona y deroga algunas disposiciones de la Subsección 1 de la Sección 7 del Capítulo 7 del Título 1 de la Parte 2 del Libro 2 del Decreto 1079 de 2015 Único Reglamentario del Sector Transporte" \
    --ramas "transporte,administrativo" --salida normativa/co-decreto-632-2019.md
gestor 104152 --id co:decreto:2264:2019 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 2264 de 2019 - Por el cual se reglamentan los artículos 27, 55, 206, 206-1, 235-2, 330, 331, 332, 333, 335 y 336 del Estatuto Tributario y se modifica y adiciona el Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria" \
    --ramas "tributario" --salida normativa/co-decreto-2264-2019.md
gestor 173806 --id co:decreto:1532:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1532 de 2021 - Por el cual se reglamentan los artículos 1, 4, 6 y 7 de la Ley 2154 de 2021 y se adiciona el Capítulo 30 al Título 1 de la Parte 6 del Libro 1 y el Título 4 Capítulo 1 a la Parte 8 del de Libro 1 del Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria" \
    --ramas "tributario" --salida normativa/co-decreto-1532-2021.md
gestor 258456 --id co:decreto:229:2025 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 229 de 2025 - Por el cual se sustituye la Sección 1 del Capítulo 8 del Título 3 de la Parte 5 del Decreto 780 de 2016, Único Reglamentario del Sector Salud y Protección Social" \
    --ramas "salud,seguridad-social,administrativo" --salida normativa/co-decreto-229-2025.md
gestor 87726 --id co:decreto:1355:2018 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1355 de 2018 - Por el cual se modifica el Decreto 780 de 2016, Único Reglamentario del Sector Salud y Protección Social, en relación con el manejo de los recursos de propiedad de las entidades territoriales destinados al aseguramiento de la población afiliada al Régimen Subsidiado" \
    --ramas "salud,seguridad-social,administrativo" --salida normativa/co-decreto-1355-2018.md
gestor 168366 --id co:decreto:890:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 890 de 2021 - Por el cual se reglamenta parcialmente el Decreto Legislativo 560 de 2020, en lo relacionado con el régimen de los bonos de riesgo y se adiciona el Capítulo 9 del Título 2 de la Parte 2 del Libro 2 del Decreto 1074 de 2015, Decreto Único Reglamentario del Sector Comercio, Industria y Turismo" \
    --ramas "comercial,societario,consumo,administrativo" --salida normativa/co-decreto-890-2021.md
gestor 173955 --id co:decreto:1644:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1644 de 2021 - Por el cual se regulan dos herramientas de Facilitación de la Inversión Extranjera Directa y se adiciona el Capítulo 8 al Título 3 de la Parte 2 del Libro 2 del Decreto 1074 de 2015, Decreto Único Reglamentario del Sector Comercio, Industria y Turismo" \
    --ramas "comercial,societario,consumo,administrativo" --salida normativa/co-decreto-1644-2021.md
gestor 153546 --id co:decreto:1690:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1690 de 2020 - Por el cual se reglamenta el artículo 5 del Decreto Legislativo 812 de 2020 sobre la administración, ejecución y operación del Programa de Protección Social al Adulto Mayor - Colombia Mayor-, el esquema de compensación del impuesto sobre las Ventas (IVA), el Programa de Ingreso Solidario y se dictan otras disposiciones" \
    --ramas "seguridad-social,administrativo" --salida normativa/co-decreto-1690-2020.md
gestor 86680 --id co:decreto:943:2018 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 943 de 2018 - Por el cual se modifica y adiciona la Sección 1, Capítulo 6 del Título III del Libro 2 del Decreto Único Reglamentario del Sector Administrativo de Minas y Energía, 1073 de 2015, relacionado con la prestación del servicio de alumbrado público" \
    --ramas "minero-energetico,administrativo" --salida normativa/co-decreto-943-2018.md
gestor 173948 --id co:decreto:1662:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1662 de 2021 - Por el cual se adiciona el Decreto 1083 de 2015 Único Reglamentario del Sector de la Función Pública, en relación con la habilitación del trabajo en casa para los servidores públicos de los organismos y entidades que conforman las ramas del poder público en sus distintos órdenes, sectores y […]" \
    --ramas "administrativo,laboral" --salida normativa/co-decreto-1662-2021.md
gestor 127884 --id co:decreto:829:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 829 de 2020 - Por el cual se reglamentan los artículos 11, 12, 13 y 14 de la Ley 1715 de 2014, se modifica y adiciona el Decreto 1625 de 2016, único Reglamentario en Materia Tributaria y se derogan algunos artículos del Decreto 1073, Único Reglamentario del Sector Administrativo de Minas y Energía" \
    --ramas "tributario" --salida normativa/co-decreto-829-2020.md
gestor 110394 --id co:decreto:286:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 286 de 2020 - Por el cual se reglamenta el numeral 1 del artículo 235-2 del Estatuto Tributario y se sustituyen unos artículos del Capítulo 22 del Título 1 de la Parte 2 del Libro 1 del Decreto 1625 de 2016 Único Reglamentario en Materia Tributaria" \
    --ramas "tributario" --salida normativa/co-decreto-286-2020.md
gestor 100163 --id co:decreto:1669:2019 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1669 de 2019 - Por el cual se reglamenta el numeral 1 del artículo 235-2 del Estatuto Tributario y se adicionan unos artículos al Capítulo 22 del Título 1 de la Parte 2 del Libro 1 del Decreto 1625 de 2016 Único Reglamentario en Materia Tributaria" \
    --ramas "tributario" --salida normativa/co-decreto-1669-2019.md
gestor 106854 --id co:decreto:221:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 221 de 2020 - Por el cual se reglamentan los numerales 4 y 5 y el parágrafo 4 del artículo 477, el parágrafo 1 del artículo 850 del Estatuto Tributario, y se sustituye, modifica, y adiciona el Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria" \
    --ramas "tributario" --salida normativa/co-decreto-221-2020.md
gestor 173958 --id co:decreto:1651:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1651 de 2021 - Por el cual se reglamenta el artículo 96 de la Ley 788 de 2002, modificado por el artículo 138 de la Ley 2010 de 2019, se sustituyen los artículos 1.3.1.9.2 . al 1.3.1.9.5 ., se renumera el artículo 1.3.1.9.6 . y se adicionan los artículos 1.3.1.9.6 . al 1.3.1.9.13 ., del Capítulo 9 del Título 1 de […]" \
    --ramas "tributario" --salida normativa/co-decreto-1651-2021.md
gestor 190086 --id co:decreto:1208:2022 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1208 de 2022 - Por el cual se reglamenta el parágrafo 4 del artículo 238 de la Ley 1819 de 2016 y el artículo 800-1 del Estatuto Tributario, modificado y adicionado por el artículo 34 de la Ley 2155 de 2021; se modifican el artículo 1.6.6.1.2 del Capítulo 1 del Título 6 de la Parte 6 del Libro 1, el artículo […]" \
    --ramas "tributario" --salida normativa/co-decreto-1208-2022.md
gestor 244816 --id co:decreto:142:2023 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 142 de 2023 - Por el cual se modifica y adiciona el Decreto 1082 de 2015, Único Reglamentario del Sector Administrativo de Planeación Nacional para promover el acceso al sistema de Compras Públicas de las Mipymes, las Cooperativas y demás entidades de la economía solidaria, se incorporan criterios sociales y […]" \
    --ramas "contratacion-estatal,administrativo" --salida normativa/co-decreto-142-2023.md
gestor 38664 --id co:decreto:126:2010 --tipo decreto --minimo 1 \
    --titulo "Decreto 126 de 2010 - Por el cual se dictan disposiciones en materia de Inspección, Vigilancia y Control, de lucha contra la corrupción en el Sistema General de Seguridad Social en Salud, se adoptan medidas disciplinarias, penales y se dictan otras disposiciones" \
    --ramas "penal" --salida normativa/co-decreto-126-2010.md
gestor 95530 --id co:decreto:1144:2019 --tipo decreto --minimo 1 \
    --titulo "Decreto 1144 de 2019 - Por el cual se establece y regula el Sistema Específico de Carrera de los empleados públicos de la Unidad Administrativa Especial Dirección de Impuestos y Aduanas Nacionales, y se expiden normas relacionadas con la administración y gestión del talento humano de la DIAN" \
    --ramas "tributario" --salida normativa/co-decreto-1144-2019.md
gestor 14621 --id co:decreto:2637:2004 --tipo decreto --minimo 1 \
    --titulo "Decreto 2637 de 2004 - Por el cual se desarrolla el Acto Legislativo número 03 de 2002" \
    --ramas "constitucional,procesal,administrativo" --salida normativa/co-decreto-2637-2004.md
gestor 172994 --id co:decreto:1379:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1379 de 2021 - Por medio del cual se sustituye la Sección 10 del Capítulo 4 del Título 4 de la Parte 2 del Libro 2 del Decreto 1074 de 2015, Decreto Único Reglamentario del Sector Comercio, Industria y Turismo, para reglamentar el guionaje turístico y su ejercicio" \
    --ramas "comercial,societario,consumo,administrativo" --salida normativa/co-decreto-1379-2021.md
gestor 62883 --id co:decreto:1246:2015 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1246 de 2015 - Por el cual se adiciona el Decreto Único Reglamentario del Sector Educación para reglamentar los criterios para la asignación y distribución de los recursos para financiar las instituciones de educación superior públicas de que trata el artículo 24 de la Ley 1607 de 2012, modificado por el artículo […]" \
    --ramas "educacion,administrativo" --salida normativa/co-decreto-1246-2015.md
gestor 173829 --id co:decreto:1627:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1627 de 2021 - Por el cual se adiciona el Capítulo 45 al Título 10 de la Parte 2 del Libro 2 del Decreto 1833 del 10 de noviembre de 2016 en relación con las reglas para la asunción de la función pensional del liquidado Instituto Nacional de los Recursos Naturales Renovables y del Ambiente - INDERENA, por parte […]" \
    --ramas "seguridad-social,administrativo" --salida normativa/co-decreto-1627-2021.md
gestor 175288 --id co:decreto:1859:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1859 de 2021 - Por el cual se adiciona el Capítulo 46 al Título 10 de la Parte 2 del Libro 2 del Decreto 1833 del 10 de noviembre de 2016 en relación con las reglas para la asunción de la función pensional del liquidado Instituto de Mercadeo Agropecuario - IDEMA, por parte de la Unidad Administrativa Especial de […]" \
    --ramas "seguridad-social,administrativo" --salida normativa/co-decreto-1859-2021.md
gestor 175126 --id co:decreto:1786:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1786 de 2021 - Por medio del cual se modifica el Capítulo 6 del Título 7, Parte 2, Libro 2 del Decreto 1072 de 2015, Decreto Único Reglamentario del Sector Trabajo, que reglamenta el Fondo para la Atención Integral de la Niñez y Jornada Escolar Complementaria- (FONIÑEZ)" \
    --ramas "laboral,seguridad-social,administrativo" --salida normativa/co-decreto-1786-2021.md
gestor 65692 --id co:decreto:2297:2015 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 2297 de 2015 - Por el cual se modifica y adiciona el Capítulo 3, Título 1, Parte 2, Libro 2 del Decreto 1079 de 2015 , en relación con la prestación del servicio público de transporte terrestre automotor individual de pasajeros en los niveles básico y de lujo" \
    --ramas "transporte,administrativo" --salida normativa/co-decreto-2297-2015.md
gestor 73793 --id co:decreto:1216:2016 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1216 de 2016 - Por medio del cual se modifica el Decreto 1081 de 2015 - Decreto Reglamentario Único del Sector de la Presidencia de la República, en lo que hace referencia al Sistema Nacional de Derechos Humanos y Derecho Internacional Humanitario y la Comisión Intersectorial de Derechos Humanos y Derecho Internacional Humanitario" \
    --ramas "administrativo,constitucional" --salida normativa/co-decreto-1216-2016.md
gestor 126460 --id co:decreto:743:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 743 de 2020 - Por el cual se reglamentan el parágrafo 2 del artículo 257 y el parágrafo del artículo 357 del Estatuto Tributario y se adicionan y sustituyen artículos de los Capítulos 4 y 5 del Título 1 de la Parte 2 del Libro 1 del Decreto 1625 de 2016, Único Reglamentario en Materia Tributaria" \
    --ramas "tributario" --salida normativa/co-decreto-743-2020.md
gestor 173346 --id co:decreto:1437:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1437 de 2021 - Por el cual se modifican los artículos 2.6.4.2.1.2 , 2.6.4.2.1.3 , 2.6.4.2.1.4 , 2.6.4.2.1.5 , 2.6.4.2.1.26 , 2.6.4.2.2.1.3 , 2.6.4.3.1.1.1 , 2.6.4.3.1.1.4 , 2.6.4.3.1.1.5 , 2.6.4.3.1.1.6 , 2.6.4.3.5.1.3 , 2.6.4.3.5.1.7 del Decreto 780 de 2016 en el sentido de adoptar medidas para incrementar la […]" \
    --ramas "salud,seguridad-social,administrativo" --salida normativa/co-decreto-1437-2021.md
gestor 141984 --id co:decreto:1233:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1233 de 2020 - Por el cual se modifica el Decreto 1068 de 2015 Decreto Único Reglamentario del Sector Hacienda y Crédito Público, en lo relacionado con la cobertura del Programa FRECH NO VIS" \
    --ramas "tributario,financiero,administrativo" --salida normativa/co-decreto-1233-2020.md
gestor 80963 --id co:decreto:772:1975 --tipo decreto --minimo 1 \
    --titulo "Decreto 772 de 1975 - Por el cual se modifica el Decreto 2820 de 1974 y el Código Civil" \
    --ramas "civil,familia" --salida normativa/co-decreto-772-1975.md
gestor 155588 --id co:decreto:57:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 57 de 2021 - Por el cual se modifica y adiciona el capítulo 6 al título 1 de la parte 1 del libro 2 del Decreto 1077 de 2015 y se dictan otras disposiciones" \
    --ramas "urbanistico,servicios-publicos,administrativo" --salida normativa/co-decreto-57-2021.md
gestor 172457 --id co:decreto:1275:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1275 de 2021 - Por el cual se modifica parcialmente el Capítulo 4 , del Título 4, de la Parle 3, del Libro 2 del Decreto Único Reglamentario del Sector de Vivienda, Ciudad y Territorio, Decreto 1077 de 2015, en lo relacionado al Programa de Conexiones lntradomiciliarias - PCI de agua potable y saneamiento básico" \
    --ramas "urbanistico,servicios-publicos,administrativo" --salida normativa/co-decreto-1275-2021.md
gestor 150046 --id co:decreto:1623:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1623 de 2020 - Por el cual se introducen modificaciones al Capítulo 10 del Título 10 de la Parte 2 del Libro 2 del Decreto 1833 de 2016 en relación con las reglas para la asunción de la función pensional de la liquidada ÁLCALIS de Colombia Ltda. por parte de la Unidad Administrativa Especial de Gestión Pensional […]" \
    --ramas "seguridad-social,administrativo" --salida normativa/co-decreto-1623-2020.md
gestor 69035 --id co:decreto:582:2016 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 582 de 2016 - Por el cual se modifican los artículos 2.2.6.1.3.1. y 2.2.6.1.3.12. y se adicionan los artículos 2.2.6.1.3.18. a 2.2.6.1.3.26. al Decreto 1072 de 2015 para reglamentar parcialmente el artículo 77 de la Ley 1753 de 2015 y adoptar medidas para fortalecer el Mecanismo de Protección al Cesante en lo […]" \
    --ramas "laboral,seguridad-social,administrativo" --salida normativa/co-decreto-582-2016.md
gestor 30389 --id co:decreto:1717:2008 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1717 de 2008 - por el cual se modifica el Decreto 4299 de 2005 y se establecen otras disposiciones" \
    --ramas "minero-energetico,administrativo" --salida normativa/co-decreto-1717-2008.md
gestor 174175 --id co:decreto:1704:2021 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1704 de 2021 - Por el cual se adiciona el Capítulo 9 al Título II de la Parte 2 del Libro 2 al Decreto Único Reglamentario del Sector Administrativo de Minas y Energía, 1073 de 2015, en relación con la gestión de los recursos que las empresas públicas, mixtas o privadas decidan aportar para extender el uso del gas combustible" \
    --ramas "minero-energetico,administrativo" --salida normativa/co-decreto-1704-2021.md
gestor 51786 --id co:decreto:198:2013 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 198 de 2013 - Por el cual se suprimen, trasladan y reforman trámites en materia de tránsito y de transporte" \
    --ramas "transporte,administrativo" --salida normativa/co-decreto-198-2013.md
gestor 154206 --id co:decreto:1778:2020 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1778 de 2020 - Por el cual se adiciona el Capítulo 2 al Título 14 de la Parte 2 del Libro 2 del Decreto 1082 de 2015, Único Reglamentario del Sector Administrativo de Planeación Nacional y se modifica el Capítulo 7, del Título 1 de la Parte 1 del Libro 2 del Decreto 1081 de 2015, Reglamentario Único del Sector […]" \
    --ramas "administrativo,constitucional" --salida normativa/co-decreto-1778-2020.md
gestor 250176 --id co:decreto:1122:2024 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 1122 de 2024 - Por el cual se reglamenta el artículo 73 de la Ley 1474 de 2011, modificado por el artículo 31 de la Ley 2195 de 2022, en lo relacionado con los Programas de Transparencia y Ética Pública" \
    --ramas "administrativo,constitucional" --salida normativa/co-decreto-1122-2024.md
gestor 225690 --id co:decreto:2039:2023 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 2039 de 2023 - Por el cual se reglamenta el artículo 20-3 del Estatuto Tributario adicionado por el artículo 57 de la Ley 2277 de 2022, el inciso octavo y el parágrafo 2 del artículo 408 del Estatuto Tributario, adicionado por el artículo 61 de la Ley 2277 de 2022, y parcialmente el artículo 555-2 del Estatuto […]" \
    --ramas "tributario" --salida normativa/co-decreto-2039-2023.md
gestor 86303 --id co:decreto:762:2018 --tipo decreto --minimo 1 --enteros \
    --titulo "Decreto 762 de 2018 - Por el cual se adiciona un capítulo al Título 4 a la Parte 4, del Libro 2, del Decreto 1066 de 2015, Único Reglamentario del Sector Interior, para adoptar la Política Pública para la garantía del ejercicio efectivo de los derechos de las personas que hacen parte de los sectores sociales LGBTI y de […]" \
    --ramas "salud,seguridad-social,administrativo" --salida normativa/co-decreto-762-2018.md
gestor 77325 --id co:decreto:1671:1997 --tipo decreto --minimo 1 \
    --titulo "Decreto 1671 de 1997 - Por el cual se suprime la Corporación Nacional de Turismo de Colombia y se ordena su liquidación" \
    --ramas "comercial,administrativo" --salida normativa/co-decreto-1671-1997.md
gestor 86750 --id co:decreto:13:1967 --tipo decreto --minimo 1 \
    --titulo "Decreto 13 de 1967 - Por el cual se incorporan al Código Sustantivo del Trabajo las disposiciones de la Ley 73 de 1966" \
    --ramas "laboral,seguridad-social" --salida normativa/co-decreto-13-1967.md
gestor 14622 --id co:decreto:2636:2004 --tipo decreto --minimo 1 \
    --titulo "Decreto 2636 de 2004 - Por el cual se desarrolla el Acto Legislativo número 03 de 2002" \
    --ramas "penal,administrativo" --salida normativa/co-decreto-2636-2004.md
