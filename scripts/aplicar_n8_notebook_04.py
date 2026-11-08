import os
import nbformat

nb_path = 'notebooks/04_varredura_semantica.ipynb'
print(f"Lendo {nb_path}...")

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# 1. Update Cell 15 (Markdown - Seção 8 com discriminação explícita de conjuntos)
cell15_source = """## 8. Exportação do Contrato Canônico de MLOps (`schema_mapping_historico.json`)

Para materializar o pipeline de MLOps de ponta a ponta, eliminar códigos *hardcoded* nos scripts de engenharia de dados e garantir **governança explícita sobre a finalidade de cada edição**, exportamos abaixo o artefato canônico **`schema_mapping_historico.json`**. 

O contrato organiza as safras mapeadas em **dois conjuntos claramente discriminados por finalidade arquitetural**:

1. **Conjunto A — Horizonte de Treinamento e Benchmark (2014 a 2023 — Década de Ouro):**
   * **Status:** `APROVADA` ($100\%$ de equivalência semântica, documental e presença física comprovada nos CSVs brutos).
   * **Finalidade:** Consumido dinamicamente pelo script `scripts/etl_parquet.py` para extração colunar particionada e geração dos datasets de treinamento e validação cruzada do **Notebook 05**.
2. **Conjunto B — Horizonte de Validação Out-of-Time e Produção (2024 e 2025):**
   * **Status:** `PENDENTE_VALIDACAO` (mapeamento semântico resolvido via SBERT, mas aguardando resolução operacional de junção bipartida em 2024 e divulgação das notas oficiais de 2025).
   * **Finalidade:** Congelado como **reserva estratégica para teste cego temporal (*Out-of-Time Validation*)** e esteira de inferência automatizada no **Apache Airflow (Etapa 3)**."""

nb.cells[15].source = cell15_source

# 2. Update Cell 16 (Code - Exportação do Contrato com _metadata e separação dos conjuntos)
cell16_source = """# 8. Geração, Validação Defensiva e Persistência do Contrato de Schema Mapping 
# com Governança Bipartida por Finalidade (Blindagem N3, N4, N7 e N8)
import os
import json
import datetime
import pandas as pd

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
caminho_artefato = os.path.join(PROCESSED_DATA_DIR, 'schema_mapping_historico.json')

# ── 1. Discriminação Explícita dos Dois Horizontes de Governança ──────────────
edicoes_treinamento = [str(ano) for ano in range(2014, 2024) if str(ano) in mapa_schema_completo]
edicoes_oot = [str(ano) for ano in [2024, 2025] if str(ano) in mapa_schema_completo]

schema_producao = {ano: mapa_schema_completo[ano] for ano in (edicoes_treinamento + edicoes_oot)}

print("=" * 80)
print("AUDITORIA DE GOVERNANÇA E DISCRIMINAÇÃO DOS CONJUNTOS DE DADOS")
print("=" * 80)

relatorio_governanca = []

# Validar e auditar conjunto de Treinamento (2014 a 2023)
for ano_treino in edicoes_treinamento:
    mapa = schema_producao[ano_treino]
    assert len(mapa) == 15, f"Erro: apenas {len(mapa)} variáveis mapeadas no ano {ano_treino}"
    assert len(set(mapa.values())) == 15, f"Erro: colisão detectada no ano {ano_treino}"
    relatorio_governanca.append({
        'Edição': ano_treino,
        'Grupo / Horizonte': 'Conjunto A (Década de Ouro)',
        'Status de Homologação': '✅ APROVADA',
        'Finalidade Arquitetural': 'Treinamento e Validação Cruzada (Note 05)',
        'Presença Física CSV': '✅ 100% Comprovada'
    })

# Validar e auditar conjunto de Reserva Out-of-Time (2024 e 2025)
for ano_oot in edicoes_oot:
    mapa = schema_producao[ano_oot]
    assert len(mapa) == 15, f"Erro: apenas {len(mapa)} variáveis mapeadas no ano {ano_oot}"
    assert len(set(mapa.values())) == 15, f"Erro: colisão detectada no ano {ano_oot}"
    relatorio_governanca.append({
        'Edição': ano_oot,
        'Grupo / Horizonte': 'Conjunto B (Reserva de Produção)',
        'Status de Homologação': '⏳ PENDENTE_VALIDACAO',
        'Finalidade Arquitetural': 'Validação Temporal Out-of-Time / Airflow (Etapa 3)',
        'Presença Física CSV': '⏳ Pendência Operacional (Bipartido/Notas)'
    })

df_gov = pd.DataFrame(relatorio_governanca)
display(df_gov)

# ── 2. Montagem do Artefato Estruturado com Metadados e Retrocompatibilidade ──
contrato_mlops = {
    "_metadata": {
        "descricao": "Contrato Canônico de MLOps - Harmonização Semântica dos Microdados ENEM",
        "versao_contrato": "2.1 (Governança Bipartida por Finalidade)",
        "data_homologacao": datetime.date.today().isoformat(),
        "horizontes": {
            "treinamento_benchmark": {
                "periodo": "2014-2023 (Década de Ouro)",
                "edicoes": edicoes_treinamento,
                "status_homologacao": "APROVADA",
                "finalidade": "Treinamento Supervisionado, Validação Cruzada K-Fold e Benchmark de Modelos (Notebook 05)",
                "auditoria_fisica": "100% comprovada nos microdados brutos CSV"
            },
            "reserva_validacao_oot": {
                "periodo": "2024-2025 (Reserva de Produção)",
                "edicoes": edicoes_oot,
                "status_homologacao": "PENDENTE_VALIDACAO",
                "finalidade": "Validação Temporal Cega (Out-of-Time) e Esteira de Inferência em Tempo Real no Apache Airflow (Etapa 3)",
                "ressalvas_operacionais": "2024 (formato bipartido sem chave direta de junção) e 2025 (aguardando divulgação das notas pelo INEP)"
            }
        }
    }
}

# Incorporar os mapeamentos das edições preservando acesso direto por chave de ano
for ano_k in (edicoes_treinamento + edicoes_oot):
    contrato_mlops[ano_k] = schema_producao[ano_k]

with open(caminho_artefato, 'w', encoding='utf-8') as f:
    json.dump(contrato_mlops, f, indent=2, ensure_ascii=False)

print(f"\\n✅ Artefato de MLOps auditado e salvo com sucesso em: {caminho_artefato}")
print(f"  • Horizonte de Treinamento (2014-2023): {len(edicoes_treinamento)} safras APROVADAS ({edicoes_treinamento})")
print(f"  • Horizonte Out-of-Time (2024-2025): {len(edicoes_oot)} safras PENDENTES ({edicoes_oot})")

# Amostra do Contrato para 2014 comprovando a resolução de drift
print(\"\\nMapeamento Canônico Homologado para o ENEM 2014:\")
print(json.dumps(contrato_mlops.get('2014', {}), indent=2, ensure_ascii=False))"""

nb.cells[16].source = cell16_source

with open(nb_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print(f"✅ Notebook {nb_path} atualizado com sucesso com schema_producao e Governança Bipartida (N8)!")
