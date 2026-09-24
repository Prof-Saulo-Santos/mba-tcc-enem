import nbformat as nbf

notebook_path = 'notebooks/02_selecao_features.ipynb'

# Lê o notebook
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

new_cells = []
for cell in nb.cells:
    if cell.cell_type == 'code' and 'pd.DataFrame({' in cell.source and 'df.isna().sum().values' in cell.source:
        # Modifica o código para adicionar a coluna de percentual
        new_source = cell.source.replace(
            "'Nulos': df.isna().sum().values\n})",
            "'Nulos': df.isna().sum().values,\n    '% Nulos': (df.isna().sum().values / len(df) * 100).round(2)\n})"
        )
        cell.source = new_source
        new_cells.append(cell)
        
        # Cria a célula Markdown explicativa
        markdown_text = """### ⚠️ Análise de Nulos e Decisão de Exclusão

Como podemos observar na tabela acima, existem grupos de variáveis (features) com um número gigantesco de células nulas (vazias). 

**Principais ofensores:**
- Variáveis de deficiência/necessidades especiais (ex: `IN_BAIXA_VISAO`, `IN_CEGUEIRA`, `IN_SURDEZ`, etc.) frequentemente possuem mais de 99% de valores nulos, pois a esmagadora maioria dos candidatos não possui essas condições.
- Variáveis específicas de infraestrutura escolar (`TP_DEPENDENCIA_ADM_ESC`, `TP_LOCALIZACAO_ESC`) possuem altíssimo percentual de nulos porque só são respondidas por alunos que ainda estão cursando o ensino médio.

**Motivação para Exclusão (Regra de Ouro em Data Science):**
Quando uma coluna possui excesso de valores nulos (geralmente acima de 30% a 50%), qualquer tentativa de "preencher" esses buracos (Imputação de Dados) usando média ou moda introduzirá um viés massivo e artificial no modelo. Além disso, algoritmos de Machine Learning (como Random Forest ou Gradient Boosting) não lidam bem com lacunas generalizadas.

Portanto, para garantir a saúde estatística do modelo, **excluiremos sumariamente** as variáveis que são predominantemente nulas. Isso evita o vazamento de ruído e foca o aprendizado da IA nos padrões das variáveis robustas socioeconômicas (Q001 a Q025) que possuem 100% de preenchimento."""
        new_cells.append(nbf.v4.new_markdown_cell(markdown_text))
    else:
        new_cells.append(cell)

nb.cells = new_cells

# Salva o notebook
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook atualizado com sucesso!")
