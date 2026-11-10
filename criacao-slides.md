# 🎬 Roteiro Guia para o Novo Chat: Criação dos Slides da Defesa e Continuidade do TCC

**Projeto:** Pipeline de MLOps para Predição de Desempenho no ENEM (`TARGET_M4`)  
**Autor:** Saulo Santos  
**Objetivo deste Documento:** Servir como ponto de partida (`handoff`) para o novo chat focado na **construção da apresentação final para a banca do MBA**, além de mapear os passos seguintes após a conclusão dos slides.

---

## 🚀 Como Iniciar o Novo Chat (Prompt Sugerido para o Saulo)

Ao abrir o novo chat, basta enviar a seguinte mensagem inicial (em inglês, se quiser manter o treino de conversação, ou em português):

> *"Please read `AGENT.md` and `criacao-slides.md` to get full context on our TCC project and follow our collaboration rules."*

---

## 🛡️ 1. Diretrizes Obrigatórias de Colaboração (Para o Agente no Novo Chat)

1. **💡 Prática de Inglês (`English Practice Tip`):**
   * Sempre que o Saulo escrever em inglês, responda em **Português do Brasil**, mas inclua obrigatoriamente no topo da resposta um bloco `> 💡 **English Practice Tip:**` analisando a frase dele, elogiando acertos e sugerindo melhorias naturais ou correções sutis.
2. **📌 Governança Git a Cada Marco:**
   * Após cada entrega relevante aprovada pelo Saulo, avise explicitamente que é hora de commitar e forneça os comandos exatos `git add ...` e `git commit -m "..."`.
3. **🤝 Modo de Colaboração Passo a Passo (`AGENT.md` Seção 6.6):**
   * Nunca aja de forma autônoma antecipando etapas. Explique o que pretende fazer, apresente opções claras e aguarde o aval explícito do Saulo antes de criar/editar arquivos ou rodar scripts.

---

## 📚 2. Inventário Completo do que Já Está Pronto no Repositório

As **3 Grandes Etapas Arquiteturais (Capítulos 01 a 08)** já estão **100% implementadas, testadas (`29/29 PASSED` no `pytest`), auditadas e documentadas**.

