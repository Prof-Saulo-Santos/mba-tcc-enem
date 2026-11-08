# 📘 Guia Passo a Passo e Documentação Complementar — Notebook 05

**Arquivo do Notebook:** [`notebooks/05_consolidacao_historica.ipynb`](notebooks/05_consolidacao_historica.ipynb)  
**Projeto de TCC:** MBA em Ciência de Dados & MLOps — Predição de Desempenho no ENEM  
**Autor:** Saulo Santos  

---

## 1. Visão Geral: Onde o Notebook 05 se Encaixa no Fluxo do Projeto?

Na arquitetura da **Etapa 1** do TCC, o projeto foi dividido com **Separação Estrita de Responsabilidades (SoR)** para isolar o processamento pesado de *Big Data* da etapa de experimentação de *Machine Learning*:

```text
[01_investigacao_estrutural.ipynb] ──> Inspeção primária da base de 2023
                │
                ▼
[02_eda.ipynb]                     ──> Limpeza metodológica e análise estatística (2023)
                │
                ▼
[03_engenharia_features.ipynb]     ──> Definição do TARGET_M4 e das 6 Features de Elite (2023)
                │
                ▼
[04_varredura_semantica.ipynb]     ──> NLP/SBERT nos dicionários (2009–2025) e homologação de 2014–2023
                │
                ▼
[05_consolidacao_historica.ipynb]  ──> ⭐ ESTE NOTEBOOK: Concatenação censitária e enxuta de 2014 a 2023
                │
                ▼
[06_treinamento_modelo.ipynb]      ──> Treinamento (Random Forest vs. XGBoost) + MLflow + SHAP -> enem.pkl
```

### Qual é a missão exata do Notebook 05?
Ler os **10 arquivos CSV brutos** da Década de Ouro (`2014` a `2023`, somando **~27,3 GB** em disco e mais de **60 milhões de inscritos brutos**), aplicar o contrato semântico do Notebook 04 (`data/processed/schema_mapping_historico.json`), filtrar os candidatos com presença integral nas 4 provas objetivas, harmonizar diferenças históricas de escala (*Value Drift*), compactar os tipos numéricos e entregar um **único arquivo Apache Parquet pronto para o treinamento** no Notebook 06.

---

## 2. Por Que Não Falta Memória RAM? (A Prova Matemática do *Downcasting*)

Uma preocupação comum ao consolidar 10 edições do ENEM é o estouro de memória (*Out-Of-Memory — OOM*). Isso só ocorreria se carregássemos as ~76 colunas brutas dos CSVs ou mantivéssemos tipos padrão de 64 bits (`int64` / `float64` / `object`).

Como selecionamos no Notebook 03 apenas **6 features preditoras + 1 alvo (`TARGET_M4`) + 1 coluna de controle temporal (`NU_ANO`)**, aplicamos **redução explícita de precisão (*Downcasting*)** sem perda de informação:

| Coluna | Natureza da Variável | Faixa de Valores | Tipo Padrão (Pandas) | Tipo Otimizado (NB05) | Economia |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `NU_ANO` | Ano da prova (controle, não entra em `X`) | `2014` a `2023` | `int64` (8 B) | **`int16` (2 B)** | -75,0% |
| `RENDA_PER_CAPITA` | Contínua (Salários Mínimos / morador) | `0,00` a `22,50` | `float64` (8 B) | **`float32` (4 B)** | -50,0% |
| `Q024` | Ordinal (Posse de computador) | `0` a `3` | `object/int64` (8+ B) | **`int8` (1 B)** | -87,5% |
| `TP_ANO_CONCLUIU` | Ordinal (Anos desde conclusão do EM) | `0` a `9` | `int64` (8 B) | **`int8` (1 B)** | -87,5% |
| `TP_LINGUA` | Binária (Inglês=0, Espanhol=1) | `0` ou `1` | `int64` (8 B) | **`int8` (1 B)** | -87,5% |
| `TP_SEXO` | Binária (Feminino=0, Masculino=1) | `0` ou `1` | `object/int64` (8+ B) | **`int8` (1 B)** | -87,5% |
| `Q002` | Categórica/Ordinal (Escolaridade da mãe) | `0` a `7` | `object/int64` (8+ B) | **`int8` (1 B)** | -87,5% |
| `TARGET_M4` | Contínua (Média das 4 notas da TRI) | `0,0` a `1000,0` | `float64` (8 B) | **`float32` (4 B)** | -50,0% |
| **TOTAL POR LINHA** | **8 Colunas Finais** | — | **64+ bytes/linha** | **15 bytes/linha** | **-76,6%** |

