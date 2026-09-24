import nbformat as nbf

notebook_path = 'notebooks/02_selecao_features.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

new_cells = []
for cell in nb.cells:
    # Checa se é a célula Markdown do Passo 2
    if cell.cell_type == 'markdown' and '## 2. Limpeza Rápida' in cell.source:
        
        # Cria a célula de código com a limpeza de colunas nulas
        codigo_limpeza = """# Filtro de Sanidade Estatística (Quality Gate)
# Vamos eliminar qualquer coluna que possua mais de 30% de valores nulos (ou seja, exige 70% de preenchimento mínimo)
limite_tolerancia = len(df) * 0.7 
colunas_antes = df.shape[1]

# O comando dropna(thresh) mantém apenas as colunas que têm PELO MENOS a quantidade de dados não-nulos exigida no limite
df = df.dropna(thresh=limite_tolerancia, axis=1)
colunas_depois = df.shape[1]

print(f"Colunas originais (Raw): {colunas_antes}")
print(f"Colunas saudáveis mantidas na base: {colunas_depois}")
print(f"Total de colunas sumariamente descartadas por excesso de nulos: {colunas_antes - colunas_depois}")"""
        
        # Insere a nova célula de código antes da célula Markdown do Passo 2
        new_cells.append(nbf.v4.new_code_cell(codigo_limpeza))
        
    # Adiciona a célula original (seja ela qual for)
    new_cells.append(cell)

nb.cells = new_cells

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook atualizado com sucesso com a célula de limpeza!")
