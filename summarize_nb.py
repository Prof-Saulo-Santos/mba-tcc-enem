import os
import json

notebooks = [
    "notebooks/01_analise_anomalias_estruturais.ipynb",
    "notebooks/02_selecao_features.ipynb",
    "notebooks/02_selecao_features_v2.ipynb",
    "notebooks/03_analise_harmonizacao_historica.ipynb",
    "notebooks/03_eda_modelagem.ipynb"
]

for nb in notebooks:
    print(f"\\n--- {nb} ---")
    try:
        with open(nb, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cells = data.get('cells', [])
            count = 0
            for c in cells:
                if c.get('cell_type') == 'markdown':
                    source = "".join(c.get('source', []))
                    if source.startswith('#'):
                        print(source.split('\\n')[0])
                        count += 1
                        if count >= 3: # just top 3 headers
                            break
    except Exception as e:
        print("Erro:", e)