* **Nota sobre `float32`:** O padrão IEEE-754 `float32` garante ~7 dígitos decimais significativos, enquanto o INEP publica notas da TRI com apenas **1 casa decimal** (ex.: `536.9`). Portanto, o erro de arredondamento é virtualmente nulo (< `0,0001` ponto) e internamente o próprio **XGBoost** converte todas as entradas para `float32`.
* **Impacto Prático:** Para ~37 a 38 milhões de candidatos presentes na década, `38.000.000 × 15 bytes ≈ 544 MB` em memória RAM — menos de **9% da memória livre** do ambiente WSL (`~6,8 GB` livres), permitindo trabalhar com **100% do censo de presentes sem qualquer amostragem**.

---

## 3. As 4 Regras Críticas de Harmonização Longitudinal (*Anti-Value Drift*)

Este é um dos pontos mais importantes para a **defesa perante a banca do TCC**. Renomear colunas via NLP/SBERT resolve mudanças de nome (*Schema Drift*), mas uma auditoria direta nos dicionários oficiais e microdados de 2014 a 2023 revelou **quatro armadilhas de escala (*Value Drift*)** que corromperiam o modelo caso não fossem tratadas no Notebook 05:

### 3.1 Deflação Estrutural da Renda em Salários Mínimos (`RENDA_PER_CAPITA`)
* **O Problema da Ilusão Monetária:** Em 2014, o Salário Mínimo (SM) nacional era `R$ 724,00`. Em 2023, era `R$ 1.320,00` (alta nominal de **+82,3%**). Se convertêssemos as faixas em Reais nominais de cada ano, uma família de baixa renda de 2023 pareceria ter a mesma renda nominal de uma família de classe média de 2014.
* **A Solução Exata:** Em todas as 10 edições (`Q003` em 2014 e `Q006` de 2015 a 2023), as 17 letras (`A` até `Q`) do INEP representam **exatamente os mesmos múltiplos do Salário Mínimo vigente** (`A = 0 SM`, `B = até 1 SM`, `C = 1 a 1,5 SM`, ..., `P = 15 a 20 SM`, `Q = acima de 20 SM`).
* Ao mapearmos cada letra diretamente para o **ponto médio em Salários Mínimos** (`0.00, 0.50, 1.25, 1.75, ..., 17.50, 22.50` SM) e dividirmos por `Q005` (`1` a `20` moradores), obtemos **`RENDA_PER_CAPITA` em Salários Mínimos por morador** — uma variável **100% deflacionada na origem** e pronta para inferência em qualquer ano futuro (2024, 2025, 2026) sem depender de tabelas externas de IPCA.

### 3.2 Correção da Inversão da Posse de Computador em 2014 (`Q024`)
* **A Descoberta nos Dicionários:**
  * De **2015 a 2023** (`Q024`): `'A' = Não possui (0)`, `'B' = 1`, `'C' = 2`, `'D' = 3`, `'E' = 4 ou mais`.
  * Em **2014** (`Q010` — Microcomputador): `'A' = 1`, `'B' = 2`, `'C' = 3 ou mais` e **`'D' = Não tenho` (`0`)**!
* **Risco Evitado:** Um `OrdinalEncoder` alfabético ingênuo (`A=0, B=1, C=2, D=3`) teria classificado todos os candidatos sem computador de 2014 (`D`) como se tivessem 3 computadores (`3`), e quem tinha 1 computador (`A`) como zero (`0`)!
* **Régua Harmonizada (`int8`):** `0 = Nenhum computador`, `1 = 1 computador`, `2 = 2 computadores`, `3 = 3 ou mais computadores` (unificando `D` e `E` de 2015–2023 com o teto `C = 3 ou mais` de 2014).

### 3.3 Alinhamento das Categorias de Escolaridade Materna em 2014 (`Q002`)
* **A Descoberta nos Dicionários:**
  * Em **2014**, `Q002` ia de `'A'` até `'I'` (9 opções): separava *Ensino Médio completo* (`E`) de *Superior incompleto* (`F`), colocava *Pós-graduação* em `'H'` e *Não sei* em `'I'`.
  * De **2015 a 2023**, `Q002` vai de `'A'` até `'H'` (8 opções): agrupa *"Completou o Ensino Médio, mas não completou a Faculdade"* na letra `'E'` (`4`), coloca *Superior completo* em `'F'` (`5`), *Pós-graduação* em `'G'` (`6`) e *Não sei* em `'H'` (`7`).
