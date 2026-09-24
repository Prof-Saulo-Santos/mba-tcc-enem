import json
import os

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Análise de Anomalias Estruturais - Microdados ENEM\n",
                "\n",
                "Este notebook tem como objetivo demonstrar, documentar e provar estatisticamente as anomalias estruturais encontradas na série histórica dos microdados do ENEM (2017-2025). \n",
                "Estas anomalias justificam a necessidade arquitetural de uma **Camada Anticorrupção (Anti-Corruption Layer)** no pipeline de MLOps do TCC."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "import os\n",
                "\n",
                "# Configurando caminhos\n",
                "RAW_DATA_DIR = '../data/raw'"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. O Padrão Monolítico Histórico (Até 2023)\n",
                "Historicamente, o INEP disponibilizou os microdados do ENEM em um único arquivo tabular consolidado (`MICRODADOS_ENEM_XXXX.csv`)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "path_2023 = os.path.join(RAW_DATA_DIR, '2023/dados/MICRODADOS_ENEM_2023.csv')\n",
                "df_2023 = pd.read_csv(path_2023, sep=';', encoding='latin-1', nrows=5)\n",
                "print(f\"Colunas em 2023: {len(df_2023.columns)}\")\n",
                "display(df_2023.head())"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. A Ruptura Estrutural (2024 e 2025)\n",
                "A partir de 2024, o formato monolítico foi abandonado. Os dados passaram a ser entregues particionados em dois arquivos: `PARTICIPANTES` e `RESULTADOS`."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "path_2024_part = os.path.join(RAW_DATA_DIR, '2024/dados/PARTICIPANTES_2024.csv')\n",
                "path_2024_res = os.path.join(RAW_DATA_DIR, '2024/dados/RESULTADOS_2024.csv')\n",
                "\n",
                "df_2024_part = pd.read_csv(path_2024_part, sep=';', encoding='latin-1', nrows=5)\n",
                "df_2024_res = pd.read_csv(path_2024_res, sep=';', encoding='latin-1', nrows=5)\n",
                "\n",
                "print(f\"Colunas Participantes 2024: {len(df_2024_part.columns)}\")\n",
                "print(f\"Colunas Resultados 2024: {len(df_2024_res.columns)}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Comprovação da Reconstrução via JOIN\n",
                "Para injetar os dados no pipeline, a camada anticorrupção deve reconstruir a estrutura monolítica usando a chave primária `NU_INSCRICAO`."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Inner join usando NU_INSCRICAO\n",
                "df_2024_reconstruido = pd.merge(df_2024_part, df_2024_res, on='NU_INSCRICAO', how='inner')\n",
                "\n",
                "print(f\"Colunas após reconstrução (2024): {len(df_2024_reconstruido.columns)}\")\n",
                "display(df_2024_reconstruido.head())"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Análise do Dicionário (Q026 e Q027)\n",
                "Ao longo dos anos, o INEP alterou o questionário socioeconômico. As questões Q026 e Q027, presentes até 2018, foram suprimidas posteriormente. Isso exige contratos de dados para não falhar o pipeline a partir de 2019."
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open('/home/saulo/mba/tcc/enem/notebooks/01_analise_anomalias_estruturais.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print("Notebook gerado com sucesso!")
