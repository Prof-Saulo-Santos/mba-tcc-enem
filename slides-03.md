# 📊 Roteiro de Slides: Notebook 03 — Engenharia e Seleção de Features
**Projeto:** TCC MBA em Ciência de Dados / MLOps — Predição de Desempenho no ENEM  
**Autor:** Saulo Santos  
**Foco:** Otimização Sociológica, Batalha de Targets e a Consagração do `TARGET_M4`

---

## 🎯 Slide 1 — Da Exploração à Engenharia: O Desafio da Modelagem

### Mensagem Central
> *"Não alimentamos algoritmos com dados brutos. A Engenharia de Features é o processo deliberado de traduzir teorias sociológicas em grandezas matemáticas contínuas e aplicar a Navalha de Ockham para encontrar o menor conjunto de dados com o maior poder preditivo."*

### Layout Visual Recomendado
* **Lado Esquerdo:** Fluxo de transição: Base Purificada do EDA ($N = 212.386$ concluintes integrais) $\rightarrow$ Laboratório de Features $\rightarrow$ Contrato Canônico de Modelagem.
* **Lado Direito:** Os 3 Pilares Metodológicos da Etapa:
  1. *Engenharia Socioeconômica:* Criação de métricas contínuas de capital econômico familiar;
  2. *Auditoria de Multicolinearidade:* Ablação da redundância de bens de consumo;
  3. *Psicometria e Anti-Leakage:* Homologação empírica do alvo supremo (`TARGET_M4`).

**Mesmo com 100% das redações válidas, a prova de Redação deve ser descartada por três motivos puramente estatísticos e psicométricos:**

1. **Incompatibilidade Metodológica de Escala (TRI vs. TCT)**
As 4 provas objetivas são avaliadas pela Teoria de Resposta ao Item (TRI). A TRI mede o traço latente cognitivo ($\theta$), calibrando a probabilidade de acerto com base em três parâmetros psicométricos matemáticos (dificuldade, discriminação e acerto casual/chute).
A Redação NÃO é TRI. Ela é avaliada pela Teoria Clássica dos Testes (TCT) como uma soma aritmética de 5 competências (de 0 a 200 pontos em degraus de 40 pontos). Somar grandezas de réguas psicométricas totalmente distintas distorce o alvo.

2. **ído de Medição Humana (Measurement Noise)**
A nota da redação depende da avaliação subjetiva de duplas de corretores humanos (o INEP tolera discrepâncias de até 80 a 100 pontos entre corretores antes de chamar um terceiro).
Essa variabilidade de estilo, humor e subjetividade do corretor atua na modelagem como um ruído aleatório (noise) que não tem correlação com a condição socioeconômica do candidato. Em estatística, adicionar uma variável ruidosa a uma média atenua (dilui) o sinal sociológico.

3. **Incompatibilidade de Escala e Distribuição**
* Objetivo (TRI): Estimar a proficiência ($\theta$) em uma escala log-odds contínua de$-\infty$ a $+\infty$ (na prática: aprox. -3.0 a +3.0).
* Redação (TCT): Distribuída em 6 faixas discretas (0, 200, 400, 600, 800, 1000). A função de ativação padrão das árvores (ReLU ou similar) tenderá a "estourar" os valores máximos com frequência, enquanto os valores baixos criarão um "efeito de teto" enviesado.


### Conteúdo dos Tópicos no Slide
* **Dataset Base:** $212.386$ candidatos concluintes com presença integral em todas as 4 provas e redação;
* **Premissa:** Testar empiricamente a hipótese do determinismo social (Bourdieu) com modelos não lineares baseados em árvores;
* **Meta de Engenharia:** Reduzir drasticamente o questionário de 76 perguntas para um "Esquadrão de Elite" parcimonioso sem perda de $R^2$.

