import json

path = '/home/saulo/mba/tcc/enem/notebooks/01_analise_anomalias_estruturais.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Clear outputs
for cell in nb['cells']:
    if 'outputs' in cell:
        cell['outputs'] = []
    if 'execution_count' in cell:
        cell['execution_count'] = None

# Modify Cell index 6 (Markdown) and 7 (Code) for the Positional Merge
nb['cells'][6]['source'] = [
    "## 3. Comprovação da Reconstrução Posicional\n",
    "A maior anomalia de 2024 é que o arquivo `RESULTADOS` **NÃO possui** a chave primária `NU_INSCRICAO`, apenas um `NU_SEQUENCIAL`.\n",
    "No entanto, as bases possuem exatamente a mesma quantidade de linhas (4.332.945 registros). O INEP fragmentou a base horizontalmente, exigindo um `concat` posicional em vez de um `merge` relacional."
]

nb['cells'][7]['source'] = [
    "# Concatenação posicional (horizontal)\n",
    "df_2024_reconstruido = pd.concat([df_2024_part, df_2024_res], axis=1)\n",
    "# Removendo colunas duplicadas que existam em ambos (ex: NU_ANO)\n",
    "df_2024_reconstruido = df_2024_reconstruido.loc[:, ~df_2024_reconstruido.columns.duplicated()]\n",
    "\n",
    "print(f\"Colunas após reconstrução (2024): {len(df_2024_reconstruido.columns)}\")\n",
    "display(df_2024_reconstruido.head())"
]

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)
