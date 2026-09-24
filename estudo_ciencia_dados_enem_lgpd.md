# Estudo de Ciência de Dados com Microdados Históricos do ENEM e LGPD

## Pergunta

> Voce é um especialista em ciência de dados e machine learning. Eu gostaria de criar um modelo de ciência de dados que fizesse um estudo sobre as bases de dados antigas do ENEM para tentar fazer previsões futuras para os novos ingressantes. É possível fazer isso, ou existe alguma lei LGPD que proíba?

## Resposta

Sim. **É perfeitamente possível desenvolver esse projeto**, e ele pode ser um excelente projeto de Ciência de Dados/ML aplicado à educação. A LGPD **não proíbe a análise dos microdados históricos do ENEM**. O ponto fundamental é **quais dados você utiliza, de onde eles vêm, para qual finalidade e se é possível reidentificar os participantes**.

### 1. O INEP disponibiliza os microdados do ENEM

O INEP mantém atualmente os microdados do ENEM, incluindo séries históricas, contendo informações sobre provas, notas, itens e questionários dos participantes.

Portanto, do ponto de vista de disponibilidade dos dados, é possível construir um estudo longitudinal, por exemplo:

> **ENEM 2015–2025 → identificar padrões históricos → treinar modelos → avaliar capacidade de previsão sobre uma edição posterior.**

Isso é uma aplicação legítima de Data Science.

### 2. O ponto crítico é a anonimização

A própria documentação do INEP informa que os microdados vêm sendo modificados para impedir a identificação dos indivíduos em conformidade com a LGPD.

A LGPD define dados anonimizados como aqueles que não permitem identificar o titular utilizando meios técnicos razoáveis.

É importante distinguir:

**Dado anonimizado ≠ dado apenas sem nome.**

Por exemplo, uma base sem nome ou CPF ainda pode apresentar risco de identificação indireta se uma combinação de atributos permitir identificar uma pessoa.

É justamente por isso que o INEP alterou a forma de disponibilização dos microdados. A divulgação de bases que permitam reidentificação deve observar as exigências da LGPD.

### 3. Isso não impede o projeto

O projeto pode ser estruturado explicitamente em torno dos dados anonimizados disponibilizados pelo INEP.

Um objetivo possível seria:

> Desenvolver modelos de Machine Learning capazes de estimar determinados indicadores de desempenho de futuros participantes do ENEM a partir de padrões observados nas edições anteriores.

É possível investigar, por exemplo:

#### Pergunta 1 — desempenho

> Quais características socioeducacionais estão mais associadas ao desempenho no ENEM?

Modelo:

```text
Características do participante
        ↓
Feature Engineering
        ↓
Modelo ML
        ↓
Previsão de desempenho
```

#### Pergunta 2 — probabilidade de alto desempenho

Por exemplo:

```text
P(nota média > 700)
```

ou:

```text
P(nota matemática > 700)
```

Isso transforma o problema em classificação binária.

#### Pergunta 3 — previsão da nota

É possível tentar prever:

```text
NOTA_MATEMATICA
NOTA_LINGUAGENS
NOTA_HUMANAS
NOTA_NATUREZA
NOTA_REDACAO
```

Nesse caso:

```text
X = características socioeconômicas + educacionais

y = nota
```

Podem ser avaliados modelos como:

- Linear Regression
- Random Forest
- XGBoost
- LightGBM
- CatBoost

### 4. Abordagem temporal

Não é recomendável simplesmente misturar todas as edições do ENEM aleatoriamente em treino e teste.

Uma abordagem metodologicamente mais robusta seria utilizar uma divisão temporal:

```text
2015 ─┐
2016  │
2017  │
2018  │
2019  ├── TREINAMENTO
2020  │
2021  │
2022 ─┘

2023 ─── VALIDAÇÃO

2024 ─── TESTE
```

Posteriormente:

```text
2025
 ↓
"novo ENEM"
 ↓
previsão
```

Isso simula uma situação real:

> "Eu só conheço os dados históricos. Consigo prever o comportamento da próxima geração de participantes?"

Essa estratégia também evita **data leakage temporal** e permite estudar fenômenos como **concept drift** e **dataset shift**.

### 5. Possibilidade de utilizar outras bases educacionais

Uma possibilidade ainda mais interessante é combinar, dentro das condições autorizadas, informações provenientes de diferentes bases educacionais, como:

- ENEM
- Censo Escolar
- Censo da Educação Superior
- ENADE
- SISU

O INEP possui mecanismos específicos para acesso a determinadas bases protegidas ou desidentificadas.

Isso permite estudar uma questão mais ampla:

> **Quais características observadas no ENEM estão associadas à probabilidade de ingresso e/ou trajetória posterior no ensino superior?**

Um fluxo conceitual seria:

```text
             ENEM
              │
              ↓
      desempenho escolar
              │
              ↓
            SISU
              │
              ↓
       ingresso no ES
              │
              ↓
      trajetória acadêmica
              │
              ↓
           ENADE
```

Isso transforma o projeto em uma pesquisa de Data Science aplicada à educação, e não apenas em um exercício de Machine Learning.

### 6. Restrição importante: não tentar reidentificar participantes

Não se deve tentar fazer engenharia reversa da anonimização.

Por exemplo, não seria apropriado tentar descobrir:

```text
ID anonimizado → CPF
ID anonimizado → nome
ID anonimizado → pessoa específica
```

