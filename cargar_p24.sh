#!/bin/bash
# P24: leyes origen que senado no tiene (las 37 «sin fuente en senado» de origenes_revisar.txt),
# desde las fuentes admitidas en esquema.md §8: normogramas Avance Jurídico de otras entidades
# (Cancillería, Colpensiones, CREG, SENA), Gestor de Función Pública y SUIN vía archive.org.
# Título = «Ley N de AAAA - <epígrafe de la fuente>»; ramas = las dos más comunes entre las normas
# que la ley afecta (cargar_origenes.ramas); fecha = Diario Oficial de la fuente. Cada carga pasa por
# verificar.py (sin «faltan 0» no se da por cargada). Un normograma puede traer solo una parte de
# la ley (Colpensiones corta las leyes largas: Ley 100/1892 tiene 88 artículos en Cancillería y 49
# en Colpensiones): se usa la fuente que trae la firma de cierre y más artículos.
cd "$(dirname "$0")" || exit 1
CREG=https://gestornormativo.creg.gov.co/gestor/entorno/docs
CAN=https://www.cancilleria.gov.co/sites/default/files/Normograma/docs
COL=https://normativa.colpensiones.gov.co/colpens/docs
JEP=https://jurinfo.jep.gov.co/normograma/compilacion/docs
SENA=https://normograma.sena.edu.co/compilacion/docs
# recortar <n> <año> <última línea del texto de la ley>: quita lo que sigue (pie del sitio, en las páginas
# de CREG y de la JEP, que no traen «Fin documento»). Sobra si ingesta_senado.procesar corta ahí.
recortar() {
    python3 - "normativa/co-ley-$1-$2.md" "$3" <<'EOF'
import sys
p, fin = sys.argv[1:]
t = open(p, encoding="utf-8").read()
i = t.rfind(fin)
assert i > 0
open(p, "w", encoding="utf-8").write(t[:i + len(fin)] + "\n")
EOF
}
# run <url> <n> <año> <ramas> <estado> <mínimo> <epígrafe>
run() {
    echo "== Ley $2 de $3"
    python3 ingesta_senado.py "$1" --minimo "$6" --id co:ley:$2:$3 --tipo ley --estado "$5" \
        --titulo "Ley $2 de $3 - $7" --ramas "$4" --salida normativa/co-ley-$2-$3.md 2>&1 \
        | grep -E "artículos ->|aristas ->|ABORTA|Error|no reconocidas|sin ancla"
    python3 verificar.py normativa/co-ley-$2-$3.md | head -1
    sleep 3
}

