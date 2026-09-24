# Parecer de Banca Examinadora — 21/09/2026

## Identificação

**Natureza:** Parecer acadêmico-metodológico sobre projeto de Ciência de Dados aplicado ao desempenho no ENEM.  
**Tema avaliado:** Seleção do alvo `TARGET_M2` (média das notas de Matemática e Linguagens), prevenção de vazamento de dados, interpretação de importância de variáveis e implicações éticas.  
**Decisão:** **Aprovado com Distinção.**

## Síntese do parecer

O trabalho apresenta uma escolha metodologicamente defensável para o alvo `TARGET_M2`, identifica corretamente a inadequação de `TARGET_REDACAO` diante de vazamento de informação e complementa a seleção de atributos com análise de correlação, importância por permutação e validação preditiva. A conclusão de que fatores socioeconômicos possuem forte poder preditivo deve ser apresentada como associação preditiva no conjunto de dados analisado, e não como demonstração causal ou determinação individual inexorável.

A banca considera que o projeto articula adequadamente ciência de dados, contexto educacional e responsabilidade ética. O uso proposto como mecanismo de apoio e focalização de recursos — e não como ferramenta de exclusão — é coerente com boas práticas de IA responsável.

## Perguntas iniciais da banca

### 1. Há vazamento de dados no alvo `TARGET_REDACAO`?

**Pergunta inicial:** A variável `TP_STATUS_REDACAO` foi produzida durante ou depois da correção e, portanto, estaria disponível no momento real em que se deseja prever a nota? Caso esteja, ela contém informação pós-evento que invalida a avaliação preditiva?

**Resposta do candidato:** O status da redação — por exemplo, em branco, cópia ou anulada — é definido após a realização da prova e sua correção. A alta importância observada para `TP_STATUS_REDACAO` no modelo de redação representa informação que não estaria disponível no cenário de previsão prospectiva. Assim, `TARGET_REDACAO` foi rejeitado como alvo oficial.

**Análise técnica da banca:** A resposta está correta. Trata-se de *target leakage*: uso de informação ilegítima, indisponível no momento de decisão, mas relacionada diretamente ao resultado que se pretende prever. A importância muito elevada dessa variável não representa capacidade legítima de generalização; representa um atalho produzido pela estrutura temporal e administrativa do dado. Excluir a variável, ou rejeitar o alvo quando o protocolo experimental não garante sua indisponibilidade, é a decisão metodológica apropriada.

### 2. Por que não usar apenas `TARGET_MT`?

**Pergunta inicial:** Se a nota de Matemática já é livre do vazamento identificado na redação, qual é a justificativa empírica e conceitual para fundi-la com Linguagens no `TARGET_M2`?

**Resposta do candidato:** A análise de Pearson encontrou correlação de **0,632** entre Matemática e Linguagens. O resultado indica associação positiva forte entre os desempenhos, o que sustenta o uso da média como medida composta. A interpretação proposta é que ambas as áreas refletem, em parte, condições compartilhadas de escolarização, recursos materiais e capital cultural.

**Análise técnica da banca:** A correlação de Pearson de 0,632 constitui evidência relevante de associação linear positiva entre as duas notas. Seu quadrado, aproximadamente 0,399, indica que cerca de 39,9% da variância linear de uma medida é compartilhada com a outra; isso não significa que as disciplinas sejam idênticas nem que uma cause a outra. A composição `TARGET_M2` é justificável quando o objetivo declarado é modelar um indicador mais amplo de desempenho em competências quantitativas e linguísticas, desde que a fórmula da média, o tratamento de ausências e a escala das notas sejam explicitados no método.

A banca recomenda manter linguagem prudente: a correlação apoia a validade operacional do construto composto, mas não prova, isoladamente, que um único fator social explique a relação. Para fortalecer a validade de construto, o texto pode informar o intervalo de confiança e o valor-p da correlação, bem como apresentar a distribuição de cada nota e a consistência do resultado em subgrupos ou particionamentos temporais, se disponíveis.

### 3. As variáveis preditoras contêm proxies mecânicos do alvo?

**Pergunta inicial:** Além dos próprios targets derivados, as variáveis candidatas de entrada — como `Q006`, `Q024` e itens socioeconômicos — contêm informação de resultado, pós-prova ou alguma codificação que reconstrua mecanicamente `TARGET_M2`?

**Resposta do candidato:** O procedimento de alerta identificou os demais targets, o que era esperado, pois `TARGET_M2` é matematicamente composto por notas relacionadas. Nenhuma variável preditora socioeconômica, como `Q006` ou `Q024`, apareceu no alerta de vazamento. A base preditiva usada no modelo contém apenas variáveis disponíveis antes da prova.

**Análise técnica da banca:** O raciocínio é adequado. Alvos auxiliares ou notas componentizadas não podem ser utilizados como preditores de uma média que elas próprias compõem, pois isso produziria dependência determinística. A ausência de variáveis socioeconômicas no alerta é evidência favorável contra vazamento mecânico. Contudo, a conclusão deve estar condicionada a uma auditoria do dicionário de dados e da linha do tempo de coleta: cada atributo deve ter sua disponibilidade anterior à prova documentada.

