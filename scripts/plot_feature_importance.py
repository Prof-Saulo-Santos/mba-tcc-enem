import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance

def main():
    print("Carregando os dados da camada Silver...")
    data_path = "data/processed/enem_2023_silver.parquet"
    
    if not os.path.exists(data_path):
        print(f"Erro: Arquivo {data_path} não encontrado.")
        print("Por favor, rode o pipeline de extração primeiro.")
        return

    # 1. Carregar os Dados
    df = pd.read_parquet(data_path)
    
    # 2. Preparar Features e Target
    features = ["TP_SEXO", "TP_ESCOLA", "Q001", "Q002", "Q006"]
    target = "NU_NOTA_MT"
    
    df_model = df[features + [target]].dropna()
    
    # Amostragem para cálculo rápido (A permutação é muito pesada computacionalmente)
    # Usaremos 200.000 registros, o que é mais do que suficiente estatisticamente.
    df_sample = df_model.sample(n=200000, random_state=42)
    
    X = df_sample[features]
    y = df_sample[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. Pipeline de Preprocessamento
    preprocessor = ColumnTransformer(transformers=[
        ('ord', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), features)
    ])
    
    # 4. Pipeline do Modelo Vencedor (HistGB)
    pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('model', HistGradientBoostingRegressor(random_state=42))
    ])
    
    print("Treinando o modelo HistGradientBoosting...")
    pipe.fit(X_train, y_train)
    
    # 5. Calcular Permutation Importance
    # Como o HistGB é baseado em histogramas contínuos, ele não expõe feature_importances_ diretamente 
    # de forma confiável no scikit-learn. O método científico correto é a Permutação.
    print("Calculando a Importância das Features (Permutation Importance)... isso pode demorar alguns segundos.")
    result = permutation_importance(pipe, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1)
    
    # 6. Organizar os Resultados
    importance_df = pd.DataFrame({
        'Feature': features,
        'Importance': result.importances_mean,
        'Std': result.importances_std
    })
    
    # Mapeamento para nomes amigáveis no gráfico
    nomes_amigaveis = {
        "Q006": "Renda Familiar",
        "Q001": "Escolaridade do Pai",
        "Q002": "Escolaridade da Mãe",
        "TP_ESCOLA": "Tipo de Escola",
        "TP_SEXO": "Sexo (Viés Estrutural)"
    }
    importance_df['Feature Name'] = importance_df['Feature'].map(nomes_amigaveis)
    importance_df = importance_df.sort_values('Importance', ascending=False)
    
    # 7. Plotar
    print("\nRanking de Importância:")
    print(importance_df[['Feature Name', 'Importance']])
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature Name', data=importance_df, palette='viridis')
    
    # Adicionar linha de erro (desvio padrão)
    plt.errorbar(
        x=importance_df['Importance'],
        y=range(len(importance_df)),
        xerr=importance_df['Std'],
        fmt='none', c='black', capsize=5
    )
    
    plt.title('Importância Sociológica das Features (Permutation Importance)\nModelo: HistGradientBoosting | Target: Matemática', fontsize=14)
    plt.xlabel('Queda no R² caso a variável seja removida (Peso da Importância)')
    plt.ylabel('')
    plt.tight_layout()
    
    # 8. Salvar o Gráfico
    os.makedirs("media", exist_ok=True)
    out_img = "media/feature_importance.png"
    plt.savefig(out_img, dpi=300)
    print(f"\nGráfico salvo com sucesso em: {out_img}")
    plt.show()

if __name__ == "__main__":
    main()
