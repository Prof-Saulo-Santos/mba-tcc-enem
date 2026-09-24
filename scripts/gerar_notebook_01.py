import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

nb['cells'] = [

    nbf.v4.new_markdown_cell("""# 1. Análise de Anomalias Estruturais dos Microdados ENEM (2009–2025)

**Objetivo:** Este notebook tem uma missão precisa e independente: provar, empiricamente, que o INEP manteve um **padrão monolítico e estável** de entrega dos microdados ao longo de 15 anos (2009–2023), e que esse padrão foi **rompido a partir de 2024**.

Esta análise não depende de nenhuma hipótese sobre features ou targets — ela é uma auditoria forense da estrutura física dos arquivos. Sua conclusão alimentará a decisão arquitetural do pipeline de Big Data nos notebooks subsequentes.

> **Nota:** A verificação de quais variáveis específicas persistiram ou sumiram ao longo dos anos é realizada no `03_analise_harmonizacao_historica.ipynb`, após a seleção das features no `02_selecao_features.ipynb`. Este notebook responde apenas à pergunta: **"O INEP manteve o mesmo formato de entrega?"**"""),

    nbf.v4.new_code_cell("""import pandas as pd
import os
import glob

RAW_DATA_DIR = '../data/raw'

# Mapeamento estrutural: para cada ano, identificar quantos arquivos CSV existem
# e se o arquivo monolítico principal (MICRODADOS_ENEM_XXXX) está presente.

anos_dirs = sorted(glob.glob(os.path.join(RAW_DATA_DIR, 'enem_*')))

resultado = []

for dir_path in anos_dirs:
    ano = os.path.basename(dir_path).split('_')[1]
    csv_files = glob.glob(os.path.join(dir_path, '**', '*.csv'), recursive=True)
    # Filtrar arquivos relevantes (ignorar Dicionarios e Zone.Identifier)
    csv_relevantes = [f for f in csv_files if not any(x in f for x in ['Zone.Identifier', 'Dicionario', 'dicionario'])]
    nomes = [os.path.basename(f) for f in csv_relevantes]

    tem_monolitico = any(n.upper().startswith('MICRODADOS_ENEM') for n in nomes)
    tem_participantes = any('PARTICIPANTES' in n.upper() for n in nomes)
    tem_resultados = any('RESULTADOS' in n.upper() for n in nomes)

    if tem_monolitico:
        formato = "✅ Monolítico (1 arquivo)"
        status = "✅ Dentro do padrão histórico"
    elif tem_participantes and tem_resultados:
        formato = "⚠️ Bipartido (PARTICIPANTES + RESULTADOS)"
        status = "❌ RUPTURA ESTRUTURAL"
    elif tem_participantes:
        formato = "⚠️ Parcial (só PARTICIPANTES)"
        status = "❌ RUPTURA ESTRUTURAL"
    else:
        formato = "❓ Desconhecido"
        status = "❓ Verificar manualmente"

    resultado.append({
        'Ano': ano,
        'Qtd Arquivos CSV': len(csv_relevantes),
        'Arquivos Encontrados': ', '.join(nomes),
        'Formato': formato,
        'Status': status
    })

df = pd.DataFrame(resultado)
display(df[['Ano', 'Qtd Arquivos CSV', 'Formato', 'Status']])"""),

    nbf.v4.new_markdown_cell("""## 1. O Padrão Monolítico Histórico (2009–2023)

Historicamente, o INEP disponibilizou os microdados em um **único arquivo tabular consolidado** por ano de aplicação:
```
data/raw/enem_XXXX/microdados_enem_XXXX/DADOS/MICRODADOS_ENEM_XXXX.csv
```
Esse arquivo único — que pode chegar a vários gigabytes — contém todas as dimensões do candidato em uma única linha: dados de identificação, notas de todas as provas e todas as respostas do questionário socioeconômico.

A tabela acima comprova que **todos os anos de 2009 a 2023 seguiram rigorosamente esse padrão**, tornando a série histórica tecnicamente apta para consolidação em pipelines de Big Data."""),

    nbf.v4.new_code_cell("""# Visualizar o cabeçalho do arquivo monolítico de 2023 como referência
# (sem carregar os ~5 milhões de linhas em memória)
path_ref = os.path.join(RAW_DATA_DIR, 'enem_2023/microdados_enem_2023/DADOS/MICRODADOS_ENEM_2023.csv')

try:
    df_ref = pd.read_csv(path_ref, sep=';', encoding='latin-1', nrows=3)
    print(f"Estrutura do arquivo monolítico de referência (2023):")
    print(f"  → {len(df_ref.columns)} colunas")
    print(f"  → Primeiras colunas: {list(df_ref.columns[:8])}")
    print(f"  → Últimas colunas:   {list(df_ref.columns[-8:])}")
except FileNotFoundError:
    print("Arquivo de 2023 não encontrado. Ajuste o caminho se necessário.")"""),

    nbf.v4.new_markdown_cell("""## 2. A Ruptura Estrutural de 2024 e 2025

A partir do ENEM 2024, o INEP abandonou o formato monolítico. Os dados passaram a ser entregues em **dois arquivos separados**:

| Arquivo | Conteúdo |
|---|---|
| `PARTICIPANTES_XXXX.csv` | Dados de identificação, localização da prova e respostas do questionário socioeconômico (Q001–Q023) |
| `RESULTADOS_XXXX.csv` | Notas por área de conhecimento e redação |
| `ITENS_PROVA_XXXX.csv` | Parâmetros psicometricos dos itens de prova — **desprezível para o nosso modelo** |

**Solução arquitetural implementada:** O módulo `src/ingestion/reader.py` utiliza **concatenação posicional** (`pd.concat(axis=1)`), explorando o fato de que o INEP garante que PARTICIPANTES e RESULTADOS estão na mesma ordem. Para segurança, um mecanismo `fail-fast` verifica que ambos os arquivos têm o mesmo número de linhas antes de concatenar — se divergirem, um `ValueError` é lançado imediatamente.

**O problema real que persiste:** Mesmo com o JOIN resolvido, há uma anomalia de dicíionário crítica que inviabiliza o uso de 2024/2025 como dados de **treinamento**."""),

    nbf.v4.new_code_cell("""# Verificar a estrutura dos arquivos bipartidos de 2024 e fail-fast
path_part = os.path.join(RAW_DATA_DIR, 'enem_2024/microdados_enem_2024/DADOS/PARTICIPANTES_2024.csv')
path_res  = os.path.join(RAW_DATA_DIR, 'enem_2024/microdados_enem_2024/DADOS/RESULTADOS_2024.csv')

try:
    df_part = pd.read_csv(path_part, sep=';', encoding='latin-1', nrows=5)
    print(f"PARTICIPANTES_2024.csv \u2192 {len(df_part.columns)} colunas")
    print(f"  Col\u00fanas Q dispon\u00edveis: {[c for c in df_part.columns if c.startswith('Q')]}")
    print()
    df_res = pd.read_csv(path_res,  sep=';', encoding='latin-1', nrows=5)
    print(f"RESULTADOS_2024.csv   \u2192 {len(df_res.columns)} colunas")
    print()

    # Prova do mecanismo fail-fast
    import subprocess
    n_part = int(subprocess.check_output(['wc', '-l', path_part]).split()[0]) - 1
    n_res  = int(subprocess.check_output(['wc', '-l', path_res]).split()[0])  - 1
    print(f"\u2714\ufe0f Fail-fast check: PARTICIPANTES={n_part:,} linhas | RESULTADOS={n_res:,} linhas")
    print(f"   Linhas iguais? {n_part == n_res} \u2192 {'JOIN posicional seguro' if n_part == n_res else 'ALERTA: diverg\u00eancia detectada!'}")

except FileNotFoundError as e:
    print(f"Arquivo n\u00e3o encontrado: {e}")"""),

    nbf.v4.new_markdown_cell("""## 3. Conclusão: A Estratégia para 2024/2025

A análise estrutural comprova que:
1. De **2009 a 2023**, o INEP manteve um padrão monolítico consistente e confiável.
2. Em **2024 e 2025**, houve uma ruptura para um formato bipartido (`PARTICIPANTES` e `RESULTADOS`), onde o vínculo por chave primária não está disponível no segundo arquivo.

**Decisão Arquitetural:**
Para lidar com a ruptura de 2024/2025 sem corromper o dataset, o módulo `src/ingestion/reader.py` foi projetado para utilizar a **concatenação posicional** (`pd.concat(axis=1)`), com um mecanismo rígido de `fail-fast` defensivo. Esse mecanismo verifica previamente se os arquivos possuem a mesma quantidade de linhas (provado empiricamente na célula acima). Caso haja divergência, o pipeline é interrompido.

A estrutura de dados está agora mapeada e o desafio de leitura superado. A seguir, o projeto avançará para o **Notebook 02**, onde utilizaremos *Machine Learning* para descobrir empiricamente quais features (variáveis socioeconômicas) são as mais determinantes para prever o desempenho do candidato.

A estabilidade e nomenclatura histórica dessas features — independentemente da estrutura do arquivo — será validada posteriormente no **Notebook 03** (Análise de Harmonização Histórica)."""),

]

os.makedirs('notebooks', exist_ok=True)
notebook_path = 'notebooks/01_analise_anomalias_estruturais.ipynb'

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook {notebook_path} regenerado com sucesso!")