### 2.1. Roteiros Detalhados de Slides por Capítulo (Já Criados)
| Capítulo | Etapa | Arquivo de Roteiro de Slides | Conteúdo Principal e Métricas Canônicas |
| :---: | :---: | :--- | :--- |
| **Cap. 01 e 02** | Etapa 1 | *(Documentado em [`AGENT.md`](AGENT.md) Seções 3.1/3.2; falta criar `slides-01-02.md`)* | Auditoria estrutural 2014–2025 (quebra LGPD em 2024, remoção de colunas de vazamento) + EDA 2023 (`212.386` concluintes, `enem_2023_silver.parquet`, *Cohen's d* de Escola `-0,967` e Raça `-0,554`, hipótese de Bourdieu). |
| **Cap. 03** | Etapa 1 | **[`slides-03.md`](slides-03.md)** | Engenharia da `RENDA_PER_CAPITA`, estudo de ablação (76 variáveis $\rightarrow$ **6 features do Esquadrão de Elite** retendo `86,1%` da importância com perda de apenas `0,0119` em $R^2$) e consagração psicométrica do **`TARGET_M4`** ($\alpha = 0,865$, $R^2 = 0,3467$ sem Redação TCT). |
| **Cap. 04** | Etapa 1 | **[`slides-04.md`](slides-04.md)** | Harmonização semântica 2014–2024 via NLP/SBERT (`paraphrase-multilingual-MiniLM-L12-v2`), matriz de similaridade de cosseno e geração do contrato [`data/processed/schema_mapping_historico.json`](data/processed/schema_mapping_historico.json). |
| **Cap. 05** | Etapa 1 | **[`slides-05.md`](slides-05.md)** *(+ [`passo-a-passo-05.md`](passo-a-passo-05.md))* | Consolidação da Década de Ouro 2014–2023 (**`37.593.629` candidatos**), deflação pelo Salário Mínimo histórico e *Downcasting* extremo (`15 bytes/linha`, **`153,17 MB`** em Parquet, `537,78 MB` em RAM). |
| **Cap. 06** | Etapa 1 | **[`slides-06.md`](slides-06.md)** *(+ [`passo-a-passo-06.md`](passo-a-passo-06.md))* | Treinamento `XGBRegressor` vs. `RandomForest` com MLflow (`sqlite:///mlflow.db`): Holdout `7,52M` ($R^2 = 0,33780$, $\text{RMSE} = 57,7439$ pts), OOT 2023 ($R^2 = 0,31842$), SHAP (`RENDA_PER_CAPITA` `41,11%`, `Q024` `22,74%`, `Q002` `16,58%`) e exportação de [`models/enem.pkl`](models/enem.pkl) (`1,727 MB`). |
| **Cap. 07** | Etapa 2 | **[`slides-07.md`](slides-07.md)** *(+ [`passo-a-passo-07-api-docker.md`](passo-a-passo-07-api-docker.md))* | Produtização FastAPI + Pydantic v2 (`extra="forbid"` bloqueando `NU_ANO` com `HTTP 422`), `25/25 PASSED` no `pytest`, Docker multi-stage enxuto (**`515 MB` OCI**, latência `6,49 ms`) e GitHub Actions CI/CD (`.github/workflows/deploy.yml`). |
| **Cap. 08** | Etapa 3 | **[`slides-08.md`](slides-08.md)** *(+ [`passo-a-passo-08-airflow-producao.md`](passo-a-passo-08-airflow-producao.md))* | DAG Autônoma Apache Airflow em 4 estágios (`2024` e `2025`): NLP/SBERT ao vivo **antes** da seleção (`Q006->Q007`, `Q024->Q021`), Gatekeeper OOT com **Circuit Breaker** contra a bipartição LGPD 2024 (`positional_match_rate = 0,0055`), Juiz MLflow Champion vs. Challenger e Auditoria de Drift (`PSI < 0,10` em 2024 e 2025). |

> ⚠️ **Atenção sobre arquivo legado:** O arquivo [`resumo-apresentacao-tcc-19-09-26.md`](resumo-apresentacao-tcc-19-09-26.md) pertence a uma versão inicial do projeto (quando havia apenas 4 notebooks e período 2017–2025) e **não deve ser usado como fonte de métricas**. As fontes canônicas atualizadas são [`AGENT.md`](AGENT.md), [`visao_geral_projeto.md`](visao_geral_projeto.md) e os arquivos `slides-03.md` a `slides-08.md`.

### 2.2. Ativos Visuais Já Disponíveis para Inserção nos Slides
* **Diagramas Arquiteturais das 3 Etapas (`media/` e `.md`):**
  * `media/pipeline-1.jpg` (Etapa 1 — Pesquisa, NLP, Consolidação e Treino)
  * `media/pipeline-2.jpg` e [`diagrama_deploy_aws.md`](diagrama_deploy_aws.md) (Etapa 2 — FastAPI, Docker, GitHub Actions e AWS)
  * `media/pipeline-3.jpg` e [`diagrama_producao_2024.md`](diagrama_producao_2024.md) (Etapa 3 — Airflow Autônomo 2024/2025)
* **Gráficos Científicos de Alta Resolução (`reports/figures/`):**
  * `reports/figures/notebook04_heatmap_sbert_2014_2024.png`
  * `reports/figures/notebook05_evolucao_decenal_2014_2023.png`
  * `reports/figures/notebook06_estabilidade_temporal_r2_rmse.png`
  * `reports/figures/notebook06_shap_beeswarm_100k.png`
  * `reports/figures/notebook06_shap_bar_importance.png`

---

## 🎯 3. Plano Passo a Passo para a Criação dos Slides (No Novo Chat)

Como os roteiros `slides-03.md` a `slides-08.md` somam juntos cerca de **41 slides técnicos detalhados** (excelentes como estudo e material de apoio), uma defesa de TCC de MBA normalmente exige uma **apresentação executiva enxuta de 15 a 20 minutos (cerca de 15 a 18 slides principais + slides de apêndice/backup para perguntas da banca)**.

No novo chat, o agente deverá conduzir com o Saulo os seguintes passos:

### Passo 1: Fechar a Lacuna dos Capítulos 01 e 02 (`slides-01-02.md`)
* Criar o roteiro **`slides-01-02.md`** cobrindo:
  1. **O Problema Sociológico e de Engenharia de Dados:** A tese de Pierre Bourdieu aplicada ao ENEM e os desafios dos microdados brutos do INEP (`2014–2025`).
  2. **Investigação Estrutural (`01_investigacao_estrutural.ipynb`):** Descoberta da mudança de layout LGPD em 2024 (`PARTICIPANTES` vs. `RESULTADOS`) e expurgo de variáveis de vazamento (*Data Leakage*).
  3. **Análise Exploratória e Purificação (`02_eda.ipynb`):** Construção da camada Silver (`212.386` concluintes em 2023) e comprovação estatística via *Tamanho de Efeito de Cohen ($d$)* da desigualdade por Dependência Administrativa ($d = -0,967$, efeito grande) e Raça/Cor ($d = -0,554$, efeito médio-grande).
* Atualizar a tabela do topo de [`visao_geral_projeto.md`](visao_geral_projeto.md) substituindo a referência antiga a `resumo-apresentacao-tcc-19-09-26.md` por `slides-01-02.md`.

### Passo 2: Construir o Deck Mestre Consolidado da Defesa (`apresentacao-final-tcc.md`)
Unificar a narrativa das **3 Grandes Etapas** em uma estrutura de alto impacto de **16 a 18 slides** (com indicação visual, texto enxuto de slide, gráfico correspondente e nota de fala de ~1 minuto por slide):
1. **Capa & Posicionamento:** Título, Autor, Arquitetura Híbrida de MLOps sobre `37,59 milhões` de candidatos.
2. **Motivação & Tese Sociológica:** Determinismo socioeconômico (Bourdieu) traduzido em Ciência de Dados auditável.
3. **Visão Geral da Arquitetura em 3 Etapas:** Os 3 Planos (`media/pipeline-1.jpg`, `pipeline-2.jpg`, `pipeline-3.jpg`).
4. **Etapa 1 (Cap. 01 e 02) — Qualidade de Dados e Evidência Preliminar:** Purificação da safra 2023 (`212k` concluintes) e *Cohen's d* (Escola e Raça).
5. **Etapa 1 (Cap. 03) — Navalha de Ockham e Psicometria:** De 76 variáveis para o **Esquadrão de Elite (6 features)** e por que o **`TARGET_M4`** (TRI pura, $\alpha = 0,865$) supera a Redação (TCT subjetiva).
6. **Etapa 1 (Cap. 04) — Resiliência contra Drift de Dicionário com NLP/SBERT:** Como `paraphrase-multilingual-MiniLM-L12-v2` mapeia `2014–2025` automaticamente (`notebook04_heatmap_sbert_2014_2024.png`).
7. **Etapa 1 (Cap. 05) — Engenharia Big Data Decenal (2014–2023):** Harmonização econômica em Salários Mínimos e *Downcasting* de `37.593.629` linhas em `153,17 MB` (`notebook05_evolucao_decenal_2014_2023.png`).
8. **Etapa 1 (Cap. 06) — Treinamento Escalável e Governança MLflow:** `XGBRegressor` vs. `RandomForest`, Holdout `7,52M` ($R^2 = 0,33780$, $\text{RMSE} = 57,74$ pts) e Validação Out-of-Time Cega 2023 ($R^2 = 0,31842$) (`notebook06_estabilidade_temporal_r2_rmse.png`).
9. **Etapa 1 (Cap. 06) — Explicabilidade Matemática com SHAP:** Decomposição do impacto de `RENDA_PER_CAPITA` (`41,11%`), `Q024` (`22,74%`) e `Q002` (`16,58%`) (`notebook06_shap_beeswarm_100k.png`).
10. **Etapa 2 (Cap. 07) — Produtização em Microserviço FastAPI & Contratos Pydantic v2:** Defesa ativa contra *Data Leakage* (`HTTP 422` para `NU_ANO`) e paridade bit-a-bit (`25/25 PASSED`).
11. **Etapa 2 (Cap. 07) — Containerização Multi-Stage FinOps e CI/CD GitHub Actions:** Redução de `>4,5 GB` para **`515 MB` OCI**, latência de `6,49 ms` e esteira `.github/workflows/deploy.yml` para Amazon ECR / AWS App Runner.
12. **Etapa 3 (Cap. 08) — Orquestração Autônoma com Apache Airflow (2024/2025):** Topologia dos 4 estágios e detecção ao vivo de drift semântico em 2024/2025 (`Q006 -> Q007` e `Q024 -> Q021`).
13. **Etapa 3 (Cap. 08) — Descoberta Científica em 2024 (Bipartição LGPD & Circuit Breaker):** Como o Gatekeeper OOT impediu *Data Poisoning* ao detectar `positional_match_rate = 0,0055` ($R^2 = -0,1917$) + Juiz MLflow Champion vs. Challenger.
14. **Etapa 3 (Cap. 08) — Inferência em Lote e Estabilidade Populacional (2024 e 2025):** Escoragem em lote e auditoria de *Data Drift* com $\text{PSI} < 0,10$ em todas as 6 variáveis (`ESTAVEL`).
15. **Conclusões, Contribuições do TCC e Trabalhos Futuros:** Síntese executiva dos entregáveis técnicos e sociológicos.
16. **Apêndice de Backup (Sabatina da Banca):** Slides extras prontos com as perguntas mais difíceis e respostas matemáticas diretas.

### Passo 3: Geração Automatizada do Arquivo Visual de Apresentação (Opcional, à Escolha do Saulo)
* Perguntar ao Saulo se ele prefere:
  * **Opção A:** Gerar automaticamente um arquivo PowerPoint editável (**`.pptx`**) via script Python (`python-pptx`) já contendo todos os textos, tabelas, notas do apresentador e as imagens de `reports/figures/` e `media/` embutidas;
  * **Opção B:** Gerar slides em **Marp / HTML interativo / PDF**; ou
  * **Opção C:** Manter apenas o roteiro estruturado em Markdown para ele mesmo montar no Canva / Google Slides / PowerPoint.

---

## 🧭 4. Instruções para Dar Continuidade ao Projeto APÓS a Conclusão dos Slides

Assim que os slides estiverem 100% finalizados e commitados no repositório, o projeto entrará na **Fase de Preparação Final e Demonstração da Defesa**. Siga o roteiro abaixo com o Saulo:

### Fase Pós-Slides 1: Ensaio Geral da Demonstração Local Ao Vivo (Custo `R$ 0,00`)
Caso o Saulo queira mostrar o sistema funcionando ao vivo durante a banca (ou gravar um vídeo curto de 2 minutos para embutir no slide de demonstração, o que é altamente recomendado contra falhas de internet no dia da defesa):
1. **Subir e demonstrar a API Dockerizada (Etapa 2):**
   ```bash
   docker compose up -d
   curl -s http://localhost:8000/health | python3 -m json.tool
   # Abrir http://localhost:8000/docs no navegador para mostrar o Swagger UI
   ```
2. **Demonstrar a DAG Autônoma do Airflow nas Safras 2024 e 2025 (Etapa 3):**
   ```bash
   .venv/bin/python dags/enem_autonomous_dag.py --year 2024 --max-rows 50000
   .venv/bin/python dags/enem_autonomous_dag.py --year 2025 --max-rows 50000
   ```
3. **Executar a Suíte Completa de Testes Automatizados (`29/29 PASSED`):**
   ```bash
   .venv/bin/python -m pytest tests/ -v
   ```

### Fase Pós-Slides 2: Deploy Pontual na AWS para o Dia da Defesa (Opcional & FinOps)
Conforme alinhado na Diretriz 1 do projeto, o provisionamento na AWS foi deixado para a véspera/dia da apresentação final para evitar custos ociosos. Se o Saulo desejar ativar o endpoint público na AWS para a banca testar ao vivo:
1. **Ativação (Véspera da Defesa):**
   * Configurar as credenciais `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` nos *GitHub Actions Secrets* do repositório;
   * Criar o repositório `enem-target-m4-api` no Amazon ECR (`us-east-1`);
   * Disparar o workflow [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) (via `git push origin main` ou botão *Run workflow* na aba Actions) para publicar a imagem de `515 MB` e iniciar o serviço no **AWS App Runner**.
2. **Desligamento Imediato Pós-Defesa (Checklist de Teardown FinOps):**
   * Assim que a banca encerrar a avaliação, deletar o serviço no AWS App Runner e a imagem no Amazon ECR para garantir **custo zero** após a apresentação:
     ```bash
     aws apprunner list-services --region us-east-1
     aws apprunner delete-service --service-arn <ARN_DO_SERVICO> --region us-east-1
     aws ecr delete-repository --repository-name enem-target-m4-api --force --region us-east-1
     ```

### Fase Pós-Slides 3: Simulação de Sabatina da Banca (*Mock Defense / Grill-Me*)
* Realizar uma rodada rápida de simulação de perguntas da banca examinadora (estatística/psicometria, engenharia de dados/SBERT e arquitetura MLOps/FinOps) para que o Saulo se sinta 100% seguro na apresentação oral.

