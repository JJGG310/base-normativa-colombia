# index.db -> grafo.json (nodos = documentos, aristas = relaciones agregadas por documento y tipo)
import sqlite3, json, re, collections, os
db = sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', 'index.db'))
doc = lambda i: i.split(':art:')[0]
docs = {r[0]: r[1:] for r in db.execute("SELECT id, clase, tipo, COALESCE(titulo_corto, titulo, id), ramas, corporacion FROM documentos")}
estados = collections.defaultdict(dict)
for d, e, n in db.execute("SELECT doc_id, estado, count(*) FROM vigencia GROUP BY 1, 2"):
    estados[d][e] = n
aristas = collections.Counter(); malas = collections.Counter()
for o, t, d, f in db.execute("SELECT origen, tipo, destino, fecha FROM relaciones"):
    k = (doc(o), doc(d), t); aristas[k] += 1
    if f and re.fullmatch(r'\d\d-\d\d-\d\d', f): malas[k] += 1
nodos = {}
for (o, d, t), n in aristas.items():
    for x in (o, d): nodos.setdefault(x, {'id': x, 'in': 0, 'out': 0})
    nodos[o]['out'] += n; nodos[d]['in'] += n
for x, v in nodos.items():
    if x in docs:
        clase, tipo, titulo, ramas, corp = docs[x]
        v.update(c=clase, t=tipo, l=titulo, r=(ramas or '').split(',')[0], corp=corp, e=estados.get(x))
    else:
        v.update(c='no_cargado', t=x.split(':')[1] if ':' in x else '', l=x, r='')
FAM = {'constitucional': 'constitucional transicional victimas electoral justicia defensa internacional-publico',
       'civil': 'civil familia procesal insolvencia arbitraje agrario urbanistico',
       'comercial': 'comercial consumo financiero propiedad-intelectual tic datos-personales',
       'penal': 'penal policivo disciplinario',
       'laboral': 'laboral seguridad-social salud',
       'tributario': 'tributario',
       'administrativo': 'administrativo contencioso-administrativo contratacion-estatal territorial servicios-publicos transporte educacion migratorio cultura deporte social',
       'ambiental': 'ambiental minero-energetico'}
FAM = {r: f for f, rs in FAM.items() for r in rs.split()}
for v in nodos.values():
    if v['c'] == 'normativa': v['f'] = FAM.get(v['r'], 'administrativo')
# sentencias y no cargados: el área de la norma (no Constitución) con la que más se relacionan
peso = collections.defaultdict(collections.Counter)
for (o, d, t), n in aristas.items():
    for a, b in ((o, d), (d, o)):
        if nodos[b]['c'] == 'normativa' and b != 'co:constitucion:1991': peso[a][nodos[b]['f']] += n
for x, v in nodos.items():
    if 'f' not in v: v['f'] = peso[x].most_common(1)[0][0] if peso[x] else FAM.get(v['r'], 'constitucional')
json.dump({'nodes': list(nodos.values()),
           'links': [{'source': o, 'target': d, 'tipo': t, 'n': n, 'mal': malas[(o, d, t)]} for (o, d, t), n in aristas.items()]},
          open(os.path.join(os.path.dirname(__file__), 'grafo.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(nodos), 'nodos', len(aristas), 'aristas', sum(malas.values()), 'fechas rotas')
