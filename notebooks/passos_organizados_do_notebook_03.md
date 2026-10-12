# 🎯 Guia de Estruturação: Engenharia de Features (Notebook 03)

Este documento foi elaborado pela IA com perfil de **Orientador de TCC** após a leitura do notebook atual `03_engenharia_features.ipynb`. O notebook possui análises brilhantes, mas a numeração das seções (ex: 1.19 -> 3 -> 4 -> 5 -> 7) e a lógica sequencial precisam ser ajustadas para garantir rigor acadêmico e evitar que features cruciais (como a Renda Per Capita) sejam acidentalmente descartadas antes do treinamento dos modelos.

Siga rigorosamente a estrutura abaixo para organizar seu notebook de forma lógica e à prova de falhas para a banca avaliadora.

---

## Estrutura Sugerida (Índice Lógico)

### 1. Introdução e Carregamento de Dados
- **Objetivo:** Importar bibliotecas, configurar o ambiente (gráficos) e carregar o dataset purificado (proveniente do Notebook 02 - EDA, focado na "safra" escolhida).

### 2. Engenharia Socioeconômica: Renda Per Capita
- **Objetivo:** Transformar as respostas categóricas sobre renda e moradores em um valor numérico contínuo.
- **Ações:** 
  - Mapear `Q006` (Renda Categórica) para `RENDA_FAMILIAR_EST` (Ponto Médio Numérico).
  - Tratar `Q005` (Moradores) para `Q005_NUM` garantindo evitar divisão por zero.
  - Criar a variável **`RENDA_PER_CAPITA`**.


### 3. Engenharia Socioeconômica: Índice via PCA (Opcional/Complementar)
- **Objetivo:** Comprimir as perguntas de bens (Q007 a Q025) em um único `INDICE_SOCIOECONOMICO_100`.
- **Nota do Orientador:** Esta etapa é linda do ponto de vista estatístico, mas o Passo 4 pode provar que ela é desnecessária. Mantenha no notebook para mostrar à banca seu domínio sobre redução de dimensionalidade. (Não esqueça de adicionar essa coluna ao filtro de features se for usá-la!).

### 4. Justificativa da Parcimônia: Estudo de Ablação
- **Objetivo:** Aplicar a Navalha de Ockham. Provar que o modelo não precisa de 19 variáveis de eletrodomésticos para ter boa performance.
- **Ações:**
  - Comparar o erro (RMSE) do modelo com 1 variável (Q006) vs. 19 variáveis.
  - O ganho marginal (ex: 3%) justificará a eliminação da poluição de dados.
  - **O Veredito:** Manteremos `Q006` (Renda Absoluta) e resgataremos `Q024` (Computador) por causa do seu claro impacto educacional.

### 5. O Laboratório de Targets (Variáveis-Alvo)
- **Objetivo:** Calcular os diferentes cenários que podemos tentar prever.
- **Ações:** Criar simultaneamente: `TARGET_MT`, `TARGET_REDACAO`, `TARGET_LC`, `TARGET_CN`, `TARGET_CH`, `TARGET_M2` (MT + LC), `TARGET_M3` e `TARGET_GERAL`.

### 6. Preparação Definitiva dos Dados (Encoding e Filtro)
- **Objetivo:** Limpar os dados para os Random Forests de validação.
- **Ações:**
  - Aplicar `OrdinalEncoder` nas variáveis que sobraram.
  - 🚨 **MOMENTO CRÍTICO:** Aqui é onde você define a variável `features = [...]`. Você deve reescrever essa lógica para garantir que a sua seleção final do Estudo de Ablação (as variáveis do Q00x, TP_xxx + `RENDA_PER_CAPITA` etc) sejam efetivamente passadas para o DataFrame de Machine Learning (`df_ml`).

### 7. O Problema do Vazamento e a Escolha do Target Oficial
- **Objetivo:** Treinar IAs provisórias para cada um dos 8 Targets e plotar o "Quadro Comparativo de Top 15 Features".
- **Ações e Argumentação:**
  - Denunciar o **Data Leakage (Vazamento de Dados)** monstruoso causado pelo `TP_STATUS_REDACAO` nos alvos de redação e médias gerais.
  - Apresentar o **`TARGET_M2`** (Matemática + Linguagens) como o "Santo Graal", pois ele reflete perfeitamente a classe social (`Q006` e `Q024` dominam o topo) e é 100% blindado contra vazamentos.

### 8. Validação Estatística (Defesa de TCC)
- **Objetivo:** Provar para a banca que o `TARGET_M2` e as variáveis escolhidas são irrefutáveis.
- **Ações:**
  - **Pearson:** Confirmar a alta correlação entre Matemática e Linguagens (prova que a fusão faz sentido).
  - **Permutation Importance:** Provar que a força da Renda (`Q006`) e do Computador (`Q024`) é real e não um viés de cálculo (Gini).
  - **O R² Final:** Testar o "Esquadrão de Elite" de features (apenas 6 variáveis) e extrair o R² médio com Validação Cruzada, provando o alto nível de determinismo social do ENEM.

### 9. Considerações Éticas (Viés Algorítmico)
- **Objetivo:** Concluir o notebook com uma análise social (que é o cerne do projeto). 
- **Ação:** O texto de encerramento destacando que esse modelo deve ser um **"Radar de Políticas Públicas"** e não uma ferramenta de segregação e exclusão.

---

**Como usar este guia:** Se a IA se perder ou o código começar a dar erros inesperados durante nossas alterações, consulte este documento. Ele é o esqueleto narrativo do que precisamos implementar e entregar no notebook final de Engenharia de Features.
