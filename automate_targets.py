import nbformat as nbf

notebook_path = 'notebooks/02_selecao_features.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

cut_index = len(nb.cells)
for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'markdown' and '## 3. Seleção da Variável-Alvo (Target)' in cell.source:
        cut_index = i
        break

# Remover as células velhas a partir do corte
nb.cells = nb.cells[:cut_index]

# Novas Células
md1 = """## 3. Experimento Automatizado de Variáveis-Alvo (Targets)

Em vez de testar manualmente uma disciplina por vez, vamos automatizar a criação de 4 alvos diferentes para vermos como o perfil socioeconômico impacta cada área de conhecimento:
1. `TARGET_MT`: Apenas Matemática
2. `TARGET_REDACAO`: Apenas Redação
3. `TARGET_M3`: Média de Matemática + Linguagens + Redação
4. `TARGET_GERAL`: Média Geral (As 5 notas)"""

code1 = """# Criando os 4 alvos simultaneamente no DataFrame
df['TARGET_MT'] = df['NU_NOTA_MT']
df['TARGET_REDACAO'] = df['NU_NOTA_REDACAO']
df['TARGET_M3'] = (df['NU_NOTA_LC'] + df['NU_NOTA_MT'] + df['NU_NOTA_REDACAO']) / 3
score_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
df['TARGET_GERAL'] = df[score_cols].mean(axis=1)

targets = ['TARGET_MT', 'TARGET_REDACAO', 'TARGET_M3', 'TARGET_GERAL']
print("Os 4 alvos foram calculados com sucesso!")"""

md2 = """## 4. Transformação de Dados (Encoding)
Vamos isolar as variáveis socioeconômicas/demográficas saudáveis e transformá-las em números via `OrdinalEncoder` para que a Inteligência Artificial consiga processá-las."""

code2 = """from sklearn.preprocessing import OrdinalEncoder

# Isolamos as features limpas
features = [c for c in df.columns if c.startswith('Q0') or c.startswith('TP_') or c.startswith('IN_') or c == 'NU_IDADE']

# Dicionário de features + targets
df_ml = df[features + targets].copy()

cat_cols = df_ml.select_dtypes(include=['object', 'category']).columns.tolist()
if cat_cols:
    enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    df_ml[cat_cols] = enc.fit_transform(df_ml[cat_cols])

print(f"Dados numéricos prontos. Temos {len(features)} variáveis independentes.")"""

md3 = """## 5. Batalha de Modelos (Random Forest Automatizado)
Agora, vamos treinar **4 Inteligências Artificiais diferentes** (uma para cada Target).
Para cada IA, extrairemos as **Top 15 Variáveis mais importantes** e, ao final, construiremos um Quadro Comparativo para analisar se as variáveis que ditam a nota de Matemática são as mesmas que ditam a nota de Redação."""

code3 = """from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
from IPython.display import display

resultados = {}

for target_name in targets:
    print(f"Treinando IA para prever: {target_name}...")
    
    X = df_ml[features]
    y = df_ml[target_name]
    
    # Amostragem para o RF não demorar muito (usamos 100k alunos por target)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, train_size=100000, random_state=42)
    
    rf = RandomForestRegressor(n_estimators=30, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    
    # Coletando a importância Gini
    importances = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)
    
    # Pegando as Top 15 e formatando
    top_15 = importances.head(15)
    # Salvando no dicionário (Nome da feature + score formatado)
    lista_formatada = [f"{idx} ({score:.3f})" for idx, score in top_15.items()]
    
    resultados[target_name] = lista_formatada

print("\\nTreinamento concluído! Gerando Quadro Comparativo...")

# Criando o DataFrame Comparativo
df_comparativo = pd.DataFrame(resultados)
df_comparativo.index = [f"Top {i+1}" for i in range(15)]

# Configurando estilo para facilitar a leitura da banca
styled_table = df_comparativo.style.set_caption("Quadro Comparativo: Top 15 Features Mais Importantes por Tipo de Prova")\\
                             .set_properties(**{'text-align': 'left', 'font-size': '13px'})\\
                             .set_table_styles([{'selector': 'caption', 'props': [('font-size', '16px'), ('font-weight', 'bold')]}])

display(styled_table)"""

# Injetando as células
nb.cells.extend([
    nbf.v4.new_markdown_cell(md1), nbf.v4.new_code_cell(code1),
    nbf.v4.new_markdown_cell(md2), nbf.v4.new_code_cell(code2),
    nbf.v4.new_markdown_cell(md3), nbf.v4.new_code_cell(code3)
])

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook automatizado com sucesso!")
