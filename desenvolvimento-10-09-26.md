# Desenvolvimento - 10/09/2026

![Diagrama Arquitetural da Camada de Ingestão e Anticorrupção](/home/saulo/.gemini/antigravity-ide/brain/e2e305d8-0432-477c-a2da-a6a25dcb5d89/diagrama_ingestao_enem_1789042256874.jpg)

## Resumo das Atividades: Camada de Ingestão e Anticorrupção (ENEM)

Neste documento, registro detalhadamente tudo o que construímos no dia de hoje. O objetivo do trabalho foi criar a **Camada de Ingestão** e a **Camada Anticorrupção** do nosso pipeline de MLOps.

Como migramos o projeto do ENADE para o ENEM, nos deparamos com o maior problema de engenharia de dados do INEP: **a partir de 2024, eles dividiram o arquivo único de microdados em dois arquivos separados** (`PARTICIPANTES` e `RESULTADOS`). Além disso, entre 2017 e 2025, colunas como a `Q026` e `Q027` foram extintas por conta da LGPD.

Nosso trabalho foi garantir que o resto do nosso sistema de Inteligência Artificial **não perceba** que essas bagunças aconteceram.

Abaixo, detalho cada passo que executamos seguindo o checklist inicial:

---

### Passo 1: O Módulo `reader.py` (Extração)
**Arquivo modificado:** `src/ingestion/reader.py`

**O que fizemos:**
Criamos a primeira porta de entrada dos dados no nosso sistema. O `reader.py` atua como um adaptador (*Adapter/Façade*) que lê os dados de duas formas diferentes, dependendo do ano que solicitarmos:
1. **Até 2023:** Lê o arquivo único `MICRODADOS_ENEM_XXXX.csv`.
2. **2024 em diante:** Aqui está a mágica. O script busca dois arquivos separados (`PARTICIPANTES` e `RESULTADOS`), os lê e junta os dois em um só.
   
**Por que tomamos essas decisões (Para a Defesa do TCC):**
- **Uso do `pd.concat(..., axis=1)`:** Em vez de usar um "INNER JOIN" (que pesquisa linha por linha para cruzar os dados, demorando muito tempo), usamos a "Concatenação Posicional". Como sabemos que os arquivos do INEP têm as linhas exatamente na mesma ordem, nós apenas "colamos" os arquivos lado a lado. Isso é incrivelmente mais rápido para bases massivas.
- **Engenharia de Software Defensiva (`fail-fast`):** Adicionamos uma barreira que checa se o número de linhas do `PARTICIPANTES` é igual ao do `RESULTADOS` antes de colar. Se divergir, o código explode um erro (`ValueError`) imediatamente. Isso impede que dados misturados e errados alimentem nosso modelo de Machine Learning silenciosamente.
- **Uso de `dtype=str`:** Ao ler o CSV, forçamos que o Pandas interprete tudo como Texto (String). Se deixássemos o Pandas adivinhar, ele cortaria o número "0" do início de inscrições (ex: "0123" viraria "123").

---

### Passo 2: O Módulo `harmonizer.py` (Harmonização Estrutural)
**Arquivo modificado:** `src/ingestion/harmonizer.py`

**O que fizemos:**
Este arquivo é o cérebro da nossa **Camada Anticorrupção (ACL)**. Ele orquestra o processo de padronização temporal. 
1. Mapeamos as colunas do ENEM em constantes Python (`TARGET_COLUMNS`, `INSTITUTIONAL_COLUMNS`, `SOCIOECONOMIC_COLUMNS`).
2. Criamos a função `drop_obsolete_columns` que caça e destroi colunas anômalas.

**Por que tomamos essas decisões:**
- **Defesa LGPD:** As questões de renda `Q026` e `Q027` existiam em 2017 e 2018, mas foram abolidas em 2019. Nós removemos cirurgicamente essas colunas das bases de 2017 e 2018.
- **Coluna Transitória:** A coluna `TP_VERSAO_DIGITAL` que só existe em 2020 foi expurgada.
O resultado? O ano de 2017, 2020 e 2025 terão **exatamente as mesmas colunas**, garantindo paridade total para a base histórica que treinará a I.A.

---

### Passo 3: Testes Unitários Automatizados (`pytest`)
**Arquivo criado:** `tests/unit/test_ingestion.py`

**O que fizemos:**
Escrevemos códigos automatizados que testam se o nosso próprio código está funcionando. Como os arquivos do ENEM pesam Gigabytes, seria muito difícil rodar testes rápidos neles. 

**Por que tomamos essas decisões:**
- Usamos uma técnica chamada **Mock**, que permite "enganar" o Python para que ele ache que está lendo um arquivo gigantesco, quando na verdade passamos um arquivo minúsculo criado ali na hora com 3 linhas (só na memória).
- Escrevemos dois testes: um provando que as colunas são somadas corretamente e as duplicadas removidas, e outro provando que o erro `ValueError` é ativado com sucesso caso os arquivos tenham tamanhos diferentes.

---

### Passo 4: O Script de Validação Prática (*End-to-End*)
**Arquivo criado:** `scripts/validate_ingestion.py`

**O que fizemos:**
Para provar na prática (e para a sua banca) que a arquitetura inteira está operante, criamos um script de simulação definitiva. Adicionamos aos nossos scripts o parâmetro `**kwargs` para permitir ler só 5 linhas (`nrows=5`) para os testes não consumirem memória do computador.

**Como o script funciona:**
1. Ele cria arquivos CSV falsos simulando a antiga estrutura de 2023 (1 arquivo) e a nova de 2024 (2 arquivos).
2. Ele aciona o `harmonizer.py` que, por debaixo dos panos, entende os anos e chama o `reader.py` apropriado.
3. Ele pega o *DataFrame* (Tabela) de 2023 gerada e compara a lista de colunas com a de 2024.
4. **Resultado:** Ao executarmos o script no terminal, ele imprimiu uma mensagem de SUCESSO afirmando que as colunas das duas bases diferentes se tornaram idênticas. A barreira funcionou perfeitamente.

---

### Conclusão do Dia
Finalizamos toda a etapa de Extração (E) e a etapa 1 da Transformação (T1). Nossos dados agora estão lidos, unificados e com o mesmo formato, não importando de qual ano eles vieram. O pipeline é imune à cisão ocorrida no INEP em 2024. O sistema está pronto para a etapa seguinte (Validação via Contratos de Dados).
