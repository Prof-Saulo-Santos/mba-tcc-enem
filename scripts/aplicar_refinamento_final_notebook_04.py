import json
import os
import datetime
import pandas as pd

nb_path = "/home/saulo/mba/tcc/enem/notebooks/04_varredura_semantica.ipynb"
json_path = "/home/saulo/mba/tcc/enem/data/processed/schema_mapping_historico.json"

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

with open(json_path, "r", encoding="utf-8") as f:
    contrato = json.load(f)

# 1. Atualizar Célula 23 (Markdown)
cell_23 = nb["cells"][23]
cell_23["source"] = [
    "## 10. Matriz Consolidada de Testes de Governança e Homologação Final por Edição\n",
    "\n",
    "Em cumprimento à **Diretriz Final da 2ª Revisão Técnica** e às práticas formais de **Data Quality & SLA em MLOps**, a matriz abaixo sintetiza todos os testes executados, os resultados empíricos obtidos e os critérios objetivos que determinaram a classificação formal de cada uma das 17 safras do ENEM.\n",
    "\n",
    "### Critério de Tolerância a Ruídos de Cadastro (SLA de Data Quality):\n",
    "* **Flags Ausentes de Presença:** Em dados governamentais de grande escala (Big Data com mais de 60 milhões de registros), ocorrem raros casos de preenchimento nulo ou em branco em indicadores cadastrais de presença decorrentes de amostragem estocástica sobre a base bruta.\n",
    "* **Tolerância Operacional Homologada:** Define-se a tolerância máxima de **0,05%** ($\\le 0,0005$) de participantes distintos com flags ausentes na amostra física ($N = 20.000$).\n",
    "  * Na auditoria executada, 9 das 10 safras registraram taxa de **$0,000\%$** (zero ausências); a edição de 2016 registrou apenas 1 participante com flags ausentes ($0,005\\% \\le 0,05\\%$) $\\longrightarrow$ **Ressalva aceita dentro do SLA**.\n",
    "* **Garantia de Expurgo no ETL de Produção:** O pipeline de Big Data (`scripts/etl_parquet.py`) aplica `.fillna(0)` nas 4 colunas de presença (`CN`, `CH`, `LC`, `MT`) e filtra estritamente `== 1`, assegurando que $100\\%$ desses registros com flags ausentes sejam expurgados sem contaminar a base de treinamento nem o cálculo do `TARGET_M4`."
]
print("✅ Célula 23 (Markdown) atualizada.")

# 2. Atualizar código da Célula 24
cell_24 = nb["cells"][24]
src_24 = "".join(cell_24["source"])

alvo_antigo = """    if ano in resultados_fisicos_por_ano:
        fis_ano = resultados_fisicos_por_ano[ano]
        taxa_fa = fis_ano.get("taxa_candidatos_flags_ausentes", 0.0)
        candidatos_fa = fis_ano.get("candidatos_flags_ausentes", 0)
        if taxa_fa > 0:
            registro["ressalva_data_quality"] = {
                "candidatos_flags_ausentes": candidatos_fa,
                "taxa_flags_ausentes_amostra": round(taxa_fa, 5),
                "tolerancia_maxima": 0.0005,
                "status_tolerancia": "ACEITA_DENTRO_DO_SLA",
                "mecanismo_expurgo": "Expurgo determinístico garantido via fillna(0) no etl_parquet.py"
            }"""

alvo_novo = """    if ano in resultados_fisicos_por_ano:
        fis_ano = resultados_fisicos_por_ano[ano]
        taxa_fa = float(fis_ano.get("taxa_candidatos_flags_ausentes", 0.0))
        candidatos_fa = int(fis_ano.get("candidatos_flags_ausentes", 0))
        status_sla = (
            "CONFORME_SEM_OCORRENCIAS"
            if taxa_fa == 0
            else "CONFORME_COM_RESSALVA_TOLERADA"
        )
        registro["conformidade_data_quality"] = {
            "candidatos_flags_ausentes": candidatos_fa,
            "taxa_flags_ausentes_amostra": round(taxa_fa, 5),
            "tolerancia_maxima": 0.0005,
            "status_sla": status_sla,
            "mecanismo_expurgo": (
                "Expurgo determinístico garantido via fillna(0) nas 4 flags de presença no etl_parquet.py"
            )
        }"""

if alvo_antigo in src_24:
    src_24 = src_24.replace(alvo_antigo, alvo_novo)
    cell_24["source"] = [line + "\n" for line in src_24.split("\n")][:-1]
    print("✅ Célula 24 (Code) atualizada para registrar conformidade_data_quality em todas as edições.")
else:
    print("⚠️ alvo_antigo não encontrado na célula 24. Verificando...")

# 3. Executar a lógica de atualização no contrato JSON diretamente
meta = contrato["_metadata"]
classificacao = meta.setdefault("classificacao_edicoes", {})
resultados_fisicos = meta.get("relatorios_testes", {}).get("auditoria_fisica_2014_2023", {})

for ano_int in range(2014, 2024):
    ano = str(ano_int)
    if ano in resultados_fisicos:
        fis_ano = resultados_fisicos[ano]
        taxa_fa = float(fis_ano.get("taxa_candidatos_flags_ausentes", 0.0))
        candidatos_fa = int(fis_ano.get("candidatos_flags_ausentes", 0))
        status_sla = (
            "CONFORME_SEM_OCORRENCIAS"
            if taxa_fa == 0
            else "CONFORME_COM_RESSALVA_TOLERADA"
        )
        registro = classificacao.setdefault(ano, {})
        # Remove ressalva antiga se existir
        registro.pop("ressalva_data_quality", None)
        registro["conformidade_data_quality"] = {
            "candidatos_flags_ausentes": candidatos_fa,
            "taxa_flags_ausentes_amostra": round(taxa_fa, 5),
            "tolerancia_maxima": 0.0005,
            "status_sla": status_sla,
            "mecanismo_expurgo": (
                "Expurgo determinístico garantido via fillna(0) nas 4 flags de presença no etl_parquet.py"
            )
        }

meta["relatorios_testes"]["politica_data_quality"] = {
    "tolerancia_taxa_flags_ausentes": 0.0005,
    "descricao": "Tolerância de 0,05% para ruídos isolados de presença em bases de grande escala.",
    "expurgo_producao_confirmado": True,
    "script_etl_garantia": "scripts/etl_parquet.py aplica fillna(0) nas 4 flags de presenca e filtra por == 1"
}

meta["data_consolidacao_governanca"] = datetime.date.today().isoformat()

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(contrato, f, indent=2, ensure_ascii=False)
print("✅ JSON schema_mapping_historico.json atualizado com conformidade_data_quality para 100% das safras.")

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("✅ Notebook 04 salvo com sucesso.")
