import json

notebook_path = "/home/saulo/mba/tcc/enem/notebooks/03_engenharia_features.ipynb"
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        src = "".join(cell['source'])
        
        # 1. Intro
        if "# Este notebook está incompleto" in src:
            src = "## 1. Introdução e Carregamento de Dados\n\nEste notebook implementa a engenharia de features focada na safra escolhida (Concluintes 2023)."
            cell['source'] = [src]
            
        # 2. Renda
        elif "#### 1.19 Análise do Questionário Socioeconômico (Q001–Q025)" in src:
            src = src.replace("#### 1.19 Análise do Questionário Socioeconômico (Q001–Q025)", "## 2. Engenharia Socioeconômica: Renda Per Capita")
            cell['source'] = [src]
            
        # 3. PCA
        elif "Nesta etapa, propõe-se a construção de um **Índice Socioeconômico**" in src and "## 3." not in src:
            src = "## 3. Engenharia Socioeconômica: Índice via PCA\n\n" + src
            cell['source'] = [src]
            
        # 4. Ablação
        elif "Excelente linha de raciocínio, Saulo!" in src and "## 4." not in src:
            src = "## 4. Justificativa da Parcimônia: Estudo de Ablação\n\n" + src
            cell['source'] = [src]
            
        # 5. Targets
        elif "## 3. Experimento Automatizado de Variáveis-Alvo (Targets)" in src:
            src = src.replace("## 3. Experimento Automatizado de Variáveis-Alvo (Targets)", "## 5. O Laboratório de Targets (Variáveis-Alvo)")
            cell['source'] = [src]
            
        # 6. Encoding
        elif "## 4. Transformação de Dados (Encoding)" in src:
            src = src.replace("## 4. Transformação de Dados (Encoding)", "## 6. Preparação Definitiva dos Dados (Encoding e Filtro)")
            cell['source'] = [src]
            
        # 7. Vazamento e Alvo Oficial
        elif "## 5. Análise exploratória de potencial preditivo" in src:
            src = src.replace("## 5. Análise exploratória de potencial preditivo das variáveis (Random Forest Automatizado)", "## 7. O Problema do Vazamento e a Escolha do Target Oficial")
            cell['source'] = [src]
            
        elif "### 🏆 Conclusão Oficial: A Escolha do TARGET_M2" in src:
            src = src.replace("### 🏆 Conclusão Oficial: A Escolha do TARGET_M2", "### 7.1 Conclusão Oficial: A Escolha do TARGET_M2")
            cell['source'] = [src]
            
        # 8. Validação Estatística
        elif "## 7. Defesa Acadêmica e Validação Estatística" in src:
            src = src.replace("## 7. Defesa Acadêmica e Validação Estatística", "## 8. Defesa Acadêmica e Validação Estatística")
            cell['source'] = [src]
            
        elif "### 7.1 Justificativa da Composição" in src:
            src = src.replace("### 7.1 Justificativa da Composição", "### 8.1 Justificativa da Composição")
            cell['source'] = [src]
            
        elif "### 7.2 Validação Rigorosa contra Leakage" in src:
            src = src.replace("### 7.2 Validação Rigorosa contra Leakage", "### 8.2 Validação Rigorosa contra Leakage")
            cell['source'] = [src]
            
        elif "### 7.3 Métricas de Performance do Modelo (R²)" in src:
            src = src.replace("### 7.3 Métricas de Performance do Modelo (R²)", "### 8.3 Métricas de Performance do Modelo (R²)")
            cell['source'] = [src]
            
        # 9. Ética
        elif "### 7.4 Considerações Finais: Viés Algorítmico e Ética em IA" in src:
            src = src.replace("### 7.4 Considerações Finais: Viés Algorítmico e Ética em IA", "## 9. Considerações Éticas e Conclusão: Viés Algorítmico e Ética em IA")
            cell['source'] = [src]
            
    elif cell['cell_type'] == 'code':
        # Replace the features filter definition
        src_lines = cell['source']
        new_src_lines = []
        in_features_block = False
        for line in src_lines:
            if line.startswith("features = ["):
                in_features_block = True
                new_src_lines.append("features_base = [\n")
            elif in_features_block and line == "]\n":
                in_features_block = False
                new_src_lines.append("]\n")
                new_src_lines.append("features_engenhadas = ['RENDA_FAMILIAR_EST', 'Q005_NUM', 'RENDA_PER_CAPITA', 'INDICE_SOCIOECONOMICO_100']\n")
                new_src_lines.append("features = features_base + features_engenhadas\n")
            elif in_features_block and line == "]": # in case it doesn't end with newline
                in_features_block = False
                new_src_lines.append("]\n")
                new_src_lines.append("features_engenhadas = ['RENDA_FAMILIAR_EST', 'Q005_NUM', 'RENDA_PER_CAPITA', 'INDICE_SOCIOECONOMICO_100']\n")
                new_src_lines.append("features = features_base + features_engenhadas\n")
            else:
                new_src_lines.append(line)
        cell['source'] = new_src_lines

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Notebook modificado com sucesso.")
