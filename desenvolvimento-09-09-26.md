# Desenvolvimento - 09/09/2026

## Documentação do Processo ETL (Camadas de Transformação)

O processo desenvolvido até agora no `harmonizer.py` representa apenas a **primeira camada** do "T" no fluxo ETL — a harmonização estrutural (tornar os schemas compatíveis entre anos). 

O "T" completo de um pipeline ETL para Machine Learning possui múltiplas camadas:

### As camadas do "T" no projeto

| Camada | Descrição | Status |
|---|---|---|
| **T1 — Harmonização estrutural** | JOIN 2024/2025, remoção de Q026/Q027, descarte de TP_VERSAO_DIGITAL, normalização de paths | ✅ Feito |
| **T2 — Limpeza (Data Cleaning)** | Remover registros inválidos, tratar ausentes, eliminar duplicatas, converter tipos | ⏳ Pendente |
| **T3 — Padronização** | Padronizar categorias (ex: valores do questionário socioeconômico), normalizar campos | ⏳ Pendente |
| **T4 — Feature Engineering** | Criar novas variáveis derivadas (ex: nota média, faixas de renda, indicadores compostos) | ⏳ Pendente |

### Distinção Conceitual para o TCC

Existe uma distinção conceitual importante que pode ser explorada pela banca:

- **T1 e T2** são responsabilidades da **Engenharia de Dados** — garantir que o dado esteja limpo, íntegro e consistente.
- **T3 e T4** vivem na fronteira entre Engenharia de Dados e **Ciência de Dados** — preparar o dado para alimentar os modelos.

No pipeline do projeto, o `validator.py` (Pandera) atua como o **guardião entre T1/T2 e T3/T4**: ele garante que apenas os dados que passem nos contratos de qualidade avancem para a etapa de *feature engineering*.

### Conclusão sobre o "L" (Load)

Desta forma, o "L" (Load final) ainda não ocorreu. O dado que reside no MinIO no momento é, na melhor das hipóteses, um dado pós-T1. O arquivo analítico final (`.parquet`) — aquele que de fato alimentará o treinamento dos modelos — só será gerado após a conclusão completa das etapas **T2**, **T3** e **T4**.

---

## Pergunta: O ETL faz parte da camada de ingestão de dados citada na linha 30 do TCC?

**Não exatamente. A relação conceitual é o inverso.**

A "Ingestão" é apenas **uma parte** do processo ETL, e não o ETL inteiro.

### 1. O ETL é o processo completo
O **ETL** (Extract, Transform, Load) é o grande "guarda-chuva" que abrange tudo o que acontece com o dado desde o momento em que ele é lido em formato bruto até o momento em que é salvo no MinIO em `.parquet`.

### 2. Onde a "Ingestão" entra no ETL?
No projeto, a **Camada de Ingestão** (que usa o `reader.py` e o `harmonizer.py`) corresponde exclusivamente à fase de **E (Extract)** e à primeiríssima etapa do **T (Transformação 1 - Harmonização)**. 
- **E:** Lê os microdados crus.
- **T1:** Faz o JOIN (para anos >= 2024), tira colunas obsoletas.

### 3. Onde está o resto do ETL?
O restante do "T" (Limpeza, Feature Engineering) e o "L" (Salvar em Parquet) ocorrem na **Camada de Processamento** (Módulos `cleaner.py` e `features.py`), detalhada na Seção 3.4 da dissertação.

### Como afirmar isso corretamente na defesa
A afirmação correta e blindada é:
> *"O pipeline ETL desenvolvido contempla duas grandes camadas da nossa arquitetura: a **Camada de Ingestão** (responsável pela Extração e Harmonização estrutural) e a **Camada de Processamento** (responsável pela Limpeza, Feature Engineering e Carga/Load no Data Lake em formato Parquet)."*

---

## Pergunta: As resoluções T1 (JOIN 2024/2025, remoção de Q026/Q027, descarte de TP_VERSAO_DIGITAL, etc) já foram feitas no notebook `01_analise_anomalias_estruturais.ipynb`?

**Sim e Não.** É fundamental distinguir o papel da "Exploração de Dados" do papel da "Engenharia de MLOps".

### Sim (Do ponto de vista de Exploração de Dados)
Isso foi feito no notebook `01_analise_anomalias_estruturais.ipynb`. O notebook é o ambiente de experimentação. Nele, foi comprovado de forma visual e estatística que os dados estavam "quebrados" e demonstrou-se como resolver o problema (fazendo o JOIN de 2024, removendo as colunas Q026/Q027, etc). O notebook atua como um **"Documento de Descoberta"**, servindo de prova acadêmica para a banca examinadora justificar o *porquê* certas decisões arquiteturais precisaram ser tomadas.

