import nbformat as nbf

notebook_path = 'notebooks/02_selecao_features.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

new_cells = []
for i, cell in enumerate(nb.cells):
    # Se encontramos a célula que carrega os dados (que termina com o read_csv)
    if cell.cell_type == 'code' and 'pd.read_csv' in cell.source and 'print(f"Erro:' in cell.source:
        new_cells.append(cell)
        
        # Insere Markdown e Código de Ausentes
        new_cells.append(nbf.v4.new_markdown_cell("## 1.1 Remoção de Candidatos Ausentes\nUm erro clássico de estratégia é analisar os nulos (em branco) de candidatos que sequer compareceram à prova. Alunos ausentes não respondem ao caderno de questões e podem distorcer o nosso percentual de dados nulos. Portanto, a primeira atitude deve ser eliminá-los."))
        
        ausentes_code = """import matplotlib.pyplot as plt

# Identificar alunos presentes em todas as provas objetivas
presencas = ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT']
if all(col in df.columns for col in presencas):
    # 'Presente' = valor 1 em todas as 4 provas objetivas
    presentes_mask = (df[presencas] == 1).all(axis=1)
    
    qtd_presentes = presentes_mask.sum()
    qtd_ausentes = len(df) - qtd_presentes
    
    # Gráfico de Pizza
    plt.figure(figsize=(7, 7))
    plt.pie([qtd_presentes, qtd_ausentes], labels=['Presentes (Em todas)', 'Faltaram em alguma'],
            autopct=lambda p: '{:.1f}%\\n({:,.0f})'.format(p, p * len(df) / 100),
            colors=['#2ecc71', '#e74c3c'], startangle=90, explode=(0, 0.1), shadow=True)
    plt.title("Proporção de Presença no ENEM 2023", fontsize=14, fontweight='bold')
    plt.show()
    
    # Executar a eliminação dos ausentes
    df = df[presentes_mask].copy()
    print(f"Alunos ausentes eliminados. A base agora contém {len(df):,} candidatos 100% presentes.")"""
        new_cells.append(nbf.v4.new_code_cell(ausentes_code))
        continue
        
    # Quando achar a célula de Limpeza Rápida (que já calculava a nota média), removemos o código repetido de ausentes
    if cell.cell_type == 'code' and 'TP_PRESENCA_CN' in cell.source and 'NU_NOTA_MEDIA' in cell.source:
        # Modificar essa célula para calcular apenas a Nota Média (pois já tiramos os ausentes)
        media_code = """# Calcula Nota Média
score_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
df = df.dropna(subset=score_cols)
df["NU_NOTA_MEDIA"] = df[score_cols].mean(axis=1)

print(f"Alunos presentes com nota válida em todas as provas: {len(df)}")"""
        cell.source = media_code
        new_cells.append(cell)
        continue

    # Caso padrão, copia a célula como está
    new_cells.append(cell)

nb.cells = new_cells

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook atualizado com sucesso!")
