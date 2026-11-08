# 📊 Roteiro para Slides: Notebook 04 — Harmonização Semântica e Governança via NLP (2009–2025)

**Projeto de TCC:** MBA em Ciência de Dados / MLOps — Predição de Desempenho no ENEM  
**Autor:** Saulo Santos  
**Objetivo deste Roteiro:** Fornecer textos curtos, diretos e blocos modulares mapeados célula por célula do [notebooks/04_varredura_semantica.ipynb](file:///home/saulo/mba/tcc/enem/notebooks/04_varredura_semantica.ipynb), com pequenos trechos de código ideais para projeção em slides.

---

## 🧭 Visão Panorâmica da Apresentação

1. **O Problema:** Deriva Semântica (*Semantic Drift*) e de Esquema em 17 anos do ENEM (2009–2025).
2. **A Solução Inteligente:** Embeddings SBERT multilíngue + Similaridade de Cosseno + *Human-in-the-Loop* (HITL).
3. **A Blindagem Matemática:** Restrição Injetiva 1-para-1 (Algoritmo Húngaro) e Tripla Validação Administrativa.
4. **Governança de Dados Baseada em Testes:** Auditoria física direta nos CSVs brutos (> 60M de linhas) e SLA de *Data Quality*.
5. **O Entregável de MLOps:** Contrato canônico auditável `schema_mapping_historico.json` com arquitetura *Dual-Contract*.

---

## 🧱 Bloco 1: Configuração, Reprodutibilidade e SBERT
> **Mapeamento no Notebook:** Célula 00 (Markdown) e Célula 01 (Código) — *Seção 1*

### Texto para o Slide (Bullets Curtos)
* **O Desafio do Big Data:** 17 edições do ENEM (2009–2025) somando > 70 milhões de inscrições brutas.
* **O Problema do Schema Drift:** O INEP altera nomes de colunas, recicla códigos e reformula enunciados textuais.
* **Modelo NLP Utilizado:** `paraphrase-multilingual-MiniLM-L12-v2` (Sentence-Transformers).
* **Reprodutibilidade Estrita:** Fixação de sementes determinísticas (`seed=42`) e registro das versões de runtime.

### Trecho de Código para o Slide
```python
# Célula 01 — Reprodutibilidade e Motor NLP
torch.manual_seed(42)
np.random.seed(42)

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
# Embeddings densos de 384 dimensões otimizados para similaridade semântica
```

### Frase de Impacto para a Banca
> *"Não usamos heurísticas manuais em Excel. Aplicamos Modelos de Linguagem sobre os metadados do INEP para automatizar a governança semântica com reprodutibilidade determinística."*

---

## 🧱 Bloco 2: Contrato Canônico de 2023 e Embeddings Base
> **Mapeamento no Notebook:** Célula 02 (Markdown) e Célula 03 (Código) — *Seção 2*

### Texto para o Slide (Bullets Curtos)
* **Ano-Base Padrão-Ouro:** ENEM 2023 (definido no Notebook 03 após rigorosa validação cruzada).
* **Escopo Estrito de 15 Variáveis Canônicas:**
  * **Identificador (1):** `NU_INSCRICAO`.
  * **Preditores de Elite (6):** `RENDA_PER_CAPITA`, `Q024` (computador), `TP_ANO_CONCLUIU`, `TP_LINGUA`, `TP_SEXO` e `Q002` (mãe).
  * **Flags de Presença (4):** `TP_PRESENCA_CN`, `CH`, `LC`, `MT`.
  * **Provas da TRI (4):** `NU_NOTA_CN`, `CH`, `LC`, `MT` (cálculo oficial do `TARGET_M4`).
* **Vetorização Canônica:** Geração dos 15 embeddings vetoriais de referência ($15 \times 384$).

### Trecho de Código para o Slide
```python
# Célula 03 — Embeddings dos Enunciados Canônicos (2023)
descricoes_canonicas = [CONTRATO_CANONICO[col]["descricao"] for col in nomes_canonicos]
embeddings_canonicos = model.encode(descricoes_canonicas, convert_to_tensor=True)
embeddings_canonicos = F.normalize(embeddings_canonicos, p=2, dim=1)
```

### Frase de Impacto para a Banca
> *"O contrato canônico é a nossa âncora. Nenhuma coluna histórica é aceita sem provar matematicamente a correspondência conceitual com as 15 variáveis padrão-ouro de 2023."*

---

## 🧱 Bloco 3: Parser Multi-Aba Robusto dos Dicionários do INEP
> **Mapeamento no Notebook:** Célula 04 (Markdown) e Célula 05 (Código) — *Seção 3*

### Texto para o Slide (Bullets Curtos)
* **A Armadilha dos Metadados Governamentais:** Planilhas Excel com cabeçalhos deslocados, mesclados e abas heterogêneas.
* **Barreiras de Qualidade do Extrator:**
  1. *Coocorrência de Cabeçalho:* Exige termos de 'Nome/Variável' E 'Descrição' simultaneamente;
  2. *Filtro Ativo:* Descarte automático de abas espúrias (`ITENS`, `HAB_ESTUDO`, `LEIA`);
  3. *Detecção de Conflitos:* Compara variáveis duplicadas inter-abas (ex.: em bases bipartidas como 2024);
  4. *Rastreamento de Linhagem:* Registro da `aba_origem` de cada variável extraída.

### Trecho de Código para o Slide
```python
# Célula 05 — Extração Robusta e Rastreável
dicionario_ano = extrair_dicionario_multiaba(caminho_planilha)
# 2024: 5 variáveis comuns entre abas validadas com 100% de identidade semântica
```

### Frase de Impacto para a Banca
> *"Antes de passar os metadados para a IA, nosso extrator audita a linhagem das abas e prova que não há conflito semântico nas planilhas do governo."*

---

## 🧱 Bloco 4: Motor de Similaridade Semântica, HITL e Injetividade
> **Mapeamento no Notebook:** Célula 06 (Markdown) e Célula 07 (Código) — *Seção 4*

### Texto para o Slide (Bullets Curtos)
* **Similaridade de Cosseno:** Mede o ângulo vetorial entre os enunciados históricos e canônicos:
  $$\text{Sim}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2} \ge 0.70$$
