import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

nb['cells'] = [
    nbf.v4.new_markdown_cell("# 3. Estudo de Viabilidade: Auditoria Histórica (Schema Drift)\n\nAntes de conectarmos 15 anos de dados em um pipeline de Big Data, precisamos provar se os dados antigos (2009 a 2016) possuem compatibilidade de dicionário com o nosso padrão-ouro de 2023.\n\nEste notebook varre as pastas de dados brutos e realiza uma **Leitura Cega** apenas do cabeçalho dos arquivos. O objetivo é identificar onde o INEP quebrou a estrutura de dados (Schema Drift) e quais variáveis sumiram ou mudaram de nome no passado."),
    
    nbf.v4.new_code_cell("""import pandas as pd
import os
import glob
import warnings

warnings.filterwarnings('ignore')

# Nosso "Esquadrão de Elite" + Targets
features_oficiais = ['Q006', 'Q024', 'TP_ANO_CONCLUIU', 'TP_LINGUA', 'TP_SEXO', 'Q002', 'NU_NOTA_MT', 'NU_NOTA_LC']

print("Variáveis requeridas para harmonização:")
print(features_oficiais)"""),

    nbf.v4.new_markdown_cell("## 1. Scanner de Arquivos\nVamos procurar todos os anos disponíveis na pasta `data/raw/`."),

    nbf.v4.new_code_cell("""raw_dir = '../data/raw'
# Encontrar todos os diretórios de anos
anos_dirs = sorted(glob.glob(os.path.join(raw_dir, 'enem_*')))

arquivos_csv = {}
for dir_path in anos_dirs:
    ano = os.path.basename(dir_path).split('_')[1]
    # Busca o CSV principal lá dentro (ignorando maiúsculas/minúsculas)
    csv_files = glob.glob(os.path.join(dir_path, '**', '*.csv'), recursive=True)
    # Filtra arquivos pequenos ou de dicionário (busca o principal)
    for f in csv_files:
        if os.path.basename(f).upper().startswith('MICRODADOS_ENEM'):
            arquivos_csv[ano] = f
            break

print(f"Encontrados arquivos CSV para {len(arquivos_csv)} anos:")
for ano, path in arquivos_csv.items():
    print(f"- {ano}: {os.path.basename(path)}")"""),

    nbf.v4.new_markdown_cell("## 2. Auditoria de Colunas (Schema Audit)\nVamos ler APENAS a primeira linha de cada CSV (super rápido, não trava a memória) para extrair as colunas e bater contra o nosso padrão-ouro."),

    nbf.v4.new_code_cell("""resultados_auditoria = []

for ano in sorted(arquivos_csv.keys()):
    caminho = arquivos_csv[ano]
    try:
        # Lê apenas 5 linhas para capturar o cabeçalho
        df_amostra = pd.read_csv(caminho, sep=';', encoding='latin-1', nrows=5)
        colunas_ano = df_amostra.columns.tolist()
        
        ausentes = [feat for feat in features_oficiais if feat not in colunas_ano]
        status = "✅ PERFEITO" if not ausentes else "❌ DRIFT ENCONTRADO"
        
        resultados_auditoria.append({
            'Ano': ano,
            'Total Colunas': len(colunas_ano),
            'Status': status,
            'Variáveis Ausentes': ", ".join(ausentes) if ausentes else "Nenhuma"
        })
    except Exception as e:
        print(f"Erro ao ler o ano {ano}: {e}")

df_auditoria = pd.DataFrame(resultados_auditoria)
display(df_auditoria)"""),

    nbf.v4.new_markdown_cell("## 3. Matriz de Decisão (Keep/Drop)\nCom base na tabela acima, defina quais anos serão eliminados da tese devido à alta complexidade de harmonização estatística. Anos com `❌ DRIFT ENCONTRADO` na Renda (`Q006`) ou no Computador (`Q024`) exigiriam metodologias de imputação retroativa não suportadas pela literatura do INEP. A recomendação acadêmica é excluí-los da base de treinamento oficial.")
]

os.makedirs('notebooks', exist_ok=True)
notebook_path = 'notebooks/03_analise_harmonizacao_historica.ipynb'

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook {notebook_path} gerado com sucesso!")
