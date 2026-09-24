# Resumo Analítico dos Notebooks (Auditoria Pré-Dissertação)

Com a decisão de migrar o TCC para uma arquitetura de Big Data com Airflow e Parquet (10 anos de histórico), é prudente revisarmos os artefatos exploratórios criados até aqui. Abaixo está o inventário dos notebooks presentes na pasta `notebooks/` e a recomendação estratégica para a sua dissertação.

---

### 1. `01_analise_anomalias_estruturais.ipynb`
**O que faz:** Atua como um grande "Dicionário de Dados" interativo. Ele mapeia as colunas do INEP (Demográficas, Escolares, Socioeconômicas e Notas) e explica a utilidade de variáveis como `Q001`, `Q002`, `TP_SEXO`, etc.
**Status:** 🟡 **Manter como Referência (Opcional)**
**Justificativa:** É um excelente anexo para a sua dissertação caso a banca questione de onde saíram os significados das siglas do INEP. No entanto, ele não roda modelos pesados. Se o seu TCC escrito já contiver a tabela de variáveis, este notebook pode ser arquivado no futuro.

### 2. `02_selecao_features.ipynb` e `02_selecao_features_v2.ipynb`
**O que fazem:** O coração da sua defesa matemática. Eles provam, através do *Gini Importance* e *Permutation Importance*, que o "Esquadrão de Elite" de 6 variáveis socioeconômicas e demográficas possui poder preditivo esmagador em relação a outras 14 variáveis. Documentam também a escolha do `TARGET_M2` para evitar *Data Leakage*.
**Status:** 🟢 **Manter Ambos (Vital)**

**Análise Comparativa Crítica (Diferença entre V1 e V2):**
Os dois notebooks usam **targets diferentes** e isso gera uma conclusão metodológica importante para a dissertação:

| Feature | V2 (`NU_NOTA_MT` — Matemática pura) | V1 (`TARGET_M2` — MT+LC combinado) |
|---|---|---|
| `Q006` (Renda) | 🥇 1º (0.511) | 🥇 1º (0.513) |
| `Q024` (Computador) | 🥈 2º (0.096) | 🥈 2º (0.110) |
| `TP_SEXO` | **5º (0.030)** | **12º (0.013)** |

**Conclusão:** Quando usamos Matemática pura como target (V2), `TP_SEXO` sobe para a 5ª posição, revelando um viés de gênero forte na nota de Matemática. Porém, ao combiná-la com Linguagens (`TARGET_M2`, no V1), `TP_SEXO` despenca para a 12ª posição (0.013), abaixo do limiar de relevância. Isso prova que o `TARGET_M2` é um alvo **mais justo e menos enviesado demograficamente**, pois o capital cultural de Linguagens compensa o viés de gênero de Matemática. Manter ambos os notebooks é estratégico para narrar essa evolução de raciocínio na dissertação.

### 3. `03_analise_harmonizacao_historica.ipynb`
**O que faz:** Faz a auditoria cega dos cabeçalhos de 2009 a 2023 para detectar *Schema Drift*.
**Status:** 🟢 **Manter (Vital)**
**Justificativa:** Acabamos de criá-lo e ele é o pilar metodológico que justifica o corte temporal da "Era de Ouro" (2014-2023). Mostra maturidade em Engenharia de Dados.


---

### Resumo da Ação Sugerida
Para mantermos o repositório limpo e alinhado com o que você vai relatar na dissertação (A pipeline MLOps Definitiva), **sugiro a exclusão do `03_eda_modelagem.ipynb`**. Os notebooks `01`, `02` e `03_harmonizacao` formam a trilogia perfeita de exploração que antecede o nosso ETL final.
