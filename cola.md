# Cola de ingesta

Estado del proyecto y del loop. Se lee al abrir cada tick y se actualiza al cerrarlo.

`[ ]` pendiente · `[~]` en curso · `[x]` hecho · `[!]` bloqueado (con motivo al lado)

Los conteos de artículos llevan `~` porque son estimados **solo para decidir si una
norma se parte en bloques**. No son dato: el número real se toma de la fuente.

---

## Procedimiento de cada tick

Una entrada por tick. Nunca dos. Un tick que abarca de más se queda a medias y deja
basura a medio escribir que el siguiente tick no sabe interpretar.

1. **Abrir `cola.md`.** Si hay una entrada `[~]`, esa es la del tick (quedó a medias);
   si no, la primera `[ ]` de la prioridad más alta.
2. **Marcarla `[~]` y guardar `cola.md` ya**, antes de trabajar. Si el tick muere,
   el siguiente sabe dónde quedó.
3. **El texto se extrae con script, nunca copiándolo a través del modelo.**
   Para secretariasenado.gov.co ya está `ingesta_senado.py` y sirve para todos los
   códigos de P1. Para una fuente nueva se escribe su parser una vez. Esto no es
   optimización: un script no puede inventar un artículo, un modelo transcribiendo sí.
   Como la extracción es mecánica, **no hay que partir las normas grandes en bloques**
   — el Código Civil entero cuesta lo mismo que un artículo. Partir solo aplica si
   alguna fuente obliga a transcripción manual.
4. **Obtener el texto de la fuente oficial** (`esquema.md` §8, en ese orden de
   preferencia). Si la primera fuente falla, se intenta la siguiente. Si fallan todas:
   `[!]` con el motivo y la URL que falló, y se pasa a la siguiente entrada.
   **Jamás se rellena con el texto que el modelo recuerda.**
5. **Verificar la extracción antes de darla por buena**: contar artículos contra el
   número conocido de la norma, y revisar 3 artículos sueltos (uno del principio, uno
   del medio, uno del final) contra la fuente. Un parser que se come el 20% de los
   artículos no falla ruidosamente, entrega un archivo que parece correcto.