* **Risco Evitado:** Sem harmonização, mães com **Pós-graduação em 2014 (`H`)** seriam misturadas com a categoria **"Não sei" (`H`)** de 2015–2023!
* **Régua Harmonizada (`int8`, `0` a `7`):** Em 2014, `'E'` e `'F'` convergem para `4`, `'G' -> 5`, `'H' -> 6` e `'I' -> 7`, alinhando perfeitamente as proporções populacionais com 2015–2023.

### 3.4 Estacionariedade de `TP_ANO_CONCLUIU` (`0` a `9`)
* **Três Regimes Históricos no INEP:**
  1. **2014:** Trazia o ano civil literal (`2013`, `2012`, ..., `2004`) ou campo em branco para não informado/concluinte (números como `2013` sequer cabem em `int8`, que vai até `127`);
  2. **2015:** Código `'0' = Não informado`, `'1' = 2015` (ano corrente), `'2' = 2014` (1 ano atrás) até `'10' = Anterior a 2007` (9+ anos atrás);
  3. **2016 a 2023:** Código `'0' = Não informado`, `'1' = T - 1` (1 ano atrás), ..., expandindo a cauda direita *"Antes de 2007"* de `10` (em 2016) até `17` (em 2023).
* **Solução Anti-Vazamento Temporal:** Convertemos todas as edições para **anos decorridos desde a conclusão** no intervalo estacionário **`0` a `9`** (`0` = Não informado / Concluinte no ano; `1` a `8` = anos exatos; `9` = 9 ou mais anos). Isso impede que valores como `15`, `16` ou `17` funcionem como um atalho oculto para o modelo descobrir que o candidato fez a prova em 2021–2023.

---

## 4. Roteiro Detalhado Célula por Célula

| Seção / Células | O que Executa | Tempo Estimado | O que Conferir na Saída |
| :--- | :--- | :---: | :--- |
| **Seção 1** (Células 01–02) | Configura imports, `SEED=42`, caminhos resilientes e telemetria `psutil` de RAM. | `< 1 s` | Mensagem `AMBIENTE DE CONSOLIDAÇÃO HISTÓRICA INICIALIZADO` e GB livres de RAM no host. |
| **Seção 2** (Células 03–04) | Lê `schema_mapping_historico.json`, filtra `2014..2023` e audita cabeçalhos dos 10 CSVs (`15` colunas do contrato + `NU_INSCRICAO`). | `~1 s` | Tabela com as 10 edições, todas com `15/15 + ID OK` e destaque para as 3 traduções de 2014 (`Q003->Q006`, `Q004->Q005`, `Q010->Q024`). |
| **Seção 3** (Células 05–06) | Declara os dicionários de harmonização e exibe a tabela de orçamento de bytes (`Downcasting`). | `< 1 s` | Confirmação de **`15 BYTES/LINHA`** (redução de `76,6%` em relação aos `64 bytes` padrão). |
| **Seção 4** (Células 07–08) | Cria `harmonizar_ano_concluiu()` e `processar_chunk_enem()`, rodando o *Smoke Test* em 5.000 linhas de `2014`, `2015` e `2023`. | `~2 s` | Mensagem `✅ Smoke Test aprovado com zero erros de domínio, zero NaNs e tipagem 100% enxuta!`. |
| **Seção 5** (Células 09–10) | Loop principal em *chunks* de `500.000` linhas pelos 10 CSVs, checando unicidade de `NU_INSCRICAO` e salvando *checkpoints* anuais. | `~3 a 6 min` (1ª vez) / `< 1 s` (reuso) | Uma linha `✅ [ANO]` para cada edição (2014 a 2023), `inscricoes_duplicadas = 0` e tabela censitária consolidada ao final. |
| **Seção 6** (Células 11–12) | Concatena os 10 Parquets enxutos em `df_decada` e executa **8 testes formais (`assert`)** de *Data Quality* e *Anti-Leakage*. | `~3 a 5 s` | `8/8 TESTES FORMAIS APROVADOS`, `15.00 bytes/linha` e consumo do DataFrame em torno de `550–600 MB`. |
| **Seção 7** (Células 13–14) | Plota painel 2×2: (1) Volume anual, (2) Estabilidade do `TARGET_M4`, (3) Renda Per Capita em SM e (4) Computador × Língua. | `~3 a 5 s` | Queda visível de presentes em 2020–2021 (pandemia), estabilidade de `TARGET_M4` (~505–530) e escada monotônica crescente por renda e PC. |
| **Seção 8** (Células 15–16) | Salva `enem_2014_2023_consolidado.parquet`, calcula hash `SHA-256` em *streaming* e exporta `contrato_consolidacao_2014_2023.json`. | `~5 a 10 s` | Exibição do caminho final, tamanho em MB, hash `SHA-256` de 64 caracteres e confirmação de conclusão do Notebook 05. |

