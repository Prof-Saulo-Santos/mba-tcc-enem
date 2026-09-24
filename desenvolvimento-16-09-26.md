# Desenvolvimento - 16/09/2026

## 1. Objetivo do Dia: Da Exploração à Modelagem (Camada Gold)

Ontem, concluímos com maestria toda a parte de **Engenharia de Dados (ETL)**. Garantimos que os dados brutos se tornassem confiáveis, tipados e limpos, consolidando a nossa Camada Gold (`enem_2023_silver.parquet`).

Hoje, nosso foco muda. Vamos vestir o chapéu de **Cientista de Dados**. O objetivo é descobrir o que os dados têm a nos dizer e treinar algoritmos para tentar prever as notas do ENEM.

---

## 2. Plano de Execução

### Passo 1: Análise Exploratória de Dados (EDA)
- [ ] O usuário deve abrir o arquivo `notebooks/03_eda_modelagem.py`.
- [ ] Verificar e selecionar o Kernel correto (`/home/saulo/mba/tcc/enem/.venv/bin/python`).
- [ ] Rodar as Células 1 a 4 do notebook.
- [ ] Validar visualmente as distribuições de notas e a influência de variáveis socioeconômicas (ex: Renda e Tipo de Escola) usando os gráficos gerados.

### Passo 2: O Laboratório de Machine Learning
- [ ] Rodar a Célula 5 para preparar os dados (Treino/Teste e Encoding).
- [ ] Rodar a Célula 6 para treinar a arena de 4 algoritmos:
  - Dummy Regressor (Nossa linha de base)
  - Regressão Linear
  - Random Forest
  - HistGradientBoosting (LightGBM)
- [ ] Rodar a Célula 7 para gerar o gráfico comparativo (RMSE e R²) que irá para a dissertação.

### Passo 3: Interpretação de Resultados e Feature Importance
- [ ] Avaliar qual modelo obteve o menor erro (RMSE) e o maior poder de explicação (R²).
- [ ] (A ser desenvolvido) Criar um novo bloco de código para extrair a "Importância das Features" do melhor modelo (ex: Random Forest), provando matematicamente para a banca quais perguntas do INEP mais afetam a nota do candidato.

### Passo 4: Evolução MLOps (Preparação)
- [ ] Após validarmos qual é o melhor modelo no notebook, discutiremos como tirá-lo do "laboratório" e levá-lo para "produção" criando um script `src/train.py`.
- [ ] Planejar a introdução do **MLflow** para rastreamento de experimentos (fundamental para justificar o "ML in Production" do seu MBA).

---

## 3. Resultados Obtidos

*Esta seção será atualizada ao longo do dia, conforme formos executando os passos.*

| Etapa | Status | Observações |
|---|---|---|
| EDA (Gráficos) | - | - |
| Modelagem (Treino) | - | - |
| Extração de Importância | - | - |
| Planejamento MLOps | - | - |
