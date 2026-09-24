import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

nb['cells'] = [
    nbf.v4.new_markdown_cell("""# 4. Harmonização Histórica via Processamento de Linguagem Natural (NLP)

Este notebook implementa a inteligência necessária para resolver o **Drift Semântico** das colunas do INEP ao longo das décadas.
Em vez de depender de códigos hardcoded (ex: `Q024` ou `Q021`), utilizamos um modelo de **Sentence Transformers (SBERT)** para ler a descrição das perguntas (ex: *Na sua residência tem computador?* vs *Em sua casa, existe computador?*) e pareá-las usando similaridade matemática (Cosine Similarity)."""),

    nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import glob
import os
import re
from sentence_transformers import SentenceTransformer, util
import torch

# 1. Carregar o Modelo NLP
print("Carregando o modelo SBERT (pode demorar alguns segundos na primeira vez)...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("Modelo carregado com sucesso!")
"""),

    nbf.v4.new_code_cell("""# 2. Fazer o parse do dicionario_features.md (Padrão Ouro de 2023)
path_dic_md = 'notebooks/dicionario_features.md'
if not os.path.exists(path_dic_md):
    path_dic_md = 'dicionario_features.md'

with open(path_dic_md, 'r', encoding='utf-8') as f:
    content = f.read()

features_base = {}
blocks = re.split(r'={40}', content)
for i in range(len(blocks)):
    if 'FEATURE:' in blocks[i]:
        feat_name = blocks[i].replace('FEATURE:', '').strip()
        if i+1 < len(blocks):
            details = blocks[i+1].strip()
            desc_match = re.search(r'Descrição:\s*(.*?)(?=\\nTamanho:)', details, re.DOTALL)
            if desc_match:
                features_base[feat_name] = desc_match.group(1).replace('\\n', ' ').strip()

print(f"Features Base Extraídas ({len(features_base)}):")
for k, v in features_base.items():
    print(f" - {k}: {v}")

# Gerar Embeddings das features base
base_feats = list(features_base.keys())
base_descs = [features_base[f] for f in base_feats]
base_embs = model.encode(base_descs, convert_to_tensor=True)
"""),

    nbf.v4.new_code_cell("""# Função robusta para extrair TODAS as descrições de um arquivo de dicionário XLSX
def parse_dicionario_total(path):
    try:
        xls = pd.ExcelFile(path, engine='openpyxl')
        sheet = next((s for s in xls.sheet_names if 'PARTICIPANTES' in s.upper() or 'MICRODADOS' in s.upper()), xls.sheet_names[0])
        df = pd.read_excel(path, sheet_name=sheet, header=None, engine='openpyxl')
        header_row = next((i for i, row in df.iterrows() if 'NOME DA VARIÁVEL' in str(row.values) or 'NOME' in str(row.values).upper()), None)
        if header_row is None:
            return {}
        df2 = pd.read_excel(path, sheet_name=sheet, header=header_row, engine='openpyxl')
        df2.columns = [str(c).strip() for c in df2.columns]
        
        col_nome = [c for c in df2.columns if 'NOME' in c.upper()]
        col_desc = [c for c in df2.columns if 'DESCRI' in c.upper()]
        
        if not col_nome or not col_desc:
            return {}
            
        df2 = df2[[col_nome[0], col_desc[0]]].dropna(subset=[col_nome[0]])
        return dict(zip(df2[col_nome[0]].astype(str).str.strip(), df2[col_desc[0]].astype(str).str.strip()))
    except Exception as e:
        print(f"Erro em {path}: {e}")
        return {}
"""),

    nbf.v4.new_code_cell("""# 3. Iterar sobre todos os anos (2009 a 2025)
RAW_DATA_DIR = '../data/raw'
anos_paths = sorted(glob.glob(os.path.join(RAW_DATA_DIR, '*/microdados_enem_*/DICIONÁRIO/Dicion*.xlsx')))

historico_drift = []

for path in anos_paths:
    match = re.search(r'enem_(\d{4})', path)
    ano = match.group(1) if match else "Desconhecido"
    
    if ano == "2023":
        continue # O ano de 2023 é o nosso padrão ouro, já temos a base
        
    dic_ano = parse_dicionario_total(path)
    if not dic_ano:
        continue
        
    target_feats = list(dic_ano.keys())
    target_descs = [str(v) for v in dic_ano.values()]
    
    # Embedding de todas as descrições do ano atual
    target_embs = model.encode(target_descs, convert_to_tensor=True)
    
    # Calcular similaridade entre as Base Features (2023) e TODAS as Target Features (Ano Atual)
    cosine_scores = util.cos_sim(base_embs, target_embs)
    
    # Encontrar a melhor correspondência para cada feature base
    linha_drift = {'Ano': ano}
    
    for i, base_feat in enumerate(base_feats):
        scores = cosine_scores[i]
        best_idx = torch.argmax(scores).item()
        best_score = scores[best_idx].item()
        best_target_feat = target_feats[best_idx]
        
        # Só consideramos um "Match" se a similaridade for razoavelmente alta (> 0.60)
        if best_score > 0.60:
            if best_target_feat == base_feat:
                linha_drift[base_feat] = f"Mantida"
            else:
                linha_drift[base_feat] = f"{best_target_feat} ({best_score:.2f})"
        else:
            linha_drift[base_feat] = f"AUSENTE"
            
    historico_drift.append(linha_drift)

df_drift = pd.DataFrame(historico_drift)
print("Processamento concluído!")
"""),

    nbf.v4.new_code_cell("""# 4. Tabela Final do Drift Semântico (2009 - 2025)
df_drift.set_index('Ano', inplace=True)
display(df_drift)
"""),
]

os.makedirs('notebooks', exist_ok=True)
notebook_path = 'notebooks/04_analise_harmonizacao_historica.ipynb'
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print(f"Notebook {notebook_path} gerado com sucesso!")
