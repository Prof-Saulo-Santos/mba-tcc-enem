import os
import nbformat

nb_path = 'notebooks/04_varredura_semantica.ipynb'
print(f"Lendo {nb_path}...")

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# 1. Update Cell 14 (Markdown - Seção 7 Veredito Metodológico Retificado com Rigor Científico N12)
cell14_source = """## 7. Veredito Metodológico da Série Temporal: Classificação de Maturidade e Governança

Com base nos resultados matemáticos do pareamento vetorial e na auditoria documental e física dos microdados, estabelecemos o veredito oficial com **classificação formal de maturidade, disponibilidade de notas e política de ingestão**:

| Edição do ENEM | Status de Governança | Situação da Base | Justificativa Metodológica | Papel no Pipeline |
| :---: | :---: | :---: | :--- | :--- |
| **2009 e 2010** | ❌ **REPROVADA** | Ruptura Estrutural | Ausência absoluta de variáveis essenciais (`Q024` - Computador e escolaridade materna padronizada). Incompatibilidade cadastral insanável. | Descarte definitivo do baseline |
| **2011 a 2013** | ⚠️ **PENDENTE_HARMONIZACAO** | Volátil / Não Mapeada | Descontinuidade de granularidade no questionário socioeconômico (faixas de renda incompatíveis). Exige engenharia reversa complexa. | Excluída do Treino Baseline (Candidata a experimentos de estresse no Notebook 05) |
| **2014 a 2023** | ✅ **APROVADA** | Definitiva | Década de Ouro: estabilidade cadastral sob a escala da TRI, com 100% de presença física comprovada nos CSVs brutos. | Treinamento e Validação Cruzada (Notebook 05) |
| **2024** | ⏳ **PENDENTE_VALIDACAO** | Definitiva Bipartida | Mapeamento semântico resolvido e notas disponíveis, exigindo pipeline de concatenação posicional segura. | Reserva para Validação Out-of-Time no Airflow (Etapa 3) |
| **2025** | ⚠️ **PRELIMINAR_SEM_NOTAS** | Preliminar Cadastral | Cadastro pré-exame (apenas PARTICIPANTES). Inexistência de notas impede cálculo do TARGET_M4. | Teste Sintático de Inferência de Features X (Inapto p/ Benchmark) |

> **Nota de Rigor Científico (Alinhamento N12):**  
> A exclusão das edições de 2011 a 2013 do conjunto canônico de treinamento fundamenta-se estritamente na **descontinuidade de esquema e na incompatibilidade da granularidade das variáveis socioeconômicas**, e não em suposições teóricas prematuras sobre desempenho preditivo. O impacto estatístico real da inclusão dessas safras na capacidade de generalização de algoritmos de Machine Learning (comparação de $R^2$ e $RMSE$) será investigado formalmente como **hipótese experimental no Notebook 05**."""

nb.cells[14].source = cell14_source

