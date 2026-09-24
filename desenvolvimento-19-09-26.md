# Desenvolvimento - 19/09/2026

## 1. Objetivo do Dia: Retomada da Modelagem (EDA e ML)

O objetivo principal hoje é retomar e finalizar a execução do nosso laboratório de Machine Learning focado no ENEM 2023. Iremos executar o notebook `03_eda_modelagem.py` do início ao fim para descobrir qual algoritmo (Regressão Linear, Random Forest, etc.) tem o melhor desempenho na previsão das notas.

---

## 2. Setup do Ambiente: Passos para Execução

Você mencionou o Docker, e é importante fazermos um alinhamento rápido: **neste momento exato do projeto, nós não precisamos do Docker para rodar o Jupyter Notebook**. 

O nosso ambiente atual foi configurado diretamente no seu WSL/Ubuntu usando o gerenciador de pacotes `uv` (ambiente virtual `.venv`). O Docker entrará em cena logo no próximo passo do nosso MBA, quando formos subir o servidor do **MLflow** para rastrear nossos modelos de forma profissional (MLOps). 

Seu comando `docker ps` retornou vazio justamente porque não há nenhum contêiner rodando (o que está perfeitamente correto para o estado atual).

Aqui estão os **passos exatos** que você deve executar no VS Code para rodar o notebook hoje:

### Passo 1: Abrir o Arquivo
- No VS Code, abra o arquivo `notebooks/03_eda_modelagem.py`.

### Passo 2: Selecionar o Kernel (O "Cérebro" do Notebook)
- No canto superior direito do VS Code (logo acima do código do notebook), procure pelo nome da versão do Python ou clique em "Select Kernel" (Selecionar Kernel).
- Vá em **"Python Environments"** (Ambientes Python).
- Selecione o ambiente virtual que criamos para este projeto: **`/home/saulo/mba/tcc/enem/.venv/bin/python`** (ou algo que indique `.venv`).
  > *Isso garante que o notebook vai usar o Pandas, o Scikit-Learn e as demais bibliotecas que instalamos no dia 15.*

### Passo 3: Executar o Laboratório
- **Célula 1 a 4:** Rode uma por uma (basta clicar no ícone de "play" ao lado de cada bloco `#%%` ou usar `Shift + Enter`). A Célula 4 não vai mais travar a sua máquina, pois já implementamos a amostragem aleatória nela.
- **Célula 5:** Esta célula fará a divisão dos dados (Treino e Teste) e preparará as variáveis categóricas.
- **Célula 6 (A Arena):** Aqui os modelos serão treinados. *Atenção: como estamos usando Random Forest, essa célula pode demorar alguns minutos para processar.*
- **Célula 7:** Vai gerar os gráficos finais de comparação (RMSE e R²).

---

## 3. Resultados Obtidos (A Preencher)

*Conforme você rodar o notebook, preencheremos esta tabela com os resultados reais do nosso modelo.*

| Algoritmo | RMSE (Erro Médio) | R² (Poder de Explicação) |
|---|---|---|
| 🐢 Dummy (Linha de Base) | 130.48 pontos | 0.0000 |
| 📐 Regressão Linear | 114.34 pontos | 0.2320 |
| 🌲 Random Forest | 112.05 pontos | 0.2624 |
| ⚡ HistGradientBoosting | **111.91 pontos** | **0.2643** |

> **Interpretação para o TCC:** O **HistGradientBoosting (LightGBM)** foi o grande vencedor da arena, com o menor erro (errando a nota do aluno em ~111 pontos) e o maior R² (explicando 26,4% da variância da nota apenas com as variáveis sócio-demográficas). 
>
> *Nota:* Um R² de 26% pode parecer baixo em outros contextos, mas nas Ciências Sociais e da Educação, explicar um quarto do desempenho de um aluno apenas olhando para "escola, sexo, escolaridade dos pais e renda familiar" (sem nem olhar o histórico acadêmico ou as notas da escola!) é um resultado matematicamente e sociologicamente muito forte!

> **Próximo Passo pós-notebook:** Uma vez escolhido o melhor modelo (HistGradientBoosting), vamos planejar a transição dele para um script de produção (`train.py`) e aí sim usaremos o Docker para subir o nosso MLflow!