### Roteiro de Fala do Apresentador
> *"Senhores membros da banca, ao final do Notebook 02 (EDA), tínhamos uma base perfeitamente purificada de 212 mil concluintes. No Notebook 03, nossa missão não foi simplesmente rodar modelos, mas fazer Ciência de Dados defensável. O objetivo foi desenhar features que capturem o capital cultural e econômico do estudante brasileiro e selecionar, com rigor estatístico, a variável-alvo ideal que represente a capacidade cognitiva real sem os ruídos subjetivos da correção humana."*

---

## 💰 Slide 2 — A Feature Soberana: `RENDA_PER_CAPITA`

### Mensagem Central
> *"A renda bruta familiar é uma ilusão estatística se não for relativizada pelo número de moradores da residência. A verdadeira alavanca educacional no Brasil é a Renda Per Capita familiar."*

### Layout Visual Recomendado
* **Destaque Superior (Fórmula em LaTeX):**
  $$\text{RENDA\_PER\_CAPITA} = \frac{\text{Ponto Médio de } Q006}{\text{Número de Moradores } (Q005)}$$
* **Gráfico Sugerido:** Boxplot ou Gráfico de Linha mostrando a Nota Média crescendo em função dos decis de Renda Per Capita (curva monotônica perfeita).
* **Card de Destaque:** *"Preditor #1 Absoluto em todos os benchmarks de Feature Importance e Permutation Importance."*

### Conteúdo dos Tópicos no Slide
* **Limitação do Dado Bruto:** R$ 3.000 para uma família de 2 pessoas representa um orçamento educacional per capita infinitamente superior ao mesmo valor rateado entre 8 moradores;
* **Tratamento Matemático:**
  * Mapeamento do ponto médio das 17 faixas categóricas de renda (`Q006`: de R$ 0 a R$ 30.000);
  * Conversão numérica e proteção contra divisão por zero no tamanho domiciliar (`Q005`);
* **Impacto no Modelo:** Consolidou-se com a maior taxa de ganho de informação (*Information Gain*) e maior estabilidade preditiva em todas as árvores de decisão.

### Roteiro de Fala do Apresentador
> *"Um dos principais diferenciais da nossa engenharia foi a criação da `RENDA_PER_CAPITA`. Em vez de usar a variável `Q006` pura e isolada, cruzamos o ponto médio financeiro declarado com a quantidade de residentes no lar. Sociologicamente, isso captura a densidade do investimento familiar por estudante. O resultado prático foi inequívoco: essa variável engenhada tornou-se, isoladamente, o preditor número um de todo o nosso sistema preditivo."*

---

## 🪒 Slide 3 — A Navalha de Ockham: Estudo de Ablação dos Bens Materiais

### Mensagem Central
> *"Mais dados não significam mais inteligência. Provamos que 19 perguntas sobre eletrodomésticos adicionam apenas ruído e redundância à renda familiar declarada."*

### Layout Visual Recomendado
* **Tabela Comparativa / Gráfico de Barras Lado a Lado:**
  * Modelo com Questionário Completo (21 features): $R^2 = 0.3546$ | Erro: $65.71$ pts
  * Modelo com Esquadrão de Elite (6 features): $R^2 = 0.3294$ | Erro: $66.98$ pts
* **Callout de Impacto:** *"Economia de 71% das perguntas do questionário com perda desprezível de apenas 7,11% no poder explicativo ($R^2$)."*

### Conteúdo dos Tópicos no Slide
* **O Dilema das Perguntas de Posse (`Q007` a `Q025`):** Geladeira, freezer, micro-ondas, máquina de lavar e aspirador de pó;
* **Multicolinearidade Estrutural:** Coeficiente de correlação de Spearman de até $\rho = 0.62$ com a renda familiar (`Q006`);
* **A Exceção Tecnológica:** A única variável de infraestrutura física resgatada foi a **Posse de Computador (`Q024`)**, que representa ferramenta direta de estudo e inclusão digital, e não mero acúmulo de patrimônio passivo;
* **Vantagem para MLOps:** Questionário mais enxuto para o usuário na API de produção, menor latência de rede e menor custo computacional de inferência.

