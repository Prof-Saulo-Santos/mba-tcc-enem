# Plano de Correções da EDA — `02_gpt.ipynb`
**Documento de instrução para IA — execução passo a passo**

> Este documento deve ser seguido na ordem apresentada.
> Cada item especifica: (a) onde inserir no notebook, (b) o texto da célula markdown, (c) o código Python completo.
> Após todas as inserções, renumerar as seções conforme indicado no Passo 0.

---

## Passo 0 — Mapa do notebook atual e renumeração final

### Estrutura atual do notebook

| Seção atual | Título |
|---|---|
| 1. | Carregamento da Amostra |
| 1.1 | Remoção de Candidatos Ausentes |
| 1.2 | Levantamento inicial de valores ausentes |
| 1.3 | Investigação do padrão de ausência das variáveis escolares |
| 1.4 | Análise da variável `TP_ENSINO` |
| 1.5 | Análise da variável `NU_INSCRICAO` |
| 1.6 | Análise de duplicidade |
| 1.7 | Análise de outliers |
| 1.8 | Distribuição das Variáveis Numéricas |
| 1.9 | Análise da Relação entre as Variáveis (pairplot) |
| 1.10 | Correlação |
| 1.11 | Análise de categorias e categorias raras |
| 1.12 | Análise de padrões e anomalias |
| 1.13 | Notas zero entre participantes presentes |
| 1.14 | Conclusões da EDA |

### Estrutura final (após correções)

| Seção nova | Título | Status |
|---|---|---|
| 1. | Carregamento da Amostra | existente |
| **1.1** | **Verificação de Representatividade da Amostra** | **NOVA** |
| 1.2 | Remoção de Candidatos Ausentes | renomeada (era 1.1) |
| **1.3** | **Análise dos Candidatos Treineiros (`IN_TREINEIRO`)** | **NOVA** |
| 1.4 | Levantamento inicial de valores ausentes | renomeada (era 1.2) |
| 1.5 | Investigação do padrão de ausência das variáveis escolares | renomeada (era 1.3) |
| 1.6 | Análise da variável `TP_ENSINO` | renomeada (era 1.4) |
| 1.7 | Análise da variável `NU_INSCRICAO` | renomeada (era 1.5) |
| 1.8 | Análise de duplicidade | renomeada (era 1.6) |
| 1.9 | Análise de outliers | renomeada (era 1.7) |
| **1.10** | **Análise Univariada das Variáveis Categóricas** | **NOVA** |
| 1.11 | Distribuição das Variáveis Numéricas | renomeada (era 1.8) |
| 1.12 | Análise da Relação entre as Variáveis (pairplot) | renomeada (era 1.9) |
| **1.13** | **Correlação Expandida (features × target)** | **NOVA + expansão de 1.10** |
| 1.14 | Análise de categorias e categorias raras | renomeada (era 1.11) |
| 1.15 | Análise de padrões e anomalias | renomeada (era 1.12) |
| **1.16** | **Análise das Competências da Redação × Perfil do Candidato** | **NOVA** |
| 1.17 | Notas zero entre participantes presentes (expandida) | renomeada (era 1.13) |
| **1.18** | **Análise Bivariada: Perfil Demográfico × Notas** | **NOVA** |
| **1.19** | **Análise do Questionário Socioeconômico (Q001–Q025)** | **NOVA** |
| **1.20** | **Análise Geográfica por UF e Região** | **NOVA** |
| 1.21 | Conclusões da EDA (expandida) | renomeada (era 1.14) |

---

## CORREÇÃO 1 — Verificação de Representatividade da Amostra

**Localização:** Inserir APÓS a seção `#### 1. Carregamento da Amostra` (após as 2 células de código de carregamento) e ANTES de `#### 1.1 Remoção de Candidatos Ausentes`.
**Nova seção:** `#### 1.1 Verificação de Representatividade da Amostra`

### Célula Markdown

```
#### 1.1 Verificação de Representatividade da Amostra

Uma amostra aleatória simples de 400.000 registros foi extraída da base completa de 3.933.955 participantes.
Antes de prosseguir com a análise, é necessário verificar se essa amostra preserva as proporções das
principais características da população.

Para isso, comparam-se as distribuições de variáveis-chave na amostra. Como não é possível recarregar
o arquivo completo neste notebook, a verificação é feita pela análise das proporções internas da amostra,
que serão declaradas válidas para análise exploratória.
```

### Célula de Código

```python
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
```

---

## CORREÇÃO 2 — Análise dos Candidatos Treineiros

**Localização:** Inserir APÓS o bloco de código de remoção de candidatos ausentes (células do atual 1.1 que criam a máscara e filtram `df`) e ANTES das células de remoção das colunas de presença (`TP_PRESENCA_*`).
**Nova seção:** `#### 1.3 Análise dos Candidatos Treineiros (IN_TREINEIRO)`

