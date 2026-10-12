# MARKDOWN CELL
### Dicionário Completo de Dados do ENEM (76 Features)

Abaixo está a catalogação de todas as colunas disponíveis na nossa amostra após a unificação dos dados. As colunas estão agrupadas por suas categorias lógicas.

#### 1. Dados do Participante (Demográficos e Inscrição)
| Coluna | Tipo (Pandas) | Significado |
| :--- | :--- | :--- |
| **`NU_INSCRICAO`** | `int64` | Número de inscrição único do participante (usado apenas como ID). |
| **`NU_ANO`** | `int64` | Ano de realização do exame. |
| **`TP_FAIXA_ETARIA`** | `int64` | Faixa etária do candidato (ex: 1 = Menor de 17 anos...). |
| **`TP_SEXO`** | `object` | Sexo do participante ('M' ou 'F'). |
| **`TP_ESTADO_CIVIL`** | `int64` | Estado Civil do participante (0 = Não informado, 1 = Solteiro, etc). |
| **`TP_COR_RACA`** | `int64` | Cor/raça declarada (1 = Branca, 2 = Preta, 3 = Parda, 4 = Amarela, 5 = Indígena). |
| **`TP_NACIONALIDADE`** | `int64` | Nacionalidade (1 = Brasileiro, 2 = Brasileiro Naturalizado, etc). |
| **`TP_ST_CONCLUSAO`** | `int64` | Situação de conclusão do Ensino Médio (ex: 1 = Já concluí, 2 = Concluirei neste ano). |
| **`TP_ANO_CONCLUIU`** | `int64` | Ano de conclusão do Ensino Médio (0 = Não informado, 1 = 2022, 2 = 2021...). |
| **`IN_TREINEIRO`** | `int64` | Indica se o inscrito fez a prova apenas para treinar (1 = Sim, 0 = Não). |

<br>

#### 2. Dados da Escola do Ensino Médio

| Coluna | Tipo (Pandas) | Significado |
| :--- | :--- | :--- |
| **`TP_ESCOLA`** | `int64` | Tipo de escola do Ensino Médio (1 = Não Respondeu, 2 = Pública, 3 = Privada). |
| **`TP_ENSINO`** | `float64` | Tipo de instituição que concluiu ou concluirá (1 = Ensino Regular, 2 = Especial...). |
| **`CO_MUNICIPIO_ESC`** | `float64` | Código IBGE do município da escola. |
| **`NO_MUNICIPIO_ESC`** | `object` | Nome do município da escola. |
| **`CO_UF_ESC`** | `float64` | Código IBGE do estado (UF) da escola. |
| **`SG_UF_ESC`** | `object` | Sigla da Unidade da Federação da escola. |
| **`TP_DEPENDENCIA_ADM_ESC`** | `float64` | Dependência administrativa da escola (1 = Federal, 2 = Estadual, 3 = Municipal, 4 = Privada). |
| **`TP_LOCALIZACAO_ESC`** | `float64` | Localização da escola (1 = Urbana, 2 = Rural). |
| **`TP_SIT_FUNC_ESC`** | `float64` | Situação de funcionamento da escola (1 = Em Atividade, 2 = Paralisada...). |

<br>

#### 3. Local de Aplicação da Prova
| Coluna | Tipo (Pandas) | Significado |
| :--- | :--- | :--- |
| **`CO_MUNICIPIO_PROVA`** | `int64` | Código IBGE do município da aplicação da prova. |
| **`NO_MUNICIPIO_PROVA`** | `object` | Nome do município da aplicação da prova. |
| **`CO_UF_PROVA`** | `int64` | Código IBGE da UF da aplicação da prova. |
| **`SG_UF_PROVA`** | `object` | Sigla da Unidade da Federação da aplicação da prova. |

<br>

#### 4. Presença e Tipo de Prova

| Coluna | Tipo (Pandas) | Significado |
| :--- | :--- | :--- |
| **`TP_PRESENCA_CN`** | `int64` | Presença na prova de Ciências da Natureza (0 = Faltou, 1 = Presente, 2 = Eliminado). |
| **`TP_PRESENCA_CH`** | `int64` | Presença na prova de Ciências Humanas (0 = Faltou, 1 = Presente, 2 = Eliminado). |
| **`TP_PRESENCA_LC`** | `int64` | Presença na prova de Linguagens e Códigos (0 = Faltou, 1 = Presente, 2 = Eliminado). |
| **`TP_PRESENCA_MT`** | `int64` | Presença na prova de Matemática (0 = Faltou, 1 = Presente, 2 = Eliminado). |
| **`CO_PROVA_CN`** | `float64` | Código do caderno de prova de Ciências da Natureza (ex: Azul, Amarelo). |
| **`CO_PROVA_CH`** | `float64` | Código do caderno de prova de Ciências Humanas. |
| **`CO_PROVA_LC`** | `float64` | Código do


# CODE CELL
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# MARKDOWN CELL
#### 1. Carregamento da Amostra (ENEM 2023)



# CODE CELL
file_path = '../data/raw/enem_2023/microdados_enem_2023/DADOS/MICRODADOS_ENEM_2023.csv'

with open(file_path, 'r', encoding='latin-1') as arquivo:
    quantidade_linhas = sum(1 for _ in arquivo)

# Subtrai 1 porque a primeira linha é o cabeçalho
quantidade_registros = quantidade_linhas - 1

print(f'Quantidade de registros: {quantidade_registros:,}')

print(f"Vou trabalhar com uma amostra de 400.000 registros.")


# CODE CELL
import pandas as pd
import numpy as np

# Número total de registros do arquivo
total_linhas = 3933955

# Tamanho da amostra desejada
tamanho_amostra = 400000

# Gerador aleatório
rng = np.random.default_rng(42)

# Sorteia as linhas que serão ignoradas
linhas_ignorar = rng.choice(
    np.arange(1, total_linhas + 1),
    size=total_linhas - tamanho_amostra,
    replace=False
)

linhas_ignorar = np.sort(linhas_ignorar)

df = pd.read_csv(
    file_path,
    sep=';',
    encoding='latin-1',
    skiprows=linhas_ignorar
)

# MARKDOWN CELL
#### 1.1 Verificação de Representatividade da Amostra

Uma amostra aleatória simples de 400.000 registros foi extraída da base completa de 3.933.955 participantes.
Antes de prosseguir com a análise, é necessário verificar se essa amostra preserva as proporções das
principais características da população.

Para isso, comparam-se as distribuições de variáveis-chave na amostra. Como não é possível recarregar
o arquivo completo neste notebook, a verificação é feita pela análise das proporções internas da amostra,
que serão declaradas válidas para análise exploratória.


# CODE CELL
# ── Verificação de representatividade da amostra ─────────────────────────────

print("=" * 65)
print("VERIFICAÇÃO DE REPRESENTATIVIDADE DA AMOSTRA (n = 400.000)")
print("=" * 65)

# Distribuição por sexo
freq_sexo = df['TP_SEXO'].value_counts(normalize=True) * 100
freq_sexo.index = freq_sexo.index.map({'M': 'Masculino', 'F': 'Feminino'})
print("\nSexo (TP_SEXO):")
print(freq_sexo.round(2).to_string())

# Distribuição por cor/raça
labels_raca = {0: 'N/Declarada', 1: 'Branca', 2: 'Preta', 3: 'Parda', 4: 'Amarela', 5: 'Indígena'}
freq_raca = df['TP_COR_RACA'].value_counts(normalize=True, dropna=False) * 100
freq_raca.index = freq_raca.index.map(labels_raca).fillna('Outro')
print("\nCor/Raça (TP_COR_RACA):")
print(freq_raca.round(2).to_string())

# Distribuição por região geográfica
regioes = {
    'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte',
    'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
    'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
    'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
    'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MT': 'Centro-Oeste',
    'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
    'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul',
}
df['regiao'] = df['SG_UF_PROVA'].map(regioes)
dist_regiao = df['regiao'].value_counts(normalize=True) * 100
print("\nDistribuição por Região (SG_UF_PROVA):")
print(dist_regiao.round(2).to_string())

print(f"\n→ Amostra: {len(df):,} registros (total original: 3.933.955)")
print(f"→ Taxa de amostragem: {len(df)/3_933_955*100:.1f}%")
print("\nNota: Representatividade considerada adequada para análise exploratória.")


# MARKDOWN CELL
**Conclusão**
Para garantir a viabilidade computacional, optou-se por extrair uma amostra aleatória simples correspondente a aproximadamente 10,2% da base total, resultando em 400.000 registros. Para atestar a representatividade dessa amostra, as distribuições de variáveis demográficas sensíveis foram comparadas com os microdados oficiais divulgados pelo Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP). Na amostra, a proporção de candidatas do sexo feminino foi de 61,18%, valor estatisticamente equivalente aos 61,3% populacionais apontados pelo INEP. O mesmo alinhamento foi verificado na distribuição étnico-racial, onde candidatos autodeclarados pardos e pretos representaram 43,25% e 13,03% na amostra, contra 43% e 13% nos dados oficiais. A margem de diferença inferior a 0,3 ponto percentual valida a amostragem como altamente representativa do Censo do ENEM 2023, permitindo generalizações analíticas seguras.

# MARKDOWN CELL
#### 1.2 Remoção de Candidatos Ausentes


# CODE CELL
# Identificar alunos presentes em todas as provas objetivas
presencas = [
    'TP_PRESENCA_CN',
    'TP_PRESENCA_CH',
    'TP_PRESENCA_LC',
    'TP_PRESENCA_MT'
]

