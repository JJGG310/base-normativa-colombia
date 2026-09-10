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
3. **Si la norma supera ~150 artículos**, no se carga entera: se reemplaza la entrada
   por sub-entradas por libro/título/parte con el conteo real de la fuente, se marca
   la primera `[~]` y se trabaja solo esa.
4. **Obtener el texto de la fuente oficial** (`esquema.md` §8, en ese orden de
   preferencia). Si la primera fuente falla, se intenta la siguiente. Si fallan todas:
   `[!]` con el motivo y la URL que falló, y se pasa a la siguiente entrada.
   **Jamás se rellena con el texto que el modelo recuerda.**
5. **Escribir el `.md`** con el formato de `esquema.md` §3 (normativa) o §4
   (jurisprudencia). Texto literal de la fuente. `fuente:` es la URL exacta usada,
   `verificado:` la fecha de hoy.
6. **Extraer las afectaciones** que traiga la fuente (notas de vigencia, "modificado
   por", "derogado por", "declarado inexequible por") y agregarlas a `relaciones.csv`.
   SUIN-Juriscol es la mejor fuente para esto. Solo lo que la fuente afirme: no se
   deduce una derogatoria.
7. **`python3 build.py`.** Si imprime avisos o falla, se corrige antes de cerrar.
8. **Marcar `[x]`**, commit con el ID de lo cargado en el mensaje.
9. Si no quedan `[ ]` en P1, **detener el loop** y reportar. Si quedan, siguiente tick.

**Regla de oro:** ante la duda entre cargar algo incompleto o no cargarlo, no se carga
y se anota qué faltó. La base vale por lo que se puede confiar, no por lo que pesa.

---

## P1 — Troncales

Los siete códigos que cubren el grueso de las consultas, intercalados con la
jurisprudencia hito que los interpreta.

- [ ] `co:constitucion:1991` — Constitución Política (~380 arts + transitorios) · rama: constitucional
- [ ] jurisprudencia constitucional — 15 sentencias hito de control de constitucionalidad y bloque de constitucionalidad
- [ ] `co:ley:1564:2012` — Código General del Proceso (~627) · procesal, civil, comercial, familia
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

## P3 — Por definir

Se llena cuando P1 esté cerrado y se vea qué falta de verdad al usar la base.
Candidatos: internacional privado, propiedad intelectual (Decisión 486 CAN),
minero-energético, urbanístico (Ley 388/1997), electoral, agrario (Ley 160/1994).

---

## Bloqueados

_(vacío — aquí van las `[!]` con motivo, URL que falló y fecha)_
