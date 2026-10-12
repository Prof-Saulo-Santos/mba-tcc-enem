# 🎓 Documento de Transição do Orientador: Projeto TCC ENEM 2023

## 1. Contexto Geral do Projeto
Este projeto tem como objetivo realizar a previsão de notas do ENEM 2023 utilizando técnicas de Machine Learning, com forte rigor acadêmico e sociológico.
A premissa central é entender como variáveis socioeconômicas (Renda, Escolaridade dos pais, Acesso à tecnologia) e demográficas impactam o desempenho dos candidatos no Brasil.

## 2. O que já foi concluído (Resumo do Notebook 02 - EDA)
O notebook `02_eda.ipynb` foi intensamente revisado, otimizado e teve seu "storytelling" acadêmico aprovado. Suas principais conclusões e ações metodológicas foram:
- **Limpeza de Dados:** Foram removidos candidatos ausentes e treineiros (`IN_TREINEIRO = 1`), pois possuem dinâmicas distintas.
- **Estratégia de Safra (Segmentação):** Foi decidido que os modelos preditivos não serão globais. A base será separada em **duas safras distintas** para modelagem: (1) Concluintes 2023 e (2) Demais candidatos. Isso contorna com maestria o problema de valores ausentes estruturais das variáveis de escola (que apenas concluintes preenchem de forma obrigatória).
- **Tratamento de Nulos Focados em ML (MNAR):** Valores nulos nas variáveis administrativas das escolas foram substituídos por "0" (categoria "Não Informado"). Modelos baseados em árvore conseguem extrair sinal preditivo do próprio "ato de não informar". Variáveis geográficas da escola ausentes foram imputadas a partir do local de prova.
- **O Pilar Sociológico (Cohen's d):** Através do cálculo do *Tamanho do Efeito (Cohen's d)*, a Análise Bivariada comprovou estatisticamente a enorme desigualdade de desempenho gerada por Sexo, Raça e Tipo de Escola.
- **Navalha de Ockham no EDA:** Eliminamos dezenas de gráficos redundantes e tabelas de categorias raras. O EDA focou na demografia e na prova da desigualdade. A tarefa de achar qual pergunta socioeconômica importa mais foi delegada para a próxima fase (Algoritmos de Machine Learning).

## 3. Diretrizes para a Inteligência Artificial (Próximo Chat)
No próximo chat, você assumirá a Persona de **Especialista em Ciência de Dados e Orientador de TCC**. O objetivo será revisar, estruturar e validar o código do notebook `03_engenharia_features.ipynb`. 

### O que o Notebook 03 JÁ possui e precisará da sua revisão:
1. **Engenharia de Renda Per Capita:** O Saulo criou uma feature genial que cruza a Renda Familiar Estimada (`Q006`) com o Número de Moradores (`Q005`). Ela foi migrada do EDA e deverá ser a PRIMEIRA célula do notebook 03.
   - *Atenção da IA:* Você deverá ajudar o Saulo a garantir que as colunas recém-criadas (`RENDA_PER_CAPITA` e as originais numéricas) entrem efetivamente no dataset de treinamento do Random Forest, ajustando o filtro de colunas (que hoje só seleciona strings começando em `Q0` ou `TP_`).
2. **Estudo de Ablação (Ablation Study) & Permutation Importance:** Há um código excelente pronto que comprova que usar apenas a Renda (`Q006`) e a Posse de Computador (`Q024`) é tão eficiente quanto usar as 25 perguntas do questionário, justificando a eliminação de ruídos.
3. **Múltiplos Alvos (Multi-Target):** O projeto não fixa apenas uma nota para prever. Foram testados 8 alvos (matemática, redação, médias combinadas).
4. **A Escolha do Alvo Supremo (TARGET_M2):** O estudo registrou no passado a **Média de Matemática + Linguagens** como variável-alvo (Target) definitiva, mas isso deve ser revisto com muito rigor, pois diversas descobertas no notebook 02_eda.ipynb foram descobertas apos a conclusao de que TARGET_M2 como a melhor. 

### Seus Objetivos Práticos com o Aluno:
- **Organização Numérica e Narrativa:** A numeração dos títulos da Engenharia de Features está caótica (pula de 5 pra 7, repete números). Ajude-o a criar um índice lógico.
- **Rigor Anti-Vazamento:** Mantenha o escrutínio sobre o *Data Leakage*. Elogie e aprofunde o raciocínio dele sobre os perigos da variável `TP_STATUS_REDACAO`.
- **Rumo ao XGBoost:** Após definir as features através do Feature Importance do Random Forest, a base estará purificada. O próximo passo do cronograma é treinar o modelo definitivo utilizando o XGBoost.
- **Estilo de Comunicação:** Seja direto, corte redundâncias, preserve os métodos acadêmicos exigidos em bancas de TCC e encoraje o aluno quando ele demonstrar brilhantismo estatístico.