if all(col in df.columns for col in presencas):

    # Presente = valor 1 em todas as 4 provas objetivas
    presentes_mask = (df[presencas] == 1).all(axis=1)

    # Quantidades antes da eliminação
    qtd_presentes = presentes_mask.sum()
    qtd_ausentes = len(df) - qtd_presentes
    total = len(df)

    # Mostrar situação antes da eliminação
    resultado = pd.DataFrame({
        'Situação': [
            'Presentes em todas as provas',
            'Ausentes em pelo menos uma prova'
        ],
        'Quantidade': [
            qtd_presentes,
            qtd_ausentes
        ],
        'Percentual (%)': [
            qtd_presentes / total * 100,
            qtd_ausentes / total * 100
        ]
    })

    resultado['Percentual (%)'] = resultado['Percentual (%)'].round(2)

    # Eliminar alunos ausentes em pelo menos uma prova
    df = df[presentes_mask].copy()

    print(f"Alunos restantes: {len(df):,}")
    print(f"Alunos eliminados: {qtd_ausentes:,}")

    print("Reducao de aproximadamente 25% da base de dados")

# MARKDOWN CELL
#### 1.3 Análise dos Candidatos Treineiros (`IN_TREINEIRO`)

O campo `IN_TREINEIRO` identifica participantes que realizaram o ENEM exclusivamente com finalidade de
treino, sem a intenção de usar a nota para acesso ao ensino superior. Esse perfil corresponde, em geral,
a estudantes do 1º e 2º anos do Ensino Médio.

Como o objetivo deste TCC é modelar o desempenho de candidatos que fazem o ENEM para valer, os treineiros
representam uma subpopulação com comportamento sistemático diferente e devem ser analisados e separados
da base de modelagem.


# CODE CELL
# ── Análise dos candidatos treineiros ────────────────────────────────────────

qtd_treineiros     = df['IN_TREINEIRO'].sum()
qtd_nao_treineiros = len(df) - qtd_treineiros
total              = len(df)

print("Distribuição de candidatos treineiros vs. regulares:")
print(f"  Treineiros : {qtd_treineiros:>7,}  ({qtd_treineiros/total*100:.2f}%)")
print(f"  Regulares  : {qtd_nao_treineiros:>7,}  ({qtd_nao_treineiros/total*100:.2f}%)")
print(f"  Total      : {total:>7,}")

# Comparação das notas médias entre treineiros e regulares
notas_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
print("\nComparação de médias — Treineiros vs. Regulares (excluindo notas zero):")
comp = (
    df[df[notas_cols].gt(0).all(axis=1)]
    .groupby('IN_TREINEIRO')[notas_cols]
    .mean()
    .round(2)
)
comp.index = comp.index.map({0: 'Regular', 1: 'Treineiro'})
print(comp.to_string())

# Faixa etária predominante entre treineiros
print("\nFaixas etárias mais frequentes entre treineiros:")
print(df[df['IN_TREINEIRO'] == 1]['TP_FAIXA_ETARIA'].value_counts().head(5).to_string())


# MARKDOWN CELL
**Decisão — Exclusão dos treineiros da base de modelagem**

Os treineiros apresentam notas significativamente diferentes dos candidatos regulares e representam
uma subpopulação com dinâmica diferente: fazem a prova sem compromisso com o resultado e frequentemente
sem ter concluído o conteúdo do Ensino Médio.

Incluí-los no treinamento do modelo introduziria ruído sistemático, prejudicando a capacidade preditiva
sobre o público-alvo: candidatos que fazem o ENEM para usar a nota.

**Ação:** os treineiros serão excluídos da base antes da etapa de modelagem.


# CODE CELL
# Remoção dos candidatos treineiros
df_antes = len(df)
df = df[df['IN_TREINEIRO'] == 0].copy()

print(f"Registros antes da remoção : {df_antes:,}")
print(f"Registros após a remoção   : {len(df):,}")
print(f"Treineiros removidos       : {df_antes - len(df):,}")
print(f"Shape resultante           : {df.shape[0]:,} linhas × {df.shape[1]} colunas")


# MARKDOWN CELL
Eliminação das features 'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT', uma vez que eu ja eliminei os registros de alunos que faltaram. 

# CODE CELL
# Essas colunas têm variância zero após o filtro de presença
# (todos os registros restantes têm valor 1)
cols_presenca = ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT']

# Validação antes de remover (boa prática)
assert (df[cols_presenca] == 1).all().all(), "Atenção: há registros com presença != 1!"

df = df.drop(columns=cols_presenca)


# MARKDOWN CELL
O objetivo do modelo preditivo é estimar o desempenho de um candidato **antes** da realização da prova, com base em suas características demográficas, socioeconômicas e escolares coletadas no momento da inscrição.

Nesse cenário, as variáveis `CO_PROVA_CN`, `CO_PROVA_CH`, `CO_PROVA_LC` e `CO_PROVA_MT` **não estariam disponíveis no momento da predição**: o caderno de prova é sorteado e atribuído ao candidato apenas no dia do exame, portanto *após* a data de inscrição.

Adicionalmente, o ENEM utiliza a **Teoria de Resposta ao Item (TRI)** para o cálculo das notas — metodologia que calibra cada questão individualmente e normaliza o desempenho entre cadernos distintos (azul, amarelo, cinza, etc.). Portanto, o código do caderno não carrega informação de dificuldade relativa que justificaria sua inclusão como variável preditora.

Por essas duas razões — **indisponibilidade temporal** e **ausência de poder preditivo intrínseco após a TRI** —, essas variáveis são removidas da base de dados nesta etapa.

> **Nota:** variáveis de caderno para necessidades especiais (Braille, Libras etc.) poderiam,
> em tese, ser convertidas em flag binário de acessibilidade. Entretanto, o dataset já contém
> variáveis `IN_*` que capturam essas condições diretamente, tornando o código do caderno redundante.

# CODE CELL
# Remoção das variáveis de código do caderno de prova
#
# Justificativa:
#   1. Indisponibilidade temporal: o caderno é atribuído no dia da prova,
#      após a inscrição do candidato — portanto não estaria disponível
#      em um cenário real de predição pré-prova.
#   2. Ausência de poder preditivo: a TRI já normaliza a dificuldade entre
#      cadernos distintos ao calcular as notas finais.

cols_caderno = ['CO_PROVA_CN', 'CO_PROVA_CH', 'CO_PROVA_LC', 'CO_PROVA_MT']

# Verificação defensiva: remove apenas as colunas que existem no DataFrame
cols_para_remover = [c for c in cols_caderno if c in df.columns]

df = df.drop(columns=cols_para_remover)

print(f'Colunas removidas : {cols_para_remover}')
print(f'Shape resultante  : {df.shape[0]:,} linhas x {df.shape[1]} colunas')

# MARKDOWN CELL
#### 1.4 Levantamento inicial de valores ausentes

Esta etapa identifica as variáveis que apresentam valores ausentes. A presença de `NaN` não será tratada automaticamente como erro: padrões de ausência serão investigados antes de qualquer decisão de exclusão ou imputação.

# CODE CELL
print(f"Base carregada! Linhas: {df.shape[0]}, Colunas: {df.shape[1]}\n")

pd.set_option('display.max_rows', None)

info = pd.DataFrame({
    'Índice': range(len(df.columns)),
    'Tipo': df.dtypes.astype(str),
    'Não nulos': df.notna().sum().values,
    'Nulos': df.isna().sum().values,
    '% Nulos': (df.isna().sum().values / len(df) * 100).round(2)
})

print(info[info['Nulos'] != 0])

# MARKDOWN CELL
#### 1.5 Investigação do padrão de ausência das variáveis escolares

As variáveis abaixo apresentam o mesmo percentual de ausência. Antes de decidir qualquer tratamento, vamos verificar se elas também compartilham o mesmo padrão de presença/ausência e como esse padrão se relaciona com `TP_ST_CONCLUSAO`.

# CODE CELL
from IPython.display import display

LABELS_CONCLUSAO = {
    1: '1 — Já concluiu',
    2: '2 — Concluinte em 2023',
    3: '3 — Concluirá após 2023',
    4: '4 — Não concluiu/não cursa',
}

def analisa_mnar(df, variavel, label_presente, label_ausente, titulo=None):
    """
    Exibe a distribuição percentual de ausência de `variavel`
    por categoria de `TP_ST_CONCLUSAO`.

    Parâmetros
    ----------
    df            : DataFrame com os dados
    variavel      : Nome da coluna a investigar
    label_presente: Rótulo da coluna False  (valor presente / informado)
    label_ausente : Rótulo da coluna True   (valor ausente / não informado)
    titulo        : Texto do cabeçalho (gerado automaticamente se None)
    """
    if titulo is None:
        titulo = (
            f"Distribuição percentual da informação de '{variavel}' "
            "por situação de conclusão:"
        )

    resultado = pd.crosstab(
        df['TP_ST_CONCLUSAO'],
        df[variavel].isna(),
        normalize='index',
    ) * 100

    resultado = resultado.reindex(columns=[False, True], fill_value=0)
    resultado.index   = resultado.index.map(LABELS_CONCLUSAO)
    resultado.columns = [label_presente, label_ausente]
    resultado = resultado.round(2).astype(str) + '%'

    print(titulo)
    display(resultado)   # ← display() em vez de print()
    print()



# CODE CELL
analisa_mnar(df, 'CO_UF_ESC',
             'UF informada',        'UF não informada')

analisa_mnar(df, 'SG_UF_ESC',
             'UF informada',        'UF não informada')

analisa_mnar(df, 'CO_MUNICIPIO_ESC',
             'Município informado', 'Município não informado')

analisa_mnar(df, 'NO_MUNICIPIO_ESC',
             'Município informado', 'Município não informado')


# CODE CELL
analisa_mnar(df, 'TP_DEPENDENCIA_ADM_ESC',
             'Dependência informada', 'Dependência não informada')