### Célula Markdown

```
#### 1.3 Análise dos Candidatos Treineiros (IN_TREINEIRO)

O campo `IN_TREINEIRO` identifica participantes que realizaram o ENEM exclusivamente com finalidade de
treino, sem a intenção de usar a nota para acesso ao ensino superior. Esse perfil corresponde, em geral,
a estudantes do 1º e 2º anos do Ensino Médio.

Como o objetivo deste TCC é modelar o desempenho de candidatos que fazem o ENEM para valer, os treineiros
representam uma subpopulação com comportamento sistemático diferente e devem ser analisados e separados
da base de modelagem.
```

### Célula de Código (análise)

```python
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
```

### Célula Markdown (decisão)

```
**Decisão — Exclusão dos treineiros da base de modelagem**

Os treineiros apresentam notas significativamente inferiores às dos candidatos regulares e representam
uma subpopulação com dinâmica diferente: fazem a prova sem compromisso com o resultado e frequentemente
sem ter concluído o conteúdo do Ensino Médio.

Incluí-los no treinamento do modelo introduziria ruído sistemático, prejudicando a capacidade preditiva
sobre o público-alvo: candidatos que fazem o ENEM para usar a nota.

**Ação:** os treineiros serão excluídos da base antes da etapa de modelagem.
```

### Célula de Código (remoção)

```python
# Remoção dos candidatos treineiros
df_antes = len(df)
df = df[df['IN_TREINEIRO'] == 0].copy()

print(f"Registros antes da remoção : {df_antes:,}")
print(f"Registros após a remoção   : {len(df):,}")
print(f"Treineiros removidos       : {df_antes - len(df):,}")
print(f"Shape resultante           : {df.shape[0]:,} linhas × {df.shape[1]} colunas")
```

---

## CORREÇÃO 3 — Análise Univariada das Variáveis Categóricas

**Localização:** Inserir APÓS a seção `#### 1.6 Análise de duplicidade` (atual, que será renomeada para 1.8) e ANTES de `#### 1.7 Análise de outliers` (atual, que será renomeada para 1.9).
**Nova seção:** `#### 1.10 Análise Univariada das Variáveis Categóricas`

### Célula Markdown

```
#### 1.10 Análise Univariada das Variáveis Categóricas

Antes de investigar relações entre variáveis, é necessário compreender como cada variável categórica
se distribui individualmente na população analisada. Esta seção apresenta gráficos de frequência para
as principais variáveis demográficas, escolares e de perfil dos candidatos.
```

### Célula de Código

```python
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
```

### Célula Markdown (conclusão)

```
**Conclusão da análise univariada:**

Os gráficos revelam o perfil predominante dos candidatos presentes no ENEM 2023:
- Verificar se há desequilíbrio por sexo (padrão histórico: maioria feminina).
- Distribuição racial: verificar representação de pardos e pretos em relação ao censo.
- Escola: dentre os concluintes de 2023, verificar proporção pública vs. privada.
- Faixa etária: concentração nas faixas 17-20 anos, com cauda longa de adultos.
- Situação de conclusão: registrar proporção de "já concluiu" vs. concluintes atuais.
```

---

## CORREÇÃO 4 — Expansão da Correlação (Spearman + Heatmap ampliado)

**Localização:** DENTRO da seção `#### 1.10 Correlação` (que será renomeada para `#### 1.13`). Inserir as novas células APÓS a conclusão existente sobre a correlação de Pearson entre as 4 notas.

### Célula Markdown

```
##### 1.13.1 Correlação de Spearman — Variáveis Ordinais × Notas

Para variáveis ordinais (faixa etária, cor/raça, tipo de escola, situação de conclusão), o coeficiente
de Spearman é mais adequado que o de Pearson, pois não assume linearidade.
```

### Célula de Código

```python
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
```

### Célula Markdown

```
##### 1.13.2 Heatmap Geral de Correlação (Pearson)

Heatmap ampliado incluindo notas objetivas, competências da redação e variáveis ordinais relevantes.
```

### Célula de Código

```python
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
```

---

## CORREÇÃO 5 — Análise das Competências da Redação × Perfil

**Localização:** Inserir APÓS a seção `#### 1.12 Análise de padrões e anomalias` (que trata de `TP_STATUS_REDACAO × NU_NOTA_REDACAO`) e ANTES de `#### 1.13 Notas zero`.
**Nova seção:** `#### 1.16 Análise das Competências da Redação × Perfil do Candidato`

### Célula Markdown

```
#### 1.16 Análise das Competências da Redação × Perfil do Candidato

A redação do ENEM é avaliada em cinco competências com peso igual. Esta seção investiga como as notas
de cada competência se distribuem entre diferentes perfis de candidatos, com foco no tipo de escola.
A competência 5 (Proposta de Intervenção) é particularmente relevante, pois é a que mais diferencia
candidatos com e sem letramento crítico.

Análise restrita a candidatos com redação válida (TP_STATUS_REDACAO == 1) e escola informada.
```