---

## 5. Tolerância a Falhas: Como Funcionam os *Checkpoints* Anuais?

Durante a **Seção 5**, cada ano concluído é imediatamente persistido na subpasta:
```text
data/processed/safras_consolidacao/
├── enem_2014_slim.parquet
├── enem_2014_auditoria.json
├── ...
├── enem_2023_slim.parquet
└── enem_2023_auditoria.json
```

* **Por que isso foi projetado assim?** Se você interromper o kernel no meio da execução (por exemplo, no ano de 2019), **nenhum trabalho anterior é perdido**. Ao rodar novamente a célula da Seção 5 com `FORCAR_REPROCESSAMENTO = False` (padrão), os anos `2014` a `2018` são validados instantaneamente (`⚡ Checkpoint reutilizado`) e a leitura retoma direto de `2019`.
* **Como forçar uma reconstrução completa do zero?** Basta alterar `FORCAR_REPROCESSAMENTO = True` na primeira linha da Célula 10 (Seção 5).

---

## 6. Por Que `NU_INSCRICAO` Fica Fora do Contrato Semântico e do Parquet Final?

1. **Separação Estrita de Contratos (Padrão `etl_parquet.py`):** O `schema_mapping_historico.json` gerado no Notebook 04 homologa estritamente as **15 variáveis analíticas e de elegibilidade** (`CONTRATO_CANONICO`). Já `NU_INSCRICAO` é declarada separadamente como `COLUNA_CONTROLE_CSV` e validada direto no cabeçalho físico de cada CSV (2014–2023) apenas para a checagem censitária de unicidade (`np.unique`) por ano.
2. **Economia de 300+ MB de Peso Morto:** Como `NU_INSCRICAO` é um identificador administrativo sem valor preditivo (cuja inclusão em `X` seria um erro grave de *overfitting*/memorização), mantê-lo em 38 milhões de linhas adicionaria `8 bytes × 38M ≈ 304 MB` extras em RAM durante o treinamento paralelo de árvores no Notebook 06. Auditá-lo na ingestão e descartá-lo na persistência une **rigor de auditoria** com **máxima eficiência computacional**.

---

## 7. Checklist de Validação Antes de Avançarmos para o Notebook 06

Após executar todas as células de [`notebooks/05_consolidacao_historica.ipynb`](notebooks/05_consolidacao_historica.ipynb) no kernel **`Python (ENEM .venv)`**, verifique:

- [ ] A Seção 2 exibiu `15/15 + ID OK` para todos os 10 anos (`2014` a `2023`)?
- [ ] O *Smoke Test* da Seção 4 passou com a mensagem `✅ Smoke Test aprovado`?
- [ ] A Seção 5 processou os 10 anos com `inscricoes_duplicadas == 0` em todas as linhas da tabela `df_auditoria_anual`?
- [ ] A Seção 6 exibiu `8/8 TESTES FORMAIS APROVADOS` e confirmou consumo do DataFrame ao redor de `~550–600 MB` (`15.00 bytes/linha`)?
- [ ] Os dois artefatos finais foram criados em `data/processed/`:
  - `data/processed/enem_2014_2023_consolidado.parquet`
  - `data/processed/contrato_consolidacao_2014_2023.json`

Assim que esses itens estiverem validados por você, estaremos 100% prontos para iniciar o **`notebooks/06_treinamento_modelo.ipynb`** (*Random Forest* vs. *XGBoost* + rastreamento no **MLflow** + explicabilidade **SHAP** + exportação do **`enem.pkl`**).