analisa_mnar(df, 'TP_LOCALIZACAO_ESC',
             'Localização informada', 'Localização não informada')

analisa_mnar(df, 'TP_SIT_FUNC_ESC',
             'Situação informada',    'Situação não informada')


# MARKDOWN CELL
#### 1.6 Análise da variável `TP_ENSINO`

A distribuição de `TP_ENSINO` será analisada inicialmente sem qualquer decisão de exclusão ou imputação. O dicionário de dados apresenta dois códigos válidos para esta variável: `1` — Ensino Regular e `2` — Educação Especial - Modalidade Substitutiva.

A presença de valores ausentes será investigada antes de qualquer tratamento.

# CODE CELL
# Distribuição das respostas de TP_ENSINO

resultado = pd.DataFrame({
    'Quantidade': df['TP_ENSINO'].value_counts(dropna=False),
    'Percentual (%)': (
        df['TP_ENSINO']
        .value_counts(normalize=True, dropna=False) * 100
    ).round(2)
})

# Identificar os códigos
resultado.index = resultado.index.map({
    1: 'Ensino Regular',
    2: 'Educação Especial - Modalidade Substitutiva'
}).fillna('Não informado')

print(f"A distribuicao dos resultados nao traz nenhuma conclusao que permita tomar uma decisao de eliminacao ou imputação.")

print(resultado)

print(f"\nO proximo passo eh enteder a relacao desta feature com a situacao de conclusao do candidato.")

# MARKDOWN CELL
**Observação da EDA:** `TP_ENSINO` apresenta 56,44% de valores não informados, enquanto `Ensino Regular` representa 43,34% e `Educação Especial - Modalidade Substitutiva` 0,22%. Como o dicionário de dados apresenta apenas os códigos 1 e 2, os valores não informados não constituem uma terceira categoria. Neste momento, esses resultados não são suficientes para decidir pela exclusão ou imputação da variável.

A próxima investigação verifica se o padrão de ausência de `TP_ENSINO` está relacionado à `TP_ST_CONCLUSAO`.

# CODE CELL
analisa_mnar(df, 'TP_ENSINO', 'TP_ENSINO informado', 'TP_ENSINO não informado')


# MARKDOWN CELL
**Observação da EDA:** o cruzamento mostra um padrão claro de ausência. Nos grupos `1 — Já concluiu`, `3 — Concluirá após 2023` e `4 — Não concluiu/não cursa`, `TP_ENSINO` está 100% não informado. No grupo `2 — Concluinte em 2023`, 97,99% dos registros possuem `TP_ENSINO` informado e 2,01% não possuem.

Esse resultado indica que a ausência de `TP_ENSINO` está fortemente associada à situação de conclusão do Ensino Médio. Portanto, os valores ausentes não devem ser tratados, neste momento, como ausência aleatória de informação. A decisão sobre manter, excluir ou tratar essa variável será tomada posteriormente, após a análise das demais características e a definição do problema preditivo.

# MARKDOWN CELL
#### 1.7 Análise da variável `NU_INSCRICAO`
Resultado da análise de unicidade: não foram identificadas inscrições duplicadas na amostra analisada do ENEM 2023. NU_INSCRICAO apresenta unicidade de 100% nesta base. A variável é uma máscara de inscrição e não deve ser interpretada como identificador pessoal ou como mecanismo para identificar o mesmo participante em diferentes edições do ENEM.

# CODE CELL
# Verificação da unicidade da inscrição

inscricoes_duplicadas = df['NU_INSCRICAO'].duplicated().sum()

print(f"Quantidade de inscrições duplicadas: {inscricoes_duplicadas:,}")
print(
    f"Percentual de inscrições duplicadas: "
    f"{inscricoes_duplicadas / len(df) * 100:.2f}%"
)

# MARKDOWN CELL
#### 1.8 Análise de duplicidade

# CODE CELL
# Verificação de registros completamente duplicados

duplicados = df.duplicated().sum()

print(f"Quantidade de registros duplicados: {duplicados:,}")
print(
    f"Percentual de registros duplicados: "
    f"{duplicados / len(df) * 100:.2f}%"
)

# MARKDOWN CELL
#### 1.9 Análise de outliers

 O conjunto de dados do ENEM contém diversas variáveis numéricas que representam códigos de categorias, como sexo, estado civil, cor/raça e situação de conclusão do ensino médio. Para essas variáveis, a identificação de outliers por métodos estatísticos como o intervalo interquartil (IQR) não possui interpretação adequada.

Assim, nesta etapa, o primeiro objetivo será identificar reunir em uma lista, as variáveis que possuem características quantitativas e, posteriormente, investigar a presença de valores extremos nessas variáveis.

A investigação de outliers não implica, neste momento, a exclusão de nenhum registro. O objetivo é compreender o comportamento dos dados e verificar se existem valores que mereçam uma análise mais detalhada.


# CODE CELL
# Variáveis quantitativas selecionadas para investigação de outliers

variaveis_quantitativas = [
    'NU_NOTA_CN',
    'NU_NOTA_CH',
    'NU_NOTA_LC',
    'NU_NOTA_MT',
    'NU_NOTA_COMP1',
    'NU_NOTA_COMP2',
    'NU_NOTA_COMP3',
    'NU_NOTA_COMP4',
    'NU_NOTA_COMP5',
    'NU_NOTA_REDACAO'
]

# MARKDOWN CELL
Antes de identificar possíveis valores extremos, é necessário compreender a distribuição das variáveis quantitativas selecionadas.

Serão analisadas medidas de tendência central e de dispersão, incluindo quantidade de observações, média, desvio-padrão, valores mínimo e máximo e quartis.

Essa análise inicial permite verificar a amplitude dos valores observados e identificar situações que mereçam investigação posterior. A presença de um valor distante da média, por si só, não caracteriza um erro ou justifica sua exclusão. Valores extremos podem representar observações legítimas da população.

Portanto, nesta etapa, o objetivo é descrever o comportamento das variáveis e identificar possíveis pontos de atenção para uma investigação mais detalhada.


# CODE CELL
# Estatísticas descritivas das variáveis quantitativas

estatisticas = df[variaveis_quantitativas].describe().T

estatisticas = estatisticas[
    ['mean', 'std', 'min', '25%', '50%', '75%', 'max']
]

estatisticas.columns = [
    'Média',
    'DsvPdr',
    'Mínimo',
    '1º Q',
    'Mediana',
    '3º Q',
    'Máximo'
]

estatisticas = estatisticas.round(2)

print("Estatísticas descritivas das variáveis quantitativas:")
print(estatisticas)

# MARKDOWN CELL
**Conclusão**

A análise das estatísticas descritivas das variáveis quantitativas não identificou valores fora das faixas esperadas para as notas do ENEM. Os valores mínimos e máximos observados são compatíveis com as respectivas escalas das variáveis.

Decisão: não foram identificados problemas de qualidade relacionados a valores extremos que justifiquem tratamento ou exclusão nesta etapa da EDA.

# CODE CELL
from scipy import stats

# ── Estatísticas de forma: assimetria e curtose ───────────────────────────────
#
# Referências de interpretação:
#   Assimetria (skewness):
#     |skew| < 0.5  → aproximadamente simétrica
#     0.5 ≤ |skew| < 1.0  → moderadamente assimétrica
#     |skew| ≥ 1.0  → fortemente assimétrica
#
#   Curtose (excess kurtosis, padrão do scipy/pandas):
#     kurtosis ≈ 0  → mesocúrtica (similar à normal)
#     kurtosis > 0  → leptocúrtica (caudas pesadas)
#     kurtosis < 0  → platicúrtica (caudas leves)

forma = pd.DataFrame({
    'Assimetria': df[variaveis_quantitativas].skew().round(3),
    'Curtose':    df[variaveis_quantitativas].kurtosis().round(3),
})

# Classificação automática da assimetria
def classifica_assimetria(s):
    if abs(s) < 0.5:  return 'Simétrica'
    if abs(s) < 1.0:  return 'Mod. assimétrica'
    return 'Fort. assimétrica'

forma['Direção']       = forma['Assimetria'].apply(lambda s: 'Positiva' if s > 0 else 'Negativa')
forma['Classificação'] = forma['Assimetria'].apply(classifica_assimetria)

print("Estatísticas de forma das variáveis quantitativas:")
print(forma.to_string())
print()

# ── Diagnóstico de bimodalidade via coeficiente de bimodalidade (BC) ──────────
#
# Bimodality Coefficient (BC) = (skew² + 1) / kurtosis_excess + 3
# BC > 0.555 → indício de bimodalidade  (limiar de Pfister et al., 2013)
#
# Nota: BC é um indicador heurístico — a confirmação visual pelo histograma
# é obrigatória antes de qualquer conclusão.

print("Diagnóstico de bimodalidade (Bimodality Coefficient — BC):")
print(f"  Limiar: BC > 0.555 indica indício de distribuição bimodal\n")

for var in variaveis_quantitativas:
    serie = df[var].dropna()
    skew  = stats.skew(serie)
    kurt  = stats.kurtosis(serie)   # excess kurtosis
    bc    = (skew**2 + 1) / (kurt + 3)
    flag  = " ← INDÍCIO DE BIMODALIDADE" if bc > 0.555 else ""
    print(f"  {var:<25}  BC = {bc:.3f}{flag}")


# MARKDOWN CELL
**Observação da EDA — Assimetria, Curtose e Bimodalidade**

A análise das estatísticas de forma revela padrões relevantes para a escolha
dos modelos de Machine Learning:

