import json

def get_plot_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for c in data.get('cells', []):
            if c.get('cell_type') == 'code':
                for o in c.get('outputs', []):
                    if o.get('output_type') == 'execute_result' and 'text/plain' in o.get('data', {}):
                        print(o['data']['text/plain'])

print("--- V1 ---")
get_plot_text("notebooks/02_selecao_features.ipynb")
print("--- V2 ---")
get_plot_text("notebooks/02_selecao_features_v2.ipynb")