Também é necessário cuidado ao combinar bases.

Por exemplo:

```text
ENEM
+
Censo Escolar
+
SISU
```

pode produzir um conjunto muito mais informativo, mas também pode aumentar o risco de reidentificação.

Portanto, qualquer cruzamento deve ser avaliado sob a perspectiva de privacidade, finalidade, necessidade, segurança e risco de identificação.

### 7. Dados protegidos e ambiente de pesquisa

Existe uma diferença importante entre:

#### Projeto com microdados públicos

```text
INEP
 ↓
microdados anonimizados
 ↓
seu notebook / servidor
 ↓
EDA + ML
```

e:

#### Pesquisa que necessita de dados protegidos

```text
INEP
 ↓
dados desidentificados/protegidos
 ↓
ambiente controlado do INEP
 ↓
pesquisa
```

No segundo caso, é necessário seguir o procedimento de acesso estabelecido pelo INEP.

### 8. Pesquisa e LGPD

A LGPD possui previsão específica para determinadas atividades de pesquisa, incluindo tratamento de dados para estudos e pesquisas por órgãos de pesquisa, acompanhado das salvaguardas apropriadas.

Isso não significa que uma pesquisa possa fazer qualquer coisa com dados pessoais.

Significa que existe base jurídica específica para determinadas atividades de pesquisa, observadas as condições e medidas de proteção aplicáveis.

### 9. Proposta de projeto

Uma proposta de projeto poderia ser:

# ENEM Predict — Predição de Desempenho Educacional

### Objetivo

Investigar, utilizando séries históricas dos microdados do ENEM, quais características socioeconômicas e educacionais possuem maior poder explicativo sobre o desempenho dos participantes e construir modelos capazes de estimar o desempenho de novas coortes.

### Pipeline

```text
                    ┌─────────────────┐
                    │ Microdados ENEM │
                    │ 2015 ... 2025   │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Data Validation │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │      EDA        │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Feature Engineer│
                    └────────┬────────┘
                             ↓
                 ┌───────────┴───────────┐
                 ↓                       ↓
          Regressão                 Classificação
                 ↓                       ↓
        previsão de nota        probabilidade
                 │                       │
                 └───────────┬───────────┘
                             ↓
                    ┌─────────────────┐
                    │ Model Evaluation│
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Explainability  │
                    │ SHAP / Feature  │
                    │ Importance      │
                    └─────────────────┘
```

### Dimensão temporal

```text
             ENEM 2015
                 ↓
             ENEM 2016
                 ↓
             ENEM 2017
                 ↓
                ...
                 ↓
             ENEM 2023
                 ↓
              MODEL
                 ↓
             ENEM 2024
             TESTE
                 ↓
             ENEM 2025
         previsão simulada
```

Assim, o estudo pode responder:

> **O modelo mantém capacidade preditiva quando aplicado a uma nova coorte temporal?**

### 10. Questão ética

É preferível evitar um sistema que rotule individualmente estudantes, por exemplo:

> "Este aluno provavelmente será ruim."

ou:

> "Este aluno tem baixa probabilidade de entrar na universidade."

Uma formulação mais adequada seria:

> **Quais fatores estão associados ao desempenho e como modelos estatísticos podem estimar tendências agregadas de desempenho de novas coortes?**

Caso seja realizada previsão individual, deve-se apresentar a previsão como estimativa estatística, incluindo incerteza, intervalos de previsão e explicabilidade quando apropriado.

## Conclusão

**Sim, o projeto é viável e pode ser um excelente projeto de Data Science.**

A LGPD **não impede o estudo dos microdados anonimizados disponibilizados oficialmente pelo INEP**, desde que o uso respeite as condições de disponibilização, finalidade, segurança e não reidentificação.

| Situação | Avaliação |
|---|---|
| Baixar microdados oficiais atuais do ENEM | ✅ |
| Fazer EDA | ✅ |
| Treinar modelos ML | ✅ |
| Estudar tendências históricas | ✅ |
| Fazer previsão sobre novas coortes | ✅ |
| Publicar métricas agregadas | ✅ |
| Utilizar dados devidamente anonimizados | ✅ |
| Tentar identificar participantes | ❌ |
| Reverter anonimização | ❌ |
| Cruzar bases buscando identificar indivíduos | ❌ |
| Utilizar dados protegidos fora do ambiente autorizado | ❌ |
| Usar características sensíveis sem avaliar as salvaguardas aplicáveis | ⚠️ |

### Avaliação final

Em vez de simplesmente fazer "previsão de nota do ENEM", o projeto pode ser estruturado como uma **pesquisa completa**, contemplando:

1. Hipóteses de pesquisa;
2. Definição das variáveis;
3. Aquisição e validação dos dados;
4. Data cleaning;
5. Análise exploratória;
6. Feature engineering;
7. Estratégia temporal de treinamento e teste;
8. Modelos de regressão e classificação;
9. Métricas de avaliação;
10. Explainability com SHAP e/ou Feature Importance;
11. Análise de viés;
12. Avaliação de concept drift/dataset shift;
13. Análise de privacidade e LGPD;
14. Documentação metodológica;
15. Reprodução dos experimentos.

Isso demonstraria competências muito mais amplas de Data Science do que simplesmente aplicar um algoritmo de Machine Learning a uma base de dados.