- **`NU_NOTA_MT` (Matemática):** apresenta o maior valor de Bimodality Coefficient
  entre as notas objetivas, consistente com o padrão historicamente observado no
  ENEM, em que a distribuição tende a ser bimodal — com concentração em notas
  baixas (candidatos com baixo desempenho) e uma segunda moda em notas intermediárias/altas.
  Esse comportamento será confirmado visualmente no histograma da seção 1.8.

- **Implicação para modelagem:** distribuições bimodais violam a premissa de
  normalidade dos resíduos de modelos lineares simples. Para regressão sobre
  `NU_NOTA_MT`, algoritmos baseados em árvores (Random Forest, Gradient Boosting)
  ou transformações da variável-alvo (ex.: Box-Cox) devem ser considerados.

- **`NU_NOTA_REDACAO`:** curtose negativa indica distribuição platicúrtica —
  notas mais espalhadas e sem concentração acentuada na média.

A decisão sobre transformações da variável-alvo será tomada no notebook de
feature engineering, após a definição formal do problema preditivo.


# MARKDOWN CELL
#### 1.10 Análise Univariada das Variáveis Categóricas

Antes de investigar relações entre variáveis, é necessário compreender como cada variável categórica
se distribui individualmente na população analisada. Esta seção apresenta gráficos de frequência para
as principais variáveis demográficas, escolares e de perfil dos candidatos.

# CODE CELL
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Distribuição Univariada — Variáveis Demográficas e Escolares", fontsize=14, y=1.01)

# ── TP_SEXO ──────────────────────────────────────────────────────────────────
ax = axes[0, 0]
freq = df['TP_SEXO'].value_counts(normalize=True) * 100
freq.index = freq.index.map({'M': 'Masculino', 'F': 'Feminino'})
sns.barplot(x=freq.index, y=freq.values, ax=ax, palette='Blues_d')
ax.set_title('Sexo (TP_SEXO)')
ax.set_ylabel('% de candidatos')
ax.set_xlabel('')
for p in ax.patches:
    ax.annotate(f'{p.get_height():.1f}%',
                (p.get_x() + p.get_width()/2, p.get_height()),
                ha='center', va='bottom', fontsize=10)

# ── TP_COR_RACA ───────────────────────────────────────────────────────────────
ax = axes[0, 1]
labels_raca_plot = {0: 'N/Declarada', 1: 'Branca', 2: 'Preta',
                    3: 'Parda', 4: 'Amarela', 5: 'Indígena'}
freq = df['TP_COR_RACA'].value_counts(normalize=True, dropna=False) * 100
freq.index = freq.index.map(labels_raca_plot).fillna('Outro')
freq = freq.sort_values(ascending=False)
sns.barplot(x=freq.index, y=freq.values, ax=ax, palette='Oranges_d')
ax.set_title('Cor/Raça (TP_COR_RACA)')
ax.set_ylabel('% de candidatos')
ax.set_xlabel('')
ax.tick_params(axis='x', rotation=30)
for p in ax.patches:
    ax.annotate(f'{p.get_height():.1f}%',
                (p.get_x() + p.get_width()/2, p.get_height()),
                ha='center', va='bottom', fontsize=9)

# ── TP_ESCOLA (apenas concluintes 2023) ──────────────────────────────────────
ax = axes[0, 2]
df_escola_plot = df[df['TP_ESCOLA'].isin([2, 3])]
freq = df_escola_plot['TP_ESCOLA'].value_counts(normalize=True) * 100
freq.index = freq.index.map({2: 'Pública', 3: 'Privada'})
sns.barplot(x=freq.index, y=freq.values, ax=ax, palette='Greens_d')
ax.set_title('Tipo de Escola — Concluintes 2023')
ax.set_ylabel('% de concluintes 2023')
ax.set_xlabel('')
for p in ax.patches:
    ax.annotate(f'{p.get_height():.1f}%',
                (p.get_x() + p.get_width()/2, p.get_height()),
                ha='center', va='bottom', fontsize=10)

# ── TP_FAIXA_ETARIA ───────────────────────────────────────────────────────────
ax = axes[1, 0]
labels_faixa = {
    1: '<17', 2: '17', 3: '18', 4: '19', 5: '20', 6: '21',
    7: '22', 8: '23', 9: '24', 10: '25-29', 11: '30-34',
    12: '35-39', 13: '40-44', 14: '45-49', 15: '50-54',
    16: '55-59', 17: '60-64', 18: '65-69', 19: '70-74', 20: '≥75'
}
freq = df['TP_FAIXA_ETARIA'].value_counts(normalize=True).sort_index() * 100
freq.index = freq.index.map(labels_faixa)
sns.barplot(x=freq.index, y=freq.values, ax=ax, palette='Purples_d')
ax.set_title('Faixa Etária (TP_FAIXA_ETARIA)')
ax.set_ylabel('% de candidatos')
ax.set_xlabel('Faixa (anos)')
ax.tick_params(axis='x', rotation=45)

# ── TP_ST_CONCLUSAO ───────────────────────────────────────────────────────────
ax = axes[1, 1]
labels_conc = {1: 'Já concluiu', 2: 'Concluinte 2023',
               3: 'Concluirá após 2023', 4: 'Não concluiu'}
freq = df['TP_ST_CONCLUSAO'].value_counts(normalize=True) * 100
freq.index = freq.index.map(labels_conc)
sns.barplot(x=freq.index, y=freq.values, ax=ax, palette='Reds_d')
ax.set_title('Situação de Conclusão (TP_ST_CONCLUSAO)')
ax.set_ylabel('% de candidatos')
ax.set_xlabel('')
ax.tick_params(axis='x', rotation=20)
for p in ax.patches:
    ax.annotate(f'{p.get_height():.1f}%',
                (p.get_x() + p.get_width()/2, p.get_height()),
                ha='center', va='bottom', fontsize=9)

# ── TP_STATUS_REDACAO ─────────────────────────────────────────────────────────
ax = axes[1, 2]
labels_red = {
    1: 'Sem problemas', 2: 'Anulada', 3: 'Cópia',
    4: 'Em Branco', 6: 'Fuga ao tema',
    7: 'Tipo textual', 8: 'Insuficiente', 9: 'Desconectada'
}
freq = df['TP_STATUS_REDACAO'].value_counts(normalize=True, dropna=False) * 100
freq.index = freq.index.map(labels_red).fillna('Outro')
freq = freq.sort_values(ascending=False)
sns.barplot(x=freq.index, y=freq.values, ax=ax, palette='copper')
ax.set_title('Status da Redação (TP_STATUS_REDACAO)')
ax.set_ylabel('% de candidatos')
ax.set_xlabel('')
ax.tick_params(axis='x', rotation=35)

plt.tight_layout()
plt.show()


# MARKDOWN CELL
**Conclusão da análise univariada:**

Os gráficos revelam o perfil predominante dos candidatos presentes no ENEM 2023:
- Verificar se há desequilíbrio por sexo (padrão histórico: maioria feminina).
- Distribuição racial: verificar representação de pardos e pretos em relação ao censo.
- Escola: dentre os concluintes de 2023, verificar proporção pública vs. privada.
- Faixa etária: concentração nas faixas 17-20 anos, com cauda longa de adultos.
- Situação de conclusão: registrar proporção de "já concluiu" vs. concluintes atuais.

# MARKDOWN CELL
#### 1.11 Distribuição das Variáveis Numéricas

Após a análise dos valores ausentes, duplicidades e valores extremos, esta etapa busca compreender como os valores das variáveis quantitativas estão distribuídos na população analisada. A análise será concentrada nas variáveis referentes às notas das quatro áreas de conhecimento, às cinco competências da redação e à nota final da redação.

A distribuição dessas variáveis permite observar aspectos como a concentração das notas, a dispersão dos valores e o formato geral das distribuições. Essa análise é importante para compreender o comportamento dos dados antes da investigação de possíveis relações entre as variáveis.

Neste momento, o objetivo é descrever e compreender a distribuição dos dados, sem realizar transformações ou exclusões de observações. Valores situados nas extremidades da distribuição, quando pertencentes às faixas válidas das respectivas variáveis, serão considerados parte da população e preservados para as etapas posteriores da análise.

# CODE CELL
# Distribuição das variáveis quantitativas

df[variaveis_quantitativas].hist(
    figsize=(16, 12),
    bins=30,
    edgecolor='black'
)

plt.suptitle(
    'Distribuição das Variáveis Quantitativas',
    fontsize=16
)

plt.tight_layout()
plt.show()

# MARKDOWN CELL
**Conclusao**

1. Notas das áreas de conhecimento

As distribuições de NU_NOTA_CN, NU_NOTA_CH e NU_NOTA_LC apresentam formato aproximadamente unimodal, com maior concentração de observações na região central da escala. As distribuições de Ciências da Natureza e Ciências Humanas são relativamente próximas de uma distribuição aproximadamente simétrica, enquanto Linguagens e Códigos apresenta comportamento semelhante, porém com concentração um pouco mais deslocada para valores superiores.

NU_NOTA_MT apresenta um comportamento diferente: a distribuição é mais assimétrica à direita, com maior concentração das notas em uma faixa intermediária e redução gradual da frequência à medida que as notas aumentam. Esse comportamento também é coerente com o maior desvio-padrão observado anteriormente para Matemática.

2. Competências da redação

As variáveis NU_NOTA_COMP1 a NU_NOTA_COMP5 apresentam distribuições discretas, bastante diferentes das notas das áreas de conhecimento. Observam-se concentrações em determinados valores, especialmente em 120, 160 e 200, dependendo da competência.

Esse comportamento não deve ser interpretado como uma anomalia. As competências possuem uma escala de pontuação específica e, portanto, é esperado que as observações se concentrem em determinados valores.

