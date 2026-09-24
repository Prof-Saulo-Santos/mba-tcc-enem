import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

nb['cells'] = [
    nbf.v4.new_markdown_cell("# 2. Seleção e Análise de Features (Feature Selection)\n\nNeste notebook, nosso objetivo é sair do achismo e ir para a matemática. O ENEM possui dezenas de colunas, e jogar todas elas em um modelo de Machine Learning vai gerar ruído (conceito de *Garbage In, Garbage Out*).\n\nAqui, nós vamos:\n1. **Analisar Valores Nulos:** Descartar colunas que são um 'queijo suíço'.\n2. **Correlação Linear (Pearson):** Ver quem tem força direta para subir ou descer a Nota Média.\n3. **Feature Importance (Random Forest):** Usar inteligência artificial para ranquear as colunas que mais ajudam a adivinhar a nota do aluno.\n\nIsso nos dará as provas matemáticas necessárias para justificar no TCC o porquê de termos escolhido variáveis específicas (como Renda e Escolaridade) em vez de usar todas."),
    
    nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import warnings

warnings.filterwarnings('ignore')
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)"""),
    
    nbf.v4.new_markdown_cell("## 1. Carregamento da Amostra (ENEM 2023)\n\nLer 5 milhões de linhas consome muita memória para uma simples exploração. Vamos ler uma amostra da base bruta e aplicar uma limpeza rápida (a mesma lógica do `cleaner.py`) apenas para termos dados coerentes para análise."),
    
    nbf.v4.new_code_cell("""# Tente carregar a base de 2023 bruta
file_path = '../data/raw/enem_2023/microdados_enem_2023/DADOS/MICRODADOS_ENEM_2023.csv'
try:
    df = pd.read_csv(file_path, sep=';', encoding='latin-1', nrows=150000)
    print(f"Base carregada! Linhas: {df.shape[0]}, Colunas: {df.shape[1]}")
except FileNotFoundError:
    print(f"Erro: O arquivo {file_path} não foi encontrado. Altere o caminho se necessário.")"""),

    nbf.v4.new_markdown_cell("## 2. Limpeza Rápida e Criação da Variável-Alvo\nFiltramos quem faltou e calculamos a Média."),
    
    nbf.v4.new_code_cell("""# 1. Filtra presentes (usando int, já que não usamos dtype=str aqui)
for col in ["TP_PRESENCA_CN", "TP_PRESENCA_CH", "TP_PRESENCA_LC", "TP_PRESENCA_MT"]:
    if col in df.columns:
        df = df[df[col] == 1]

# 2. Calcula Nota Média
score_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
df = df.dropna(subset=score_cols)
df["NU_NOTA_MEDIA"] = df[score_cols].mean(axis=1)

print(f"Alunos presentes com nota válida: {len(df)}")"""),

    nbf.v4.new_markdown_cell("## 3. Análise de Nulos nas Features\nVamos descartar features que estão vazias demais."),
    
    nbf.v4.new_code_cell("""# Selecionar variáveis candidatas (Q001 a Q025 socioeconômicas + dados escolares/pessoais)
features_candidatas = [c for c in df.columns if c.startswith('Q0') or c.startswith('TP_') or c.startswith('NU_IDADE')]

# Calcular % de nulos
nulos = df[features_candidatas].isnull().sum() / len(df) * 100
nulos = nulos[nulos > 0].sort_values(ascending=False)

if not nulos.empty:
    plt.figure(figsize=(10,4))
    sns.barplot(x=nulos.index, y=nulos.values, palette="rocket")
    plt.title("Porcentagem de Nulos por Feature")
    plt.xticks(rotation=90)
    plt.show()
else:
    print("As features candidatas não possuem valores nulos preocupantes.")"""),

    nbf.v4.new_markdown_cell("## 4. Correlação Linear\nAvaliamos quais features contínuas ou ordinais têm relação matemática direta com a Nota Média."),
    
    nbf.v4.new_code_cell("""# Seleção de variáveis numéricas e de interesse
num_features = ["NU_IDADE", "TP_COR_RACA", "TP_ESCOLA", "TP_ST_CONCLUSAO", "TP_SEXO", "NU_NOTA_MEDIA"]
cols = [c for c in num_features if c in df.columns]

# TP_SEXO é string ('M', 'F'). Vamos converter para número (0, 1) só para a matriz
df_temp = df[cols].copy()
if 'TP_SEXO' in df_temp.columns:
    df_temp['TP_SEXO'] = df_temp['TP_SEXO'].map({'M': 0, 'F': 1})

corr = df_temp.corr()
plt.figure(figsize=(8,6))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1)
plt.title("Correlação (Pearson) com a Nota Média")
plt.show()"""),

    nbf.v4.new_markdown_cell("## 5. Feature Importance via Árvore de Decisão\nEm vez de olharmos apenas relações lineares, o *Random Forest* nos dirá o que ele julga mais importante para adivinhar a nota. É daqui que tiramos a decisão final para o pipeline (Feature Engineering)."),
    
    nbf.v4.new_code_cell("""# Cópia das features para rodar o modelo
X = df[features_candidatas].copy()
y = df["NU_NOTA_MEDIA"]

# Preencher nulos com um placeholder e converter strings em números rapidamente
le = LabelEncoder()
for col in X.columns:
    X[col] = X[col].fillna(-1)
    if X[col].dtype == 'object':
        X[col] = le.fit_transform(X[col].astype(str))

# Treinar um modelo rápido e raso
rf = RandomForestRegressor(n_estimators=30, max_depth=10, random_state=42, n_jobs=-1)
rf.fit(X, y)

# Gerar Ranking
importancias = pd.Series(rf.feature_importances_, index=X.columns)
importancias = importancias.nlargest(15)

plt.figure(figsize=(10,6))
importancias.plot(kind='barh', color='teal').invert_yaxis()
plt.title("Top 15 Features Mais Importantes para Prever a Nota Média (Random Forest)")
plt.xlabel("Importância Relativa")
plt.show()""")
]

# Garantir que o diretório notebooks existe
os.makedirs('/home/saulo/mba/tcc/enem/notebooks', exist_ok=True)
notebook_path = '/home/saulo/mba/tcc/enem/notebooks/02_selecao_features.ipynb'

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook gerado com sucesso em: {notebook_path}")