### Roteiro de Fala do Apresentador
> *"Diante de 19 perguntas sobre bens materiais no questionário, aplicamos o princípio da parcimônia — a Navalha de Ockham. Realizamos um Estudo de Ablação rigoroso: ao descartar quase 70% das perguntas supérfluas e manter apenas a Renda, a Escolaridade e o Computador, o $R^2$ caiu apenas 7,1%. Mostramos à banca que um modelo enxuto e escalável em produção é infinitamente superior a um modelo inflado de dados redundantes que sofre com multicolinearidade."*

---

## ⚔️ Slide 4 — A Arena dos Alvos: Benchmark Multialvo (5-Fold CV)

### Mensagem Central
> *"Não assumimos arbitrariamente o que o modelo deveria prever. Colocamos 10 variáveis-alvo candidatas em uma arena comparativa sob Validação Cruzada de 5 dobras."*

### Layout Visual Recomendado
* **Tabela Oficial do Benchmark:**

| Alvo Avaliado | Descrição Conceitual | $R^2$ Médio (↑) | RMSE Médio (↓) | Erro Relativo ($RMSE/\sigma$) |
| :--- | :--- | :---: | :---: | :---: |
| `TARGET_RD` | Prova de Redação Isolada | $0.1942$ | $130.62$ pts | $0.8976$ |
| `TARGET_CN` | Ciências da Natureza Isolada | $0.2441$ | $63.35$ pts | $0.8694$ |
| `TARGET_CH` | Ciências Humanas Isolada | $0.2941$ | $69.75$ pts | $0.8402$ |
| `TARGET_MT` | Matemática Isolada | $0.3014$ | $92.65$ pts | $0.8358$ |
| `TARGET_LC` | Linguagens e Códigos Isolada | $0.3032$ | $57.14$ pts | $0.8347$ |
| `TARGET_M3` | Média MT + LC + Redação | $0.3050$ | $81.71$ pts | $0.8336$ |
| `TARGET_M5` | Média Geral das 5 Provas | $0.3286$ | $69.04$ pts | $0.8194$ |
| `TARGET_M2` | Média MT + LC (Objetivas Core) | $0.3362$ | $68.42$ pts | $0.8147$ |
| **`TARGET_M4`** | **Média Aritmética das 4 da TRI** | **`0.3467`** | **`66.12` pts** | **`0.8083`** |

### Conteúdo dos Tópicos no Slide
* **Protocolo Experimental:** `HistGradientBoostingRegressor` com K-Fold ($K=5$) estratificado por distribuição de notas;
* **Fenômeno Estatístico:** Quanto mais provas objetivas homogêneas são agregadas, menor o erro relativo e maior o poder de captura do determinismo social ($R^2$ salta de $0.24$ para $0.35$);
* **O Vencedor Incontestável:** **`TARGET_M4`** registrou o maior $R^2$ e o menor erro padronizado entre todas as opções.

### Roteiro de Fala do Apresentador
> *"Essa tabela resume um dos pontos mais densos da nossa pesquisa. Testamos notas individuais e médias compostas. Notem que notas isoladas possuem previsibilidade limitada — Redação tem míseros 19% de $R^2$ e Ciências da Natureza 24%. Porém, à medida que combinamos as provas cognitivas da TRI, o ruído individual se dissipa e o sinal sociológico emerge com força máxima no `TARGET_M4`, alcançando o topo da performance com $R^2$ de quase 35% e o menor erro relativo de toda a arena."*

---

## 🚫 Slide 5 — Por que Descartar a Redação? O Fim do Data Leakage

### Mensagem Central
> *"A prova de Redação é pedagógica e socialmente nobre, mas estatisticamente ruidosa e administrativamente perigosa para um pipeline de MLOps."*

### Layout Visual Recomendado
* **Diagrama Causal / Alerta Vermelho:**
  * Comparativo: $M4$ (sem Redação, $R^2 = 0.3467$) $\longrightarrow$ Inclusão da Redação ($M5$, $R^2 = 0.3286$ — **Queda de Performance!**).
  * Diagrama de Vazamento: `TP_STATUS_REDACAO` $\rightarrow$ Anulação/Nota Zero Administrativa $\rightarrow$ *Data Leakage*.