run $CAN/ley_0100_1892.htm 100 1892 "civil, constitucional" vigente 80 "Sobre reformas judiciales"
run $CAN/ley_0075_1968.htm 75 1968 "civil, familia" vigente 60 "Por la cual se dictan normas sobre filiación y se crea el Instituto Colombiano de Bienestar Familiar"
run $CREG/ley_0130_1913.htm 130 1913 "constitucional" vigente 100 "sobre la Jurisdicción de lo contencioso-Administrativo"
run $SENA/ley_0188_1959.htm 188 1959 "laboral, seguridad-social" vigente 10 "Por la cual se regula el contrato de aprendizaje"
# Nota de encabezado: «Ley derogada por el artículo 123 del Decreto 1260 de 1970» -> estado derogada
# y arista manual a nivel de norma (ver el final de este script).
run $CAN/ley_0092_1938.htm 92 1938 "civil, familia" derogada 25 "por la cual se dictan algunas disposiciones sobre registro civil y cementerios"
# JEP trae la jurisprudencia más reciente (SU-138/2021, T-301/2018…): 7 aristas frente a 2 en Colpensiones.
run $JEP/ley_0171_1961.htm 171 1961 "laboral, seguridad-social" vigente 15 "Por la cual se reforma la Ley 77 de 1959 y se dictan otras Disposiciones sobre pensiones"
recortar 171 1961 "El Ministro de Hacienda y Crédito Público"   # pie del portal de la JEP
run $COL/ley_0050_1936.htm 50 1936 "civil, familia" vigente 2 "Sobre prescripciones y nulidades civiles"
run $COL/ley_0095_1890.htm 95 1890 "civil, familia" vigente 40 "Sobre reformas civiles"
run $CAN/ley_0104_1922.htm 104 1922 "civil, constitucional" vigente 40 "sobre reformas judiciales"
run $COL/ley_0067_1930.htm 67 1930 "civil, familia" vigente 3 "Sobre reformas al Código Civil"
run $CREG/ley_0084_1915.htm 84 1915 "constitucional" vigente 7 "por la cual se reforman y adicionan las Leyes 4 y 97 de 1913"
recortar 84 1915 "MIGUEL ABADIA MÉNDEZ"   # pie de CREG (Volver arriba, teléfonos…); Ley 57/1887 art. 338 igual
run $CAN/ley_0048_1968.htm 48 1968 "laboral, seguridad-social" vigente 6 "Por la cual se adopta como legislación permanente algunos decretos legislativos, se otorgan facultades al Presidente de la República y a las Asambleas, se introducen reformas al Código Sustantivo del trabajo y se dictan otras disposiciones"
run $COL/ley_0027_1974.htm 27 1974 "laboral, seguridad-social" vigente 12 "Por la cual se dictan normas sobre la creación y sostenimiento de Centros de atención integral al Pre-escolar, para los hijos de empleados y trabajadores de los sectores públicos y privados"
run $COL/ley_0001_1976.htm 1 1976 "civil, familia" vigente 30 "Por la cual se establece el divorcio en el matrimonio civil, se regulan la separación de cuerpos y de bienes en el matrimonio civil y en el canónico, y se modifican algunas disposiciones de los Códigos Civil y de Procedimiento Civil en materia de Derecho de Familia"
run $COL/ley_0165_1941.htm 165 1941 "civil, familia" vigente 6 "Sobre protección del salario"
run $CAN/ley_0118_1931.htm 118 1931 "civil, constitucional" vigente 14 "Por la cual se prorroga el término indicado en el artículo 2º de la Ley 11 de 1931 y se dictan algunas disposiciones sobre reformas judiciales"
run $COL/ley_0008_1922.htm 8 1922 "civil, familia" vigente 6 "Por la cual se adiciona el Código Civil"
run $SENA/ley_0075_1986.htm 75 1986 "laboral, seguridad-social" vigente 100 "Por la cual se expiden normas en materia tributaria de catastro, de fortalecimiento y democratización del mercado de capitales, se conceden unas facultades extraordinarias y se dictan otras disposiciones"
run $COL/ley_0057_1990.htm 57 1990 "civil, constitucional" vigente 2 "Por medio de la cual se modifica el artículo 11 de la Ley 57 de 1887"
# Nota de encabezado: «Ley derogada por el artículo 3 de la Ley 2129 de 2021» -> estado derogada + arista manual.
run $CAN/ley_0054_1989.htm 54 1989 "civil, familia" derogada 2 "Por medio de la cual se reforma el artículo 53 del Decreto 1260 de 1970"
run $CAN/ley_0051_1983.htm 51 1983 "laboral, seguridad-social" vigente 4 "Por la cual se traslada el descanso remunerado de algunos días festivos"
run $COL/ley_0045_1930.htm 45 1930 "civil, familia" vigente 2 "Por la cual se reforma el Código Civil (pactum reservati dominii)"
run $CAN/ley_0040_1907.htm 40 1907 "civil, constitucional" vigente 170 "Sobre reformas judiciales"
run $COL/ley_0038_1945.htm 38 1945 "civil, constitucional" vigente 2 "Por la cual se adicionan y modifican los artículos 740 de la Ley 105 de 1931 y 42 de la Ley 57 de 1887"
run $COL/ley_0036_1931.htm 36 1931 "civil, familia" vigente 7 "Sobre Reformas Civiles y Judiciales"
run $CREG/ley_0010_1990.htm 10 1990 "tributario" vigente 50 "Por la cual se reorganiza el Sistema Nacional de Salud y se dictan otras disposiciones"
run $CAN/ley_0078_1931.htm 78 1931 "constitucional" vigente 3 "En desarrollo del artículo 64 de la Constitución"
# Ley 73/1988: solo la trae el normograma de la JEP, que marca los artículos como
# `<a name="1"></a><span class="bookmarkaj">ARTICULO 1o.</span>` y ANCLA de ingesta_senado no lo lee (0 artículos).
# Se cargó con este reemplazo aplicado en memoria a `paginas()` (y a verificar.py); mientras ingesta_senado no lo
# incorpore, esta línea aborta con «no se extrajo ningún artículo» sin tocar el archivo:
#   doc = re.sub(r'<a name="([^"]+)"></a>\s*<span class="bookmarkaj">(.*?)</span>', r'<a class="bookmarkaj" name="\1">\2</a>', doc, flags=re.S)
run $JEP/ley_0073_1988.htm 73 1988 "salud, ambiental" vigente 9 "Por la cual se adiciona la Ley 09 de 1979 y se dictan otras disposiciones en materia de donación y trasplante de órganos y componentes anatómicos para fines de transplantes u otros usos terapéuticos"