A banca recomenda incluir uma tabela de governança de variáveis contendo: nome da coluna, descrição, instante de disponibilidade, justificativa de inclusão, risco de leakage e decisão final. Essa documentação torna o pipeline reprodutível e protege o trabalho contra questionamentos sobre dados pós-evento.

### 4. A importância de `Q006` é robusta ou efeito do viés do Gini?

**Pergunta inicial:** Como evitar que o destaque de `Q006` decorra apenas do viés conhecido da importância por impureza/Gini, especialmente quando há variáveis categóricas com números distintos de categorias?

**Resposta do candidato:** Foi aplicada *Permutation Importance*. Ao embaralhar `Q006`, a performance do modelo sofreu queda de **0,1575**, indicando que a renda possui contribuição preditiva relevante além do resultado obtido pela importância de Gini.

**Análise técnica da banca:** A estratégia é correta e é um ponto forte do trabalho. Importâncias baseadas em redução de impureza podem favorecer atributos com maior cardinalidade ou mais oportunidades de divisão. A importância por permutação mede a perda de desempenho quando a relação entre uma variável e o alvo é destruída no conjunto de avaliação; portanto, é uma validação complementar mais diretamente ligada à utilidade preditiva.

A queda de 0,1575 deve ser interpretada de acordo com a métrica efetivamente usada no código: se a métrica foi R², significa uma redução de 0,1575 ponto de R²; se foi outra função de escore, a unidade deve ser reportada exatamente. Para robustez, a banca recomenda reportar média, desvio-padrão ou intervalo de confiança de múltiplas repetições da permutação, calculadas exclusivamente em dados de teste ou em validação cruzada. Também convém reconhecer que, na presença de atributos fortemente correlacionados, a importância por permutação pode subestimar a importância individual de variáveis substituíveis; logo, ela indica contribuição preditiva condicional ao restante do conjunto de variáveis, não causalidade isolada.

### 5. O modelo apresenta desempenho suficiente e generaliza?

**Pergunta inicial:** Qual é a performance fora da amostra do modelo final e como ela deve ser interpretada no contexto educacional?

**Resposta do candidato:** O modelo apresentou R² médio de aproximadamente **0,29**, usando seis questões socioeconômicas. O resultado foi entendido como expressivo para um fenômeno educacional complexo, no qual diversas causas não observadas — qualidade da escola, práticas pedagógicas, saúde, motivação, contexto familiar e condições do dia da prova — também afetam o desempenho.

**Análise técnica da banca:** Um R² médio próximo de 0,29 indica que o modelo explica aproximadamente 29% da variância observada de `TARGET_M2` no procedimento de avaliação empregado. É um resultado informativo e potencialmente útil para triagem e planejamento, sobretudo porque utiliza poucas variáveis pré-prova. Ainda assim, R² não possui um limiar universal de “bom” ou “ruim”: sua adequação depende da finalidade, do erro tolerável, da comparabilidade com baselines e da estabilidade fora da amostra.

A afirmação de que “quase um terço de tudo que define a nota” deve ser revisada. O R² quantifica variância estatística explicada por um modelo, não a proporção de causas verdadeiras da nota, nem predeterminação individual. A formulação cientificamente apropriada é: “no conjunto e protocolo avaliados, as variáveis socioeconômicas selecionadas explicaram cerca de 29% da variação observada em `TARGET_M2`”.

Para a versão final, devem ser reportados: esquema de separação treino/teste ou validação cruzada; número de folds e repetições; média e dispersão de R²; MAE e RMSE; desempenho de um baseline simples; parâmetros e semente aleatória; e confirmação de que todo pré-processamento foi ajustado apenas no treinamento de cada fold. Essas medidas permitem avaliar generalização, estabilidade e magnitude prática do erro.

## Avaliação da escolha do alvo

O `TARGET_REDACAO` deve permanecer excluído da definição operacional principal se sua modelagem emprega, direta ou indiretamente, informação gerada após a prova, como `TP_STATUS_REDACAO`. A decisão protege a validade temporal do experimento e impede métricas artificialmente infladas.

O `TARGET_MT` é um alvo legítimo para uma análise específica de desempenho quantitativo. Entretanto, o `TARGET_M2`, definido como média de Matemática e Linguagens, é mais apropriado quando a pergunta de pesquisa busca um indicador composto de desempenho acadêmico que reúna dimensões quantitativas e linguísticas.

A banca aprova a escolha de `TARGET_M2` como alvo oficial, condicionada às seguintes definições explícitas no TCC:

- Fórmula exata: `TARGET_M2 = (nota_matematica + nota_linguagens) / 2`, ou outra especificação efetivamente usada.
- Regras para dados ausentes, notas inválidas e registros excluídos.
- Separação inequívoca entre colunas-alvo e colunas preditoras.
- Disponibilidade temporal pré-prova de todas as variáveis de entrada.
- Avaliação do modelo em dados não usados no ajuste.

## Interpretação dos resultados

