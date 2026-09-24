# Desenvolvimento - 21/09/2026

## 1. Contexto e Objetivo do Dia
No dia anterior, fechamos a teoria sociológica e escolhemos um "Esquadrão de Elite" enxuto de 6 variáveis com altíssimo poder preditivo: `Q006, Q024, TP_ANO_CONCLUIU, TP_LINGUA, TP_SEXO e Q002`.

Para o TCC, não basta afirmar que essas 6 variáveis são as melhores; nós precisamos provar isso matematicamente para a banca examinadora. A primeira missão de hoje será construir essa prova (A Arena Definitiva de Features).

## 2. Passo 1: A Prova Matemática (Arena de 20 Features)
- **Onde atuar:** Atualização do laboratório no arquivo `notebooks/02_selecao_features_v2.ipynb` (através de um gerador Python).
- **O que fazer:** Vamos colocar **20 features** no modelo (sendo as 6 selecionadas misturadas com 14 outras features conhecidas do ENEM, como internet em casa, tipo de escola, faixa etária, etc).
- **Objetivo do Gráfico:** O resultado desse laboratório será um Gráfico de *Feature Importance* onde ficará visualmente escancarado que as nossas 6 variáveis dominam o topo e que o ganho de informação das outras 14 despenca brutalmente. Essa será a defesa perfeita para justificar a "Navalha de Ockham" (usar um modelo enxuto e barato) no MLOps de Produção.

### Atualização (Executada no Passo 1) - Foco em "Storytelling de Dados"
Para garantir que a banca humana compreenda profundamente o laboratório, inserimos novas células didáticas no notebook V2:
1. **Auditoria de Dados Ausentes (%):** Uma célula dedicada a calcular a porcentagem de nulos (Missing Values) de todas as 20 variáveis.
2. **Análise de Outliers (Boxplot):** Inclusão de um Boxplot (estilo *candlestick*) da Variável Alvo (`NU_NOTA_MT`) mostrando fisicamente a dispersão, a linha média e a existência explícita de "outliers" superiores e inferiores.
3. **Comportamento Sociológico (Variância Zero):** A aplicação severa de exclusão de nulos (`dropna()`) acidentalmente revelou o viés do "Treineiro" (média matemática superior). Confirmou-se estatisticamente que é um erro estratégico excluí-los em produção (quando usarmos apenas 6 features), pois sua alta renda reforça nosso modelo base. 
4. **O "Santo Graal" das Variáveis-Alvo (`TARGET_M2`):** Após automatizar o laboratório para comparar a Inteligência Artificial contra 8 notas diferentes simultaneamente (Matemática, Redação, Humanas, Natureza e Médias), foi provado matematicamente que o **`TARGET_M2` (Média de Matemática + Linguagens)** é o Alvo supremo. Ele blinda o modelo contra o terrível Data Leakage (Vazamento de Dados) gerado pelo "Status da Redação" e maximiza a predição da Renda (`Q006`), pois funde o peso de exatas com o capital cultural da leitura. **O `TARGET_M2` será o Alvo Oficial do MLOps em Produção**.

## 3. Passo 2: Produtização MLOps (O Salto para Produção)
Com a prova matemática garantida para os slides, vamos dar o salto final exigido pelo MBA: abandonar os notebooks e ir para Engenharia de Dados pesada.

- **Onde atuar:** Criação do script de treinamento `src/train.py` e configuração do `docker-compose.yml`.
- **O que fazer:** 
  1. Escrever o script de produção com a lógica limpa e encadeada do modelo.
  2. Subir um contêiner Docker contendo o Servidor do **MLflow**.
  3. Plugar o código Python para fazer o *Tracking* automático no MLflow (registrar hiperparâmetros, RMSE, R² e gravar a versão oficial do modelo).
- **Objetivo:** Mostrar o ciclo de vida completo do MLOps (Rastreabilidade e Model Registry).

---

> **Aviso para a IA Assistente (Instrução Sistêmica):** Ao iniciar a sessão baseada neste documento, o **Passo 1 é mandatório**. Você deve refatorar o gerador do notebook V2 para que ele rode com as 20 variáveis exigidas, gerando o gráfico comparativo definitivo. Só depois de entregar essa prova matemática para o usuário, você pedirá autorização para iniciar o Passo 2 (O MLOps).
