# 📊 Roteiro de Slides: Notebook 05 — Consolidação Censitária e Engenharia de Big Data (2014–2023)

**Projeto de TCC:** MBA em Ciência de Dados / MLOps — Predição de Desempenho no ENEM  
**Autor:** Saulo Santos  
**Notebook de Referência:** [`notebooks/05_consolidacao_historica.ipynb`](file:///home/saulo/mba/tcc/enem/notebooks/05_consolidacao_historica.ipynb)  
**Foco da Defesa:** Processamento em *Streaming* de **56,57 milhões** de inscrições brutas (`25,45 GB`), Neutralização de *Value Drift* e Inflação Monetária, Compactação Extrema de Memória (*Downcasting* para `15 bytes/linha`) e Governança por Testes Formais.

---

## 🧭 Visão Panorâmica da Apresentação (Arco Narrativo para a Banca)

1. **Separação Estrita de Responsabilidades (SoR):** Isolar o ETL pesado de *Big Data* (`25,45 GB` de CSVs brutos) do laboratório de modelagem preditiva (Notebook 06).
2. **Engenharia de Memória (*Downcasting*):** Reduzir o custo por estudante de `64+ bytes` para **`15,00 bytes/linha`** (`-76,6%`), viabilizando **100% do censo da década (`37,59M` alunos)** em apenas **`537,78 MB` de RAM** sem recorrer a amostragem.
3. **Neutralização de *Value Drift*:** Ir além da renomeação semântica do SBERT (Notebook 04) corrigindo **4 armadilhas silenciosas de escala** (inflação nominal, inversão de computador em `2014`, escolaridade materna em `2014` e vazamento temporal em `TP_ANO_CONCLUIU`).
4. **Tolerância a Falhas e Qualidade Censitária:** Leitura em *chunks* de `500.000` linhas com *checkpoints* idempotentes, zero duplicatas de inscrição e **8 travas formais (`assert`)**.
5. **Entregável Canônico de MLOps:** Compressão de **99,4% em disco** (`25,45 GB` $\rightarrow$ **`153,17 MB`** em Apache Parquet `snappy`) assinado criptograficamente via `SHA-256`.

---

## 🎯 Slide 1 — Arquitetura Big Data ETL e Separação de Responsabilidades
> **Mapeamento no Notebook:** Seções 1 e 2 — Células 01 a 04 (Telemetria `psutil`, Leitura do Contrato SBERT e Auditoria de Cabeçalhos CSV)

### Mensagem Central
> *"Um pipeline maduro de MLOps não mistura ingestão bruta de 25 gigabytes com treinamento de modelos: criamos uma camada dedicada de consolidação guiada por contrato semântico."*

### Layout Visual Recomendado
* **Fluxo Arquitetural na Parte Superior:**
  `10 CSVs Brutos INEP (2014–2023 | 25,45 GB | 56,57M linhas)` + [`schema_mapping_historico.json`](file:///home/saulo/mba/tcc/enem/data/processed/schema_mapping_historico.json) $\longrightarrow$ **[Notebook 05: Streaming + Harmonização + Downcasting]** $\longrightarrow$ [`enem_2014_2023_consolidado.parquet`](file:///home/saulo/mba/tcc/enem/data/processed/enem_2014_2023_consolidado.parquet) (`153,17 MB`).
* **Destaque das Traduções Automáticas de 2014 Validadas nos Cabeçalhos Físicos:**
  * `Q003` (2014) $\longrightarrow$ `Q006` (Renda Familiar)
  * `Q004` (2014) $\longrightarrow$ `Q005` (Residentes no Domicílio)
  * `Q010` (2014) $\longrightarrow$ `Q024` (Posse de Computador)

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Princípio de Engenharia (SoR):** O Notebook 05 atua como *Feature Store* histórica offline, entregando dados limpos e imutáveis para o Notebook 06;
* **Consumo Estrito de Contrato:** Nenhuma coluna é mapeada manualmente — o pipeline lê dinamicamente o JSON homologado pelo SBERT no Notebook 04;
* **Auditoria Pré-Voo nos 10 CSVs (`2014–2023`):** Verificação física de `15/15` colunas analíticas + `NU_INSCRICAO` aprovada em **100% das edições** em menos de `1 segundo`.

### Trecho de Código para o Slide
```python
# Célula 04 — Validação Física Guiada pelo Contrato do Notebook 04
faltantes = [c for c in COLUNAS_CANONICAS_15 if c not in mapa_ano]
assert not faltantes, f"Ano {ano}: violação do contrato semântico!"
assert COLUNA_CONTROLE_CSV in colunas_csv_fisico  # NU_INSCRICAO presente nos 10 anos
```

### Roteiro de Fala do Apresentador
> *"Senhores membros da banca, após homologarmos a Década de Ouro (2014 a 2023) via NLP no Notebook 04, aplicamos o princípio de Separação de Responsabilidades criando o Notebook 05 exclusivamente para engenharia de Big Data. Antes de ler uma única linha de dados, o pipeline consome o contrato JSON do SBERT e audita o cabeçalho físico dos 10 arquivos CSV — que somam mais de 25 gigabytes e 56,5 milhões de inscrições — confirmando 100% de integridade estrutural."*

---

## 💾 Slide 2 — Engenharia de Memória (*Downcasting*): 37,6M de Alunos em 537,8 MB
> **Mapeamento no Notebook:** Seção 3 — Células 05 e 06 (Orçamento Matemático de Bytes por Registro)

### Mensagem Central
> *"O mito da falta de RAM em Big Data nasce da tipagem desperdiçada: ao projetar tipos numéricos exatos, reduzimos cada estudante de 64 para 15 bytes e carregamos o censo inteiro em meio gigabyte."*

### Layout Visual Recomendado
* **Tabela Oficial do Orçamento de Memória (*Downcasting* Sem Perda de Informação):**

| Coluna Consolidada | Papel | Domínio Exato | Pandas Padrão | Tipo Otimizado (NB05) | Economia |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`NU_ANO`** | Controle/Split | `2014..2023` | `int64` (`8 B`) | **`int16` (`2 B`)** | `-75,0%` |
| **`RENDA_PER_CAPITA`** | Feature #1 | `0,00..22,50 SM` | `float64` (`8 B`) | **`float32` (`4 B`)** | `-50,0%` |
| **`Q024`**, **`TP_ANO_CONCLUIU`**, **`Q002`** | Features Ordinais | `0..3` / `0..9` / `0..7` | `int64/obj` (`8+ B`) | **`int8` (`1 B` cada)** | `-87,5%` |
| **`TP_LINGUA`**, **`TP_SEXO`** | Features Binárias | `0` ou `1` | `int64/obj` (`8+ B`) | **`int8` (`1 B` cada)** | `-87,5%` |
| **`TARGET_M4`** | Alvo Oficial TRI | `0,0..1000,0` | `float64` (`8 B`) | **`float32` (`4 B`)** | `-50,0%` |
| **TOTAL POR ALUNO** | **8 Colunas** | — | **`64+ bytes`** | **`15,00 bytes`** | **`-76,6%`** |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Precisão Científica Preservada (`IEEE-754 float32`):** Garante ~7 dígitos significativos para notas da TRI que o INEP publica com apenas **1 casa decimal** (erro `< 0,0001 ponto`), além de ser o tipo nativo interno do **XGBoost**;
* **Descarte Inteligente Pós-Auditoria (`NU_INSCRICAO`):** Validada para garantir unicidade na leitura e removida antes da gravação final, economizando **`+300 MB` de peso morto** e blindando contra memorização de ID;
* **Impacto Real Medido:** `37.593.629 × 15 bytes` = **`537,78 MB` em RAM** (`< 9%` da memória da máquina local).

### Roteiro de Fala do Apresentador
> *"Muitos projetos recorrem a amostras pequenas alegando falta de memória RAM. Nós provamos matematicamente o contrário: graças à parcimônia das 6 features de elite definidas no Notebook 03 e ao downcasting rigoroso para `int8`, `int16` e `float32`, cada candidato ocupa exatos 15 bytes. Isso nos permitiu consolidar todos os 37,59 milhões de estudantes presentes da década em apenas 537,8 megabytes de RAM — trabalhando com o censo completo, sem perder um único aluno."*

---

## ⚖️ Slide 3 — Além do *Schema Drift*: Neutralizando o *Value Drift* (Parte 1)
> **Mapeamento no Notebook:** Seção 3 — Células 05 e 06 (Deflação Estrutural da Renda e Reversão de Escala do Computador em 2014)

### Mensagem Central
> *"Renomear colunas não basta quando o significado das respostas muda ou a moeda sofre 82% de inflação: neutralizamos o Value Drift diretamente na origem."*

### Layout Visual Recomendado
* **Card Esquerdo — Armadilha #1: Ilusão Monetária (`2014` vs. `2023`):**
  * Salário Mínimo (SM): `R\$ 724` (2014) $\longrightarrow$ `R\$ 1.320` (2023) (**`+82,3%` de inflação nominal!**).
  * **Solução Estrutural:** Converter as 17 letras (`A..Q`) diretamente em **Salários Mínimos por morador**:
    $$\text{RENDA\_PER\_CAPITA}_{\text{SM}} = \frac{\text{Ponto Médio em SM}(Q006)}{Q005}$$
* **Card Direito — Armadilha #2: Inversão Crítica do Computador em `2014` (`Q010` vs. `Q024`):**
  * **2015–2023 (`Q024`):** `'A' = Não possui (0)`, `'B' = 1`, `'C' = 2`, `'D'/'E' = 3+`
  * **2014 (`Q010`):** `'A' = 1`, `'B' = 2`, `'C' = 3+` e **`'D' = Não tenho (0)`**!

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Vantagem MLOps da Renda em SM:** Variável **100% deflacionada na origem** e estacionária para `2024`, `2025` ou `2026` na AWS, sem depender de tabelas externas de IPCA na API;
* **Erro Catastrófico Evitado em 2014:** Um `OrdinalEncoder` alfabético padrão (`A=0..D=3`) teria rotulado **5,95 milhões de candidatos de 2014** de cabeça para baixo — tratando quem não tinha computador (`D`) como se possuísse 3 computadores (`3`)!

### Roteiro de Fala do Apresentador
> *"Aqui está uma das maiores contribuições técnicas deste notebook. Mesmo após o SBERT descobrir que `Q010` em 2014 equivale a `Q024` em 2023, auditamos as categorias internas e descobrimos duas armadilhas fatais. Primeiro: a inflação de 82% no período distorceria qualquer valor em Reais nominais; resolvemos isso expressando a Renda Per Capita em múltiplos de Salários Mínimos por morador. Segundo: em 2014, a letra 'D' significava 'Não tenho computador', enquanto de 2015 em diante 'Não possui' virou a letra 'A'! Sem essa harmonização explícita, quase 6 milhões de alunos entrariam invertidos no modelo."*

---

## 🧩 Slide 4 — Neutralizando o *Value Drift* (Parte 2) e *Smoke Test* Pré-Voo
> **Mapeamento no Notebook:** Seções 3 e 4 — Células 05 a 08 (Harmonização de `Q002`, Estacionariedade de `TP_ANO_CONCLUIU` e Teste de Fumaça)

### Mensagem Central
> *"Alinhamos a escolaridade materna de 2014 e truncamos a cauda de conclusão do Ensino Médio em `[0..9]`, impedindo que o modelo descubra o ano da prova por atalho numérico."*

### Layout Visual Recomendado
* **Quadro Comparativo das Regras #3 e #4:**

| Variável | Anomalia Histórica Detectada | Regra de Harmonização Canônica (`int8`) | Risco Mitigado |
| :--- | :--- | :--- | :--- |
| **`Q002`** *(Escolaridade da Mãe)* | `2014` tinha **9 letras (`A..I`)**; `2015–2023` têm **8 letras (`A..H`)** | Unifica `E` e `F` de 2014 em `4` (*EM completo / Sup. incompleto*); realinha `G->5`, `H->6` (*Pós*) e `I->7` (*Não sei*) | Evita misturar mães **Pós-graduadas (`H` em 2014)** com **"Não sei" (`H` em 2015+)** |
| **`TP_ANO_CONCLUIU`** *(Tempo desde o EM)* | **3 regimes:** ano civil literal em `2014` (`2013..`), deslocado em `2015` e cauda até `17` em `2023` | Converte todos os anos para **anos decorridos estacionários `[0..9]`** (`0` = Concluinte/NI; `9` = `9+` anos) | Bloqueia **Vazamento Temporal** (código `17` só existia em `2023`) e cabe em `int8` |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Validação Rápida (*Fail-Fast Smoke Test* — Célula 08):** Antes de processar os `25,45 GB`, a função `processar_chunk_enem()` foi testada em lotes reais de `5.000` linhas dos 3 regimes distintos (`2014`, `2015` e `2023`);
* **Resultado do *Smoke Test* (`~2s`):** Zero valores nulos, domínios discretos respeitados e orçamento cravado em `15,00 bytes/linha`.

### Trecho de Código para o Slide
```python
# Célula 07 — Estacionariedade Anti-Temporal Leakage (0 a 9 anos)
anos_decorridos = np.where(ano == 2014, ano - valor_bruto, ...)
tp_ano_harmonizado = np.clip(anos_decorridos, 0, 9).astype(np.int8)
```

### Roteiro de Fala do Apresentador
> *"Encontramos mais duas armadilhas sutis: em 2014, a escolaridade materna tinha 9 letras e colocava Pós-graduação na letra 'H' — exatamente a letra que de 2015 em diante passou a significar 'Não sei'! Além disso, `TP_ANO_CONCLUIU` mudava de codificação três vezes e abria códigos até 17 em 2023, o que permitiria às árvores adivinharem o ano da prova. Harmonizamos tudo em uma escala estacionária de 0 a 9 anos e validamos os três regimes com um Smoke Test instantâneo antes de disparar a carga completa."*

---

## ⚙️ Slide 5 — Motor de *Streaming* em *Chunks* (`500k`) e *Checkpoints* Idempotentes
> **Mapeamento no Notebook:** Seção 5 — Células 09 e 10 (Processamento em Blocos, Unicidade de `NU_INSCRICAO` e Persistência Anual)

### Mensagem Central
> *"Varremos 56.568.785 inscrições brutas em blocos constantes de 500 mil linhas, auditando unicidade de chave primária e gravando checkpoints anuais tolerantes a falhas."*

### Layout Visual Recomendado
* **Diagrama do Funil Censitário da Década (`2014–2023`):**
  * **Entrada Bruta Varrida (10 CSVs):** `56.568.785` inscritos (`100,0%`)
  * $\downarrow$ *Filtro de Presença Integral nas 4 Provas Objetivas (`CN, CH, LC, MT == 1`):* `37.621.772` presentes (`66,51%`)
  * $\downarrow$ *Saneamento de Notas Válidas e Questionário Socioeconômico Completo:* `-28.143` registros (`0,05%`)
  * **Censo Final Consolidado:** **`37.593.629` candidatos elegíveis (`66,46%` de retenção)** | **`0` duplicatas!**

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Consumo Constante de Memória ($O(1)$ por bloco):** Leitura via `pd.read_csv(..., chunksize=500_000, usecols=...)` carregando apenas as 16 colunas necessárias em cada janela;
* **Auditoria Censitária de Unicidade:** Acúmulo em vetor `int64` e verificação com `np.unique` comprovando **`inscricoes_duplicadas = 0`** em todas as 10 edições;
* **Arquitetura Idempotente (`safras_consolidacao/`):** Cada safra concluída salva imediatamente `enem_{ano}_slim.parquet` + `enem_{ano}_auditoria.json` — permitindo retomada automática em `< 1 segundo` em caso de queda de energia ou reinício de kernel (`18,8 min` totais na 1ª carga fria).

### Roteiro de Fala do Apresentador
> *"Para processar 56,57 milhões de linhas em uma máquina de 7,7 GB de RAM sem jamais chegar perto de um erro de memória, construímos um motor de streaming em chunks de 500 mil registros com checkpoints anuais idempotentes. Auditamos cada número de inscrição confirmando zero duplicatas em toda a década e retivemos 37.593.629 candidatos com presença integral nas quatro provas objetivas."*

---

## 📊 Slide 6 — Retrato Censitário da Década de Ouro (`2014–2023`)
> **Mapeamento no Notebook:** Seções 5 e 7 — Células 10, 13 e 14 (Tabela Anual Consolidada e Painel Diagnóstico `2×2`)

### Mensagem Central
> *"Os números consolidados contam a história educacional da última década no Brasil: da expansão de 2014–2016 ao choque de abstenção pandêmica em 2020, mantendo notável estabilidade psicométrica."*

### Layout Visual Recomendado
* **Tabela Histórica Selecionada (Extraída do Contrato Auditado):**

| Edição | Inscritos Brutos | Retidos Finais (`4 Provas`) | Retenção | Sem PC (`Q024=0`) | Renda Média (`SM/mor.`) | Média `TARGET_M4` ($\pm \sigma$) | Parquet Slim |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`2014`** | `8.722.248` | `5.947.909` | `68,19%` | `33,05%` | `0,68 SM` | `502,97 ± 67,13` | `24,34 MB` |
| **`2016`** | `8.627.179` | `5.818.261` | `67,44%` | `35,87%` | `0,68 SM` | `506,25 ± 65,76` | `23,67 MB` |
| **`2018`** | `3.063.481` | `2.272.217` | `74,17%` | `41,06%` | `0,71 SM` | **`533,49 ± 68,66`** | `9,22 MB` |
| **`2020`** | `5.783.109` | `2.561.304` | **`44,29%`** | `44,22%` | `0,73 SM` | `512,87 ± 79,40` | `10,55 MB` |
| **`2022`** | `3.476.105` | `2.344.823` | `67,46%` | `42,16%` | `0,85 SM` | `522,12 ± 72,78` | `9,55 MB` |
| **`2023`** | `3.933.955` | `2.678.264` | `68,08%` | `47,93%` | `0,82 SM` | `519,11 ± 81,91` | `11,02 MB` |
| **TOTAL** | **`56.568.785`** | **`37.593.629`** | **`66,46%`** | — | — | **`511,05 ± 70,97`** | **`153,17 MB`** |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Fenômeno Pandêmico (`2020`):** Retenção despenca de `~72%` para **`44,29%`** (abstenção histórica da COVID-19) e dispersão de notas salta para `σ = 79,40 pts`;
* **Transição Digital (`Q024=0`):** Crescimento da proporção de lares sem desktop/notebook (`33%` $\rightarrow$ `47,9%`), refletindo a migração popular apenas para smartphones — tornando o computador residencial um marcador ainda mais forte de elite educacional;
* **Estabilidade do Alvo (`TARGET_M4`):** Média global ancorada em **`511,05 pontos`**, destacando já na exploração o deslocamento atípico de calibração TRI em `2018` (`533,49 pts`).

### Roteiro de Fala do Apresentador
> *"Esta tabela sintetiza 10 anos de educação brasileira processados pelo nosso pipeline. Vemos com nitidez cirúrgica o impacto da pandemia em 2020, quando a taxa de presença integral caiu de 72% para 44%, aumentando a desigualdade das notas. Notem também um achado sociológico fascinante: o percentual de inscritos sem computador em casa subiu de 33% em 2014 para quase 48% em 2023 devido à substituição do PC pelo celular nas classes populares, fazendo da posse de computador um diferencial competitivo ainda mais agudo."*

---

## ✅ Slide 7 — Governança por Testes: As 8 Travas Formais (`assert`) de Qualidade
> **Mapeamento no Notebook:** Seção 6 — Células 11 e 12 (Concatenação em Memória e Bateria de Validação de *Data Quality*)

### Mensagem Central
> *"Nenhum dado avança para o treinamento por confiança visual: submetemos os 37,59 milhões de registros concatenados a 8 asserções matemáticas bloqueantes."*

### Layout Visual Recomendado
* **Painel de Checkboxes Verdes (`8/8 TESTES FORMAIS APROVADOS`):**
  1. ✅ **Cobertura Histórica Completa:** Presença exata das 10 safras `{2014..2023}`;
  2. ✅ **Contrato Estrito de Schema:** Exatas `8` colunas na ordem canônica homologada;
  3. ✅ **Orçamento Exato de Memória:** Cravado em **`15,00 bytes/linha`** (`537,78 MB` totais);
  4. ✅ **Completude Absoluta:** **`0` valores `NaN`, `null` ou infinitos** nas `300.749.032` células da matriz (`37,59M × 8`);
  5. ✅ **Fronteira Psicométrica da TRI:** `100%` de `TARGET_M4` estritamente dentro de `[0.0, 1000.0]`;
  6. ✅ **Domínio Discreto de `Q024` e `Q002`:** Subconjuntos exatos de `{0..3}` e `{0..7}`;
  7. ✅ **Domínio Binário e Temporal:** `TP_LINGUA ∈ {0,1}`, `TP_SEXO ∈ {0,1}` e `TP_ANO_CONCLUIU ∈ {0..9}`;
  8. ✅ **Sanidade Econômica:** `RENDA_PER_CAPITA` finita e contida em `[0.0, 25.0] SM/morador`.

### Trecho de Código para o Slide
```python
# Célula 12 — Bateria Automatizada de Data Quality (Zero Tolerância)
assert df_decada.isna().sum().sum() == 0, "Falha: Nulos detectados!"
assert bytes_por_linha == 15.0, f"Estouro de tipagem: {bytes_por_linha} B"
assert df_decada["TARGET_M4"].between(0.0, 1000.0).all()
# Resultado: 8/8 TESTES FORMAIS APROVADOS EM 37.593.629 LINHAS
```

### Roteiro de Fala do Apresentador
> *"Após concatenar os 10 anos na memória, aplicamos engenharia de software orientada a testes sobre dados: oito cláusulas `assert` varrem as mais de 300 milhões de células da matriz consolidada. Confirmamos zero células nulas, zero notas fora da escala da TRI, domínios categóricos 100% fechados e exatamente 15,00 bytes por linha."*

---

## 📦 Slide 8 — Artefato Apache Parquet (`99,4%` Menor) e Contrato Criptográfico
> **Mapeamento no Notebook:** Seção 8 — Células 15 e 16 (Serialização Colunar `snappy`, Hash `SHA-256` e Contrato JSON)

### Mensagem Central
> *"Comprimimos 25,45 GB de CSVs governamentais em um único artefato colunar de 153,17 MB assinado com SHA-256, acelerando a carga do treinamento de 19 minutos para 6 segundos."*

### Layout Visual Recomendado
* **Comparativo Visual de Transformação Física (Antes $\times$ Depois):**
  * **Antes (10 CSVs Brutos INEP):** `25.450 MB` (`25,45 GB`) | Leitura fria: `~19 minutos` | Nomes e escalas divergentes
  * **Depois ([`enem_2014_2023_consolidado.parquet`](file:///home/saulo/mba/tcc/enem/data/processed/enem_2014_2023_consolidado.parquet)):** **`153,17 MB`** (**`-99,4%` de disco!**) | Leitura no NB06: **`~6 segundos`** | `100%` harmonizado
* **Rodapé de Governança ([`contrato_consolidacao_2014_2023.json`](file:///home/saulo/mba/tcc/enem/data/processed/contrato_consolidacao_2014_2023.json)):**
  * `SHA-256`: `a7fbce7cd5f6e89244351c8712be588f53dbbdf4ff46e9d3b397157647438d3a`

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Eficiência Colunar (`PyArrow + Snappy`):** Dicionários internos de compressão *Run-Length Encoding (RLE)* exploram a baixa cardinalidade dos colunas `int8`, derrubando o arquivo final para `153,17 MB`;
* **Contrato de Linhagem Completa:** O JSON exportado documenta as fórmulas exatas de conversão (reutilizadas no contrato da FastAPI na Etapa 2), métricas anuais de retenção e o hash `SHA-256` verificado automaticamente na abertura do Notebook 06.

### Roteiro de Fala do Apresentador
> *"Concluímos o Notebook 05 entregando uma compressão física de 99,4%: vinte e cinco gigabytes e meio de arquivos texto brutos tornam-se um único Parquet colunar de 153 megabytes que carrega em 6 segundos no Notebook 06, acompanhado de um contrato JSON com assinatura SHA-256. Esta base enxuta, auditada e deflacionada é o alicerce que viabilizou o treinamento censitário do nosso modelo campeão."*

---

## ❓ Perguntas Prováveis da Banca sobre o Notebook 05 (e Respostas Blindadas)

**1. "Por que vocês não utilizaram um cluster distribuído como Apache Spark ou Dask para processar os 56,5 milhões de registros?"**
> *Resposta:* "Porque a boa engenharia de dados escolhe a ferramenta proporcional à geometria real do problema, evitando sobrecarga operacional desnecessária (*overengineering*). Embora os CSVs brutos somem `25,45 GB` por conterem 76 colunas textuais, demonstramos matematicamente que nosso vetor canônico de 8 colunas com *downcasting* exige apenas `15 bytes/linha` — totalizando `537,78 MB` em RAM para os `37,59 milhões` de alunos! Ao combinar leitura seletiva (`usecols`) em *streaming* de `500k` linhas com *checkpoints* Parquet colunares, processamos toda a década localmente com consumo constante de memória, zero custo de serialização JVM/rede do Spark e reprodutibilidade determinística imediata."

**2. "Por que deflacionar a renda pelo Salário Mínimo da época em vez de corrigir os valores em Reais pelo IPCA do IBGE?"**
> *Resposta:* "Por dois motivos estruturais do próprio exame do INEP. Primeiro, os questionários originais do ENEM (de 2014 a 2023) são desenhados nativamente em múltiplos exatos do Salário Mínimo vigente (17 faixas fixas de `0` até `acima de 20 SM`). Logo, converter para Reais e depois aplicar IPCA introduziria erro duplo de discretização nas bordas das faixas. Segundo, na arquitetura de MLOps em produção (Etapas 2 e 3), trabalhar diretamente em Salários Mínimos per capita torna a feature auto-ajustável para qualquer ano futuro (2024, 2025, 2026) sem acoplar o microsserviço FastAPI a índices externos de inflação."

**3. "Em 2020 houve a exclusão de `27.377` candidatos presentes por questionário incompleto, enquanto nos outros anos esse número foi zero ou quase zero. Isso gera algum viés?"**
> *Resposta:* "Excelente observação! Auditamos especificamente esse ponto na tabela de linhagem anual: na edição pandêmica de 2020 (que incluiu a aplicação piloto do ENEM Digital e inscrições excepcionais), `27.377` presentes tiveram campos socioeconômicos não preenchidos na base do INEP. Esse volume representa apenas `1,06%` dos presentes de 2020 e míseros `0,07%` do universo consolidado de `37,59 milhões` de estudantes. Expurgá-los no filtro do Notebook 05 manteve o dataset 100% livre de imputações artificiais em variáveis críticas como renda e escolaridade materna, sem alterar a média ou a variância da edição."

**4. "Por que a coluna `NU_INSCRICAO` foi validada nos CSVs, mas não foi mantida no arquivo `enem_2014_2023_consolidado.parquet`?"**
> *Resposta:* "Pela aplicação conjunta de governança e eficiência de memória. Na ingestão (Seção 5), lemos `NU_INSCRICAO` para provar formalmente via `np.unique` que não há nenhuma inscrição duplicada em nenhum dos 10 anos (`0` duplicatas em `37,59M` de alunos). Uma vez cumprido seu papel de auditoria transacional, mantê-la no Parquet de modelagem adicionaria `300,7 MB` de inteiros de 64 bits em RAM (`+56%` de volume extra) para uma chave administrativa sem poder preditivo legítimo."

---

## 📋 Resumo Executivo — Quadro de Fechamento do Notebook 05

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ SÍNTESE DE HOMOLOGAÇÃO DO NOTEBOOK 05 (CONSOLIDAÇÃO CENSITÁRIA 2014–2023)                    │
├──────────────────────────────┬───────────────────────────────────────────────────────────────┤
│ Dimensão de Engenharia       │ Resultado Oficial Homologado                                  │
├──────────────────────────────┼───────────────────────────────────────────────────────────────┤
│ Insumo Bruto Varrido         │ 10 CSVs oficiais (25,45 GB | 56.568.785 inscrições brutas)    │
│ Universo Elegível Retido     │ 37.593.629 candidatos presentes nas 4 provas (66,46% | 0 dup) │
│ Otimização de Memória RAM    │ 64+ B -> 15,00 bytes/linha (-76,6% | Total: 537,78 MB em RAM) │
│ Harmonização Anti-Drift      │ Renda em SM/morador + Fix Q010/Q002 (2014) + Ano EM [0..9]    │
│ Auditoria de Data Quality    │ 8/8 asserções formais aprovadas (0 NaNs em 300,7M de células) │
│ Artefato Colunar Exportado   │ enem_2014_2023_consolidado.parquet (153,17 MB | -99,4% disco) │
│ Assinatura Criptográfica     │ SHA-256: a7fbce7cd5f6e89244351c8712be588f53dbbdf4ff46e9d3b... │
└──────────────────────────────┴───────────────────────────────────────────────────────────────┘
```