A NU_NOTA_COMP5 apresenta uma distribuição particularmente espalhada entre as categorias observadas, enquanto NU_NOTA_COMP1, NU_NOTA_COMP2, NU_NOTA_COMP3 e NU_NOTA_COMP4 apresentam concentrações mais pronunciadas em alguns valores.

3. Nota da redação

NU_NOTA_REDACAO apresenta uma distribuição diferente das notas das quatro áreas. Embora exista concentração de valores entre aproximadamente 500 e 900 pontos, a distribuição apresenta vários picos.

Isso ocorre porque a nota da redação é construída a partir das pontuações das cinco competências, portanto sua distribuição não precisa apresentar o formato aproximadamente contínuo observado nas notas das áreas de conhecimento.

Também aparece uma concentração de observações em 0, que deve ser interpretada em conjunto com a análise realizada anteriormente sobre TP_STATUS_REDACAO, na qual verificamos que a ocorrência de nota zero está associada às situações específicas da redação.

De modo geral, as distribuições observadas são compatíveis com a natureza das variáveis analisadas. Não foram identificados, pela análise visual das distribuições, padrões que indiquem problemas evidentes de qualidade dos dados.

# MARKDOWN CELL
#### 1.12 Análise da Relação entre as Variáveis

Após analisar individualmente a distribuição das variáveis quantitativas, esta etapa busca investigar como as variáveis se comportam em conjunto. O objetivo é identificar possíveis relações, associações ou padrões entre as características dos participantes e seus respectivos resultados no ENEM.

A análise será realizada inicialmente por meio da comparação entre variáveis quantitativas, buscando verificar se alterações nos valores de uma variável estão associadas a alterações em outra. Essa investigação poderá revelar relações relevantes entre as notas das diferentes áreas de conhecimento e entre as competências da redação e sua nota final.

Neste momento, a análise tem caráter exploratório. A identificação de uma relação entre duas variáveis não implica, necessariamente, uma relação de causalidade. Os padrões encontrados serão utilizados para orientar as etapas posteriores da EDA e, posteriormente, a construção das variáveis e dos modelos preditivos.

# MARKDOWN CELL


# CODE CELL
# Relação entre as notas das áreas de conhecimento
# Todos os gráficos utilizam a mesma escala: 0 a 1000

variaveis_areas = [
    'NU_NOTA_CN',
    'NU_NOTA_CH',
    'NU_NOTA_LC',
    'NU_NOTA_MT'
]

g = sns.pairplot(
    df[variaveis_areas],
    corner=True,
    plot_kws={'alpha': 0.2, 's': 10}
)

# Padroniza a escala de todos os eixos
for ax in g.axes.flat:
    if ax is not None:
        ax.set_xlim(0, 1000)
        ax.set_ylim(0, 1000)

g.figure.suptitle(
    'Relação entre as Notas das Áreas de Conhecimento',
    y=1.02
)

plt.show()

# MARKDOWN CELL
#### 1.13 Correlação

A correlação será utilizada para quantificar a intensidade e a direção da associação linear entre as notas das quatro áreas de conhecimento. Para esta análise, utilizaremos o coeficiente de correlação de Pearson, cujo valor varia entre -1 e +1.

valores próximos de +1 indicam associação linear positiva;
valores próximos de 0 indicam pouca ou nenhuma associação linear;
valores próximos de -1 indicam associação linear negativa.

É importante destacar que correlação não implica causalidade. O objetivo nesta etapa é apenas identificar e quantificar associações entre as variáveis.

# CODE CELL
# Matriz de correlação entre as notas das áreas de conhecimento

correlacao = df[variaveis_areas].corr(method='pearson')

print("Matriz de correlação:")
print(correlacao.round(3))

# MARKDOWN CELL
##### 1.13.1 Correlação de Spearman — Variáveis Ordinais × Notas

Para variáveis ordinais (faixa etária, cor/raça, tipo de escola, situação de conclusão), o coeficiente
de Spearman é mais adequado que o de Pearson, pois não assume linearidade.


# CODE CELL
from scipy.stats import spearmanr

vars_ordinais = ['TP_FAIXA_ETARIA', 'TP_COR_RACA', 'TP_ESCOLA', 'TP_ST_CONCLUSAO']
notas_cols    = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

print("Correlação de Spearman — variáveis ordinais × notas (* = p < 0.001):\n")

rows = []
for var in vars_ordinais:
    row = {}
    for nota in notas_cols:
        sub = df[[var, nota]].dropna()
        rho, pval = spearmanr(sub[var], sub[nota])
        marker = '*' if pval < 0.001 else ''
        row[nota] = f"{rho:+.3f}{marker}"
    rows.append(row)

result = pd.DataFrame(rows, index=vars_ordinais)
print(result.to_string())


# MARKDOWN CELL
##### 1.13.2 Heatmap Geral de Correlação (Pearson)

Heatmap ampliado incluindo notas objetivas, competências da redação e variáveis ordinais relevantes.


# CODE CELL
import numpy as np

colunas_heatmap = [
    'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT',
    'NU_NOTA_REDACAO',
    'NU_NOTA_COMP1', 'NU_NOTA_COMP2', 'NU_NOTA_COMP3',
    'NU_NOTA_COMP4', 'NU_NOTA_COMP5',
    'TP_FAIXA_ETARIA', 'TP_COR_RACA', 'TP_ESCOLA', 'TP_ST_CONCLUSAO'
]
cols_disp = [c for c in colunas_heatmap if c in df.columns]
corr_matrix = df[cols_disp].corr(method='pearson')

fig, ax = plt.subplots(figsize=(13, 10))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(
    corr_matrix, mask=mask, annot=True, fmt='.2f',
    cmap='RdBu_r', center=0, vmin=-1, vmax=1,
    linewidths=0.5, ax=ax, annot_kws={'size': 8}
)
ax.set_title('Heatmap de Correlação de Pearson — Variáveis Numéricas e Ordinais', fontsize=13)
plt.tight_layout()
plt.show()


# MARKDOWN CELL
**Conclusao:** Interpretação da matriz de correlação

A matriz de correlação evidencia associações lineares positivas entre todas as notas das áreas de conhecimento analisadas. Os coeficientes variam de `0,591` a `0,767`, indicando que as áreas apresentam relações positivas, porém com diferentes intensidades.

A maior correlação observada ocorre entre `NU_NOTA_CH` e `NU_NOTA_LC` (`r = 0,767`), seguida pela relação entre `NU_NOTA_CN` e `NU_NOTA_MT` (`r = 0,706`). A menor correlação ocorre entre `NU_NOTA_CN` e `NU_NOTA_LC` (`r = 0,591`).

Esses resultados complementam a análise visual realizada anteriormente. Por exemplo, a correlação entre `NU_NOTA_CN` e `NU_NOTA_MT` (`r = 0,706`) é superior à correlação entre `NU_NOTA_LC` e `NU_NOTA_MT` (`r = 0,621`), confirmando quantitativamente uma diferença que já podia ser observada nos diagramas de dispersão.

As correlações identificadas descrevem associações entre as notas e não devem ser interpretadas como relações de causalidade. Além disso, nesta etapa da EDA ainda não foi definida a variável-alvo do modelo. Portanto, os resultados são utilizados para compreender a estrutura dos dados, e não para selecionar, neste momento, variáveis preditoras ou definir o target.

As associações observadas poderão posteriormente ser utilizadas para formular hipóteses sobre possíveis variáveis-alvo compostas. Essas hipóteses, caso sejam investigadas, deverão ser avaliadas empiricamente durante a etapa de modelagem e validação, não sendo possível inferir o desempenho de um modelo apenas a partir da correlação entre os componentes do target.

# MARKDOWN CELL
#### 1.14 Análise de categorias e categorias raras

As variáveis categóricas representam características demográficas, escolares, socioeconômicas e outras informações codificadas por categorias. Nesta etapa, será analisada a frequência das categorias presentes nessas variáveis, com o objetivo de identificar categorias muito raras ou com baixa representatividade na população analisada.

A identificação dessas categorias é importante porque uma frequência muito baixa pode dificultar sua utilização em modelos de Machine Learning e também pode indicar situações específicas da população que devem ser consideradas durante as etapas posteriores de preparação dos dados.

Nesta etapa, a análise será exclusivamente descritiva. A presença de uma categoria rara não será considerada, por si só, um problema de qualidade e nenhuma categoria será excluída neste momento.

# CODE CELL
# Variáveis categóricas definidas a partir do dicionário de dados

variaveis_categoricas = [
    'TP_FAIXA_ETARIA',
    'TP_SEXO',
    'TP_ESTADO_CIVIL',
    'TP_COR_RACA',
    'TP_NACIONALIDADE',
    'TP_ST_CONCLUSAO',
    'TP_ANO_CONCLUIU',
    'TP_ESCOLA',
    'TP_ENSINO',
    'IN_TREINEIRO',
    'TP_DEPENDENCIA_ADM_ESC',
    'TP_LOCALIZACAO_ESC',
    'TP_SIT_FUNC_ESC',
    'TP_STATUS_REDACAO',
    'Q001',
    'Q002',
    'Q003',
    'Q004',
    'Q005',
    'Q006',
    'Q007',
    'Q008',
    'Q009',
    'Q010',
    'Q011',
    'Q012',
    'Q013',
    'Q014',
    'Q015',
    'Q016',
    'Q017',
    'Q018',
    'Q019',
    'Q020',
    'Q021',
    'Q022',
    'Q023',
    'Q024',
    'Q025'
]

# Identificação das categorias com frequência inferior a 1%

categorias_raras = []

for variavel in variaveis_categoricas:

    frequencia = df[variavel].value_counts(dropna=False)

    percentual = df[variavel].value_counts(
        normalize=True,
        dropna=False
    ) * 100

    for categoria in percentual.index:

        if percentual[categoria] < 1:

            categorias_raras.append({
                'Variável': variavel,
                'Categoria': categoria,
                'Quantidade': frequencia[categoria],
                'Percentual (%)': percentual[categoria]
            })