# 2. Update Cell 16 (Code - Injeção de politica_edicoes_anteriores em _metadata)
cell16_source = """# 8. Geração, Validação Defensiva e Persistência do Contrato de Schema Mapping 
# com Governança Bipartida e Evidências Auditáveis de Decisão (Blindagem N3, N4, N7, N8, N9, N10, N11 e N12)
import os
import json
import datetime
import pandas as pd

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
caminho_artefato = os.path.join(PROCESSED_DATA_DIR, 'schema_mapping_historico.json')

# ── 1. Discriminação dos Horizontes e Classificação Formal da Maturidade ─────────
edicoes_treinamento = [str(ano) for ano in range(2014, 2024) if str(ano) in mapa_schema_completo]
edicoes_oot = [str(ano) for ano in [2024, 2025] if str(ano) in mapa_schema_completo]

schema_producao = {ano: mapa_schema_completo[ano] for ano in (edicoes_treinamento + edicoes_oot)}

# Metadados de maturidade, procedência e disponibilidade de notas por edição
classificacao_edicoes = {}

for ano_t in edicoes_treinamento:
    classificacao_edicoes[ano_t] = {
        'situacao_base': 'DEFINITIVA',
        'dicionario': 'Disponível (Completo)',
        'microdados': 'Disponível (Monolítico Completo)',
        'disponibilidade_notas': '✅ Disponível (100% calculável TARGET_M4)',
        'status_governanca': '✅ APROVADA',
        'finalidade_arquitetural': 'Treinamento Supervisionado e Validação Cruzada (Note 05)',
        'justificativa': 'Microdados censitários consolidados com 100% de presença física comprovada.',
        'origem_dados': f'INEP / Microdados Consolidados ENEM {ano_t}'
    }

classificacao_edicoes['2024'] = {
    'situacao_base': 'DEFINITIVA_BIPARTIDA',
    'dicionario': 'Disponível (Multi-aba)',
    'microdados': 'Disponível (Bipartido: PARTICIPANTES + RESULTADOS)',
    'disponibilidade_notas': '✅ Disponível (Contido em RESULTADOS_2024.csv)',
    'status_governanca': '⏳ PENDENTE_VALIDACAO',
    'finalidade_arquitetural': 'Validação Temporal Out-of-Time no Apache Airflow (Etapa 3)',
    'justificativa': 'Notas disponíveis; partição física exige pipeline de concatenação posicional segura.',
    'origem_dados': 'INEP / Microdados Bipartidos ENEM 2024'
}

classificacao_edicoes['2025'] = {
    'situacao_base': 'PRELIMINAR_CADASTRO',
    'dicionario': 'Disponível (Multi-aba Preliminar)',
    'microdados': 'Parcial (Exclusivamente PARTICIPANTES_2025.csv; RESULTADOS inexistente)',
    'disponibilidade_notas': '❌ Indisponível (Exame não apurado na data de extração)',
    'status_governanca': '⚠️ PRELIMINAR_SEM_NOTAS',
    'finalidade_arquitetural': 'Teste Sintático de Features X (Inapto para Benchmark Preditivo)',
    'justificativa': 'Ausência total de notas e gabaritos impede cálculo do TARGET_M4 e avaliação de resíduos.',
    'origem_dados': 'INEP / Base Preliminar de Inscritos ENEM 2025'
}

# ── Gatekeeper de Integridade e Tabela de Governança ──────────────────────────
print("=" * 80)
print("AUDITORIA DE GOVERNANÇA, MATURIDADE E DISCRIMINAÇÃO DOS DADOS")
print("=" * 80)

relatorio_governanca = []
for ano_k, meta_k in classificacao_edicoes.items():
    mapa = schema_producao[ano_k]
    assert len(mapa) == 15, f"Erro: apenas {len(mapa)} variáveis mapeadas no ano {ano_k}"
    assert len(set(mapa.values())) == 15, f"Erro: colisão detectada no ano {ano_k}"
    relatorio_governanca.append({
        'Edição': ano_k,
        'Situação da Base': meta_k['situacao_base'],
        'Microdados': meta_k['microdados'],
        'TARGET_M4': meta_k['disponibilidade_notas'],
        'Status de Governança': meta_k['status_governanca'],
        'Finalidade Arquitetural': meta_k['finalidade_arquitetural']
    })

df_gov = pd.DataFrame(relatorio_governanca)
display(df_gov)

# ── 2. Montagem do Artefato Estruturado com Metadados e Evidências de Decisão (N11 e N12) ──
data_auditoria_iso = datetime.date.today().isoformat()
modelo_sbert_nome = "neuralmind/bert-base-portuguese-cased"

# Filtrar as evidências detalhadas para as edições homologadas
evidencias_producao = {
    ano_p: mapa_evidencias_completo.get(ano_p, {}) 
    for ano_p in (edicoes_treinamento + edicoes_oot)
}

contrato_mlops = {
    "_metadata": {
        "descricao": "Contrato Canônico de MLOps - Harmonização Semântica e Evidências Auditáveis dos Microdados ENEM",
        "versao_contrato": "3.2 (Contrato Canônico Auditável com Política de Edições Históricas)",
        "data_auditoria": data_auditoria_iso,
        "modelo_sbert": {
            "nome": modelo_sbert_nome,
            "descricao": "BERTimbau Base - Transformer pré-treinado em Língua Portuguesa",
            "pooling": "Mean Pooling com Normalização de Cosseno"
        },
        "criterios_decisao": {
            "limiar_minimo_similaridade": 0.70,
            "preferencia_semantica_delta": 0.15,
            "limiar_identidade_nominal": 0.60,
            "restricao_injetividade": "1-para-1 estrita (Counter zero collisions)"
        },
        "politica_edicoes_anteriores": {
            "2009-2010": {
                "status": "REPROVADA",
                "motivo": "Ruptura estrutural insanável (ausência absoluta de posse de computador Q024 no questionário do INEP)."
            },
            "2011-2013": {
                "status": "PENDENTE_HARMONIZACAO",
                "motivo": "Descontinuidade de granularidade em faixas de renda e questionário. Excluída do baseline de treinamento; candidata a teste empírico de impacto preditivo no Notebook 05."
            }
        },
        "classificacao_edicoes": classificacao_edicoes,
        "horizontes": {
            "treinamento_benchmark": {
                "periodo": "2014-2023 (Década de Ouro)",
                "edicoes": edicoes_treinamento,
                "status_homologacao": "APROVADA",
                "finalidade": "Treinamento Supervisionado, Validação Cruzada K-Fold e Benchmark de Modelos (Notebook 05)",
                "auditoria_fisica": "100% comprovada nos microdados brutos CSV"
            },
            "reserva_validacao_oot": {
                "periodo": "2024 (Reserva de Produção com Alvo)",
                "edicoes": ["2024"],
                "status_homologacao": "PENDENTE_VALIDACAO",
                "finalidade": "Validação Temporal Cega (Out-of-Time) no Apache Airflow (Etapa 3)",
                "ressalvas_operacionais": "Formato bipartido sem chave direta de junção (exige merge posicional seguro)"
            },
            "reserva_inferencia_sintatica": {
                "periodo": "2025 (Prévia Cadastral sem Alvo)",
                "edicoes": ["2025"],
                "status_homologacao": "PRELIMINAR_SEM_NOTAS",
                "finalidade": "Auditoria e Teste Sintático de Inferência das Features X (Inapto para validação de notas)",
                "ressalvas_operacionais": "Arquivo RESULTADOS_2025.csv inexistente (exame sem notas divulgadas)"
            }
        },
        "evidencias_decisao": evidencias_producao
    }
}

# Incorporar os mapeamentos preservando acesso direto por chave de ano (100% retrocompatível com ETL)
for ano_k in (edicoes_treinamento + edicoes_oot):
    contrato_mlops[ano_k] = schema_producao[ano_k]

with open(caminho_artefato, 'w', encoding='utf-8') as f:
    json.dump(contrato_mlops, f, indent=2, ensure_ascii=False)

print(f"\\n✅ Contrato Canônico de MLOps Auditável salvo com sucesso em: {caminho_artefato}")
print(f"  • Versão do Contrato: {contrato_mlops['_metadata']['versao_contrato']}")
print(f"  • Modelo SBERT Registrado: {modelo_sbert_nome}")
print(f"  • Total de Edições com Evidências Minuciosas: {len(evidencias_producao)}")

# Exibir Amostra da Ficha de Evidência para o ENEM 2014 (comprovando a resolução da N10, N11 e N12)
print(\"\\n\" + \"=\" * 80)
print(\"RASTREABILIDADE DE AUDITORIA: FICHA DE EVIDÊNCIAS DE DECISÃO (ENEM 2014)\")
print(\"=\" * 80)

df_evidencias_2014 = pd.DataFrame([
    {
        'Canônica (2023)': k,
        'Eleita (2014)': v['coluna_eleita'],
        'Score SBERT': f\"{v['score_similaridade']:.4f}\",
        'Tipo Match': v['tipo_correspondencia'],
        'Aba Origem': v.get('aba_origem', 'N/A'),
        'Justificativa Metodológica': v['justificativa_decisao']
    }
    for k, v in evidencias_producao.get('2014', {}).items()
])
display(df_evidencias_2014)"""

nb.cells[16].source = cell16_source

with open(nb_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print(f"✅ Notebook {nb_path} atualizado com sucesso com Rigor Metodológico N12!")
