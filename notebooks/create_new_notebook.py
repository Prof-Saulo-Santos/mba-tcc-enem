import json

source_path = "/home/saulo/mba/tcc/enem/notebooks/03_engenharia_features.ipynb"
target_path = "/home/saulo/mba/tcc/enem/notebooks/03_criado_por_IA.ipynb"

with open(source_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Extract code cells
code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']

# We will build a brand new notebook
new_nb = {
    "cells": [],
    "metadata": nb.get('metadata', {}),
    "nbformat": nb.get('nbformat', 4),
    "nbformat_minor": nb.get('nbformat_minor', 5)
}

def add_md(text):
    new_nb['cells'].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [text]
    })

def add_code(source):
    new_nb['cells'].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source if isinstance(source, list) else [source]
    })

# Passo 1
add_md("## 1. Introdução e Carregamento de Dados\n\nEste notebook implementa a engenharia de features focada na safra escolhida (Concluintes 2023), preparando a base de dados refinada para a modelagem preditiva final.")
add_code(code_cells[0]['source']) # Imports

# Passo 2
add_md("## 2. Engenharia Socioeconômica: Renda Per Capita\n\nTransformação das respostas categóricas sobre renda (`Q006`) e moradores (`Q005`) em valores numéricos contínuos para criar a feature `RENDA_PER_CAPITA`.")
add_code(code_cells[1]['source']) # Renda

# Passo 3
add_md("## 3. Engenharia Socioeconômica: Índice via PCA\n\nAplicação de Análise de Componentes Principais (PCA) para comprimir as perguntas de posse de bens materiais (`Q007` a `Q025`) em um único `INDICE_SOCIOECONOMICO_100` contínuo.")
add_code(code_cells[2]['source']) # PCA

# Passo 4
add_md("## 4. Justificativa da Parcimônia: Estudo de Ablação\n\nAplicação da Navalha de Ockham. Treinamos um modelo com 19 variáveis e outro com apenas 1 (Renda) para provar que a complexidade dezenas de colunas não se justifica pelo ganho preditivo marginal.")
add_code(code_cells[3]['source']) # Ablacao

# Passo 5
add_md("## 5. O Laboratório de Targets (Variáveis-Alvo)\n\nCriação de 8 variáveis-alvo diferentes para analisar como o impacto socioeconômico varia dependendo da área de conhecimento.")
add_code(code_cells[4]['source']) # Targets

# Passo 6
add_md("## 6. Preparação Definitiva dos Dados (Encoding e Filtro)\n\nCodificação das variáveis categóricas usando `OrdinalEncoder` e definição explícita do filtro de variáveis preditoras (`features`), garantindo que nossas criações (`RENDA_PER_CAPITA`, etc) não sejam perdidas.")
add_code(code_cells[5]['source']) # Encoding

# Passo 7
add_md("## 7. O Problema do Vazamento e a Escolha do Target Oficial\n\nTreinamento de 8 Random Forests (um para cada Target) para demonstrar o viés da variável `TP_STATUS_REDACAO` e justificar a escolha de `TARGET_M2` (Matemática + Linguagens) como a variável sociológica suprema livre de Data Leakage.")
# The code cell for training the 8 RFs is the 7th code cell (index 6)
add_code(code_cells[6]['source']) 

# Passo 8
add_md("## 8. Defesa Acadêmica e Validação Estatística\n\n### 8.1 Justificativa da Composição\nComprovação estatística (Correlação de Pearson) de que fundir Matemática e Linguagens faz sentido.")
add_code(code_cells[7]['source']) # Pearson

add_md("### 8.2 Validação Rigorosa contra Leakage\nUso de Permutation Importance para confirmar que o poder preditivo da Renda e do Computador é estrutural e não um viés algorítmico do cálculo Gini.")
add_code(code_cells[8]['source']) # Leakage

add_md("### 8.3 Métricas de Performance do Modelo (R²)\nAvaliação do 'Esquadrão de Elite' (as 6 melhores features) provando seu alto poder explicativo isolado no ENEM.")
add_code(code_cells[9]['source']) # R2
add_code(code_cells[10]['source']) # Elite squad print

# Passo 9
add_md("## 9. Considerações Éticas e Conclusão: Viés Algorítmico e Ética em IA\n\n**O Risco do Viés:** O modelo provou matematicamente o determinismo social (Renda + Escolaridade -> Nota). Se usado para seleção, ele agiria como máquina de segregação.\n\n**Uso Ético Sugerido:** Transformar o modelo em um **Radar de Políticas Públicas**. O output da predição deve acionar a distribuição de bolsas de estudo, tutorias e políticas de reparação para os grupos previstos com notas baixas, quebrando a predição da máquina em vez de apenas cumpri-la.")

with open(target_path, 'w', encoding='utf-8') as f:
    json.dump(new_nb, f, indent=1, ensure_ascii=False)

print(f"Notebook {target_path} criado com sucesso!")