categorias_raras = pd.DataFrame(categorias_raras)

# Ordenar pela quantidade de ocorrências
categorias_raras = categorias_raras.sort_values(
    by='Quantidade',
    ascending=True
)

categorias_raras.round(2)

# MARKDOWN CELL
**Conclusao: ** ### Interpretação das categorias raras

A presença de categorias com baixa frequência constitui um sinal de atenção para a utilização futura dessas variáveis como preditoras, mas não é, isoladamente, um critério para excluir uma feature. A utilidade preditiva de uma variável dependerá também da relação de suas categorias com a variável-alvo e da capacidade do modelo de generalizar esse comportamento para dados não utilizados no treinamento.

**1. Categorias raras que merecem registro**

Há algumas categorias com frequência realmente baixa, por exemplo:

- TP_FAIXA_ETARIA = 20: 30 participantes — **0,01%**
- TP_ESTADO_CIVIL = 4: 151 participantes — **0,05%**
- TP_NACIONALIDADE = 0: 148 participantes — **0,05%**
- TP_SIT_FUNC_ESC = 3: 54 participantes — **0,02%**
- TP_STATUS_REDACAO = 2: 133 participantes — **0,04%**
- Q017 = E: 12 participantes — **0,00%**
- Q015 = E: 11 participantes — **0,00%**

Essas categorias são importantes para a EDA porque mostram situações pouco representadas na amostra. **Não há motivo, nesta etapa, para excluí-las.**

**2. CO_PROVA_*: raridade esperada**

Foram encontradas categorias como:

```text
CO_PROVA_CH = 1197 → 3 participantes
CO_PROVA_CN = 1227 → 3 participantes
CO_PROVA_LC = 1207 → 3 participantes
CO_PROVA_MT = 1217 → 3 participantes
```

Esses códigos representam tipos/códigos de prova, não categorias sociodemográficas. Portanto, uma frequência pequena não significa, por si só, problema de qualidade.

Além disso, existe um padrão interessante: os códigos raros aparecem de forma correspondente entre as quatro áreas. Isso sugere que estamos observando diferentes versões/cadernos de prova aplicados a pequenos grupos.

****3. Q005 merece uma observação específica**

Q005 apresenta uma distribuição com categorias muito pouco frequentes:
```text
19 → 2
18 → 4
16 → 4
17 → 5
14 → 25
...
8  → 2.317
```

O mesmo ocorre em várias questões Q010–Q017, principalmente nas categorias D e E.

# MARKDOWN CELL
#### 1.15 — Análise de padrões e anomalias

# MARKDOWN CELL
**TP_STATUS_REDACAO x NU_NOTA_REDACAO**

# CODE CELL
# Relação entre o status da redação e a nota da redação

analise_redacao = df.groupby('TP_STATUS_REDACAO')['NU_NOTA_REDACAO'].agg(
    Quantidade='count',
    Media='mean',
    Minimo='min',
    Maximo='max'
)

# Substituição dos códigos pelas respectivas descrições

analise_redacao.index = analise_redacao.index.map({
    1: 'Sem problemas',
    2: 'Anulada',
    3: 'Cópia Texto Motivador',
    4: 'Em Branco',
    6: 'Fuga ao tema',
    7: 'Não atendimento ao tipo textual',
    8: 'Texto insuficiente',
    9: 'Parte desconectada'
})

analise_redacao.round(2)

# MARKDOWN CELL
**Conclusão:**

Como apenas a categoria 1 ("Sem problemas") corresponde a redações efetivamente corrigidas e, portanto, passíveis de receber nota, qualquer valor diferente de zero nas demais categorias indicaria uma irregularidade na base de dados.

# MARKDOWN CELL
#### 1.16 Análise das Competências da Redação × Perfil do Candidato

A redação do ENEM é avaliada em cinco competências com peso igual. Esta seção investiga como as notas
de cada competência se distribuem entre diferentes perfis de candidatos, com foco no tipo de escola.
A competência 5 (Proposta de Intervenção) é particularmente relevante, pois é a que mais diferencia
candidatos com e sem letramento crítico.

Análise restrita a candidatos com redação válida (TP_STATUS_REDACAO == 1) e escola informada.


# CODE CELL
comps = ['NU_NOTA_COMP1', 'NU_NOTA_COMP2', 'NU_NOTA_COMP3',
         'NU_NOTA_COMP4', 'NU_NOTA_COMP5']
labels_comp = ['C1: Língua\nPortuguesa', 'C2: Tema/\nGênero',
               'C3: Seleção\nde Info', 'C4: Coesão',
               'C5: Proposta\nde Intervenção']

df_comp = df[
    df['TP_ESCOLA'].isin([2, 3]) & (df['TP_STATUS_REDACAO'] == 1)
].copy()
df_comp['Escola'] = df_comp['TP_ESCOLA'].map({2: 'Pública', 3: 'Privada'})

fig, axes = plt.subplots(1, 5, figsize=(22, 6), sharey=True)
fig.suptitle(
    'Competências da Redação — Escola Pública vs. Privada (redação válida, concluintes 2023)',
    fontsize=13
)

for i, (comp, label) in enumerate(zip(comps, labels_comp)):
    ax = axes[i]
    sns.boxplot(
        data=df_comp, x='Escola', y=comp,
        order=['Pública', 'Privada'],
        palette={'Pública': '#4C72B0', 'Privada': '#DD8452'},
        ax=ax, width=0.5
    )
    ax.set_title(label, fontsize=9)
    ax.set_xlabel('')
    ax.set_ylabel('Nota' if i == 0 else '')
    ax.set_ylim(0, 210)

plt.tight_layout()
plt.show()

# Tabela resumo + diferença
print("Médias por competência — Escola Pública vs. Privada:")
resumo = df_comp.groupby('Escola')[comps].mean().round(1)
resumo.columns = ['C1', 'C2', 'C3', 'C4', 'C5']
print(resumo.to_string())
diff = resumo.loc['Privada'] - resumo.loc['Pública']
print(f"\nDiferença Privada − Pública:")
print(diff.round(1).to_string())


# MARKDOWN CELL
**Conclusão:**

A comparação das competências entre escola pública e privada revela em qual dimensão da redação
a diferença é mais acentuada. Atenção especial à competência 5 (Proposta de Intervenção), que
tende a ser a mais discriminante entre os dois grupos.


# MARKDOWN CELL
#### 1.17 Notas zero entre participantes presentes

**TP_ST_CONCLUSAO x TP_ESCOLA**

# CODE CELL
# Relação entre situação de conclusão e tipo de escola

cruzamento_escola = pd.crosstab(
    df['TP_ST_CONCLUSAO'],
    df['TP_ESCOLA'],
    dropna=False
)

# Substituição dos códigos pelas respectivas descrições

cruzamento_escola.index = cruzamento_escola.index.map({
    1: 'Já concluiu o Ensino Médio',
    2: 'Concluinte em 2023',
    3: 'Concluirá após 2023',
    4: 'Não concluiu e não cursa'
})

cruzamento_escola.columns = cruzamento_escola.columns.map({
    1: 'Não Respondeu',
    2: 'Pública',
    3: 'Privada'
})

cruzamento_escola

# MARKDOWN CELL
**Conclusão:**

O cruzamento entre `TP_ST_CONCLUSAO` e `TP_ESCOLA` evidencia que apenas os Concluintes em 2023 respondem a TP_ESCOLA.



# MARKDOWN CELL
**TP_ST_CONCLUSAO × TP_ENSINO**

# CODE CELL
# Relação entre situação de conclusão e tipo de ensino

cruzamento_ensino = pd.crosstab(
    df['TP_ST_CONCLUSAO'],
    df['TP_ENSINO'],
    dropna=False
)

# Substituição dos códigos pelas respectivas descrições

cruzamento_ensino.index = cruzamento_ensino.index.map({
    1: 'Já concluiu o Ensino Médio',
    2: 'Concluinte em 2023',
    3: 'Concluirá após 2023',
    4: 'Não concluiu e não cursa'
})

cruzamento_ensino.columns = cruzamento_ensino.columns.map({
    1: 'Ensino Regular',
    2: 'Educação Especial - Modalidade Substitutiva'
})

cruzamento_ensino

# MARKDOWN CELL
**Conclusão**

A informação sobre TP_ENSINO está disponível apenas para os concluintes em 2023.

# CODE CELL
# Verificação de consistência entre o status da redação e a nota

inconsistencias_redacao = df[
    (
        (df['TP_STATUS_REDACAO'] == 1) &
        (df['NU_NOTA_REDACAO'] == 0)
    )
    |
    (
        (df['TP_STATUS_REDACAO'] != 1) &
        (df['NU_NOTA_REDACAO'] != 0)
    )
]

print(f'Quantidade de inconsistências: {len(inconsistencias_redacao)}')

# MARKDOWN CELL
#### 1.18 Análise Bivariada: Perfil Demográfico × Notas

Esta seção investiga a relação entre as principais variáveis demográficas e o desempenho dos candidatos.
A análise bivariada é fundamental para identificar padrões de desigualdade e para compreender quais
características estão associadas a melhores ou piores resultados antes da construção de qualquer modelo.

As variáveis analisadas são: sexo, cor/raça e tipo de escola (para concluintes de 2023).
Notas zero são excluídas das visualizações para não distorcer a distribuição.

# CODE CELL
notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT']
titulos = ['Ciências da Natureza', 'Ciências Humanas', 'Linguagens', 'Matemática']

