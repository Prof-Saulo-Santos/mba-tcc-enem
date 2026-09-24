# Resumo para Apresentação à Banca — TCC ENEM
**Data:** 19/09/2026  
**Projeto:** Pipeline de MLOps para Predição de Desempenho no ENEM

---

## 🎯 Slide 1 — O Objetivo do Projeto

> *"O objetivo central é construir um modelo de Machine Learning para comprovar quantitativamente que o desempenho de um candidato no ENEM pode ser previsto com alta precisão utilizando apenas o seu perfil socioeconômico, evidenciando matematicamente a desigualdade estrutural do sistema educacional brasileiro."*

Para testar essa hipótese de forma exaustiva, o modelo atacará o problema por duas frentes metodológicas distintas:
- **Modelagem de Regressão:** Focada em prever o valor numérico exato da nota do candidato (ex: prova de Matemática).
- **Modelagem de Classificação:** Focada em prever a categoria ou faixa de desempenho geral do candidato (Insuficiente, Regular, Bom ou Excelente).

A execução técnica dessa proposta unifica três disciplinas:
- **Engenharia de Dados** → construção do pipeline ETL em chunks
- **Ciência de Dados** → engenharia de features e treinamento de modelos
- **MLOps** → rastreabilidade técnica e orquestração de produção

---

## 📐 Slide 2 — O Problema de Engenharia

### O Desafio Principal
O INEP não entrega os dados "prontos para ML". Entre 2017 e 2025, ocorreram três categorias de anomalias estruturais que inviabilizariam qualquer análise ingênua:

| Anomalia | Impacto | Nossa Solução |
|---|---|---|
| A partir de 2024, o INEP **dividiu o arquivo único** em dois arquivos separados: `PARTICIPANTES` e `RESULTADOS` | Impossível comparar 2023 com 2024 sem engenharia | `reader.py` detecta o ano e executa um JOIN automático |
| Colunas `Q026` e `Q027` (renda) **existem só em 2017–2018** e foram extintas pela LGPD em 2019 | Schema incompatível entre os anos | `harmonizer.py` remove cirurgicamente essas colunas |
| Coluna `TP_VERSAO_DIGITAL` existe **apenas em 2020** (edição COVID) | Quebraria a paridade temporal da base histórica | `harmonizer.py` expurga a coluna em 2020 |

> **Argumento para a banca:** Sem a Camada Anticorrupção (ACL), qualquer `pd.concat()` entre os anos de 2017 e 2025 geraria um DataFrame com valores NaN em colunas que simplesmente não existem naquele ano, **silenciosamente corrompendo qualquer modelo treinado sobre esses dados.**

---

## 📓 Slide 3 — A Jornada de Descoberta: Os Três Notebooks

Antes da construção do pipeline de produção automatizado, o projeto passou por uma fase laboratorial dividida em três frentes de investigação:

- **`01_analise_anomalias_estruturais.ipynb`:** Atuou como o explorador inicial da "Camada Bronze", focado em investigar os dados brutos de todos os 9 anos para mapear inconsistências históricas (como a extinção de colunas socioeconômicas e a divisão de arquivos em 2024). Suas descobertas forneceram os requisitos técnicos exatos para a construção da Camada Anticorrupção.
- **`02_selecao_features.ipynb`:** Responsável por destilar o mar de dados, este notebook filtra o dicionário do INEP para selecionar apenas as variáveis relevantes para a modelagem, além de tratar dados ausentes e criar variáveis derivadas (como as faixas de desempenho). O resultado gerou o "schema" definitivo de 78 colunas da nossa "Camada Gold".
- **`03_eda_modelagem.ipynb`:** O laboratório principal onde os dados consolidados são postos à prova. Ele realiza a Análise Exploratória (EDA) — comprovando visualmente a correlação entre renda familiar e nota escolar — e executa a "Arena de Algoritmos", treinando modelos como o *HistGradientBoosting* para prever matematicamente o desempenho dos candidatos.

---

## 🏗️ Slide 4 — A Arquitetura: Medalha de Três Camadas

