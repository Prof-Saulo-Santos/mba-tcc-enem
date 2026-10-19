# Conclusões do Notebook 03

## Pergunta de Saulo Santos:

Antes de eu abrir um novo chat, me responda algo que me traz duvidas. No meu entendimento, eu iria trabalhar com o objetivo de fazer a predicao dos targets de MT, CN, CH. LC e REDACAO. Esse objetivo ainda permanece?

---

## Resposta do Orientador (Agente de IA):

Essa é uma dúvida **fundamental** e excelente de esclarecer antes de darmos o próximo passo!

A resposta curta e direta é: **Depende da decisão arquitetural que você deseja defender no seu TCC (1 Modelo Síntese vs. 5 Modelos Especializados)**. 

Os dados que preparamos permitem seguir **qualquer um dos dois caminhos**, mas vamos entender como e por que o projeto convergiu para um **Alvo Unificado (`TARGET_M4`)**, e o que muda se você quiser prever as 5 notas individuais:

---

### 1. Por que o projeto convergiu para um Alvo Síntese (`TARGET_M4`)?

Nos documentos originais de arquitetura do seu projeto ([visao_geral_projeto.md](file:///home/saulo/mba/tcc/enem/visao_geral_projeto.md) e [AGENT.md](file:///home/saulo/mba/tcc/enem/AGENT.md)), o foco da modelagem foi desenhado para prever um **desfecho único consolidado** (originalmente `TARGET_M2`, agora otimizado para `TARGET_M4`). 

Os dois grandes motivos foram:

1. **Rigor Estatístico e Sociológico (Estabilidade do Sinal):**
   * Quando tentamos prever uma prova isolada (como Redação com $R^2 = 0.19$ ou Natureza com $R^2 = 0.24$), há muito ruído específico (o cansaço do aluno no dia, chutes pontuais, o tema da redação).
   * Ao unir as 4 provas no **`TARGET_M4`**, os ruídos individuais se cancelam e o sinal do **determinismo socioeconômico salta para $R^2 = 0.35$**. A banca vê isso como a medição do "Capital Educacional Global" do estudante frente à desigualdade social.
2. **Engenharia de MLOps e Nuvem (Etapas 2 e 3):**
   * No TCC, você vai colocar esse modelo em produção real na **AWS via Docker e FastAPI**, rastreando tudo no **MLflow** e orquestrando no **Airflow**.
   * Gerenciar, empacotar em Docker, monitorar *Data Drift* e fazer deploy de **1 modelo campeão** (`enem.pkl`) na nuvem é o padrão da indústria. Monitorar 5 modelos simultâneos na AWS quintuplica o consumo de memória, os endpoints e o custo de infraestrutura.

---

### 2. Mas o objetivo de prever as 5 notas pode permanecer?

**Sim, com certeza!** Se você ou seu orientador acadêmico tiverem como premissa original que o sistema deve entregar o boletim completo do aluno (prevendo as 5 notas: MT, CN, CH, LC e Redação), nós temos **duas opções estratégicas** para o Notebook 05:

| Estratégia | Como funciona na prática? | Vantagens | Desvantagens |
| :--- | :--- | :--- | :--- |
| **Opção A: Alvo Síntese (`TARGET_M4`)**<br/>*(Arquitetura atual do repositório)* | Treina **1 modelo XGBoost** para prever a nota média geral da TRI (`TARGET_M4`). | • Maior precisão ($R^2 = 0.35$).<br/>• Pipeline de MLOps enxuto e elegante na AWS.<br/>• Fácil de explicar e defender. | Não entrega a nota discriminada de cada matéria na API. |
| **Opção B: Multi-Output ou 5 Modelos**<br/>*(Predição das 5 notas individuais)* | Treina **5 modelos XGBoost** (um para cada prova: MT, LC, CN, CH e RED) ou um regressor Multi-Target. | • Entrega a predição detalhada das 5 notas para o usuário.<br/>• Permite comparar onde o determinismo social pesa mais (ex.: MT pesa mais que LC). | • Redação terá um erro alto ($R^2 = 0.19$).<br/>• A API FastAPI terá que carregar e inferir 5 modelos simultâneos. |

---

### 3. Minha recomendação como seu Orientador de TCC

A forma mais rica e bem avaliada para a banca é **combinar o melhor dos dois mundos**:

1. **No TCC escrito / Notebook 03:** Você mostra o benchmark das 5 provas isoladas e prova matematicamente que o determinismo socioeconômico atua sobre um construto cognitivo unificado (Alfa de Cronbach = 0.865).
2. **No Modelo de Produção (Notebook 05 + API AWS):**
   * **Se o foco for a facilidade de MLOps:** Elegemos o `TARGET_M4` como o modelo oficial de deploy (1 modelo campeão).
   * **Se você faz questão de entregar o boletim com as 5 notas:** Treinamos os 5 modelos no Notebook 05 com MLflow (registrando os 5 experimentos) e a nossa API FastAPI retornará um JSON com as notas de MT, CN, CH, LC, RED e a Média M4!

O que você prefere para o seu trabalho: **focar no modelo campeão do `TARGET_M4`** ou **manter a predição das 5 notas individuais** no treinamento do Notebook 05?
