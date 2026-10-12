import json

notebook_path = "/home/saulo/mba/tcc/enem/notebooks/03_criado_por_IA.ipynb"
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find the first code cell
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        # Check if df = pd.read is already there to avoid duplicates
        has_load = any("df =" in line and "read_" in line for line in cell['source'])
        if not has_load:
            # Append to the end of the cell
            if cell['source'] and not cell['source'][-1].endswith('\n'):
                cell['source'][-1] += '\n'
            cell['source'].append("df = pd.read_parquet('../data/processed/enem_2023_silver.parquet')\n")
        break

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Data load injected successfully.")
