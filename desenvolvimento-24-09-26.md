# Diário de Desenvolvimento - 24/09/2026 (ou Data Lógica Atual)

## O Problema do Drift Semântico nos Dicionários
Durante a checagem das features extraídas para o arquivo `dicionario_features.md`, identificamos uma barreira metodológica enorme para a automação total do pipeline. O INEP não apenas troca os códigos das variáveis (ex: a clássica `Q024` virou `Q021` em 2025), como altera sutilmente a redação da pergunta no dicionário oficial.
Exemplo:
- 2023 (`Q024`): "Na sua residência tem computador?"
- 2025 (`Q021`): "Em sua casa, existe computador/notebook?"

Se o Airflow for programado usando "hardcode" (regras fixas baseadas em chaves), ele quebrará assim que o INEP lançar o ENEM 2026 com mais uma variação do questionário.

## Próximo Passo (Para amanhã)
- **Refatorar o Notebook `04_analise_harmonizacao_historica.ipynb`**.
- Abandonar a tentativa de reconciliação de schemas baseada apenas nos nomes das colunas.
- Implementar uma solução baseada em **Processamento de Linguagem Natural (NLP)**.
- Vamos usar a biblioteca **Sentence Transformers (SBERT)** para transformar as frases das descrições do dicionário em Embeddings (vetores matemáticos).
- O algoritmo deverá calcular a Similaridade de Cosseno (Cosine Similarity) para entender, usando Inteligência Artificial local, que "casa" e "residência" são sinônimos perfeitos, mapeando dinamicamente a `Q021` para o nosso formato canônico `Q024`.
- Essa lógica será a base que, posteriormente, rodará em produção no nosso pipeline (no script `harmonizer.py`).

## Plano de Implementação (Notebook 04 - NLP)
- Fazer o parse/leitura direta do arquivo `dicionario_features.md` gerado no NB 03 para carregar as descrições 'padrão ouro' de 2023 das nossas features de elite.
- Carregar o modelo `SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')`.
- Fazer um loop iterando sobre todos os anos de 2009 a 2025 (ignorando 2023).
- Para cada ano, carregar o dicionário oficial `.xlsx` e extrair todas as variáveis e descrições.
- Computar a similaridade de cosseno (Cosine Similarity) para cada feature base (2023) contra todas as do ano atual no loop.
- Extrair a 'feature campeã' (maior score).
- Consolidar os resultados em um DataFrame mestre mostrando o Drift Semântico de cada coluna ao longo da história.