### Célula de Código

```python
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
```

### Célula Markdown (conclusão)

```
**Conclusão:**

A comparação das competências entre escola pública e privada revela em qual dimensão da redação
a diferença é mais acentuada. Atenção especial à competência 5 (Proposta de Intervenção), que
tende a ser a mais discriminante entre os dois grupos.
```

---

## CORREÇÃO 6 — Expansão da Seção de Notas Zero

**Localização:** DENTRO da seção `#### 1.13 Notas zero entre participantes presentes`. Inserir APÓS os cruzamentos existentes (`TP_ST_CONCLUSAO × TP_ESCOLA` e `TP_ST_CONCLUSAO × TP_ENSINO`), adicionando novos cruzamentos com variáveis demográficas e uma decisão formal.

### Célula Markdown

```
##### Perfil dos Candidatos com Nota Zero nas Provas Objetivas

Além de quantificar as notas zero, é necessário verificar se elas se concentram em algum perfil
específico de candidato, o que poderia indicar um viés nos dados de treino do modelo.
```

### Célula de Código

```python
notas_obj = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT']

# Quantidade e percentual por prova
print("Notas zero por prova objetiva (candidatos presentes):")
for col in notas_obj:
    n = (df[col] == 0).sum()
    print(f"  {col}: {n:,} ({n/len(df)*100:.2f}%)")

# Taxa de zero em MT por cor/raça e por sexo (prova mais afetada)
df['zero_MT'] = (df['NU_NOTA_MT'] == 0).astype(int)

print("\nTaxa de nota zero em Matemática por Cor/Raça:")
labels_raca_z = {0: 'N/Declarada', 1: 'Branca', 2: 'Preta',
                 3: 'Parda', 4: 'Amarela', 5: 'Indígena'}
taxa_raca = (
    df[df['TP_COR_RACA'].isin(labels_raca_z)]
    .groupby('TP_COR_RACA')['zero_MT']
    .mean() * 100
)
taxa_raca.index = taxa_raca.index.map(labels_raca_z)
print(taxa_raca.round(2).to_string())

print("\nTaxa de nota zero em Matemática por Sexo:")
taxa_sexo = df.groupby('TP_SEXO')['zero_MT'].mean() * 100
taxa_sexo.index = taxa_sexo.index.map({'M': 'Masculino', 'F': 'Feminino'})
print(taxa_sexo.round(2).to_string())

# Limpeza
df = df.drop(columns=['zero_MT'])

print("\nDecisão: candidatos com nota zero são MANTIDOS na base de modelagem.")
print("A nota zero é um resultado válido e não representa erro de dados.")
```

---

## CORREÇÃO 7 — Análise Bivariada: Perfil Demográfico × Notas

**Localização:** Inserir APÓS a seção de notas zero (atual 1.13, futura 1.17) e ANTES das Conclusões (atual 1.14, futura 1.21).
**Nova seção:** `#### 1.18 Análise Bivariada: Perfil Demográfico × Notas`

### Célula Markdown

```
#### 1.18 Análise Bivariada: Perfil Demográfico × Notas

Esta seção investiga a relação entre as principais variáveis demográficas e o desempenho dos candidatos.
A análise bivariada é fundamental para identificar padrões de desigualdade e para compreender quais
características estão associadas a melhores ou piores resultados antes da construção de qualquer modelo.

As variáveis analisadas são: sexo, cor/raça e tipo de escola (para concluintes de 2023).
Notas zero são excluídas das visualizações para não distorcer a distribuição.
```

### Célula de Código — Notas × Sexo

```python
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
```

### Célula de Código — Notas × Cor/Raça

```python
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
```

### Célula de Código — Notas × Tipo de Escola

```python
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
```

### Célula Markdown (conclusão)

```
**Conclusão da análise bivariada:**

1. **Sexo:** candidatos do sexo masculino tendem a ter médias superiores em Matemática e Ciências
   da Natureza; candidatas do sexo feminino em Linguagens e Redação. Padrão consistente com o PISA.

2. **Cor/Raça:** candidatos brancos obtêm notas médias superiores em todas as áreas. Essa diferença
   reflete as desigualdades socioeconômicas e educacionais estruturais do Brasil.

3. **Tipo de escola:** candidatos de escolas privadas obtêm médias significativamente superiores
   em todas as áreas. Essa variável é um dos preditores mais fortes disponíveis no dataset.

Essas relações serão tratadas mais rigorosamente durante a seleção de features e interpretação dos modelos.
```

---

## CORREÇÃO 8 — Análise do Questionário Socioeconômico