### Conteúdo dos Tópicos no Slide
1. **Degradação de Desempenho:** A Redação atua como vetor de atenuação de sinal. Sua inclusão derruba a precisão tanto do $M4$ para o $M5$ quanto do $M2$ para o $M3$;
2. **Subjetividade Avaliativa:** Ao contrário das 4 provas objetivas calibradas via Teoria de Resposta ao Item (TRI), a redação depende de dupla correção humana subjetiva;
3. **Blindagem contra Data Leakage:** A anulação de redações (fuga ao tema, folha em branco, cópia) gera zeros artificiais que violam a premissa de aptidão socioeconômica;
4. **Isolamento de Erro:** Sem a redação, o modelo de inferência em produção fica 100% ancorado na escala padronizada e unificada da TRI.

### Roteiro de Fala do Apresentador
> *"Muitos poderiam perguntar: por que não prever a média tradicional de 5 notas que inclui a Redação? A resposta é puramente científica: a prova de Redação derruba o poder preditivo do modelo! A inclusão da redação faz o $R^2$ cair de 0.3467 para 0.3286. Além da subjetividade da correção humana, a redação traz o risco de Data Leakage através da variável de anulação de texto. Ao adotar o `TARGET_M4`, blindamos nosso pipeline contra anomalias administrativas e maximizamos o rigor estatístico."*

---

## 📐 Slide 6 — Validação Psicométrica: Consistência Interna Unidimensional

### Mensagem Central
> *"As 4 provas objetivas medem um mesmo construto cognitivo fundamental. A união no `TARGET_M4` possui respaldo psicométrico internacional."*

### Layout Visual Recomendado
* **Lado Esquerdo — Matriz de Correlação de Pearson entre as Provas:**

| Prova | Natureza (CN) | Humanas (CH) | Linguagens (LC) | Matemática (MT) |
| :--- | :---: | :---: | :---: | :---: |
| **CN** | $1.00$ | $0.68$ | $0.66$ | $0.68$ |
| **CH** | $0.68$ | $1.00$ | $0.76$ | $0.63$ |
| **LC** | $0.66$ | $0.76$ | $1.00$ | $0.60$ |
| **MT** | $0.68$ | $0.63$ | $0.60$ | $1.00$ |

* **Lado Direito — Indicador Psicométrico em Destaque:**
  * **Alfa de Cronbach:** **`\alpha = 0.865`**
  * Classificação: *Alta Consistência Interna / Unidimensionalidade Psicométrica*

### Conteúdo dos Tópicos no Slide
* **Intercorrelação Robusta:** Todas as 4 provas da TRI correlacionam fortemente entre si ($r = 0.60$ a $0.76$);
* **Justificativa Psicométrica:** Um Alfa de Cronbach de $0.865$ ultrapassa com folga o limiar acadêmico de confiabilidade ($> 0.80$);
* **Defesa para a Banca:** Prova matemática de que agregar as 4 notas na média aritmética `TARGET_M4` não é uma arbitrariedade, mas a representação fiel da habilidade geral do candidato na régua da TRI.

### Roteiro de Fala do Apresentador
> *"Para defender o `TARGET_M4` perante uma banca rigorosa, não nos limitamos ao erro do modelo de ML. Fomos buscar na Psicometria a validação do construto. Calculamos o Alfa de Cronbach entre as 4 notas e obtivemos expressivos 0.865! Na literatura psicométrica, qualquer índice acima de 0.80 comprova alta consistência interna. Isso prova que as 4 provas avaliam facetas harmônicas de uma mesma capacidade cognitiva geral, legitimando a agregação."*

---

## 👑 Slide 7 — O "Esquadrão de Elite": As 6 Features Homologadas

### Mensagem Central
> *"Seis variáveis essenciais que resumem o capital econômico, cultural e temporal do estudante brasileiro."*

