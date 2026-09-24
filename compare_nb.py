import json

def dump_last_cells(filepath, n_cells=5):
    print(f"\n========== {filepath} ==========")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        cells = data.get('cells', [])
        for i, c in enumerate(cells[-n_cells:]):
            print(f"\n--- Cell {len(cells) - n_cells + i + 1} ({c.get('cell_type')}) ---")
            source = "".join(c.get('source', []))
            print("SOURCE:\n", source[:500] + ("..." if len(source) > 500 else ""))
            if c.get('cell_type') == 'code':
                outputs = c.get('outputs', [])
                for o in outputs:
                    if o.get('output_type') == 'stream':
                        print("OUTPUT (stream):", "".join(o.get('text', [])))
                    elif o.get('output_type') == 'execute_result':
                        data = o.get('data', {})
                        if 'text/plain' in data:
                            print("OUTPUT (result):", "".join(data['text/plain'])[:200])

dump_last_cells("notebooks/02_selecao_features.ipynb")
dump_last_cells("notebooks/02_selecao_features_v2.ipynb")
