import json

path = '/home/saulo/mba/tcc/enem/notebooks/01_analise_anomalias_estruturais.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Clear outputs
for cell in nb['cells']:
    if 'outputs' in cell:
        cell['outputs'] = []
    if 'execution_count' in cell:
        cell['execution_count'] = None

# Fix paths
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            line = line.replace('2023/dados/MICRODADOS_ENEM_2023.csv', 'enem_2023/microdados_enem_2023/DADOS/MICRODADOS_ENEM_2023.csv')
            line = line.replace('2024/dados/PARTICIPANTES_2024.csv', 'enem_2024/microdados_enem_2024/DADOS/PARTICIPANTES_2024.csv')
            line = line.replace('2024/dados/RESULTADOS_2024.csv', 'enem_2024/microdados_enem_2024/DADOS/RESULTADOS_2024.csv')
            new_source.append(line)
        cell['source'] = new_source

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)
