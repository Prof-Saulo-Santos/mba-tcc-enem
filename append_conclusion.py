import nbformat as nbf

notebook_path = 'notebooks/02_selecao_features.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

md_conclusion = """### 🏆 Conclusão Oficial: A Escolha do TARGET_M2

Se olharmos friamente para os números do quadro acima, um olho leigo poderia argumentar que o `TARGET_REDACAO` é o melhor alvo de todos, já que a sua principal variável possui um score Gini absurdo de **0.634**. No entanto, isso é uma **miragem matemática** conhecida como **Data Leakage (Vazamento de Dados)**.

Vamos analisar os 3 principais competidores:

1. **A Miragem (`TARGET_REDACAO`):** A variável que supostamente "prevê" a redação com 0.634 de precisão é o `TP_STATUS_REDACAO`. O status da redação (Em Branco, Cópia, Anulada) é uma nota dada pelo corretor *meses depois* da prova. Usá-la para prever o futuro é uma trapaça algorítmica. Um modelo não pode espiar o gabarito do corretor para tentar adivinhar a nota do aluno. Portanto, as métricas da Redação são artificialmente infladas por fraude estatística.

2. **O Alvo Honesto (`TARGET_MT` - Matemática):** A Matemática é livre de vazamentos (o status da redação cai para a irrelevância do Top 8). Aqui, vemos a Renda (`Q006`) brilhar com **0.511** de peso. Matemática mede a capacidade analítica dura, algo violentamente influenciado pela classe social (pagamento de cursinhos, tutores particulares).

3. **O Santo Graal (`TARGET_M2` - Média Matemática + Linguagens):** Ao fundirmos a Matemática com Linguagens, nós unimos as habilidades de Exatas com o **Capital Cultural** (hábito de leitura, acesso a idiomas estrangeiros). O resultado? A Renda (`Q006`) atinge seu poder máximo de predição (**0.513**) e a posse de Computador (`Q024`) salta para o 2º lugar absoluto (**0.110**). Tudo isso mantendo o modelo blindado contra o vazamento de dados da Redação.

**Veredito:**
A média de Matemática + Linguagens (`TARGET_M2`) é a métrica sociológica suprema. Ela destila perfeitamente o impacto do poder aquisitivo no desempenho do aluno, sem recorrer a trapaças de avaliação futura. **O `TARGET_M2` será o nosso Alvo Oficial para a Inteligência Artificial em Produção.**"""

# Adiciona a célula no final
nb.cells.append(nbf.v4.new_markdown_cell(md_conclusion))

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Célula de conclusão adicionada com sucesso!")
