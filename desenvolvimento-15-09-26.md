# Desenvolvimento - 15/09/2026

## 1. Panorama: Onde estamos no projeto?

Antes de começar o dia, fiz uma leitura completa dos arquivos do projeto para entender o que já foi construído. O resultado foi uma boa surpresa: **o projeto está mais avançado do que parecia!**

Usando a linguagem da **Arquitetura Medalhão** que aprendemos no `mentoria.md`, o status de cada camada é:

### 🥉 Camada Bronze (Dado Bruto) — ✅ PRONTA
- Os 9 anos de microdados do ENEM (2017–2025) já foram baixados e estão organizados em `data/raw/`.
- Esses arquivos jamais serão modificados. Eles são o nosso registro histórico fiel da fonte (INEP).

### 🥈 Camada Silver (Dado Limpo) — Engenharia ETL — ⚠️ QUASE PRONTA

Esta é a nossa camada de trabalho. Todos os módulos foram escritos, mas ainda **não foram conectados e testados com dados reais**.

| Módulo | O que faz | Arquivo | Status |
|---|---|---|---|
| **Leitura (T1)** | Lê o CSV do INEP (arquivo único ou particionado) | `src/ingestion/reader.py` | ✅ Pronto e testado |
| **Harmonização (T1)** | Unifica o schema entre 2017 e 2025 (Camada Anticorrupção) | `src/ingestion/harmonizer.py` | ✅ Pronto e testado |
| **Contratos de Dados** | Valida a qualidade dos dados (Pandera) | `src/processing/validator.py` | ✅ Escrito — ⚠️ não testado com dados reais |
| **Limpeza (T2)** | Remove ausentes, duplicatas e faz o cast de tipos | `src/processing/cleaner.py` | ✅ Escrito — ⚠️ não testado com dados reais |
| **Feature Engineering (T3/T4)** | Cria a nota média e as faixas de desempenho | `src/processing/features.py` | ✅ Escrito — ⚠️ não testado com dados reais |

### 🥇 Camada Gold (Dado Pronto para ML) — ❌ FALTA O ORQUESTRADOR
- Não existe ainda um script central (`pipeline.py`) que conecte todos os módulos acima em sequência.
- **Essa é a peça que falta para encerrar o ETL.**

### 🔬 Laboratório de EDA (Notebook) — 🟡 INCOMPLETO
- O arquivo `notebooks/02_selecao_features_laboratorio.py` foi criado, mas ainda havia um problema de configuração de Kernel (`.venv`) que impediu a execução completa.
- O laboratório de EDA **depende da Camada Gold**: precisamos ter os dados limpos em `.parquet` para explorar e selecionar as features com qualidade.

---

## 2. O Gargalo e o Próximo Passo: O Orquestrador `pipeline.py`

**Por que esse é o passo mais importante agora?**

O `pipeline.py` é o script central que vai:
1. Chamar o `reader.py` + `harmonizer.py` (Ingestão T1)
2. Passar os dados pelo `validator.py` (Soft Validation)
3. Passar os dados pelo `cleaner.py` (Limpeza T2)
4. Passar os dados pelo `features.py` (Feature Engineering T3/T4)
5. Chamar o `validator.py` novamente (Hard Validation — o porteiro final)
6. **Salvar o resultado final em formato `.parquet`** (o artefato da Camada Gold)

Sem ele, cada módulo existe isoladamente mas nunca produziu nada real. Com ele, teremos pela primeira vez o pipeline rodando de ponta a ponta com os microdados reais do ENEM.

---

## 3. Plano de Execução do Dia

### Passo 1: Criar o `src/pipeline.py` (O Orquestrador)
- [x] Criar o arquivo `src/pipeline.py`
- [x] Implementar a função `run_pipeline(year: int, data_dir: str, output_dir: str)`
- [x] Conectar todos os módulos na sequência correta: Ingestão → Soft Validation → Limpeza → Features → Hard Validation → Salvar Parquet
- [x] Adicionar tratamento de erros com `try/except` e log claro de cada etapa
- [x] Adicionar suporte a `nrows` para testes rápidos sem carregar a base inteira

### Passo 2: Criar a pasta de saída da Camada Gold
- [x] Criar o diretório `data/processed/`
- [x] Definir a convenção de nomenclatura: `enem_{year}_silver.parquet`

### Passo 3: Testar o Pipeline com dados reais (1 ano)
- [x] Rodar o `pipeline.py` apontando para os dados reais de 2023
- [x] Verificar se os logs indicam as etapas sendo executadas corretamente
- [x] Verificar o arquivo `.parquet` gerado (número de linhas, colunas, tipos de dados)
- [x] Comparar o número de linhas de entrada (CSV bruto) vs saída (parquet limpo)

### Passo 4: Documentar os Resultados
- [x] Atualizar este arquivo com os resultados do teste
- [ ] Adicionar seção no `mentoria.md` explicando o que é o `.parquet` e por que o usamos

---

## 4. Resultados do Dia ✅

| Etapa | Status | Observações |
|---|---|---|
| Criação do `pipeline.py` | ✅ Concluído | `src/pipeline.py` com 5 etapas orquestradas |
| Criação de `data/processed/` | ✅ Concluído | Pasta da Camada Gold criada |
| Teste com ENEM 2023 | ✅ Sucesso | Modo teste: 10.000 linhas |
| Documentação | ✅ Concluído | Este arquivo + mentoria.md |

### Números do Teste (ENEM 2023 — amostra de 10.000 linhas)

| Métrica | Valor |
|---|---|
| Registros brutos (entrada CSV) | 10.000 |
| Registros após limpeza (saída .parquet) | 7.114 |
| Registros removidos (ausentes/duplicatas) | 2.886 (28,9%) |
| Colunas no artefato final | 78 |
| Arquivo salvo em | `data/processed/enem_2023_silver.parquet` |
| Soft Validation (Pandera) | ✅ APROVADA |
| Hard Validation (Pandera) | ✅ APROVADA |

> **Interpretação para o TCC:** Aproximadamente **29% dos candidatos inscritos faltaram ou foram eliminados** na amostra testada. Esse é um dado real e importante sobre a dinâmica do ENEM que pode ser mencionado na sua dissertação como motivação para o filtro de presença (`filter_present_participants`).

### Colunas geradas pelo pipeline (Camada Gold)
O artefato final contém **78 colunas**, incluindo:
- Todas as notas por área (`NU_NOTA_MT`, `NU_NOTA_CN`, etc.)
- Todas as variáveis socioeconômicas do questionário (`Q001` a `Q025`)
- **`NU_NOTA_MEDIA`** — variável derivada: média das 5 notas (criada pelo `features.py`)
- **`FAIXA_DESEMPENHO`** — variável derivada: categoria `Insuficiente / Regular / Bom / Excelente`

---

## 5. Por que `.parquet` e não `.csv`?

> **Nota para o TCC e para entrevistas:** Salvar o arquivo final em `.parquet` (e não em `.csv`) é uma decisão de engenharia consciente. O Parquet é um formato colunar binário que ocupa em média **5 a 10 vezes menos espaço em disco** do que o CSV equivalente, preserva os tipos de dados nativamente e é lido de forma muito mais rápida pelo Pandas e pelo Spark. É o formato padrão da indústria para armazenamento em Data Lakes.