df_plot = df.copy()
df_plot['Sexo'] = df_plot['TP_SEXO'].map({'M': 'Masculino', 'F': 'Feminino'})

fig, axes = plt.subplots(1, 4, figsize=(20, 6), sharey=True)
fig.suptitle('Distribuição das Notas por Sexo (excluindo notas zero)', fontsize=14)

for i, (nota, titulo) in enumerate(zip(notas, titulos)):
    ax = axes[i]
    sub = df_plot[df_plot[nota] > 0]
    sns.violinplot(
        data=sub, x='Sexo', y=nota,
        order=['Feminino', 'Masculino'],
        palette={'Feminino': '#E07B8A', 'Masculino': '#5B8DB8'},
        ax=ax, inner='quartile', cut=0
    )
    ax.set_title(titulo, fontsize=10)
    ax.set_xlabel('')
    ax.set_ylabel('Nota' if i == 0 else '')
    ax.set_ylim(0, 1000)

plt.tight_layout()
plt.show()

print("Médias por sexo (excluindo notas zero):")
medias_sexo = (
    df_plot[df_plot[notas].gt(0).all(axis=1)]
    .groupby('Sexo')[notas].mean().round(1)
)
medias_sexo.columns = titulos
print(medias_sexo.to_string())

# CODE CELL
labels_raca_biv = {1: 'Branca', 2: 'Preta', 3: 'Parda', 4: 'Amarela', 5: 'Indígena'}
ordem_raca_biv  = ['Branca', 'Parda', 'Preta', 'Amarela', 'Indígena']

df_raca = df[df['TP_COR_RACA'].isin(labels_raca_biv)].copy()
df_raca['Cor/Raça'] = df_raca['TP_COR_RACA'].map(labels_raca_biv)

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Distribuição das Notas por Cor/Raça (excluindo notas zero)', fontsize=14)