# Gestor de Función Pública (ingesta_gestor.py). Las notas «Derogado por la Ley 6a.de 1928, Artículo 11»,
# «Modificado por el Artículo 8 de la Ley 62 de 1939» y «Modificado por la Ley 14 de 1969» (Ley 71/1916
# arts. 3, 7 y 8) no las reconoce RE_AFECTA («de la Ley», «6a.de»): aristas manuales al final.
echo "== Ley 71 de 1916"
python3 ingesta_gestor.py 8322 --id co:ley:71:1916 --tipo ley --enteros --minimo 5 \
    --titulo "Ley 71 de 1916 - Por la cual se adiciona y reforma la ley 4a. de 1913" \
    --ramas "constitucional" --salida normativa/co-ley-71-1916.md 2>&1 | grep -E "artículos ->|aristas ->|ABORTA|Error|no reconocidas"
python3 verificar.py normativa/co-ley-71-1916.md | head -1; sleep 3
echo "== Ley 84 de 1989"
python3 ingesta_gestor.py 8242 --id co:ley:84:1989 --tipo ley --enteros --minimo 40 --fecha 1989-12-27 \
    --titulo "Ley 84 de 1989 - Por la cual se adopta el Estatuto Nacional de Protección de los Animales y se crean unas contravenciones y se regula lo referente a su procedimiento y competencia" \
    --ramas "civil, familia" --salida normativa/co-ley-84-1989.md 2>&1 | grep -E "artículos ->|aristas ->|ABORTA|Error|no reconocidas"
python3 verificar.py normativa/co-ley-84-1989.md | head -1; sleep 3

# SUIN-Juriscol vía archive.org (fuente 10; `verificado` = fecha de la captura). Fecha = publicación en el Diario Oficial.
echo "== Ley 89 de 1936"
python3 ingesta_suin.py 1630543 --id co:ley:89:1936 --tipo ley --fecha 1936-06-10 --minimo 5 \
    --titulo "Ley 89 de 1936 - Por la cual se hacen extensivas a algunos Municipios del país las facultades concedidas en la Ley 72 de 1926 y se dictan otras disposiciones sobre régimen municipal" \
    --ramas "constitucional" --salida normativa/co-ley-89-1936.md
python3 verificar.py normativa/co-ley-89-1936.md | head -1

# El id 1592912 salió del enlace «Artículo 3 LEY 37 de 1935» de la captura SUIN de la Ley 4/1913; el encabezado coincide.
# SUIN anota «Derogada orgánicamente mediante la Ley 91 de 1989» (derogación tácita: sin arista) con «ESTADO DE VIGENCIA: Vigente».
echo "== Ley 37 de 1935"
python3 ingesta_suin.py 1592912 --id co:ley:37:1935 --tipo ley --fecha 1935-11-12 --minimo 3 \
    --titulo "Ley 37 de 1935 - Por la cual se dan unas normas sobre la carrera del Magisterio y se reforma el numeral 24 del artículo 127 de la Ley 4ª de 1913" \
    --ramas "constitucional" --salida normativa/co-ley-37-1935.md
python3 verificar.py normativa/co-ley-37-1935.md | head -1

# SISJUR — Alcaldía de Bogotá (fuente 11; ingesta_suin.py sisjur:<i>): página viva, `verificado` = hoy.
# verificar.py no cubre SISJUR (2 «Artículo N» en la fuente, 2 en el .md: contrastado a mano).
echo "== Ley 24 de 1986"
python3 ingesta_suin.py sisjur:106625 --id co:ley:24:1986 --tipo ley --fecha 1986-01-28 --minimo 2 \
    --titulo "Ley 24 de 1986 - Por la cual se adiciona el artículo 236 del Capítulo V del Código Sustantivo del Trabajo" \
    --ramas "laboral, seguridad-social" --salida normativa/co-ley-24-1986.md

# Aristas manuales (anadir_aristas.py del orquestador; nota «manual:» -> sobreviven a re-ingestas):
#   co:decreto:1260:1970:art:123 deroga co:ley:92:1938        (encabezado de la fuente, Cancillería)
#   co:ley:2129:2021:art:4       deroga co:ley:54:1989        (encabezado de la fuente, Cancillería, que cita el art. 3; el texto cargado de la 2129 la deroga en el 4)
#   co:ley:6:1928:art:11  deroga  co:ley:71:1916:art:3        (Gestor: «Derogado por la Ley 6a.de 1928, Artículo 11.»)
#   co:ley:62:1939:art:8  modifica co:ley:71:1916:art:7       (Gestor)
#   co:ley:14:1969        modifica co:ley:71:1916:art:8       (Gestor)
