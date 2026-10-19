# 🎓 Visão Geral do Projeto: Previsão de Notas do ENEM e Arquitetura de Dados

Este documento tem como objetivo apresentar à banca avaliadora a arquitetura ponta a ponta do projeto, esclarecendo o papel da fase de pesquisa (Jupyter Notebooks), a estratégia de validação cronológica (2024-2025) e a engenharia de dados em nuvem para colocar a Inteligência Artificial em produção.

---

## 🔬 Etapa 1: A Fase de Pesquisa e Modelagem (Os Notebooks)
Nesta primeira etapa, o ambiente interativo (Jupyter) é utilizado como laboratório para embasar as decisões sociológicas e estatísticas do projeto. 

1. **`01_iniciando_dados.ipynb` (Ingestão Inicial):** Onde ocorre o reconhecimento da base original do INEP, mapeamento de metadados e carregamento estrutural inicial.
2. **`02_eda.ipynb` (Análise Exploratória):** Limpeza rigorosa, tratamento focado em Machine Learning (substituição de nulos estruturais), definição da estratégia de safra (Concluintes 2023) e o uso estatístico do *Cohen's d* para comprovar a desigualdade por raça e escola. O output é o dataset purificado (`enem_2023_silver.parquet`).
3. **`03_engenharia_features.ipynb` (Engenharia de Features):** Criação de novas variáveis como a *Renda Per Capita*, Estudo de Ablação (Navalha de Ockham para simplificar o modelo) e testes de correlação. O laboratório comprova o *Target_M2* (Matemática + Linguagens) como o alvo supremo e livre de *Data Leakage*.
4. **`04_varredura_semantica.ipynb` (Harmonização por NLP):** Uso de *Sentence Transformers (SBERT)* para mapear automaticamente colunas históricas do ENEM. Resolve o *Drift Semântico* (quando o governo muda o nome da coluna de Q021 para Q006 entre os anos), pareando os dicionários de dados matematicamente para o Padrão Ouro de 2023.
5. **`05_modelagem_xgboost.ipynb` (Em breve - A Construção do Modelo):** É **neste notebook** que a Inteligência Artificial será definitivamente treinada. Utilizaremos o algoritmo *XGBoost* para encontrar os melhores hiperparâmetros, extrair o modelo treinado e exportá-lo como um arquivo serializado (ex: `.pkl` ou `.joblib`) pronto para ir para a nuvem.

---

## ⏳ Etapa 2: A Validação Temporal (Testando o Futuro com 2024 e 2025)
Em projetos de Machine Learning, é muito comum que um modelo sofra degradação com o passar do tempo. A intenção de baixar e aplicar o modelo preditivo nas bases do ENEM de 2024 e 2025 tem dois grandes propósitos para a banca:
1. **Teste de Robustez Cega (Out-of-Time Validation):** Em vez de validar o modelo apenas separando 20% dos alunos de 2023, nós o testaremos em **alunos que fizeram a prova no futuro**. Se o $R^2$ se mantiver alto em 2024 e 2025, provamos que o algoritmo não "decorou" o padrão de 2023, mas sim que **aprendeu uma regra sociológica atemporal** do Brasil.
2. **Monitoramento do Determinismo Social:** Acompanhar se o impacto do Computador ou da Renda aumentou ou diminuiu nas provas futuras, oferecendo uma janela incrível para debates sobre políticas públicas recentes.

---

## ⚙️ Etapa 3: Fluxo de Dados Automatizado (Pipeline via Apache Airflow)
A banca perguntará: *"O que acontece quando o INEP lança a base de 2024?"* 
O projeto foi desenhado para não depender de trabalho manual. O fluxo orquestrado pelo Apache Airflow será o seguinte:

1. **Trigger de Download:** O Airflow roda periodicamente um web-scraper ou consome uma API para verificar se os microdados novos do ENEM estão disponíveis. Ao detectar o lançamento, faz o download do `.zip`.
2. **Descompressão e Dicionário:** O arquivo é descompactado. O Airflow extrai o Excel do Dicionário de Dados do novo ano.
3. **Acionamento da Varredura Semântica (NLP):** O script em Python contendo a lógica do Notebook 04 (*SBERT*) é ativado. Ele lê o dicionário novo, compara com o Padrão Ouro de 2023 e descobre como as colunas do novo ano devem se chamar.
4. **Transformação e Ingestão (ETL):** O dataset novo tem as colunas renomeadas instantaneamente pela IA, passa pelos filtros de limpeza (Concluintes, sem treineiros) e é formatado em Parquet.
5. **Append no Data Lake:** Os dados de 2024 são soldados (append) à base imensa histórica (2009-2023), atualizando o banco de dados principal do projeto sem intervenção humana.

---

## ☁️ Etapa 4: Produtização e Deploy na Nuvem (AWS)
O objetivo final de um projeto de Machine Learning moderno não é o Jupyter Notebook, mas sim a entrega do modelo como um serviço (MaaS - Model as a Service).

1. **Empacotamento do Modelo (FastAPI):** O arquivo `.pkl` gerado no Notebook 05 será acoplado a uma API escrita em Python usando a biblioteca `FastAPI`. Esta API receberá um JSON com as respostas socioeconômicas do aluno e retornará a previsão da nota *TARGET_M2*.
2. **Containerização (Docker):** A aplicação FastAPI será colocada dentro de um container Docker, garantindo que rode exatamente da mesma forma em qualquer computador do mundo.
3. **Deploy na AWS:**
   - **Armazenamento:** O *Amazon S3* servirá como o Data Lake para hospedar os pesados arquivos parquet da base de dados imensa.
   - **Hospedagem da API:** Utilizaremos serviços como o *AWS App Runner*, *ECS (Elastic Container Service)* ou uma instância *EC2* simples para rodar a imagem Docker com o FastAPI 24 horas por dia.
4. **Apresentação:** Um simples front-end ou chamadas via Postman consumirão essa API alocada na AWS. A banca poderá digitar "Renda: 3000, Computador: Sim, Escolaridade: Superior" e o sistema baterá no servidor da AWS e responderá ao vivo qual seria o futuro acadêmico projetado para aquele jovem.
