import json
with open('notebooks/02_selecao_features_v2.ipynb', 'r', encoding='utf-8') as f:
    data = json.load(f)
    for c in data.get('cells', []):
        if c.get('cell_type') == 'code':
            for o in c.get('outputs', []):
                if o.get('output_type') == 'execute_result':
                    if 'text/html' in o.get('data', {}):
                        print("HTML:", o['data']['text/html'][:500])
                    if 'text/plain' in o.get('data', {}):
                        print("TEXT:", o['data']['text/plain'])
