import nbformat as nbf

notebook_path = 'notebooks/02_selecao_features.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code' and "df['TARGET_MT'] = df['NU_NOTA_MT']" in cell.source:
        
        new_source = """# Criando os 8 alvos simultaneamente no DataFrame
df['TARGET_MT'] = df['NU_NOTA_MT']
df['TARGET_REDACAO'] = df['NU_NOTA_REDACAO']
df['TARGET_LC'] = df['NU_NOTA_LC']
df['TARGET_CN'] = df['NU_NOTA_CN']
df['TARGET_CH'] = df['NU_NOTA_CH'] # Corrigido de CI para CH (Ciências Humanas)
df['TARGET_M2'] = (df['NU_NOTA_LC'] + df['NU_NOTA_MT']) / 2 # Renomeado para M2 para não sobrescrever
df['TARGET_M3'] = (df['NU_NOTA_LC'] + df['NU_NOTA_MT'] + df['NU_NOTA_REDACAO']) / 3
score_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
df['TARGET_GERAL'] = df[score_cols].mean(axis=1)

# Atualizando a lista para treinar as 8 IAs!
targets = ['TARGET_MT', 'TARGET_REDACAO', 'TARGET_LC', 'TARGET_CN', 'TARGET_CH', 'TARGET_M2', 'TARGET_M3', 'TARGET_GERAL']
print(f"Os {len(targets)} alvos foram calculados com sucesso e estão prontos para a batalha!")"""
        
        cell.source = new_source

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Célula de targets corrigida no notebook!")