* **Superação da "Caixa-Preta" (HITL):** O SBERT recomenda candidatos; a homologação final exige validação documental humana.
* **Restrição Injetiva 1-para-1:** Uso da formulação matemática de atribuição ótima (*Algoritmo Húngaro*): duas perguntas canônicas não podem mapear para a mesma pergunta histórica.
* **Tripla Validação Administrativa:** Nomes idênticos (`TP_ST_CONCLUSAO`, `TP_ANO_CONCLUIU`) só são aceitos após checagem de domínio categórico e enunciado.

### Trecho de Código para o Slide
```python
# Célula 07 — Atribuição Linear Ótima e Gatekeeper HITL
sim_matrix = cosine_similarity(embeddings_canonicos, embeddings_historicos)
row_ind, col_ind = linear_sum_assignment(-sim_matrix)  # Maximização Global

# Restrição defensiva: injetividade 1-para-1 obrigatória
assert len(set(mapeamento.values())) == len(mapeamento), "Colisão de Schema detectada!"
```

### Frase de Impacto para a Banca
> *"Eliminamos falsos positivos do NLP aplicando a Restrição Injetiva do Algoritmo Húngaro e mantendo o especialista humano no circuito decisório."*

---

## 🧱 Bloco 5: Matriz de Drift e Diagnóstico Visual (Heatmap)
> **Mapeamento no Notebook:** Células 08 a 11 — *Seção 5*

### Texto para o Slide (Bullets Curtos)
* **Heatmap Longitudinal (2009–2025):** Mapa de calor visual exibindo a similaridade semântica ao longo dos 17 anos.
* **Descoberta do Drift Nominal:**
  * Computador: `Q010` (2014) $\rightarrow$ `Q024` (2015–2023) $\rightarrow$ `Q021` (2024–2025) (Similaridade $> 0.95$).
  * Renda Familiar: `Q003` (2014) $\rightarrow$ `Q006` (2015–2025) (Similaridade $> 0.92$).
