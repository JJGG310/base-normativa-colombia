#!/bin/bash
# P3: lo que faltaba después de los códigos (P1) y las 14 especializadas (P2).
# Mismo mecanismo que cargar_p2.sh: senado + --minimo como red contra el truncamiento.
# Los --minimo son cotas inferiores prudentes, no el conteo real de la norma:
# solo existen para que una descarga corta no se escriba en silencio.
cd "$(dirname "$0")" || exit 1
B=http://www.secretariasenado.gov.co/senado/basedoc

run() { echo "== $1"; python3 ingesta_senado.py "$B/$1.html" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|sin ancla|no reconocidas|ABORTA|fecha|Error|error"; }

# --- A. Procesal constitucional y troncal administrativo -----------------------
run decreto_2591_1991 --minimo 40 --id co:decreto:2591:1991 --tipo decreto \
    --titulo "Decreto 2591 de 1991 - Acción de tutela" --corto "D. Tutela" \
    --ramas "constitucional, procesal" --salida normativa/co-decreto-2591-1991.md

run ley_0472_1998 --minimo 60 --id co:ley:472:1998 --tipo ley \
    --titulo "Ley 472 de 1998 - Acciones populares y de grupo" \
    --ramas "constitucional, procesal, ambiental, consumo" --salida normativa/co-ley-472-1998.md

run ley_0393_1997 --minimo 20 --id co:ley:393:1997 --tipo ley \
    --titulo "Ley 393 de 1997 - Acción de cumplimiento" \
    --ramas "constitucional, procesal, administrativo" --salida normativa/co-ley-393-1997.md

run ley_0270_1996 --minimo 120 --id co:ley-estatutaria:270:1996 --tipo ley-estatutaria \
    --titulo "Ley 270 de 1996 - Estatutaria de la Administración de Justicia" \
    --ramas "constitucional, procesal, administrativo" --salida normativa/co-ley-estatutaria-270-1996.md

run ley_0600_2000 --minimo 380 --id co:ley:600:2000 --tipo ley \
    --titulo "Ley 600 de 2000 - Código de Procedimiento Penal (Ley 600)" --corto "CPP/600" \
    --ramas "penal, procesal" --salida normativa/co-ley-600-2000.md

run ley_1708_2014 --minimo 150 --id co:ley:1708:2014 --tipo ley \
    --titulo "Ley 1708 de 2014 - Código de Extinción de Dominio" --corto "CED" \
    --ramas "penal, procesal, civil" --salida normativa/co-ley-1708-2014.md

run ley_2213_2022 --minimo 10 --id co:ley:2213:2022 --tipo ley \
    --titulo "Ley 2213 de 2022 - Uso de las TIC en las actuaciones judiciales" \
    --ramas "procesal, administrativo" --salida normativa/co-ley-2213-2022.md

run ley_0489_1998 --minimo 90 --id co:ley:489:1998 --tipo ley \
    --titulo "Ley 489 de 1998 - Organización y funcionamiento de la Administración Pública" \
    --ramas "administrativo" --salida normativa/co-ley-489-1998.md

run ley_0909_2004 --minimo 45 --id co:ley:909:2004 --tipo ley \
    --titulo "Ley 909 de 2004 - Empleo público, carrera administrativa y gerencia pública" \
    --ramas "administrativo, laboral" --salida normativa/co-ley-909-2004.md

run ley_1474_2011 --minimo 90 --id co:ley:1474:2011 --tipo ley \
    --titulo "Ley 1474 de 2011 - Estatuto Anticorrupción" \
    --ramas "administrativo, penal, disciplinario, contratacion-estatal" \
    --salida normativa/co-ley-1474-2011.md

run ley_1712_2014 --minimo 25 --id co:ley-estatutaria:1712:2014 --tipo ley-estatutaria \
    --titulo "Ley 1712 de 2014 - Transparencia y acceso a la información pública" \
    --ramas "administrativo, constitucional" --salida normativa/co-ley-estatutaria-1712-2014.md

run ley_0005_1992 --minimo 280 --id co:ley:5:1992 --tipo ley \
    --titulo "Ley 5 de 1992 - Reglamento del Congreso" \
    --ramas "constitucional, administrativo" --salida normativa/co-ley-5-1992.md

# --- B. Civil, societario, laboral y consumo ----------------------------------
run ley_0222_1995 --minimo 150 --id co:ley:222:1995 --tipo ley \
    --titulo "Ley 222 de 1995 - Reforma al régimen de sociedades" \
    --ramas "comercial, societario, insolvencia" --salida normativa/co-ley-222-1995.md

run ley_1258_2008 --minimo 30 --id co:ley:1258:2008 --tipo ley \
    --titulo "Ley 1258 de 2008 - Sociedad por Acciones Simplificada" --corto "SAS" \
    --ramas "comercial, societario" --salida normativa/co-ley-1258-2008.md

run ley_1010_2006 --minimo 12 --id co:ley:1010:2006 --tipo ley \
    --titulo "Ley 1010 de 2006 - Acoso laboral" \
    --ramas "laboral" --salida normativa/co-ley-1010-2006.md

run ley_0776_2002 --minimo 15 --id co:ley:776:2002 --tipo ley \
    --titulo "Ley 776 de 2002 - Prestaciones del Sistema General de Riesgos Profesionales" \
    --ramas "laboral, seguridad-social" --salida normativa/co-ley-776-2002.md

run ley_1562_2012 --minimo 20 --id co:ley:1562:2012 --tipo ley \
    --titulo "Ley 1562 de 2012 - Sistema General de Riesgos Laborales" \
    --ramas "laboral, seguridad-social" --salida normativa/co-ley-1562-2012.md

run ley_0797_2003 --minimo 15 --id co:ley:797:2003 --tipo ley \
    --titulo "Ley 797 de 2003 - Reforma al Sistema General de Pensiones" \
    --ramas "seguridad-social, laboral" --salida normativa/co-ley-797-2003.md

run ley_1996_2019 --minimo 40 --id co:ley:1996:2019 --tipo ley \
    --titulo "Ley 1996 de 2019 - Capacidad legal de las personas con discapacidad" \
    --ramas "civil, familia" --salida normativa/co-ley-1996-2019.md

run decreto_1260_1970 --minimo 80 --id co:decreto:1260:1970 --tipo decreto \
    --titulo "Decreto 1260 de 1970 - Estatuto del Registro del Estado Civil" \
    --ramas "civil, familia, notarial-registral" --salida normativa/co-decreto-1260-1970.md

run ley_1257_2008 --minimo 25 --id co:ley:1257:2008 --tipo ley \
    --titulo "Ley 1257 de 2008 - Violencia y discriminación contra las mujeres" \
    --ramas "familia, penal, constitucional" --salida normativa/co-ley-1257-2008.md

run ley_1123_2007 --minimo 80 --id co:ley:1123:2007 --tipo ley \
    --titulo "Ley 1123 de 2007 - Código Disciplinario del Abogado" \
    --ramas "disciplinario, procesal" --salida normativa/co-ley-1123-2007.md

run ley_1266_2008 --minimo 15 --id co:ley-estatutaria:1266:2008 --tipo ley-estatutaria \
    --titulo "Ley 1266 de 2008 - Habeas data financiero" \
    --ramas "datos-personales, comercial, constitucional" --salida normativa/co-ley-estatutaria-1266-2008.md

run ley_1915_2018 --minimo 25 --id co:ley:1915:2018 --tipo ley \
    --titulo "Ley 1915 de 2018 - Derecho de autor y derechos conexos" \
    --ramas "propiedad-intelectual, comercial" --salida normativa/co-ley-1915-2018.md

# --- C. Territorial, ambiental, electoral y víctimas ---------------------------
run ley_0388_1997 --minimo 100 --id co:ley:388:1997 --tipo ley \
    --titulo "Ley 388 de 1997 - Desarrollo territorial y ordenamiento urbano" \
    --ramas "urbanistico, administrativo, civil" --salida normativa/co-ley-388-1997.md

run ley_0160_1994 --minimo 80 --id co:ley:160:1994 --tipo ley \
    --titulo "Ley 160 de 1994 - Sistema Nacional de Reforma Agraria" \
    --ramas "agrario, administrativo, civil" --salida normativa/co-ley-160-1994.md

run decreto_2811_1974 --minimo 250 --id co:decreto-ley:2811:1974 --tipo decreto-ley \
    --titulo "Decreto Ley 2811 de 1974 - Código Nacional de Recursos Naturales Renovables" \
    --corto "CNRN" --ramas "ambiental, administrativo" --salida normativa/co-decreto-ley-2811-1974.md

run ley_1448_2011 --minimo 150 --id co:ley:1448:2011 --tipo ley \
    --titulo "Ley 1448 de 2011 - Víctimas y restitución de tierras" \
    --ramas "victimas, agrario, procesal, constitucional" --salida normativa/co-ley-1448-2011.md

run decreto_2241_1986 --minimo 180 --id co:decreto:2241:1986 --tipo decreto \
    --titulo "Decreto 2241 de 1986 - Código Electoral" \
    --ramas "electoral, administrativo" --salida normativa/co-decreto-2241-1986.md

run ley_1475_2011 --minimo 25 --id co:ley:1475:2011 --tipo ley \
    --titulo "Ley 1475 de 2011 - Organización y funcionamiento de los partidos políticos" \
    --ramas "electoral, constitucional" --salida normativa/co-ley-1475-2011.md

run ley_0136_1994 --minimo 120 --id co:ley:136:1994 --tipo ley \
    --titulo "Ley 136 de 1994 - Organización y funcionamiento de los municipios" \
    --ramas "territorial, administrativo" --salida normativa/co-ley-136-1994.md

run ley_1551_2012 --minimo 30 --id co:ley:1551:2012 --tipo ley \
    --titulo "Ley 1551 de 2012 - Modernización de la organización de los municipios" \
    --ramas "territorial, administrativo" --salida normativa/co-ley-1551-2012.md

run decreto_1421_1993 --minimo 120 --id co:decreto-ley:1421:1993 --tipo decreto-ley \
    --titulo "Decreto Ley 1421 de 1993 - Estatuto Orgánico de Bogotá" \
    --ramas "territorial, administrativo" --salida normativa/co-decreto-ley-1421-1993.md

run ley_0142_1994 --minimo 140 --id co:ley:142:1994 --tipo ley \
    --titulo "Ley 142 de 1994 - Régimen de los servicios públicos domiciliarios" \
    --ramas "servicios-publicos, administrativo" --salida normativa/co-ley-142-1994.md
