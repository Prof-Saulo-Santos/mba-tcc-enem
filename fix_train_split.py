import nbformat as nbf

notebook_path = 'notebooks/02_selecao_features.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code' and 'train_test_split' in cell.source and 'train_size=100000' in cell.source:
        # Remover a limitação absoluta de train_size para não quebrar em bases menores
        new_source = cell.source.replace(
            "train_test_split(X, y, test_size=0.2, train_size=100000, random_state=42)",
            "train_test_split(X, y, test_size=0.2, random_state=42)"
        )
        cell.source = new_source

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Bug corrigido no notebook!")
