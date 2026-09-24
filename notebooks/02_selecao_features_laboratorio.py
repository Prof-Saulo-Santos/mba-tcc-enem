# %% [markdown]
# # Laboratório Exploratório: Teste e Comparação de Algoritmos (Regressão)
# Neste experimento, vamos carregar uma amostra dos dados, aplicar o básico de Engenharia de Features e treinar 4 algoritmos diferentes para prever a Nota de Matemática do ENEM (`NU_NOTA_MT`).
#
# **Alvo (Target):** `NU_NOTA_MT`
# **Métricas:** RMSE (Menor é melhor) e R² (Maior é melhor, máximo 1.0)

# %% [markdown]
# ### 1. Importação das Bibliotecas e Leitura da Amostra
# Aqui usamos a nossa própria arquitetura (Ingestão T1) para ler uma amostra de 10.000 linhas da base monolítica de 2023.

# %%
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração visual dos gráficos
sns.set_theme(style="whitegrid")

# Caminho para o arquivo CSV de 2023
# Vamos tentar carregar da nossa pasta de testes, ou do diretório real
filepath = "../scratch/dummy_data/enem_2023/microdados_enem_2023/DADOS/MICRODADOS_ENEM_2023.csv"

print(f"Lendo arquivo bruto: {filepath}")

try:
    # Lendo o CSV "na raça" usando o pandas clássico! 
    # (Como aprendemos, usamos dtype=str para não perder os zeros à esquerda)
    df_raw = pd.read_csv(filepath, sep=";", encoding="latin-1", dtype=str, nrows=10000)
    print(f"Dados carregados com sucesso! Shape: {df_raw.shape}")
    display(df_raw.head())
except Exception as e:
    print(f"Erro ao carregar dados: {e}")

# %% [markdown]
# ### 2. Limpeza (O Chapéu do EDA)
# A "Regra de Ouro": Se o alvo for Nulo, jogamos a linha fora. O aluno faltou.

# %%
target_col = "NU_NOTA_MT"

print(f"Tamanho original: {len(df_raw)}")

# 1. Remover quem não tem nota (Alunos que faltaram)
df_clean = df_raw.dropna(subset=[target_col]).copy()
print(f"Tamanho após descartar alunos ausentes: {len(df_clean)}")

# 2. Selecionar algumas features explicativas
features_categoricas = ["TP_SEXO", "TP_ESCOLA", "Q006"] # Sexo, Tipo de Escola (Pública/Privada), Renda
# Q006 é a renda familiar: A (Nenhuma) até Q (Mais de 20 mil)

# Garantir que as features não tenham nulos (preenchendo com categoria genérica para simplificar no lab)
for col in features_categoricas:
    df_clean[col] = df_clean[col].fillna("Desconhecido")
    
# Converter o Target para numérico (nossa Ingestão lê tudo como string por segurança)
df_clean[target_col] = pd.to_numeric(df_clean[target_col], errors='coerce')

# Remover algum nulo que possa ter sobrado na conversão numérica
df_clean = df_clean.dropna(subset=[target_col])

X = df_clean[features_categoricas]
y = df_clean[target_col]

print(f"Dataset final pronto para treino. Instâncias: {len(X)}")

# %% [markdown]
# ### 3. Divisão de Treino/Teste e Pipeline de Engenharia (Encoding)
# Precisamos converter o texto ("Masculino", "Feminino", "A", "B") em números para os modelos entenderem.

# %%
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Divisão 80% treino, 20% teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# O Transformador: Transforma categorias de texto em matriz numérica
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), features_categoricas)
    ])

# %% [markdown]
# ### 4. A Arena de Treinamento: Avaliando os Competidores
# Vamos instanciar 4 modelos estatísticos distintos.

# %%
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Dicionário com os algoritmos que vamos testar
modelos = {
    "1. Dummy (Baseline)": DummyRegressor(strategy="mean"),
    "2. Regressão Linear": LinearRegression(),
    "3. Random Forest": RandomForestRegressor(n_estimators=50, random_state=42),
    "4. LightGBM (HistGB)": HistGradientBoostingRegressor(random_state=42)
}

resultados = []

print("Iniciando arena de treinamento...\n")

for nome, algoritmo in modelos.items():
    print(f"Treinando {nome}...")
    
    # Cria o funil: Primeiro aplica o encoder numérico, depois passa pro modelo treinar
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', algoritmo)
    ])
    
    # Fase de Aprendizado
    pipeline.fit(X_train, y_train)
    
    # Fase de Adivinhação (Inferência)
    y_pred = pipeline.predict(X_test)
    
    # Métricas de Avaliação
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)
    
    resultados.append({
        "Algoritmo": nome,
        "RMSE (Menor=Melhor)": rmse,
        "R2 (Maior=Melhor)": r2
    })

df_resultados = pd.DataFrame(resultados)
print("\n--- Resultados Finais ---")
display(df_resultados)

# %% [markdown]
# ### 5. Visualização Comparativa
# Gerando um gráfico para colocar na sua dissertação!

# %%
plt.figure(figsize=(10, 5))
ax = sns.barplot(data=df_resultados, x='RMSE (Menor=Melhor)', y='Algoritmo', palette='Blues_r')
plt.title('Comparação de Erro (RMSE) por Algoritmo', fontsize=14, pad=15)
plt.xlabel('RMSE (Pontos do ENEM de Erro)', fontsize=12)
plt.ylabel('')

# Adiciona os números na barra
for p in ax.patches:
    ax.annotate(f"{p.get_width():.2f}", 
                (p.get_width(), p.get_y() + p.get_height() / 2.), 
                ha='left', va='center', 
                xytext=(5, 0), textcoords='offset points', fontsize=11)

plt.tight_layout()
plt.show()

# %% [markdown]
# **Interpretação para o TCC:**
# - O **Dummy** errou em média X pontos (ele só chuta a média de matemática do país).
# - A **Regressão Linear** conseguiu entender que a Renda (Q006) altera a nota e diminuiu o erro.
# - O **LightGBM / Random Forest** lidam melhor com as interações não-lineares, geralmente alcançando o menor erro possível com os dados fornecidos.
