#!/bin/bash
# Carga las normas especializadas de P2 que viven en secretariasenado.
# La fecha se lee del Diario Oficial en la propia fuente, salvo donde no aparece.
# --minimo aborta la escritura si la descarga quedó corta (ver cargar_p1.sh).
cd "$(dirname "$0")" || exit 1
B=http://www.secretariasenado.gov.co/senado/basedoc

run() { echo "== $1"; python3 ingesta_senado.py "$B/$1.html" "${@:2}" 2>&1 \
    | grep -E "artículos ->|aristas ->|sin ancla|no reconocidas|ABORTA|fecha"; }

run ley_1563_2012 --minimo 100 --id co:ley:1563:2012 --tipo ley \
    --titulo "Ley 1563 de 2012 - Estatuto de Arbitraje Nacional e Internacional" \
    --ramas "arbitraje, procesal, comercial" --salida normativa/co-ley-1563-2012.md

run ley_2136_2021 --minimo 60 --id co:ley:2136:2021 --tipo ley \
    --titulo "Ley 2136 de 2021 - Política Integral Migratoria" \
    --ramas "migratorio, internacional-publico" --salida normativa/co-ley-2136-2021.md

run ley_0100_1993 --minimo 240 --id co:ley:100:1993 --tipo ley \
    --titulo "Ley 100 de 1993 - Sistema de Seguridad Social Integral" \
    --ramas "seguridad-social, salud, laboral" --salida normativa/co-ley-100-1993.md

run ley_0080_1993 --minimo 60 --id co:ley:80:1993 --tipo ley \
    --titulo "Ley 80 de 1993 - Estatuto General de Contratación de la Administración Pública" \
    --ramas "contratacion-estatal, administrativo" --salida normativa/co-ley-80-1993.md

run ley_1150_2007 --minimo 25 --id co:ley:1150:2007 --tipo ley \
    --titulo "Ley 1150 de 2007 - Medidas de eficiencia y transparencia en la contratación estatal" \
    --ramas "contratacion-estatal, administrativo" --salida normativa/co-ley-1150-2007.md

run ley_1116_2006 --minimo 100 --id co:ley:1116:2006 --tipo ley \
    --titulo "Ley 1116 de 2006 - Régimen de Insolvencia Empresarial" \
    --ramas "insolvencia, comercial" --salida normativa/co-ley-1116-2006.md

run ley_1098_2006 --minimo 180 --id co:ley:1098:2006 --tipo ley \
    --titulo "Ley 1098 de 2006 - Código de la Infancia y la Adolescencia" --corto "CIA" \
    --ramas "familia" --salida normativa/co-ley-1098-2006.md

# El Estatuto Tributario no trae la línea del Diario Oficial: la fecha va explícita.
run estatuto_tributario --minimo 700 --id co:decreto:624:1989 --tipo decreto \
    --titulo "Decreto 624 de 1989 - Estatuto Tributario" --corto "ET" --fecha 1989-03-30 \
    --ramas "tributario" --salida normativa/co-decreto-624-1989.md

run ley_1581_2012 --minimo 20 --id co:ley-estatutaria:1581:2012 --tipo ley-estatutaria \
    --titulo "Ley 1581 de 2012 - Protección de Datos Personales" \
    --ramas "datos-personales, constitucional" --salida normativa/co-ley-estatutaria-1581-2012.md

run ley_1801_2016 --minimo 200 --id co:ley:1801:2016 --tipo ley \
    --titulo "Ley 1801 de 2016 - Código Nacional de Seguridad y Convivencia Ciudadana" \
    --ramas "policivo, administrativo" --salida normativa/co-ley-1801-2016.md

run ley_0099_1993 --minimo 95 --id co:ley:99:1993 --tipo ley \
    --titulo "Ley 99 de 1993 - Sistema Nacional Ambiental" \
    --ramas "ambiental, administrativo" --salida normativa/co-ley-99-1993.md

run ley_1480_2011 --minimo 65 --id co:ley:1480:2011 --tipo ley \
    --titulo "Ley 1480 de 2011 - Estatuto del Consumidor" \
    --ramas "consumo, comercial" --salida normativa/co-ley-1480-2011.md

run ley_1952_2019 --minimo 200 --id co:ley:1952:2019 --tipo ley \
    --titulo "Ley 1952 de 2019 - Código General Disciplinario" \
    --ramas "disciplinario, administrativo" --salida normativa/co-ley-1952-2019.md

run ley_0769_2002 --minimo 130 --id co:ley:769:2002 --tipo ley \
    --titulo "Ley 769 de 2002 - Código Nacional de Tránsito Terrestre" \
    --ramas "transporte, policivo" --salida normativa/co-ley-769-2002.md

echo "== reconstruyendo"
python3 build.py && python3 export.py