* **Fronteira Histórica Nítida:** Ruptura estrutural clara anterior a 2014; estabilidade de 2014 em diante.

### Trecho de Código para o Slide
```python
# Célula 11 — Visualização da Estabilidade Longitudinal
sns.heatmap(df_similaridades_heatmap, cmap="YlGnBu", annot=True, vmin=0.6, vmax=1.0)
plt.title("Estabilidade Semântica Longitudinal dos Preditores do ENEM (2009–2025)")
```

### Frase de Impacto para a Banca
> *"O heatmap visual comprova como perguntas conceituais idênticas migraram silenciosamente de código, provando a necessidade imperativa do NLP."*

---

## 🧱 Bloco 6: Auditoria de Categorias e Valores (*Value Drift*)
> **Mapeamento no Notebook:** Célula 12 (Markdown) e Célula 13 (Código) — *Seção 6*

### Texto para o Slide (Bullets Curtos)
* **O Conceito de Value Drift:** Variáveis com o mesmo nome e enunciado podem alterar sua escala numérica interna.
* **Auditoria de Renda (2014 vs. 2023):**
  * Confronto direto dos limites monetários oficiais de Salário Mínimo (SM).
  * Ambos os questionários adotam rigorosamente a mesma régua de **17 faixas proporcionais ao Salário Mínimo** (Letras de A a Q).
* **Conclusão:** A conversão contínua em múltiplos de Salário Mínimo neutraliza a inflação e assegura comparabilidade temporal perfeita.

### Trecho de Código para o Slide
```python
# Célula 13 — Validação de Categorias de Renda
categorias_2014 = extrair_opcoes("Q003", dicionario_2014)  # 17 faixas de SM (A a Q)
categorias_2023 = extrair_opcoes("Q006", dicionario_2023)  # 17 faixas de SM (A a Q)
assert len(categorias_2014) == len(categorias_2023) == 17, "Descontinuidade de faixas!"
```

### Frase de Impacto para a Banca
> *"Auditamos a escala interna da renda: a correspondência de 17 faixas baseadas no Salário Mínimo protege o modelo contra distorções inflacionárias na série temporal."*

---

## 🧱 Bloco 7: Veredito Metodológico e o Contrato Canônico de MLOps
> **Mapeamento no Notebook:** Células 14 a 17 — *Seções 7 e 8*

### Texto para o Slide (Bullets Curtos)
* **Framework dos Três Horizontes de Maturidade:**
  * **Conjunto A (2014–2023):** *Treinamento e Benchmark* $\rightarrow$ `APROVADA_PARA_BASELINE` (A Década de Ouro).
  * **Conjunto B (2024):** *Reserva Out-of-Time* $\rightarrow$ `PENDENTE_CONFIRMACAO_ALINHAMENTO` (Base Bipartida).
  * **Conjunto C (2025):** *Teste Sintático* $\rightarrow$ `PRELIMINAR_SEM_NOTAS` (Inapto para prever target).
  * **Reprovadas (2009–2010):** Descarte por ausência física da variável de computador (`Q024`).
  * **Pendentes (2011–2013):** Descontinuidade de faixas de renda (hipótese para teste de estresse).
* **Padrão Dual-Contract (`schema_mapping_historico.json`):**
  1. *Raiz do JSON:* Dicionários `{canonica: historica}` ($100\%$ retrocompatível com ETL);
  2. *Nó `_metadata`:* Hashes SHA-256 dos 17 arquivos Excel, parâmetros do SBERT e fichas de decisão.