### Não (Do ponto de vista de Engenharia de Dados / MLOps)
Ainda não foi implementado no **pipeline de produção real**. O código em um Jupyter Notebook:
- Não escala de forma performática para bases massivas sem adaptação.
- Não é facilmente testável (ex: testes unitários com `pytest`).
- Não pode ser orquestrado e agendado pelo Apache Airflow de forma robusta e modularizada.

### Conclusão: A Transição para Engenharia de Machine Learning
Esse cenário ilustra perfeitamente o momento de transição entre a "Ciência de Dados Exploratória" e a "Engenharia de Machine Learning". O próximo passo arquitetural é extrair toda a inteligência e lógica desenvolvida e validada no notebook exploratório e transformá-la em **código de produção estruturado**, empacotando essas regras dentro dos módulos Python definitivos da Camada de Ingestão (`src/ingestion/reader.py` e `src/ingestion/harmonizer.py`).

---

## Implementação da Camada de Ingestão (E + T1)

Com base no planejamento, os códigos oficiais da Camada de Ingestão foram escritos e estruturados no formato de produção dentro da pasta `src/ingestion/`. 

Dois novos arquivos foram criados, consolidando as camadas de **Extração (E)** e **Harmonização (T1)**:

### 1. `reader.py`
- **Responsabilidade:** Encapsula as regras de leitura e normalização de caminhos (trata as mudanças de diretório que ocorreram em 2023).
- **Padrão Adapter:** Para os anos até 2023, realiza a leitura simples da base monolítica. A partir de 2024, realiza a leitura particionada (`PARTICIPANTES` e `RESULTADOS`) e executa de forma transparente um `INNER JOIN` via chave primária `NU_INSCRICAO`.
- **Prevenção de Erros:** O carregamento inicial é forçado como `dtype=str`. Essa decisão é uma "Engenharia de Software Defensiva", pois impede que a inferência automática do Pandas remova zeros à esquerda de códigos de identificação numéricos.

### 2. `harmonizer.py`
- **Responsabilidade:** Implementa o **Padrão Translator** da Camada Anticorrupção.
- **Defesa Estrutural:** Realiza a remoção cirúrgica de "anomalias" estruturais mapeadas na fase de exploração, garantindo paridade temporal exata entre todos os datasets:
  - Destrói as questões de renda antigas `Q026` e `Q027` nas edições de 2017 e 2018 para que o schema "case" perfeitamente com os anos mais recentes.
  - Remove a coluna isolada `TP_VERSAO_DIGITAL`, introduzida apenas na edição atípica de 2020.

Esses módulos mudam o status dos "Passos 1 e 2" do checklist técnico para **Concluído**, deixando os dados crus (Raw) preparados para as etapas de Validação Rigorosa e Limpeza Pesada (T2).
O próximo passo lógico no pipeline (seguindo o nosso checklist) seria desenhar os Data Contracts (Validação via Pandera) que vão atuar como "fiscais" para impedir que algum lixo ou coluna indesejada passe da Ingestão (T1) para a Limpeza (T2).

---

## Pergunta: O arquivo `cleaner.py` (Camada T2) faz o trabalho pesado que um ser humano geralmente faria ao analisar a base?

**Exatamente.** Ele automatiza e institucionaliza o trabalho braçal e repetitivo da análise de dados.

Tradicionalmente, um cientista ou analista de dados gastaria cerca de **80% do seu tempo** fazendo atividades manuais exaustivas, tais como:
- Procurar participantes com nota nula e remover a linha;
- Filtrar os participantes que faltaram à prova ou foram eliminados;
- Checar se há inscrições duplicadas;
- Corrigir colunas que vieram como texto, mas deveriam ser números.

O papel do `cleaner.py` dentro da engenharia de MLOps é pegar esse "trabalho humano", que é suscetível a falhas, e **automatizá-lo de forma determinística**.

### Argumento para a Defesa do TCC
Transferir esse trabalho para o código (no `cleaner.py`) traz três vantagens incontestáveis:
1. **Escalabilidade:** Cada edição do ENEM possui de 4 a 5 milhões de linhas. O Excel trava e falha com esse volume, mas o script executa a limpeza em segundos.
2. **Reprodutibilidade Exata:** O código não possui "lapso de memória". Se um humano limpa os dados de 2023, pode esquecer de aplicar a mesma regra em 2024. O `cleaner.py` garante que a exata mesma matemática de exclusão seja aplicada para todas as edições de 2017 a 2025 de forma idêntica.
3. **Erradicação do Retrabalho:** Quando o INEP liberar o ENEM 2026, não será necessário gastar semanas limpando dados manualmente para retreinar os modelos. Com o pipeline orquestrado, a base de 2026 será ingerida, harmonizada e limpa automaticamente pelo sistema.
