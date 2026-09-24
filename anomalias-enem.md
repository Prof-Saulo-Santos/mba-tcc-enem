# Anomalias e Inconsistências — Microdados Históricos do ENEM

> Documento de registro das anomalias, inconsistências e observações relevantes
> identificadas durante a etapa de aquisição e validação dos microdados do ENEM.
>
> **Última atualização:** 2026-09-08
> **Escopo:** Anos 2015, 2017, 2019, 2020, 2021, 2022, 2023, 2024, 2025

---

## 1. Problemas de Aquisição dos Dados

### 1.1 Falha de Download — Anos 2016 e 2018

| Campo | Detalhe |
|---|---|
| **Anos afetados** | 2016, 2018 |
| **Tipo** | Falha de conectividade SSL/TLS |
| **Mensagem de erro** | `Unable to establish SSL connection` / `OpenSSL SSL_connect: Connection reset by peer` |
| **Causa provável** | Incompatibilidade de cipher suite entre o servidor do INEP (`download.inep.gov.br`) e a versão local do OpenSSL. O servidor utiliza certificado emitido pela RNP (Rede Nacional de Ensino e Pesquisa — `CN=RNP ICPEdu GR46 OV TLS CA 2025`), cuja CA raiz não consta na cadeia de confiança local. |
| **Status** | ❌ Não resolvido automaticamente. O arquivo de 2018 está sendo baixado manualmente. O arquivo de 2016 permanece ausente. |
| **Impacto no projeto** | Lacuna na série temporal de 2016 e possivelmente 2018. A série disponível é: 2015, 2017, 2019–2025. |
| **Ação recomendada** | Tentar download via VPN governamental ou navegador web. URL: `https://download.inep.gov.br/microdados/microdados_enem_2016.zip` |

---

### 1.2 Estrutura de Diretórios Inconsistente após Extração

| Campo | Detalhe |
|---|---|
| **Anos afetados** | 2023, 2024, 2025 |
| **Tipo** | Estrutura interna do ZIP diferente |
| **Descrição** | Nos anos 2015–2022, os arquivos são extraídos diretamente para `enem_XXXX/{DADOS, DICIONÁRIO, INPUTS, ...}`. Nos anos 2023–2025, o ZIP contém um subdiretório adicional interno: `enem_XXXX/microdados_enem_XXXX/{DADOS, ...}` |
| **Exemplo** | `enem_2022/DADOS/ITENS_PROVA_2022.csv` vs. `enem_2023/microdados_enem_2023/DADOS/ITENS_PROVA_2023.csv` |
| **Impacto no projeto** | Scripts de leitura que assumem caminho fixo precisam tratar os dois padrões. |
| **Ação recomendada** | Normalizar os caminhos via script de pré-processamento ou usar `glob`/`find` para localizar os arquivos independente do nível de aninhamento. |

---

## 2. Inconsistências de Schema — `ITENS_PROVA_XXXX.csv`

### 2.1 Coluna Extra no ENEM 2020: `TP_VERSAO_DIGITAL`

| Campo | Detalhe |
|---|---|
| **Arquivo afetado** | `ITENS_PROVA_2020.csv` |
| **Tipo** | Coluna adicional ausente nos demais anos |
| **Coluna** | `TP_VERSAO_DIGITAL` |
| **Anos sem a coluna** | 2015, 2017, 2019, 2021, 2022, 2023, 2024, 2025 |
| **Causa provável** | Em 2020, o INEP realizou uma aplicação digital do ENEM (ENEM Digital). A coluna indica a versão digital da prova. Nos anos seguintes, o campo foi removido. |
| **Impacto no projeto** | Ao concatenar as bases de múltiplos anos, a coluna aparecerá como `NaN` para todos os demais anos, podendo introduzir ruído se incluída como feature. |
| **Ação recomendada** | Descartar a coluna `TP_VERSAO_DIGITAL` ao consolidar a base histórica, ou mantê-la com flag explícita de ausência para os demais anos. |

---

### 2.2 Crescimento do Volume de Itens ao Longo dos Anos

| Ano | N° de linhas (itens) |
|---|---:|
| 2015 | 2.775 |
| 2017 | 1.850 |
| 2019 | 1.945 |
| 2020 | 4.415 |
| 2021 | 5.365 |
| 2022 | 5.365 |
| 2023 | 5.550 |
| 2024 | 5.550 |
| 2025 | 6.105 |

| Campo | Detalhe |
|---|---|
| **Tipo** | Variação volumétrica (não é erro, mas é relevante) |
| **Observação** | O número de itens cresceu significativamente a partir de 2020, mais que dobrando em relação a 2015–2019. Isso reflete o crescimento do banco de itens do INEP. |
| **Impacto no projeto** | Modelos treinados com dados pré-2020 podem ter comportamento diferente por conta da menor diversidade de itens. Considerar isso na análise de concept drift. |

---

## 3. Observações sobre Schema — `ITENS_PROVA_XXXX.csv`

### 3.1 Colunas Estáveis (presentes em todos os anos disponíveis)

As 14 colunas abaixo são **idênticas em todos os 9 anos** analisados:

| # | Coluna | Descrição |
|---|---|---|
| 1 | `CO_POSICAO` | Posição do item na prova |
| 2 | `SG_AREA` | Sigla da área do conhecimento (LC, MT, CN, CH) |
| 3 | `CO_ITEM` | Código identificador do item |
| 4 | `TX_GABARITO` | Letra do gabarito correto |
| 5 | `CO_HABILIDADE` | Código da habilidade avaliada (Matriz de Referência) |
| 6 | `IN_ITEM_ABAN` | Indicador de item anulado (0/1) |
| 7 | `TX_MOTIVO_ABAN` | Texto do motivo de anulação |
| 8 | `NU_PARAM_A` | Parâmetro A do modelo TRI (discriminação) |
| 9 | `NU_PARAM_B` | Parâmetro B do modelo TRI (dificuldade) |
| 10 | `NU_PARAM_C` | Parâmetro C do modelo TRI (acerto casual) |
| 11 | `TX_COR` | Cor/versão do caderno de prova |
| 12 | `CO_PROVA` | Código da prova |
| 13 | `TP_LINGUA` | Tipo de língua estrangeira (inglês/espanhol) |
| 14 | `IN_ITEM_ADAPTADO` | Indicador de item adaptado para acessibilidade |

---

## 4. Inconsistências de Schema — Base de Participantes

### 4.1 Desmembramento da Base Principal em 2024 e 2025

| Campo | Detalhe |
|---|---|
| **Arquivos afetados** | `MICRODADOS_ENEM_2024.csv`, `MICRODADOS_ENEM_2025.csv` (inexistentes) |
| **Tipo** | Mudança estrutural drástica |
| **Descrição** | Até 2023, todas as informações (perfil, notas, respostas, questionário socioeconômico) vinham em um único arquivo chamado `MICRODADOS_ENEM_XXXX.csv` (com ~76 colunas). A partir de 2024, o INEP desmembrou essa base em dois arquivos distintos: `PARTICIPANTES_XXXX.csv` (38 colunas, apenas dados de perfil e questionário) e `RESULTADOS_XXXX.csv` (42 colunas, contendo as notas `NU_NOTA_*`, códigos de prova e gabaritos/respostas). |
| **Confirmação no Dicionário** | Os arquivos de dicionário de dados (`Dicionário_Microdados_Enem_XXXX.xlsx`) **refletem exatamente essa mudança**. Até 2023, os dicionários possuíam as planilhas `MICRODADOS_ENEM_XXXX` e `ITENS_PROVA_XXXX`. Em 2024 e 2025, os dicionários passaram a ter três planilhas principais: `PARTICIPANTES_XXXX`, `RESULTADOS_XXXX` e `ITENS_PROVA_XXXX`, o que formaliza o desmembramento feito pelo INEP. |
| **Impacto no projeto** | Modelos preditivos que necessitam prever a nota (`NU_NOTA_*`) não podem usar apenas o arquivo `PARTICIPANTES_XXXX.csv` a partir de 2024. Será necessário realizar um **JOIN** (relacionamento) entre `PARTICIPANTES` e `RESULTADOS` (presumivelmente usando a chave primária `NU_INSCRICAO` ou `NU_SEQUENCIAL`) para reconstruir o equivalente ao `MICRODADOS_ENEM` dos anos anteriores. |
| **Ação recomendada** | Ao construir a pipeline de carga de dados (ETL), adicionar uma etapa que verifique se o ano é >= 2024 e, em caso positivo, leia ambos os arquivos (`PARTICIPANTES` e `RESULTADOS`) e faça o *merge* deles antes de concatenar com os anos anteriores. |

---

### 4.2 Remoção das Questões Socioeconômicas Q026 e Q027

| Campo | Detalhe |
|---|---|
| **Anos afetados** | 2019, 2020, 2021, 2022, 2023 (e também nos anos subsequentes) |
| **Tipo** | Remoção de colunas |
| **Descrição** | Em 2017 e 2018 o arquivo `MICRODADOS_ENEM` possuía 78 colunas, incluindo as questões `Q026` e `Q027` do questionário socioeconômico. A partir de 2019, o arquivo passou a ter 76 colunas, sem estas duas perguntas. |
| **Impacto no projeto** | As colunas `Q026` e `Q027` ficarão como nulas para a maior parte do dataset se incluídas. |
| **Ação recomendada** | Remover essas duas features do dataset consolidado. |

---

## 5. Inconsistências de Schema — Bases Auxiliares

### 5.1 Base Extra em 2022: Questionário de Hábitos de Estudo

| Campo | Detalhe |
|---|---|
| **Ano afetado** | 2022 |
| **Tipo** | Base de dados exclusiva e adicional |
| **Descrição** | Em 2022, o pacote de dados e o dicionário de variáveis incluem um arquivo extra: `QUEST_HAB_ESTUDO.csv`, referenciado na planilha `QUEST_HAB_ESTUDO` dentro de `Dicionário_Microdados_Enem_2022.xlsx`. Esse questionário adicional (sobre hábitos de estudo) não existe em nenhum outro ano da série histórica. |
| **Impacto no projeto** | Se o projeto buscar criar um modelo de validade longitudinal (2017 a 2025), variáveis presentes exclusivamente em 2022 não poderão ser utilizadas para treinar modelos genéricos ou testar coortes de outros anos. |
| **Ação recomendada** | Ignorar a base `QUEST_HAB_ESTUDO.csv` se o foco for construir um modelo preditivo unificado para todos os anos, ou tratá-la em uma análise separada restrita ao ano de 2022. |

---

## 6. Pendências

| # | Pendência | Status |
|---|---|---|
| 1 | Download do ENEM 2016 | ❌ Pendente |
| 2 | Download do ENEM 2018 | 🔄 Em andamento (manual) |
| 3 | Análise de schema do arquivo `MICRODADOS_ENEM_XXXX.csv` (participantes) | ✅ Concluída |
| 4 | Comparação de colunas do dicionário de variáveis entre anos | ✅ Concluída |
| 5 | Normalização da estrutura de diretórios (2023–2025 com subpasta extra) | ⏳ Não iniciada |

---

*Documento gerado automaticamente durante a etapa de aquisição e validação — TCC MBA Ciência de Dados.*