### Layout Visual Recomendado
* **Gráfico de Barras Horizontais:** *Permutation Importance* decrescente das 6 features homologadas.
* **Tabela Resumo dos Preditores:**

| Feature | Descrição e Interpretação Sociológica | Papel no Modelo |
| :--- | :--- | :---: |
| **`RENDA_PER_CAPITA`** | Renda familiar mensal estimada por morador do domicílio | **#1** (Capital Econômico Supremo) |
| **`Q024`** | Posse de computador (inclusão digital e ferramenta de estudo) | **#2** (Ferramenta de Aprendizado) |
| **`TP_ANO_CONCLUIU`** | Tempo de conclusão do Ensino Médio (frescor acadêmico) | **#3** (Defasagem Temporal) |
| **`TP_LINGUA`** | Escolha de Inglês vs. Espanhol (proxy de capital cultural) | **#4** (Letramento / Segunda Língua) |
| **`TP_SEXO`** | Gênero do candidato (captura assimetrias de MT e LC) | **#5** (Demografia Estrutural) |
| **`Q002`** | Escolaridade da mãe (Capital cultural herdado de Bourdieu) | **#6** (Background Educacional Familiar) |

### Conteúdo dos Tópicos no Slide
* **Blindagem de Seleção:** Uso de *Permutation Importance* sobre conjunto de validação out-of-fold para eliminar o viés de cardinalidade da impureza de Gini;
* **Interpretabilidade Sociológica Clara:** Alinhamento direto com as teorias da sociologia educacional de Pierre Bourdieu (Capital Econômico + Capital Cultural + Tempo);
* **Persistência do Artefato Canônico:** Base salva em `data/processed/enem_2023_features_modelagem.parquet` ($212.386$ linhas $\times$ $8$ colunas).

### Roteiro de Fala do Apresentador
> *"Chegamos assim ao nosso 'Esquadrão de Elite'. Comprovado via Permutation Importance, este sexteto de variáveis une a Renda Per Capita e a posse de computador com o frescor de conclusão do Ensino Médio, a língua estrangeira escolhida, o sexo e a escolaridade materna. Temos aqui uma síntese perfeita entre parcimônia computacional para a engenharia de MLOps e densidade sociológica para a ciência educacional. Este é o dataset final exportado em Parquet que alimenta as etapas seguintes."*

---

## ❓ Perguntas Prováveis da Banca sobre o Notebook 03 (e Respostas Blindadas)

**1. "Por que vocês não utilizaram PCA para juntar as perguntas de bens socioeconômicos?"**
> *Resposta:* "Nós investigamos o PCA na fase exploratória, mas o Estudo de Ablação provou que o ganho marginal de todas as 19 variáveis de bens combinadas era inferior a 3% no erro preditivo. Adotar o PCA adicionaria complexidade arquitetural desnecessária e retiraria a interpretabilidade direta dos coeficientes e SHAP Values. Optamos pela simplicidade elegante da Navalha de Ockham mantendo a Renda Per Capita e o Computador."

**2. "Eliminar a Redação não prejudica a visão holística do aluno?"**
> *Resposta:* "Pedagogicamente sim, mas econometricamente e estatisticamente não. O ENEM utiliza a TRI nas 4 provas objetivas, que possuem propriedades psicométricas de invariância de escala. A Redação é uma nota ordinal somada em 5 competências por duplas de corretores humanos, com forte variância subjetiva ($R^2 = 0.19$). Como o objetivo do modelo é mensurar o determinismo social e prever com precisão na AWS, a inclusão da redação introduziria ruído de medição indesejado."

**3. "O R² de 0.35 não é baixo para um modelo preditivo?"**
> *Resposta:* "Na literatura de Ciências Sociais e Educação, explicar 35% da variância de notas utilizando estritamente 6 dados cadastrais — sem ter acesso ao histórico escolar, notas prévias ou simulados — é um resultado extraordinariamente alto. Prova que mais de um terço do sucesso cognitivo de um concluinte no Brasil é pré-determinado antes mesmo de ele abrir o caderno de provas."
