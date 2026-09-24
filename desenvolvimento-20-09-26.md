# Desenvolvimento - 20/09/2026

## 1. Contexto Atual do Projeto
No dia anterior (19/09), concluímos o laboratório de modelagem no arquivo `notebooks/03_eda_modelagem.ipynb`. O algoritmo vencedor na nossa "Arena" foi o **HistGradientBoosting**, alcançando o menor erro (RMSE de ~111) e o maior poder explicativo (R² de ~0.26). Toda a base conceitual sociológica e a arquitetura técnica do MLOps já foram validadas e documentadas nos arquivos `mentoria.md`, `diagramas-mermaid-tcc.md` e na apresentação da banca (`resumo-apresentacao-tcc-19-09-26.md`).

## 2. O Que Precisamos Desenvolver Hoje
Para darmos andamento prático ao TCC, temos duas frentes de trabalho de engenharia mapeadas. A IA assistente que ler este documento deve perguntar ao usuário qual destas opções ele deseja atacar primeiro:

### Opção A: Extração de Feature Importance (A Defesa Sociológica)
- **Onde atuar:** `notebooks/03_eda_modelagem.ipynb` (ou um novo script de análise).
- **O que fazer:** Calcular e plotar a Importância das Features (*Feature Importance* / *Permutation Importance*) do modelo treinado de `HistGradientBoosting`.
- **Objetivo:** Provar para a banca examinadora exatamente QUAIS variáveis (Renda, Escolaridade da Mãe, Tipo de Escola, etc.) tiveram o maior peso na predição da nota. Isso é essencial para provar o "Viés Algorítmico" discutido na documentação e garantir interpretabilidade ao modelo.

### Opção B: Produtização e MLOps (O Salto para a Produção)
- **Onde atuar:** Criação do script `src/train.py` e configuração de um `docker-compose.yml`.
- **O que fazer:** 
  1. Extrair a lógica vencedora (Pipeline + HistGradientBoosting) do ambiente Jupyter e refatorá-la em um código de produção no arquivo `src/train.py`.
  2. Subir um contêiner Docker contendo o servidor local do **MLflow**.
  3. Integrar o código do `train.py` com o MLflow para fazer o "Tracking" automático (registrar as métricas, os parâmetros e salvar o artefato `.joblib` do modelo — conforme mapeado no Diagrama 9).
- **Objetivo:** Cumprir o requisito central de "Machine Learning em Produção" exigido pelo MBA, demonstrando rastreabilidade, registro e versionamento do modelo.

---

## 3. Resultados da Opção A: Feature Importance (Defesa Sociológica)

Executado o script `scripts/plot_feature_importance.py` no dia 20/09, a extração das features mais importantes do modelo HistGradientBoosting revelou o seguinte comportamento da IA:

1. **A Renda Familiar esmaga todas as outras:** Com um "peso" de importância de `0.1883` (Permutation Importance), a Renda Familiar se provou quase **6 vezes mais decisiva** do que qualquer outra variável de forma isolada.
2. **A Comprovação do Viés Algorítmico de Gênero:** O dado mais chocante do experimento revelou que a variável **Sexo (`0.0315`)** carrega um poder preditivo maior do que o próprio **Tipo de Escola (`0.0231`)**. A IA encontrou que saber se o candidato é Homem ou Mulher facilita mais a previsão da nota de Matemática do que saber se ele estudou em Escola Pública ou Privada. Isso comprova matematicamente o viés estrutural: o algoritmo "aprende" as barreiras que desestimulam meninas a seguir ciências exatas ao longo da vida escolar.
3. **A Mãe supera o Pai:** A "Escolaridade da Mãe" (`0.0266`) se mostrou superior à do Pai (`0.0236`), alinhando-se à sociologia educacional (mães como base do cuidado e apoio do letramento primário).

> **Status Atual:** A Opção A foi concluída com sucesso. O gráfico gerado foi armazenado na pasta `media/feature_importance.png`.

---

## 4. Exploração Expandida de Variáveis (Laboratório V2)

Para garantir que o nosso modelo não estava deixando passar nenhuma variável sociológica importante, geramos o notebook `notebooks/02_selecao_features_v2.ipynb` para testar 14 variáveis sugeridas pela literatura no GitHub.

As conclusões vitais desse laboratório foram:
1. **A Descoberta de Novas Potências:**
   - `Q024` (Ter Computador): Assumiu o 2º lugar absoluto em poder de previsão. Ter acesso tecnológico em casa é o maior divisor educacional atrás apenas da Renda.
   - `TP_LINGUA` (Inglês vs Espanhol): Assumiu o 3º lugar, atuando como um "proxy" fortíssimo de capital cultural (Inglês = alta renda/privada; Espanhol = vulnerabilidade/pública).
   - `TP_ANO_CONCLUIU`: Mede o "frescor" do conhecimento do aluno, sendo incrivelmente forte para predição.
2. **Vazamento de Dados (Data Leakage) Evitado:** A variável `TP_STATUS_REDACAO` parecia poderosa, mas era apenas um falso positivo (Data Leakage). Como nosso `cleaner.py` já filtra os alunos eliminados, todo aluno na Camada Gold tem o status "1" (Sem problema). Variáveis sem variância após a limpeza são inúteis e perigosas.
3. **O "Sweet Spot" de Machine Learning:** Aplicando o Princípio da Parcimônia (Navalha de Ockham), optamos por não sujar o ETL de produção com dezenas de colunas de baixo rendimento. O modelo final usará estritamente as 6 variáveis supremas que dominam o poder preditivo: **`Q006, Q024, TP_ANO_CONCLUIU, TP_LINGUA, TP_SEXO e Q002`**.

---

> **Aviso para a IA Assistente (Instrução Sistêmica):** Ao iniciar a sessão baseada na leitura deste documento, vá direto para a execução técnica da **Opção B (Produtização e MLOps com MLflow)**. O novo script `src/train.py` **deverá ser escrito utilizando estritamente as 6 variáveis escolhidas na Seção 4**. Solicite a autorização do usuário e inicie a configuração do Docker e do MLflow.