### Trecho de Código para o Slide
```python
# Célula 17 — Exportação do Contrato Canônico Auditável
contrato_mlops = {
    "_metadata": {
        "versao_contrato": "3.5",
        "modelo_sbert": "paraphrase-multilingual-MiniLM-L12-v2",
        "hashe_insumos_sha256": hashes_dicionarios,
        "horizontes": {"conjunto_a": "2014-2023", "conjunto_b": "2024", "conjunto_c": "2025"}
    },
    "2014": {"Q006": "Q003", "Q024": "Q010", ...},  # Operacional direto
    "2015": {"Q006": "Q006", "Q024": "Q024", ...}
}
```

### Frase de Impacto para a Banca
> *"Nosso artefato não é uma lista estática de variáveis. É um contrato de MLOps criptograficamente rastreável com SHA-256 que orienta a esteira de Big Data."*

---

## 🧱 Bloco 8: Auditoria Física Amostral dos Microdados (2014–2023)
> **Mapeamento no Notebook:** Célula 18 (Markdown) e Célula 19 (Código) — *Seção 9*

### Texto para o Slide (Bullets Curtos)
* **Da Teoria à Realidade Transacional:** Dicionário é metadado nominal; foi mandatório auditar os arquivos CSV brutos.
* **Amostragem Ponderada por Blocos:** $20.000$ registros sorteados de forma equilibrada em cada ano ($N = 200.000$ auditados).
* **Evidências Empíricas Comprovadas (2014–2023):**
  * **Presença Física das 15 Colunas:** $15/15$ confirmadas no cabeçalho de todos os anos ($100\%$).
  * **Zero Notas Inválidas:** Nenhuma nota fora do intervalo $[0, 1000]$ ou corrompida.
  * **Estabilidade Psicométrica do Alvo (`TARGET_M4`):** Média estável em torno de $502$ a $534$ pontos ao longo de uma década inteira.

### Tabela Resumo para o Slide
| Edição | Linhas no CSV | Mapeadas | Flags Inválidas | Notas Inválidas | Elegíveis Amostra | Média TARGET_M4 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2014** | 8.722.248 | 15/15 | 0 | 0 | 13.584 (67,9%) | **502,46** |
| **2016** | 8.627.179 | 15/15 | 0 | 0 | 13.608 (68,0%) | **506,83** |
| **2018** | 3.063.481 | 15/15 | 0 | 0 | 14.711 (73,6%) | **534,55** |
| **2020** | 5.783.109 | 15/15 | 0 | 0 | 8.910 (44,6%*) | **512,86** |
| **2023** | 3.933.955 | 15/15 | 0 | 0 | 13.602 (68,0%) | **519,55** |
*\*Nota: Queda de elegibilidade em 2020 explicada pela abstenção recorde na pandemia de COVID-19.*

### Frase de Impacto para a Banca
> *"Comprovamos na prática: o TARGET_M4 mantém estabilidade histórica contínua em 10 anos de provas, blindando o baseline de treinamento."*

---

## 🧱 Bloco 9: Auditoria Específica da Edição Bipartida (ENEM 2024)
> **Mapeamento no Notebook:** Célula 20 (Markdown) e Célula 21 (Código) — *Seção 9.1*

### Texto para o Slide (Bullets Curtos)
* **A Mudança Estrutural do ENEM 2024:** Primeira edição histórica disponibilizada em arquivos separados:
  * `PARTICIPANTES_2024.csv` (Dados cadastrais / questionário)
  * `RESULTADOS_2024.csv` (Notas das provas)
* **Auditoria de Cardinalidade:** Exatamente **4.332.944 linhas** em cada arquivo (paridade absoluta).
* **O Problema da Chave Primária:** `RESULTADOS_2024.csv` **não possui** a coluna `NU_INSCRICAO`.
* **Decisão Metodológica de Governança:**
  * Paridade de linhas **não prova** correspondência posicional 1:1;
  * Integração mantida **bloqueada** (`PENDENTE_CONFIRMACAO_ALINHAMENTO`) para evitar o risco catastrófico de vincular o perfil socioeconômico de um aluno às notas de outro.

