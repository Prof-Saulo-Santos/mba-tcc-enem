import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

nb['cells'] = [
    nbf.v4.new_markdown_cell("# 3. Dicionário de Features Selecionadas\n\nNeste notebook, extraímos as features selecionadas do notebook 02 e buscamos suas respectivas definições no dicionário oficial do INEP."),
    
    nbf.v4.new_code_cell("""import json
import ast
import pandas as pd
import pprint

# 1. Abrir o notebook 02 para saber quais sao as features selecionadas
path_nb02 = '02_selecao_features.ipynb'

with open(path_nb02, 'r', encoding='utf-8') as f:
    nb_data = json.load(f)

features_oficiais = []
for cell in nb_data.get('cells', []):
    if cell['cell_type'] == 'code':
        source = "".join(cell.get('source', []))
        if "elite_features =" in source:
            import re
            match = re.search(r"elite_features\s*=\s*\[(.*?)\]", source, re.DOTALL)
            if match:
                raw_items = match.group(1).split(',')
                features_oficiais = [item.strip().strip("'").strip('"') for item in raw_items if item.strip()]
            break

print("Features identificadas no Notebook 02:", features_oficiais)
"""),

    nbf.v4.new_code_cell("""# 2. Abrir o Dicionário_Microdados_Enem_2023.xlsx
path_dicionario = '../data/raw/enem_2023/microdados_enem_2023/DICIONÁRIO/Dicionário_Microdados_Enem_2023.xlsx'

# Pular as primeiras linhas de cabeçalho irrelevante
df_dic = pd.read_excel(path_dicionario, sheet_name='MICRODADOS_ENEM_2023', skiprows=2)

# Fazer forward fill nas colunas NOME DA VARIÁVEL e Descrição para agrupar as categorias
col_nome = df_dic.columns[0]
col_desc = df_dic.columns[1]
col_cat_key = df_dic.columns[2]
col_cat_val = df_dic.columns[3]
col_tam = df_dic.columns[4]

df_dic[col_nome] = df_dic[col_nome].ffill()
df_dic[col_desc] = df_dic[col_desc].ffill()

# 3. Criar o dicionário (features_selecionadas)
features_selecionadas = {}

for feature in features_oficiais:
    df_feat = df_dic[df_dic[col_nome] == feature]
    
    if df_feat.empty:
        features_selecionadas[feature] = "Feature não encontrada no dicionário."
        continue
        
    desc = str(df_feat[col_desc].iloc[0]).strip()
    tamanho = str(df_feat[col_tam].iloc[0]).strip()
    
    # Montar a lista de categorias
    categorias = []
    for _, row in df_feat.iterrows():
        k = row[col_cat_key]
        v = row[col_cat_val]
        if pd.notna(k) or pd.notna(v):
            k_str = str(k).strip() if pd.notna(k) else ""
            v_str = str(v).strip() if pd.notna(v) else ""
            if k_str or v_str:
                categorias.append(f"{k_str}: {v_str}")
            
    features_selecionadas[feature] = {
        'Descrição': desc,
        'Categorias': categorias,
        'Tamanho': tamanho
    }

# 4. Listar as informações deste dicionário para checagem
pprint.pprint(features_selecionadas, sort_dicts=False)
"""),
]

os.makedirs('notebooks', exist_ok=True)
notebook_path = 'notebooks/03_dicionario.ipynb'

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook {notebook_path} gerado com sucesso!")
