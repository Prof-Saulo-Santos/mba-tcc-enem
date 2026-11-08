"""Estágio 2 da DAG Autônoma: Mapeamento Semântico via NLP/SBERT ANTES da Seleção.

Executa a leitura multi-aba do dicionário oficial do INEP (.xlsx) da nova edição
e utiliza o modelo Sentence-Transformers (`paraphrase-multilingual-MiniLM-L12-v2`)
para descobrir dinamicamente quais códigos de colunas correspondem às variáveis
canônicas do Padrão-Ouro 2023 ANTES de abrir o arquivo CSV de microdados.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd

CONTRATO_CANONICO_2023: Dict[str, str] = {
    "Q006": "Qual é a renda mensal de sua família? (Some a sua renda com a dos seus familiares.)",
    "Q005": "Incluindo você, quantas pessoas moram atualmente em sua residência?",
    "Q024": "Na sua residência tem computador? (computador de mesa, microcomputador ou notebook)",
    "Q002": "Até que série sua mãe, ou a mulher responsável por você, estudou?",
    "TP_ANO_CONCLUIU": "Ano de Conclusão do Ensino Médio",
    "TP_LINGUA": "Língua Estrangeira (Inglês ou Espanhol)",
    "TP_SEXO": "Sexo",
    "NU_NOTA_CN": "Nota da prova de Ciências da Natureza",
    "NU_NOTA_CH": "Nota da prova de Ciências Humanas",
    "NU_NOTA_LC": "Nota da prova de Linguagens e Códigos",
    "NU_NOTA_MT": "Nota da prova de Matemática",
    "TP_PRESENCA_CN": "Presença na prova de Ciências da Natureza",
    "TP_PRESENCA_CH": "Presença na prova de Ciências Humanas",
    "TP_PRESENCA_LC": "Presença na prova de Linguagens e Códigos",
    "TP_PRESENCA_MT": "Presença na prova de Matemática",
}


def extrair_dicionario_multiaba(path_excel: Path) -> Dict[str, str]:
    """Extrai {CODIGO_COLUNA: DESCRICAO_TEXTUAL} de todas as abas válidas do dicionário INEP."""
    xls = pd.ExcelFile(path_excel, engine="openpyxl")
    sheets_validas = [
        s
        for s in xls.sheet_names
        if not s.upper().startswith("ITENS") and not s.upper().startswith("LEIA")
    ]
    dicionario_consolidado: Dict[str, str] = {}

    for sheet in sheets_validas:
        df_raw = pd.read_excel(path_excel, sheet_name=sheet, header=None, engine="openpyxl")
        header_idx = next(
            (
                i
                for i, row in df_raw.iterrows()
                if any("NOME" in str(v).upper() for v in row.values)
                and any("DESCRI" in str(v).upper() for v in row.values)
            ),
            None,
        )
        if header_idx is None:
            continue

        df_sheet = pd.read_excel(
            path_excel, sheet_name=sheet, header=header_idx, engine="openpyxl"
        )
        df_sheet.columns = [str(c).strip() for c in df_sheet.columns]

        col_nome = next((c for c in df_sheet.columns if "NOME" in c.upper()), None)
        col_desc = next((c for c in df_sheet.columns if "DESCRI" in c.upper()), None)

        if col_nome and col_desc:
            sub = df_sheet[[col_nome, col_desc]].dropna(subset=[col_nome, col_desc])
            for _, r in sub.iterrows():
                var_name = str(r[col_nome]).strip()
                var_desc = str(r[col_desc]).strip().replace("\n", " ")
                if (
                    var_name
                    and var_desc
                    and var_name not in dicionario_consolidado
                    and not var_name.upper().startswith("NOME")
                    and not var_name.upper().startswith("DADOS")
                ):
                    dicionario_consolidado[var_name] = var_desc

    return dicionario_consolidado


def run_sbert_schema_mapping(
    ingest_report: Dict[str, Any],
    use_live_sbert: bool = True,
    schema_contract_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Executa o pareamento semântico via SBERT sobre o dicionário da edição antes da seleção."""
    project_root = Path(__file__).resolve().parent.parent.parent
    contract_file = (
        Path(schema_contract_path)
        if schema_contract_path
        else project_root / "data" / "processed" / "schema_mapping_historico.json"
    )

    year_str = str(ingest_report["year"])
    dict_path = Path(ingest_report["dictionary_path"])
    dic_ano = extrair_dicionario_multiaba(dict_path)

    if not dic_ano:
        raise ValueError(f"Não foi possível extrair variáveis do dicionário: {dict_path}")

    column_mapping: Dict[str, str] = {}
    similarity_scores: Dict[str, float] = {}
    sbert_mode = "CONTRACT_CACHE"

    if use_live_sbert:
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            base_keys = list(CONTRATO_CANONICO_2023.keys())
            base_descs = [CONTRATO_CANONICO_2023[k] for k in base_keys]

            # Separamos questões do questionário socioeconômico (Q*) das variáveis administrativas
            q_target_keys = [k for k in dic_ano.keys() if k.upper().startswith("Q")]
            q_target_descs = [dic_ano[k] for k in q_target_keys]

            base_embs = model.encode(base_descs, normalize_embeddings=True)
            q_embs = model.encode(q_target_descs, normalize_embeddings=True)
            sim_matrix_q = np.matmul(base_embs, q_embs.T)

            used_q_targets = set()
            for idx, b_key in enumerate(base_keys):
                if b_key.startswith("Q"):
                    scores = sim_matrix_q[idx].copy()
                    # Restrição injetiva 1-para-1 nas perguntas Q*
                    for u_idx, t_k in enumerate(q_target_keys):
                        if t_k in used_q_targets:
                            scores[u_idx] = -1.0
                    best_i = int(np.argmax(scores))
                    best_k = q_target_keys[best_i]
                    best_sim = round(float(scores[best_i]), 4)
                    column_mapping[b_key] = best_k
                    similarity_scores[b_key] = best_sim
                    used_q_targets.add(best_k)
                else:
                    # Variáveis administrativas e de notas mantêm estabilidade nominal se presentes
                    if b_key in dic_ano:
                        column_mapping[b_key] = b_key
                        similarity_scores[b_key] = 1.0

            sbert_mode = "LIVE_SBERT_MINILM_L12_V2"
        except Exception as exc:
            print(f"[SBERT Fallback] Usando contrato pré-homologado devido a: {exc}")

    # Cross-check / Fallback com o contrato auditado schema_mapping_historico.json
    if contract_file.exists():
        with open(contract_file, "r", encoding="utf-8") as f:
            contrato_hist = json.load(f)
        if year_str in contrato_hist:
            for k_can, k_hist in contrato_hist[year_str].items():
                if k_can not in column_mapping:
                    column_mapping[k_can] = k_hist
                    similarity_scores[k_can] = 1.0
                elif k_can.startswith("Q") and column_mapping[k_can] != k_hist:
                    # Prioriza o veredito HITL homologado no contrato canônico
                    column_mapping[k_can] = k_hist

    detected_drifts = {
        k_can: {
            "canonical_2023": k_can,
            "mapped_in_edition": k_dest,
            "cosine_similarity": similarity_scores.get(k_can, 1.0),
            "canonical_description": CONTRATO_CANONICO_2023.get(k_can, ""),
            "edition_description": dic_ano.get(k_dest, ""),
        }
        for k_can, k_dest in column_mapping.items()
        if k_can != k_dest
    }

    return {
        "year": ingest_report["year"],
        "sbert_mode": sbert_mode,
        "dictionary_variables_extracted": len(dic_ano),
        "column_mapping": column_mapping,
        "similarity_scores": similarity_scores,
        "detected_drifts": detected_drifts,
        "drift_count": len(detected_drifts),
    }