### Trecho de Código para o Slide
```python
# Célula 21 — Trava de Segurança no ENEM 2024
assert registros_participantes == registros_resultados == 4_332_944
ALINHAMENTO_POSICIONAL_DOCUMENTADO_2024 = False  # Trava defensiva mandatória

# Bloqueio deliberado para proteção de integridade
status_2024 = "PENDENTE_CONFIRMACAO_ALINHAMENTO"
```

### Frase de Impacto para a Banca
> *"Agimos com responsabilidade de engenharia: sem comprovação oficial de alinhamento posicional do INEP, não fazemos junção às cegas de notas e cadastros."*

---

## 🧱 Bloco 10: Governança de Data Quality, SLA e Matriz Final de Homologação
> **Mapeamento no Notebook:** Células 23 (Markdown) e 24 (Código) — *Seção 10*

### Texto para o Slide (Bullets Curtos)
* **SLA de Data Quality para Big Data:** Tolerância máxima de **$0,05\%$** para ruídos cadastrais de presença decorrentes de sorteio estocástico.
* **Resultado Empírico:** 9 das 10 safras com $0,000\%$ de ausências; 2016 com 1 caso ($0,005\% \le 0,05\%$) $\rightarrow$ *Conforme dentro do SLA*.
* **Garantia de Expurgo no ETL de Produção ([etl_parquet.py](file:///home/saulo/mba/tcc/enem/scripts/etl_parquet.py)):**
  * Converte nulos de presença para `0` via `.fillna(0)`;
  * Filtra estritamente `(chunk[presencas] == 1).all(axis=1)` em todas as 4 provas.
* **Matriz Final de Decisão:**
  * **10 Safras Homologadas (2014 a 2023):** `APROVADA_PARA_BASELINE`
  * **2024:** `PENDENTE_CONFIRMACAO_ALINHAMENTO` (Reserva *Out-of-Time*)
  * **2025:** `PRELIMINAR_SEM_NOTAS` (Prévia cadastral)
  * **2009–2010:** `REPROVADA_DOCUMENTALMENTE` | **2011–2013:** `PENDENTE_HARMONIZACAO`

### Trecho de Código para o Slide
```python
# Célula 24 — Decisão Orientada por Evidências e Tolerância SLA
TOLERANCIA_TAXA_FLAGS_AUSENTES = 0.0005  # SLA de 0,05%
flags_ausentes_ok = taxa_flags_ausentes <= TOLERANCIA_TAXA_FLAGS_AUSENTES

fisico_ok = colunas_ok and (flags_invalidas == 0) and (notas_invalidas == 0) and flags_ausentes_ok
decisao = "APROVADA_PARA_BASELINE" if (schema_ok and fisico_ok) else "PENDENTE_OU_REPROVADA"
```

### Frase de Impacto para a Banca
> *"A governança do Notebook 04 está concluída e auditada: a Década de Ouro está 100% pronta para alimentar o treinamento do modelo preditivo no Notebook 05."*

---

## 📋 Resumo Executivo para Slides de Fechamento

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ LINHA DO TEMPO HOMOLOGADA — STATUS DE GOVERNANÇA (17 EDIÇÕES DO ENEM)                  │
├─────────────────┬───────────────────────────────┬──────────────────────────────────────┤
│ Período         │ Status Oficial de Governança  │ Destinação Metodológica no TCC       │
├─────────────────┼───────────────────────────────┼──────────────────────────────────────┤
│ 2009 a 2010     │ ❌ REPROVADA_DOCUMENTALMENTE   │ Descarte definitivo (ausência Q024)   │
│ 2011 a 2013     │ ⚠️ PENDENTE_HARMONIZACAO       │ Hipótese para teste no Notebook 05   │
│ 2014 a 2023     │ ✅ APROVADA_PARA_BASELINE     │ Treinamento e Validação (10 safras)  │
│ 2024            │ ⏳ PENDENTE_ALINHAMENTO        │ Validação Temporal Out-of-Time       │
│ 2025            │ ⚠️ PRELIMINAR_SEM_NOTAS       │ Teste sintático de inferência de X   │
└─────────────────┴───────────────────────────────┴──────────────────────────────────────┘
```
