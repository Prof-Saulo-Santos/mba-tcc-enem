# Diário de Desenvolvimento: 22 de Setembro de 2026

## O Ponto de Inflexão: Do Laboratório para a Engenharia de Dados em Larga Escala

Hoje realizamos um pivot arquitetural crítico para garantir a defesa acadêmica do TCC, respondendo diretamente às exigências do parecer técnico da banca. O parecer apontou que a tese terminava abruptamente sem a implementação prática dos modelos em larga escala. 

Para resolver isso, decidimos que o pipeline de MLOps não será rodado em uma base pequena ou de um único ano. Faremos a **Consolidação Histórica** do ENEM, o que exigirá uma etapa pesada de Engenharia de Dados (Big Data).

### 1. A Estratégia de Tempo (Out-of-Time Validation)
- **O Passado (Treino/Validação):** Anos de 2009 a 2023. Serão utilizados para treinar o `RandomForest` e provar a robustez socioeconômica ao longo das décadas.
- **O Futuro (Simulação de Produção):** Anos de 2024 e 2025. Serão mantidos intocados até a etapa de orquestração com o **Apache Airflow**, simulando dados novos chegando em tempo real para o modelo fazer a inferência live.

### 2. O Problema da Deriva de Esquema (Schema Drift)
Uma tentativa ingênua seria apenas concatenar os CSVs do INEP de 2009 a 2023. No entanto, mapeamos que o Dicionário de Dados do INEP muda consideravelmente (Schema Drift). Colunas mudam de nome, tipos de dados se alteram e as opções de respostas socioeconômicas mudam.

**Solução - Auditoria de Harmonização Histórica:**
Criamos a estrutura para o notebook `03_analise_harmonizacao_historica.ipynb`. A missão dele é varrer o cabeçalho dos arquivos brutos antigos e cruzar com o nosso *Esquadrão de Elite* de variáveis (`Q006`, `Q024`, `TP_ANO_CONCLUIU`, etc).
- **Regra Defensiva:** Se um ano apresentar *Schema Drift* nas variáveis vitais de forma irreversível, nós **descartaremos o ano inteiro** da base. É muito melhor justificar metodologicamente um corte de escopo do que usar imputações estatísticas falhas que destruiriam a credibilidade da tese.

### 3. A Ferramenta de Big Data
Descobrimos que abrir 15 anos de ENEM no Pandas causaria estouro de memória (OOM). A solução arquitetural será:
- Extrair apenas as colunas vitais de cada ano.
- Salvar no formato ultracompacto `.parquet`.
- Ler a pasta inteira simultaneamente usando ferramentas modernas durante o MLflow.

### Status Atual
- O script `scripts/download_microdados.sh` foi atualizado para varrer os anos a partir de 2009.
- O script gerador `scripts/gerar_auditoria.py` está pronto para criar a auditoria cega dos esquemas.
- **Ação Pendente para a Próxima Sessão:** Rodar o script de download para capturar os anos antigos, em seguida executar `gerar_auditoria.py` e abrir o notebook de análise de harmonização para decidirmos de forma definitiva a linha de corte dos anos. Em seguida, iniciamos a conversão de fato para Parquet e o MLOps com Docker.
