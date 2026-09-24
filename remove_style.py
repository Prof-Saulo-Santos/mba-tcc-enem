import nbformat as nbf

notebook_path = 'notebooks/02_selecao_features.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code' and 'styled_table = df_comparativo.style' in cell.source:
        
        # Substitui a parte do estilo pela exibição simples do dataframe
        old_code = """# Configurando estilo para facilitar a leitura da banca
styled_table = df_comparativo.style.set_caption("Quadro Comparativo: Top 15 Features Mais Importantes por Tipo de Prova")\\
                             .set_properties(**{'text-align': 'left', 'font-size': '13px'})\\
                             .set_table_styles([{'selector': 'caption', 'props': [('font-size', '16px'), ('font-weight', 'bold')]}])

display(styled_table)"""
        
        new_code = """print("\\n*** Quadro Comparativo: Top 15 Features Mais Importantes por Tipo de Prova ***\\n")
display(df_comparativo)"""

        cell.source = cell.source.replace(old_code, new_code)

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Bug de estilo (Jinja2) corrigido no notebook!")