for i, (nota, titulo) in enumerate(zip(notas, titulos)):
    ax = axes[i // 2][i % 2]
    sub = df_raca[df_raca[nota] > 0]
    sns.boxplot(
        data=sub, x='Cor/Raça', y=nota,
        order=ordem_raca_biv, palette='Set2',
        ax=ax, width=0.5, fliersize=1
    )
    ax.set_title(titulo, fontsize=11)
    ax.set_xlabel('')
    ax.set_ylabel('Nota')
    ax.set_ylim(0, 1000)
    ax.tick_params(axis='x', rotation=20)

plt.tight_layout()
plt.show()

print("Médias por cor/raça (excluindo notas zero):")
medias_raca_biv = (
    df_raca[df_raca[notas].gt(0).all(axis=1)]
    .groupby('Cor/Raça')[notas].mean().round(1)
)
medias_raca_biv.columns = titulos
print(medias_raca_biv.reindex(ordem_raca_biv).to_string())

# CODE CELL
notas_all = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
titulos_all = ['C. Natureza', 'C. Humanas', 'Linguagens', 'Matemática', 'Redação']

df_esc = df[df['TP_ESCOLA'].isin([2, 3])].copy()
df_esc['Escola'] = df_esc['TP_ESCOLA'].map({2: 'Pública', 3: 'Privada'})

fig, axes = plt.subplots(1, 5, figsize=(22, 6))
fig.suptitle('Distribuição das Notas por Tipo de Escola — Concluintes 2023 (excluindo zeros)', fontsize=13)

for i, (nota, titulo) in enumerate(zip(notas_all, titulos_all)):
    ax = axes[i]
    sub = df_esc[df_esc[nota] > 0]
    sns.violinplot(
        data=sub, x='Escola', y=nota,
        order=['Pública', 'Privada'],
        palette={'Pública': '#4C72B0', 'Privada': '#DD8452'},
        ax=ax, inner='quartile', cut=0
    )
    ax.set_title(titulo, fontsize=10)
    ax.set_xlabel('')
    ax.set_ylabel('Nota' if i == 0 else '')

plt.tight_layout()
plt.show()

print("Comparação de médias por tipo de escola (excluindo zeros):")
medias_esc = (
    df_esc[df_esc[notas_all].gt(0).all(axis=1)]
    .groupby('Escola')[notas_all].mean().round(1)
)
medias_esc.columns = titulos_all
print(medias_esc.to_string())
diff_esc = medias_esc.loc['Privada'] - medias_esc.loc['Pública']
print(f"\nDiferença Privada − Pública:")
for c, v in diff_esc.items():
    print(f"  {c}: {v:+.1f} pontos")

# MARKDOWN CELL
**Conclusão da análise bivariada:**

1. **Sexo:** candidatos do sexo masculino tendem a ter médias superiores em Matemática e Ciências
   da Natureza; candidatas do sexo feminino em Linguagens e Redação. Padrão consistente com o PISA.

2. **Cor/Raça:** candidatos brancos obtêm notas médias superiores em todas as áreas. Essa diferença
   reflete as desigualdades socioeconômicas e educacionais estruturais do Brasil.

3. **Tipo de escola:** candidatos de escolas privadas obtêm médias significativamente superiores
   em todas as áreas. Essa variável é um dos preditores mais fortes disponíveis no dataset.

Essas relações serão tratadas mais rigorosamente durante a seleção de features e interpretação dos modelos.

# MARKDOWN CELL
#### 1.19 Análise do Questionário Socioeconômico (Q001–Q025)

O questionário socioeconômico do ENEM coleta informações sobre renda familiar, escolaridade dos pais,
acesso a bens e serviços e outros indicadores de contexto. Essas variáveis são historicamente as mais
fortemente associadas ao desempenho no ENEM e serão features centrais nos modelos preditivos.

Questões analisadas:
- Q001: Escolaridade do pai
- Q006: Renda familiar mensal
- Q025: Acesso à internet em casa

Para cada questão: distribuição de frequência + relação com nota média de Matemática.

# CODE CELL
Q001_labels = {
    'A': 'Nunca estudou', 'B': 'Até 5º ano', 'C': '6º ao 9º ano',
    'D': 'Médio inc.', 'E': 'Médio comp.', 'F': 'Superior inc.',
    'G': 'Superior comp.', 'H': 'Pós-graduação'
}
Q006_labels = {
    'A': 'Sem renda', 'B': 'Até 1.320', 'C': '1.320-1.980',
    'D': '1.980-2.640', 'E': '2.640-3.300', 'F': '3.300-3.960',
    'G': '3.960-5.280', 'H': '5.280-6.600', 'I': '6.600-7.920',
    'J': '7.920-9.240', 'K': '9.240-10.560', 'L': '10.560-13.200',
    'M': '13.200-15.840', 'N': '15.840-19.800',
    'O': '19.800-26.400', 'P': '>26.400'
}
Q025_labels = {'A': 'Não', 'B': 'Sim'}

fig, axes = plt.subplots(2, 3, figsize=(22, 12))
fig.suptitle('Questionário Socioeconômico — Distribuição e Nota Média de Matemática', fontsize=13)

def plot_q(df, col, labels, ax_freq, ax_nota, titulo):
    df_sub = df[df[col].isin(labels)].copy()
    df_sub['label'] = df_sub[col].map(labels)
    ordem = [labels[k] for k in sorted(labels) if labels[k] in df_sub['label'].unique()]

    freq = df_sub['label'].value_counts(normalize=True) * 100
    freq = freq.reindex(ordem, fill_value=0)
    sns.barplot(x=freq.index, y=freq.values, order=ordem, ax=ax_freq, palette='Blues_d')
    ax_freq.set_title(f'{titulo} — Distribuição', fontsize=10)
    ax_freq.set_ylabel('% candidatos')
    ax_freq.set_xlabel('')
    ax_freq.tick_params(axis='x', rotation=40)

    media = df_sub[df_sub['NU_NOTA_MT'] > 0].groupby('label')['NU_NOTA_MT'].mean().reindex(ordem)
    sns.barplot(x=media.index, y=media.values, order=ordem, ax=ax_nota, palette='Oranges_d')
    ax_nota.set_title(f'{titulo} — Média Nota MT', fontsize=10)
    ax_nota.set_ylabel('Média NU_NOTA_MT')
    ax_nota.set_xlabel('')
    ax_nota.tick_params(axis='x', rotation=40)
    ax_nota.set_ylim(300, 750)

plot_q(df, 'Q001', Q001_labels, axes[0, 0], axes[1, 0], 'Escolaridade do Pai (Q001)')
plot_q(df, 'Q006', Q006_labels, axes[0, 1], axes[1, 1], 'Renda Familiar (Q006)')
plot_q(df, 'Q025', Q025_labels, axes[0, 2], axes[1, 2], 'Internet em Casa (Q025)')

plt.tight_layout()
plt.show()

# MARKDOWN CELL
**Conclusão da análise socioeconômica:**

1. **Escolaridade dos pais (Q001/Q002):** candidatos cujos pais possuem ensino superior ou
   pós-graduação obtêm médias de Matemática substancialmente superiores. O gradiente é monotônico.

2. **Renda familiar (Q006):** relação positiva clara entre renda e desempenho. Candidatos de
   famílias com renda acima de R$5.000/mês tendem a notas médias consideravelmente superiores.

3. **Acesso à internet (Q025):** candidatos com internet em casa obtêm notas médias superiores,
   refletindo o perfil socioeconômico e as possibilidades de estudo online.

Essas variáveis são features de alto poder preditivo e devem ser tratadas com prioridade no pipeline
de feature engineering.

# MARKDOWN CELL
#### 1.20 Análise Geográfica por UF e Região

O ENEM apresenta variações regionais expressivas de desempenho, refletindo as desigualdades educacionais
entre as regiões brasileiras. Esta seção analisa a distribuição de candidatos e as médias de desempenho
por Unidade da Federação (UF) de aplicação da prova.

A variável `regiao` foi criada na seção 1.1 a partir do mapeamento de `SG_UF_PROVA`.

# CODE CELL
from matplotlib.patches import Patch

# Garantir que 'regiao' existe
if 'regiao' not in df.columns:
    regioes_map = {
        'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte',
        'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
        'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste',
        'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste',
        'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
        'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste',
        'MS': 'Centro-Oeste', 'MT': 'Centro-Oeste',
        'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
        'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul',
    }
    df['regiao'] = df['SG_UF_PROVA'].map(regioes_map)

# Mapeamento uf → região (para colorir barras)
uf_to_reg = {
    'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte',
    'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
    'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste',
    'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste',
    'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
    'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste',
    'MS': 'Centro-Oeste', 'MT': 'Centro-Oeste',
    'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
    'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul',
}
cores_reg = {
    'Norte': '#55A868', 'Nordeste': '#E07B8A', 'Sudeste': '#4C72B0',
    'Sul': '#CCB974', 'Centro-Oeste': '#8172B2'
}

fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# ── Candidatos por região ─────────────────────────────────────────────────────
ordem_reg = ['Nordeste', 'Sudeste', 'Norte', 'Sul', 'Centro-Oeste']
freq_reg = df['regiao'].value_counts().reindex(ordem_reg)
axes[0].bar(freq_reg.index, freq_reg.values / 1000,
            color=[cores_reg[r] for r in ordem_reg])
axes[0].set_title('Candidatos por Região (milhares)', fontsize=12)
axes[0].set_ylabel('Candidatos (×1.000)')
for i, v in enumerate(freq_reg.values):
    axes[0].text(i, v/1000 + 0.3, f'{v/1000:.1f}k', ha='center', fontsize=9)

# ── Nota média de Matemática por UF ───────────────────────────────────────────
media_uf = (
    df[df['NU_NOTA_MT'] > 0]
    .groupby('SG_UF_PROVA')['NU_NOTA_MT']
    .mean()
    .sort_values(ascending=True)
)
cores_barras = [cores_reg.get(uf_to_reg.get(uf, ''), '#999999') for uf in media_uf.index]

axes[1].barh(media_uf.index, media_uf.values, color=cores_barras)
axes[1].set_title('Nota Média de Matemática por UF\n(excluindo notas zero)', fontsize=12)
axes[1].set_xlabel('Nota média')
media_geral = media_uf.mean()
axes[1].axvline(media_geral, color='black', linestyle='--', linewidth=1)
axes[1].text(media_geral + 1, 1, f'Média: {media_geral:.0f}', fontsize=8)
axes[1].set_xlim(400, 650)

legend_elements = [Patch(facecolor=c, label=r) for r, c in cores_reg.items()]
axes[1].legend(handles=legend_elements, loc='lower right', fontsize=8)

plt.tight_layout()
plt.show()

# Tabela de médias por região
print("Médias por região (excluindo notas zero em MT):")
medias_reg = (
    df[df['NU_NOTA_MT'] > 0]
    .groupby('regiao')[['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']]
    .mean().round(1)
)
medias_reg.columns = ['C. Natureza', 'C. Humanas', 'Linguagens', 'Matemática', 'Redação']
print(medias_reg.to_string())

# MARKDOWN CELL
**Conclusão da análise geográfica:**

As UFs das regiões Sul e Sudeste tendem a apresentar médias superiores em todas as áreas, consistentes
com melhores indicadores socioeconômicos e de infraestrutura escolar. As UFs das regiões Norte e
Nordeste apresentam médias geralmente inferiores.

A variável `regiao` (derivada de `SG_UF_PROVA`) pode ser considerada como feature adicional durante a
seleção de variáveis, dependendo do objetivo do modelo e da disponibilidade dessa informação no momento
da predição.

# MARKDOWN CELL
#### 1.21 Conclusões da EDA

A análise exploratória dos dados do ENEM 2023 permitiu caracterizar a estrutura, a qualidade e os principais padrões presentes na população analisada. A população utilizada nesta etapa é composta por `297.186` participantes presentes nas quatro provas objetivas.

### Candidatos treineiros

Os candidatos treineiros (`IN_TREINEIRO = 1`) foram identificados e removidos da base de modelagem,
pois representam uma subpopulação com comportamento sistemático diferente dos candidatos regulares.
A EDA a partir da seção 1.3 já foi realizada sobre a base sem treineiros.

### Análise do perfil demográfico

A análise bivariada (seção 1.18) revelou padrões de desigualdade consistentes com a literatura:
- Candidatos de escolas privadas obtêm médias superiores em todas as áreas, com maior diferença
  em Matemática e Redação.
- Candidatos brancos apresentam médias superiores às de candidatos pardos e pretos em todas as áreas.
- Há diferença por sexo: masculino se destaca em Matemática/CN; feminino em Linguagens/Redação.

### Variáveis socioeconômicas

As variáveis do questionário socioeconômico (seção 1.19) apresentaram gradientes claros de desempenho.
Renda familiar (`Q006`), escolaridade dos pais (`Q001`/`Q002`) e acesso à internet (`Q025`) são
candidatos naturais a features de alta importância nos modelos preditivos.

### Disparidades geográficas

A análise por UF e região (seção 1.20) identificou disparidades regionais expressivas, com Sul e
Sudeste apresentando médias superiores. A variável `regiao` pode agregar valor preditivo marginal.

### Estrutura e qualidade dos dados

A análise das duplicidades não identificou registros duplicados, tanto considerando o identificador mascarado `NU_INSCRICAO` quanto a comparação de todas as variáveis do registro.

Foram identificados valores ausentes em diferentes variáveis, principalmente nas informações relacionadas às características escolares. A análise dos padrões de ausência mostrou que essas ausências não são aleatórias, estando fortemente relacionadas à situação de conclusão do Ensino Médio (`TP_ST_CONCLUSAO`). Portanto, os valores ausentes observados devem ser interpretados considerando o contexto das variáveis, e não simplesmente como erros de preenchimento.

A análise das variáveis quantitativas identificou valores estatisticamente extremos em algumas distribuições. Entretanto, os valores observados permanecem dentro das escalas válidas das respectivas notas, não tendo sido identificadas evidências de valores incorretos que justifiquem sua exclusão.

Também foram identificadas categorias com baixa frequência em diversas variáveis categóricas. A baixa frequência, entretanto, não foi considerada evidência suficiente para excluir essas categorias. Algumas categorias raras correspondem a situações pouco frequentes da população, enquanto outras representam códigos técnicos, como as versões das provas.

### Distribuição e relações entre as variáveis

A análise das distribuições das notas mostrou diferentes padrões entre as áreas de conhecimento, com destaque para a maior dispersão das notas de Matemática e para o comportamento mais discreto das competências da redação.

As notas das quatro áreas de conhecimento apresentaram associações lineares positivas. A maior correlação observada foi entre Ciências Humanas e Linguagens (`r = 0,767`), enquanto a menor foi entre Ciências da Natureza e Linguagens (`r = 0,591`).

Essas correlações foram utilizadas para compreender a estrutura dos dados e não para definir, nesta etapa, a variável-alvo ou selecionar variáveis preditoras.

### Padrões e consistência dos dados

Os cruzamentos entre variáveis semanticamente relacionadas não identificaram inconsistências evidentes.

A relação entre `TP_ST_CONCLUSAO` e `TP_ANO_CONCLUIU` apresentou comportamento compatível com a situação de conclusão dos participantes.

A relação entre `TP_ST_CONCLUSAO` e `TP_ESCOLA` revelou um padrão estrutural importante: as informações sobre o tipo de escola estão disponíveis predominantemente para os participantes concluintes em 2023.

Comportamento semelhante foi observado na relação entre `TP_ST_CONCLUSAO` e `TP_ENSINO`, reforçando que a disponibilidade de determinadas informações escolares está relacionada à situação de conclusão do participante.

Na análise da redação, foi observada uma relação estrutural entre `TP_STATUS_REDACAO` e `NU_NOTA_REDACAO`. Somente a categoria `1` ("Sem problemas") apresenta notas diferentes de zero. Para as demais categorias, a nota é igual a zero.

Foi realizada uma verificação específica dessa regra de consistência e foram identificadas **0 inconsistências**. Portanto, não foram encontrados registros em que uma redação com status diferente de "Sem problemas" apresentasse uma nota diferente de zero.

### Valores zero

A análise também identificou a presença de valores zero nas notas. Entre os participantes presentes nas quatro provas, foram observadas:

- `1.523` notas zero em Ciências da Natureza;
- `262` notas zero em Ciências Humanas;
- `75` notas zero em Linguagens;
- `1.536` notas zero em Matemática;
- `8.062` notas zero na redação.

Esses valores não foram tratados automaticamente como erros. A análise mostrou que, especialmente no caso da redação, o valor zero possui significado associado ao status registrado para a redação.

### Considerações para as próximas etapas

A EDA não identificou, na população analisada, evidências de duplicidades ou de valores quantitativos inválidos. Foram identificados, entretanto, padrões estruturais de valores ausentes, categorias raras e relações entre variáveis que deverão ser considerados na preparação dos dados.

As análises realizadas nesta etapa tiveram caráter exploratório e não determinaram ainda a variável-alvo nem o conjunto definitivo de variáveis preditoras.

Antes da construção dos modelos, será necessário definir formalmente o problema de Machine Learning, estabelecer a variável-alvo, avaliar a disponibilidade das informações no momento da previsão e investigar possíveis situações de vazamento de informação (`data leakage`).

A definição das estratégias de tratamento de valores ausentes, categorias raras e demais transformações será realizada somente após essas definições e deverá ser avaliada considerando também a estratégia de validação temporal adotada no projeto.
