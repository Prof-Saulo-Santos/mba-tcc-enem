import nbformat as nbf
import os

def create_notebook():
    nb = nbf.v4.new_notebook()
    
    nb.cells = [
        nbf.v4.new_markdown_cell("# Laboratório V2: Testando Features Ampliadas do ENEM\n\nEste notebook explora o impacto de um novo conjunto de variáveis sugeridas por outros pesquisadores no GitHub. O objetivo é testar se variáveis de infraestrutura (internet, computador) e demográficas (idade, raça) adicionam forte poder preditivo comparado ao conjunto clássico (Renda e Escolaridade)."),
        
        nbf.v4.new_code_cell("""import pandas as pd\nimport seaborn as sns\nimport matplotlib.pyplot as plt\n\n# 1. Carregar os dados limpos (Camada Silver)\ndf = pd.read_parquet('../data/processed/enem_2023_silver.parquet')\nprint(f"Total de registros carregados: {len(df):,}")"""),
        
        nbf.v4.new_markdown_cell("## 1. Definindo o Conjunto de Variáveis e Checando Ausentes\nAntes de apagar qualquer dado, vamos verificar qual a porcentagem de valores nulos (em branco) para cada uma das 20 perguntas analisadas."),
        nbf.v4.new_code_cell("""# Features: As 6 oficiais do modelo misturadas com 14 outras para provar o "Retorno Decrescente"\nfeatures = [\n    'Q006', 'Q024', 'TP_ANO_CONCLUIU', 'TP_LINGUA', 'TP_SEXO', 'Q002', \n    'TP_ST_CONCLUSAO', 'TP_FAIXA_ETARIA', 'Q013', 'Q001', \n    'TP_ESCOLA', 'Q021', 'Q003', 'Q005', 'TP_COR_RACA', \n    'TP_ESTADO_CIVIL', 'TP_NACIONALIDADE', 'IN_TREINEIRO', \n    'TP_DEPENDENCIA_ADM_ESC', 'TP_LOCALIZACAO_ESC'\n]\n\ntarget = 'NU_NOTA_MT'\n\n# Vamos verificar se essas colunas realmente existem no parquet de 2023\nmissing = [c for c in features + [target] if c not in df.columns]\nif missing:\n    print(f"ATENÇÃO - Colunas ausentes no schema de 2023: {missing}")\n\n# Filtrar apenas as colunas válidas\ncols_validas = [c for c in features if c in df.columns]\n\n# Calcular o percentual de dados nulos por coluna\nprint("--- Percentual de Dados Ausentes por Variável ---")\nnull_percent = (df[cols_validas].isnull().sum() / len(df)) * 100\nprint(null_percent.sort_values(ascending=False).round(2).astype(str) + " %")"""),
        
        nbf.v4.new_markdown_cell("## 2. Análise de Outliers na Variável Alvo (Boxplot)\nO gráfico de Boxplot (que se assemelha a um *candle* do mercado financeiro) é excelente para a banca entender a distribuição estatística das notas e onde estão os *outliers* (pontos fora da curva)."),
        nbf.v4.new_code_cell("""plt.figure(figsize=(8, 6))\nsns.boxplot(y=df[target], color='lightblue', fliersize=3)\nplt.title("Distribuição e Outliers da Nota de Matemática (ENEM 2023)", fontsize=14)\nplt.ylabel("Nota no ENEM")\n\n# Adicionando uma linha para mostrar a média\nplt.axhline(df[target].mean(), color='red', linestyle='--', label=f"Média: {df[target].mean():.1f}")\nplt.legend()\nplt.show()\n\nprint("Interpretação para a Banca:")\nprint("A 'caixa' principal contém 50% dos alunos (do percentil 25 ao 75).")\nprint("Os pontos pretos soltos nas extremidades superior e inferior são os 'outliers' (pessoas com notas excepcionalmente altas ou baixas).")"""),

        nbf.v4.new_markdown_cell("## 3. Limpeza Restrita (DropNA)"),
        nbf.v4.new_code_cell("""# Agora sim, vamos remover as linhas que possuem nulos para podermos calcular a matriz de correlação\ndf_eda = df[cols_validas + [target]].dropna()\n\nprint(f"Base de dados validada (apenas alunos que responderam a todas as {len(cols_validas)} perguntas): {len(df_eda):,} registros")"""),

        nbf.v4.new_markdown_cell("## 4. Correlação Não-Linear (Spearman)"),
        nbf.v4.new_code_cell("""from sklearn.preprocessing import OrdinalEncoder\n\ncat_cols = df_eda[cols_validas].select_dtypes(include=['object', 'category']).columns.tolist()\n\ndf_corr = df_eda.copy()\nif cat_cols:\n    enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)\n    df_corr[cat_cols] = enc.fit_transform(df_eda[cat_cols])\n\ncorr = df_corr.corr(method='spearman')\n\nplt.figure(figsize=(14, 10))\nsns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)\nplt.title("Matriz de Correlação de Spearman - Features Expandidas")\nplt.show()"""),
        
        nbf.v4.new_markdown_cell("## 5. Teste Rápido de Importância (Feature Importance)"),
        nbf.v4.new_code_cell("""from sklearn.ensemble import RandomForestRegressor\nfrom sklearn.model_selection import train_test_split\n\n# Para não demorar horas no laboratório, vamos treinar uma árvore com uma amostra de 150 mil registros\ndf_sample = df_corr.sample(n=150000, random_state=42)\n\nX = df_sample[cols_validas]\ny = df_sample[target]\n\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\nprint("Treinando Random Forest Regressor para extrair a importância bruta...")\nrf = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)\nrf.fit(X_train, y_train)\n\n# R² da Amostra\nr2 = rf.score(X_test, y_test)\nprint(f"R² do modelo expandido na amostra: {r2:.4f}")\n\n# Obter as feature importances brutas (Gini impurity)\nimportances = rf.feature_importances_\n\nimport_df = pd.DataFrame({'Feature': cols_validas, 'Importancia': importances}).sort_values('Importancia', ascending=False)\n\nplt.figure(figsize=(12, 6))\nsns.barplot(x='Importancia', y='Feature', data=import_df, palette='viridis')\nplt.title("Ranking de Importância (Baseline Gini Impurity)")\nplt.show()""")
    ]
    
    os.makedirs('notebooks', exist_ok=True)
    with open('notebooks/02_selecao_features_v2.ipynb', 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print("Notebook gerado com sucesso!")

if __name__ == "__main__":
    create_notebook()