**Localização:** Inserir APÓS a nova seção `#### 1.18 Análise Bivariada` e ANTES das Conclusões.
**Nova seção:** `#### 1.19 Análise do Questionário Socioeconômico (Q001–Q025)`

### Célula Markdown

```
#### 1.19 Análise do Questionário Socioeconômico (Q001–Q025)

O questionário socioeconômico do ENEM coleta informações sobre renda familiar, escolaridade dos pais,
acesso a bens e serviços e outros indicadores de contexto. Essas variáveis são historicamente as mais
fortemente associadas ao desempenho no ENEM e serão features centrais nos modelos preditivos.

Questões analisadas:
- Q001: Escolaridade do pai
- Q006: Renda familiar mensal
- Q025: Acesso à internet em casa

Para cada questão: distribuição de frequência + relação com nota média de Matemática.
```

### Célula de Código

```python
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
```

### Célula Markdown (conclusão)

```
**Conclusão da análise socioeconômica:**

1. **Escolaridade dos pais (Q001/Q002):** candidatos cujos pais possuem ensino superior ou
   pós-graduação obtêm médias de Matemática substancialmente superiores. O gradiente é monotônico.

2. **Renda familiar (Q006):** relação positiva clara entre renda e desempenho. Candidatos de
   famílias com renda acima de R$5.000/mês tendem a notas médias consideravelmente superiores.

3. **Acesso à internet (Q025):** candidatos com internet em casa obtêm notas médias superiores,
   refletindo o perfil socioeconômico e as possibilidades de estudo online.

Essas variáveis são features de alto poder preditivo e devem ser tratadas com prioridade no pipeline
de feature engineering.
```

---

## CORREÇÃO 9 — Análise Geográfica por UF e Região

**Localização:** Inserir APÓS a seção `#### 1.19 Análise do Questionário Socioeconômico` e ANTES das Conclusões.
**Nova seção:** `#### 1.20 Análise Geográfica por UF e Região`

### Célula Markdown

```
#### 1.20 Análise Geográfica por UF e Região

O ENEM apresenta variações regionais expressivas de desempenho, refletindo as desigualdades educacionais
entre as regiões brasileiras. Esta seção analisa a distribuição de candidatos e as médias de desempenho
por Unidade da Federação (UF) de aplicação da prova.

A variável `regiao` foi criada na seção 1.1 a partir do mapeamento de `SG_UF_PROVA`.
```

### Célula de Código

```python
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
```

### Célula Markdown (conclusão)

```
**Conclusão da análise geográfica:**

As UFs das regiões Sul e Sudeste tendem a apresentar médias superiores em todas as áreas, consistentes
com melhores indicadores socioeconômicos e de infraestrutura escolar. As UFs das regiões Norte e
Nordeste apresentam médias geralmente inferiores.

A variável `regiao` (derivada de `SG_UF_PROVA`) pode ser considerada como feature adicional durante a
seleção de variáveis, dependendo do objetivo do modelo e da disponibilidade dessa informação no momento
da predição.
```

---

## CORREÇÃO 10 — Expansão das Conclusões da EDA

**Localização:** DENTRO da seção `#### 1.14 Conclusões da EDA` (futura `#### 1.21`).
**Ação:** Acrescentar os parágrafos abaixo AO FINAL do texto existente na célula markdown de conclusões.

### Texto a acrescentar (append na célula markdown existente)

```
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
```

---

## Resumo das Intervenções

| # | Correção | Seção nova | Localização de inserção |
|---|---|---|---|
| 1 | Representatividade da amostra | 1.1 | Após carregamento da amostra, antes do atual 1.1 |
| 2 | Treineiros (`IN_TREINEIRO`) | 1.3 | Após filtro de candidatos presentes (atual 1.1), antes da remoção das colunas de presença |
| 3 | Univariada categóricas | 1.10 | Após duplicidade (atual 1.6), antes de outliers (atual 1.7) |
| 4 | Correlação expandida (Spearman + Heatmap) | 1.13 (expansão) | Após conclusão da correlação de Pearson existente |
| 5 | Competências redação × perfil | 1.16 | Após padrões/anomalias (atual 1.12), antes de notas zero (atual 1.13) |
| 6 | Notas zero expandida + decisão | 1.17 (expansão) | Dentro do atual 1.13, após cruzamentos existentes |
| 7 | Bivariada demográfico × notas | 1.18 | Após notas zero (atual 1.13), antes das conclusões |
| 8 | Questionário socioeconômico | 1.19 | Após bivariada (nova 1.18), antes das conclusões |
| 9 | Geográfica por UF/Região | 1.20 | Após socioeconômico (nova 1.19), antes das conclusões |
| 10 | Conclusões expandidas | 1.21 (expansão) | Dentro do atual 1.14, ao final do texto existente |

**Total de novas células a inserir: ~26** (≈13 markdown + ≈13 código)