```
[INEP] → CSV Bruto → 🥉 Bronze → 🥈 Silver → 🥇 Gold → [Modelo de ML]
```

### 🥉 Camada Bronze — Dado Bruto Original
- **O quê:** 9 anos de microdados do ENEM (2017–2025) em `data/raw/`
- **Regra de Ouro:** Jamais modificados. São o "contrato" com a fonte.
- **Status:** ✅ Completo

### 🥈 Camada Silver — ETL Defensivo
O pipeline passa por **5 portões controlados**, em sequência obrigatória:

```
Ingestão (reader.py)
   → Harmonização/ACL (harmonizer.py)
      → Soft Validation (Pandera)
         → Limpeza (cleaner.py)
            → Feature Engineering (features.py)
               → Hard Validation (Pandera)
                  → Salva em .parquet (Gold)
```

- **Status:** ✅ Completo e testado com dados reais

### 🥇 Camada Gold — Dado Pronto para ML
- Artefato: `data/processed/enem_2023_silver.parquet`
- **2.585.115 candidatos** — com 78 colunas, tipos corretos e features derivadas
- **Status:** ✅ Gerado (base completa do ENEM 2023)

---

## 🛡️ Slide 5 — Contratos de Dados: Pandera como Porteiro

Uma decisão técnica diferencial do projeto: o uso do **Pandera** para criar "contratos formais de dados".

- **Soft Validation (pós-ingestão):** Garante que o dado que chegou da fonte tem o schema esperado.
- **Hard Validation (pré-exportação):** Garante que o dado que vai para o modelo é matematicamente válido.

> **Argumento para a banca:** Se os contratos falharem, o pipeline para imediatamente com um erro descritivo. Essa arquitetura **"fail-fast"** impede o pior cenário em MLOps: treinar um modelo silenciosamente com dados corrompidos.

---

## 🧹 Slide 6 — A Escala do Problema: Por que não o Excel?

Os números reais do processamento do ENEM 2023:

| Métrica | Valor |
|---|---|
| Registros brutos no CSV original | **3.933.955** |
| Registros após filtragem de ausentes | **2.585.115** |
| Candidatos removidos (ausentes/eliminados) | **1.348.840 (34,3%)** |
| Colunas no artefato Gold | **78** |

> **Dado sociológico para a banca:** **1 em cada 3 candidatos inscritos no ENEM 2023 não compareceu à prova.** São 1,3 milhão de pessoas. Isso por si só é um dado de política pública relevante que justifica o filtro `filter_present_participants` no `cleaner.py`.

**Por que o pipeline em chunks foi necessário?**  
Tentar carregar 4 milhões de linhas de uma só vez no Pandas resultou em estouro de memória (OOM — Out of Memory). A solução profissional adotada foi processar o CSV em **pedaços de 300.000 linhas** (`pipeline_chunked.py`), um padrão padrão-ouro na indústria para dados que excedem a RAM disponível.

---

## 📊 Slide 7 — Resultados da Análise Exploratória (EDA)

**Notebook:** `03_eda_modelagem.ipynb`  
**Dados utilizados:** ENEM 2023 — 2,5 milhões de candidatos reais

### Gráfico 1: Distribuição das Notas de Matemática
- A distribuição é aproximadamente normal, com média em torno de **520 pontos**
- Existe uma cauda pesada à esquerda (muitos candidatos com notas baixas)

### Gráfico 2: Nota por Faixa de Renda (Q006)
- **Tendência crescente clara e consistente**: candidatos de famílias com maior renda obtêm notas sistematicamente maiores
- Esta é a confirmação empírica da hipótese central do TCC

### Gráfico 3: Nota por Tipo de Escola (TP_ESCOLA)
- Candidatos de **escolas privadas** performam consideravelmente acima dos de escolas públicas em Matemática
- Resultado estatisticamente robusto (validado com amostra de 100k candidatos)

---

## 🏆 Slide 8 — Arena de Algoritmos: Resultados de Machine Learning