Os resultados sustentam que renda familiar (`Q006`) e acesso a computador (`Q024`), juntamente com as demais variáveis selecionadas, possuem associação preditiva com o desempenho composto analisado. A convergência entre importância por Gini e importância por permutação fortalece a evidência de que `Q006` acrescenta informação útil ao modelo.

Todavia, o trabalho não deve afirmar que renda “causa”, por si só, a nota nem que 29% do desempenho individual está predeterminado. Modelos observacionais treinados com questionários revelam padrões de associação e capacidade de previsão; inferência causal exige hipóteses adicionais, controle de confundidores, desenho quase-experimental ou experimental e análise específica de causalidade.

A redação recomendada é: “Os resultados evidenciam que indicadores socioeconômicos disponíveis antes da prova são fortes preditores estatísticos de `TARGET_M2` no conjunto analisado. Essa associação é compatível com desigualdades estruturais de acesso a recursos educacionais, mas não autoriza, isoladamente, inferências causais individuais.”

## Ética e uso responsável

A seção ética apresentada é consistente com o risco real de retroalimentação de desigualdades. Um sistema que use renda, escolaridade familiar ou infraestrutura doméstica para selecionar candidatos a vagas, bolsas competitivas ou empregos pode reproduzir desvantagens históricas caso transforme previsão em critério de exclusão.

A aplicação recomendada — um “radar de políticas públicas” — é ética e socialmente mais defensável, desde que o modelo seja usado para ampliar suporte, e não reduzir oportunidades. Exemplos de ações compatíveis incluem oferta de reforço, tutoria, conectividade, acompanhamento psicopedagógico, informação ativa sobre bolsas e direcionamento de recursos às escolas ou estudantes com maior risco estimado.

Para operacionalizar esse uso, o projeto deve prever:

- Proibição explícita de emprego do escore para reprovação, exclusão, seleção universitária, contratação ou redução de direitos.
- Supervisão humana qualificada e possibilidade de contestação das decisões assistidas pelo modelo.
- Avaliação de erros por grupos relevantes, incluindo renda, raça/cor, sexo, região e tipo de escola, conforme disponibilidade e base legal.
- Monitoramento de calibração, taxas de falso positivo e falso negativo, pois um sistema de intervenção não deve deixar de apoiar grupos que mais necessitam.
- Minimização de dados, segurança, controle de acesso, transparência sobre a finalidade e respeito à legislação de proteção de dados aplicável.
- Avaliação de impacto: medir se as intervenções reduzem, ao longo do tempo, as desigualdades de desempenho, em vez de apenas melhorar métricas preditivas.

O mérito ético central do projeto está em propor que a instituição tente “quebrar a predição” por meio de apoio material e pedagógico. Essa perspectiva desloca o algoritmo de instrumento classificatório para instrumento de cuidado e justiça distributiva.

## Limitações reconhecidas

A banca registra como limitações, que devem constar no texto final:

- Correlação e importância de variável não demonstram causalidade.
- O desempenho preditivo pode variar em outros anos, regiões, redes de ensino e grupos demográficos.
- Variáveis socioeconômicas podem capturar efeitos compartilhados com fatores não medidos, tais como qualidade escolar, território, trajetória de aprendizagem e acesso a serviços.
- Métricas globais podem ocultar desempenho desigual entre subgrupos; a avaliação desagregada é indispensável antes de qualquer implantação.
- A previsão de risco é probabilística e não define potencial, mérito, valor ou futuro de qualquer estudante individual.

## Recomendação de ajustes formais

Antes do depósito final, recomenda-se:

1. Inserir a tabela de auditoria temporal e risco de leakage para todas as variáveis.
2. Descrever integralmente o protocolo de validação cruzada e o isolamento de pré-processamento dentro de cada fold.
3. Reportar R², MAE, RMSE, baseline e intervalos de dispersão ou confiança.
4. Reportar a importância por permutação com múltiplas repetições e a métrica usada em sua escala correta.
5. Reformular afirmações causais ou deterministas como associações estatísticas e limitações observacionais.
6. Incluir plano de avaliação de equidade e governança para qualquer uso futuro do modelo.

## Decisão da banca

**APROVADO COM DISTINÇÃO.**

O trabalho demonstra domínio técnico de modelagem preditiva, reconhecimento correto de vazamento de dados, uso complementar de métodos de importância de atributos, reflexão metodológica sobre validade dos resultados e posicionamento ético consistente. A escolha do `TARGET_M2` está aprovada como alvo oficial da pesquisa, pois combina duas dimensões relevantes do desempenho acadêmico e permanece compatível com o requisito de previsão pré-prova, desde que se mantenha a exclusão de atributos pós-evento e a documentação do pipeline.

A distinção é concedida não por transformar correlações em causalidade, mas pela qualidade com que o projeto identifica essa fronteira, quantifica desigualdades preditivas e propõe empregar o conhecimento para orientar suporte educacional. Com os ajustes formais indicados, o texto alcança padrão elevado para um Trabalho de Conclusão de Curso em Ciência da Computação, Sistemas de Informação ou área correlata.

---

**Emitido em:** 21 de setembro de 2026  
**Parecerista:** Professor Doutor — Ciência da Computação, Sistemas de Informação e Inteligência Artificial  
**Assinatura:** ____________________________________
