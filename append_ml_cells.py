import nbformat as nbf

notebook_path = 'notebooks/02_selecao_features.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

# Vamos manter todas as células até a célula do Quality Gate
# (que contém 'Colunas saudáveis mantidas na base:')
cut_index = len(nb.cells)
for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code' and 'Colunas saudáveis mantidas na base:' in cell.source:
        cut_index = i + 1
        break

# Remove células residuais no fim do notebook
nb.cells = nb.cells[:cut_index]

# 1. Variável-Alvo
md1 = """## 3. Seleção da Variável-Alvo (Target)
Para o treinamento da IA, precisamos definir o que ela vai tentar prever. O ENEM possui 5 notas diferentes. 

Nesta célula, você pode experimentar qual alvo deseja prever:
1. `NU_NOTA_MT` (Apenas Matemática)
2. `NU_NOTA_LC` (Apenas Linguagens)
3. `NU_NOTA_REDACAO` (Apenas Redação)
4. Média de Matemática + Redação
5. Média Geral (As 5 notas somadas divididas por 5)

Vamos criar a coluna `TARGET` para centralizar a nossa análise."""
code1 = """# Defina aqui qual será o seu alvo (descomente a opção desejada):

# Opção A: Apenas Matemática (Descomente abaixo)
df['TARGET'] = df['NU_NOTA_MT']

# Opção B: Apenas Redação
# df['TARGET'] = df['NU_NOTA_REDACAO']

# Opção C: Média de Matemática + Redação
# df['TARGET'] = (df['NU_NOTA_MT'] + df['NU_NOTA_REDACAO']) / 2

# Opção D: Média Geral (5 Provas)
# score_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
# df['TARGET'] = df[score_cols].mean(axis=1)

print("Variável TARGET definida com sucesso! Amostra das notas:")
print(df['TARGET'].head())"""

# 2. Encoding
md2 = """## 4. Transformação de Dados (Encoding)
Algoritmos de *Machine Learning* e de cálculos de Correlação não sabem ler letras (como a renda que vai de 'A' a 'Q') ou palavras (como Sexo 'M' ou 'F'). 

Para que a matemática funcione, aplicaremos um `OrdinalEncoder`, que transformará automaticamente respostas de texto em categorias numéricas sequenciais."""
code2 = """from sklearn.preprocessing import OrdinalEncoder

# Isolamos apenas as colunas socioeconômicas e demográficas limpas e o Target
features = [c for c in df.columns if c.startswith('Q0') or c.startswith('TP_') or c.startswith('IN_') or c == 'NU_IDADE']
df_ml = df[features + ['TARGET']].copy()

# Encontrar colunas de texto/categóricas
cat_cols = df_ml.select_dtypes(include=['object', 'category']).columns.tolist()

if cat_cols:
    enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    df_ml[cat_cols] = enc.fit_transform(df_ml[cat_cols])

print(f"Dados numéricos prontos para processamento. {len(features)} variáveis independentes.")"""

# 3. Correlação
md3 = """## 5. Matriz de Correlação (Spearman)
Agora que os dados são numéricos, vamos plotar o Heatmap de Spearman. 

**Por que Spearman e não Pearson?** Porque nossas categorias de renda (1, 2, 3...) não são grandezas matemáticas puras, são "ordens" (grandezas ordinais). O cálculo de Spearman é desenhado exatamente para medir o impacto não-linear entre escalas ordinais e a Nota Final."""
code3 = """import matplotlib.pyplot as plt
import seaborn as sns

# Para não poluir o gráfico com dezenas de variáveis irrelevantes, vamos filtrar apenas as correlações mais fortes com o Target
corr = df_ml.corr(method='spearman')
target_corr = corr['TARGET'].drop('TARGET').abs().sort_values(ascending=False)

# Pegar as 15 variáveis mais fortemente correlacionadas
top_features = target_corr.head(15).index.tolist()
plot_cols = top_features + ['TARGET']

plt.figure(figsize=(14, 10))
sns.heatmap(df_ml[plot_cols].corr(method='spearman'), annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Matriz de Correlação (Top 15 Variáveis)")
plt.show()"""

# 4. Feature Importance
md4 = """## 6. Prova de Fogo: Feature Importance (Random Forest)
A correlação isolada não conta toda a história, pois ela avalia cada variável individualmente contra a nota. 

Nesta célula, soltaremos uma Inteligência Artificial (`RandomForestRegressor`) nos dados. A IA vai combinar todas as variáveis ao mesmo tempo e decidir quais são absolutamente indispensáveis para adivinhar a nota do candidato. Este é o método definitivo para escolhermos nosso **Esquadrão de Elite**."""
code4 = """from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Separar X (features) e y (target)
X = df_ml[features]
y = df_ml['TARGET']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Treinando Floresta Aleatória para extrair importância de features... (isso pode levar alguns segundos)")
rf = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

# Coletando a importância Gini e plotando
importances = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=True)

plt.figure(figsize=(10, 8))
importances.tail(15).plot(kind='barh', color='teal')
plt.title("Ranking de Importância (Top 15 Features que mais definem a nota)")
plt.xlabel("Importância Relativa (Gini)")
plt.ylabel("Variável do ENEM")
plt.show()"""

# Adicionando ao notebook
nb.cells.extend([
    nbf.v4.new_markdown_cell(md1), nbf.v4.new_code_cell(code1),
    nbf.v4.new_markdown_cell(md2), nbf.v4.new_code_cell(code2),
    nbf.v4.new_markdown_cell(md3), nbf.v4.new_code_cell(code3),
    nbf.v4.new_markdown_cell(md4), nbf.v4.new_code_cell(code4)
])

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook concluído com todas as etapas!")