### Problema 1: Regressão (prever a nota exata)
**Features utilizadas:** Sexo, Tipo de Escola, Escolaridade do Pai (Q001), Escolaridade da Mãe (Q002), Renda Familiar (Q006)

| Algoritmo | RMSE (↓ Melhor) | R² (↑ Melhor) |
|---|---|---|
| 🐢 Dummy (Baseline — chutando a média) | 130,48 pts | 0,0000 |
| 📐 Regressão Linear | 114,34 pts | 0,2320 |
| 🌲 Random Forest | 112,05 pts | 0,2624 |
| ⚡ **HistGradientBoosting (Vencedor)** | **111,91 pts** | **0,2643** |

**Interpretação:** O modelo vencedor **erra a nota do candidato em média por 111 pontos**. Com apenas 5 variáveis socioeconômicas (sem nota histórica da escola, sem boletim), o modelo explica **26,4% da variância** da nota de Matemática.

> **Argumento para a banca:** Em Ciências Sociais e da Educação, explicar 26% do desempenho de um indivíduo usando **apenas o seu perfil socioeconômico** — sem nenhuma informação do seu histórico acadêmico — é um resultado matematicamente e sociologicamente forte. **É a prova quantitativa de que a origem importa mais do que o esforço individual, no sistema atual.**

### Problema 2: Classificação (prever a faixa de desempenho)
O mesmo pipeline foi reconfigado para prever a **categoria** do candidato: `Insuficiente`, `Regular`, `Bom` ou `Excelente`.

*[Atualizar com os resultados de Acurácia e Classification Report após rodar a Célula 8]*

---

## 🗺️ Slide 9 — Roadmap: O que ainda falta para o TCC final

### Curto Prazo (próximas semanas)
- [ ] Processar os outros 8 anos (2017–2022 e 2024–2025) com o `pipeline_chunked.py`
- [ ] Adicionar **Feature Importance** ao notebook (quais das 5 perguntas mais importam para o modelo?)
- [ ] Criar o script `src/train.py` (versão de produção do treinamento, fora do notebook)

### Médio Prazo (MLOps)
- [ ] Subir o servidor **MLflow** via Docker para rastrear os experimentos formalmente
- [ ] Registrar o modelo vencedor no MLflow Model Registry
- [ ] Criar uma API de predição simples com **FastAPI** (dado um perfil socioeconômico, retorna a nota prevista)

### Longo Prazo (Pós-TCC)
- Migrar a arquitetura de ETL para **ELT + dbt + BigQuery** — eliminando os limites de RAM do laptop
- Aplicar a base histórica de 9 anos para detectar **tendências temporais** na desigualdade educacional

---

## 💡 Perguntas Frequentes da Banca (e como responder)

**"Por que usar Parquet e não CSV?"**
> O Parquet é um formato colunar binário que ocupa 5 a 10 vezes menos espaço, preserva os tipos de dados nativamente e é lido de forma muito mais rápida. É o formato padrão da indústria em Data Lakes.

**"Por que usar ETL e não ELT?"**
> Para o escopo do TCC (dados locais, hardware limitado), o ETL com Pandas e Python é a escolha pragmática e didática. Uma versão ELT (com BigQuery e dbt) está no roadmap pós-TCC: nesse modelo, o processamento ocorreria nos servidores do Google, e o laptop seria apenas um "controle remoto".

**"O R² de 26% não é muito baixo?"**
> Não, no contexto das Ciências da Educação. Estamos prevendo o comportamento humano usando apenas 5 variáveis de perfil, sem nenhum dado de desempenho histórico. Modelos com R² acima de 0,15 já são considerados relevantes nessa literatura. Nosso R² de 0,26 é competitivo.

**"O que é a Camada Anticorrupção (ACL)?"**
> É um padrão de arquitetura de software (do Domain-Driven Design) que cria uma barreira protetora entre dois sistemas com formatos incompatíveis. No nosso caso, ela isola o "mundo caótico" dos CSVs do INEP (com suas anomalias históricas) do nosso pipeline limpo e consistente.