6. **Extraer las afectaciones** que traiga la fuente (notas de vigencia, "modificado
   por", "derogado por", "declarado inexequible por") y agregarlas a `relaciones.csv`.
   SUIN-Juriscol es la mejor fuente para esto. Solo lo que la fuente afirme: no se
   deduce una derogatoria.
7. **`python3 build.py && python3 export.py`.** Si imprimen avisos o fallan, se
   corrige antes de cerrar. `contexto.jsonl` es el entregable: si no se regenera,
   el tick no sirvió de nada.
8. **Marcar `[x]`**, commit con el ID de lo cargado en el mensaje.
9. Si no quedan `[ ]` en P1, **detener el loop** y reportar. Si quedan, siguiente tick.

**Regla de oro:** ante la duda entre cargar algo incompleto o no cargarlo, no se carga
y se anota qué faltó. La base vale por lo que se puede confiar, no por lo que pesa.

---

## P1 — Troncales

Los siete códigos que cubren el grueso de las consultas, intercalados con la
jurisprudencia hito que los interpreta.

- [x] `co:constitucion:1991` — Constitución Política · **texto cargado**: 380 arts + 78 transitorios (incluidos los de los AL 02/2017 y 02/2021). `afectaciones: pendiente`
- [x] `co:constitucion:1991` — **afectaciones cargadas**: 6.516 aristas, 60 Actos Legislativos, 20 artículos muertos, 4 condicionados. Fuente resuelta: las notas viven en `js/<pagina>.js` (funciones `insRowNN`), no en el HTML. `ingesta_senado.py` ya las extrae para cualquier código de esta fuente.
- [ ] jurisprudencia constitucional — 15 sentencias hito de control de constitucionalidad y bloque de constitucionalidad
- [x] `co:ley:1564:2012` — CGP: 628 arts, 133 aristas, 6 muertos (art. 121 por C-443-19), 6 condicionados, reformas hasta 2025
- [ ] jurisprudencia procesal — 15 hito sobre CGP (competencia, nulidades, pruebas, recursos)
- [ ] `co:ley:84:1873` — Código Civil (~2684) · civil, familia
- [ ] jurisprudencia civil — 15 hito (contratos, responsabilidad, bienes, obligaciones)
- [ ] jurisprudencia familia — 15 hito (custodia, alimentos, unión marital, filiación, adopción)
- [ ] `co:ley:599:2000` — Código Penal (~476) · penal
- [ ] `co:ley:906:2004` — Código de Procedimiento Penal (~533) · penal, procesal
- [ ] jurisprudencia penal — 15 hito (dolo, tipicidad, garantías, prueba ilícita)
- [ ] `co:decreto:410:1971` — Código de Comercio (~2036) · comercial
- [ ] jurisprudencia comercial — 15 hito (sociedades, títulos valores, competencia desleal)
- [ ] `co:ley:1437:2011` — CPACA, con reforma Ley 2080/2021 (~309) · administrativo, contencioso-administrativo
- [ ] jurisprudencia contencioso-administrativa — 15 hito del Consejo de Estado (nulidad, reparación directa, medio de control contractual)
- [ ] `co:decreto-ley:2663:1950` — Código Sustantivo del Trabajo (~492) · laboral
- [ ] jurisprudencia laboral — 15 hito (contrato realidad, estabilidad reforzada, acoso)

## P2 — Especializadas

- [ ] `co:ley:1563:2012` — Estatuto de Arbitraje Nacional e Internacional (~119) · arbitraje
- [ ] `co:ley:2136:2021` — Política Integral Migratoria (~100) · migratorio
- [ ] `co:decreto:1067:2015` — Decreto Único Reglamentario Relaciones Exteriores · migratorio, internacional-publico
- [ ] `co:ley:100:1993` — Sistema de Seguridad Social Integral (~289) · seguridad-social, salud
- [ ] `co:ley:80:1993` + `co:ley:1150:2007` — Contratación Estatal · contratacion-estatal
- [ ] `co:ley:1116:2006` — Régimen de Insolvencia Empresarial (~126) · insolvencia, comercial
- [ ] `co:ley:1098:2006` — Infancia y Adolescencia (~217) · familia
- [ ] `co:decreto:624:1989` — Estatuto Tributario · tributario
- [ ] `co:ley:1581:2012` + `co:decreto:1377:2013` — Datos personales · datos-personales
- [ ] `co:ley:1801:2016` — Código Nacional de Seguridad y Convivencia (~243) · policivo
- [ ] `co:ley:99:1993` — Sistema Nacional Ambiental (~118) · ambiental
- [ ] `co:ley:1480:2011` — Estatuto del Consumidor (~84) · consumo
- [ ] `co:ley:1952:2019` — Código General Disciplinario · disciplinario
- [ ] `co:ley:769:2002` — Código Nacional de Tránsito · transporte
- [ ] `co:decreto:1165:2019` — Regulación Aduanera · aduanero

## Pendientes de la fuente senado (no bloquean, mejoran)

- [ ] `concordancias` (713 cajas en la Constitución): remisiones normativa↔normativa. No afectan vigencia, sí navegación.
- [ ] tipo de relación `renumera`: el AL 2/2015 renumeró artículos (el 262 pasó a 261). Hoy se ignora; el artículo viejo y el nuevo quedan sin enlazar.
- [ ] SUIN-Juriscol sigue caído por `curl` (bloqueo de bot, no TLS). Sirve como segunda fuente para cotejar afectaciones.

## P3 — Por definir

Se llena cuando P1 esté cerrado y se vea qué falta de verdad al usar la base.
Candidatos: internacional privado, propiedad intelectual (Decisión 486 CAN),
minero-energético, urbanístico (Ley 388/1997), electoral, agrario (Ley 160/1994).

---

## Bloqueados

_(vacío — aquí van las `[!]` con motivo, URL que falló y fecha)_
