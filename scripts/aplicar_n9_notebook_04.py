import os
import nbformat

nb_path = 'notebooks/04_varredura_semantica.ipynb'
print(f"Lendo {nb_path}...")

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# 1. Update Cell 14 (Markdown - Seção 7 Veredito Metodológico com Situação da Base e Status Específico para 2025)
cell14_source = """## 7. Veredito Metodológico da Série Temporal: Os Três Estados de Homologação

Com base nos resultados matemáticos do pareamento vetorial e na auditoria semântica e física dos microdados, estabelecemos o veredito acadêmico oficial estruturado com **classificação formal de maturidade e disponibilidade de notas**:

| Edição do ENEM | Status de Governança | Situação da Base | Justificativa Metodológica | Papel no Pipeline |
| :---: | :---: | :---: | :--- | :--- |
| **2009 e 2010** | ❌ **REPROVADA** | Obsoleta | Ruptura estrutural insanável. Ausência de posse de computador (`Q024`) e escolaridade materna. | Descarte definitivo |
| **2011 a 2013** | ❌ **REPROVADA** | Volátil | Volatilidade severa do questionário socioeconômico e risco de contaminação por ruído. | Descarte definitivo |
| **2014 a 2023** | ✅ **APROVADA** | Definitiva | Década de Ouro: estabilidade cadastral sob a escala da TRI, com 100% de presença física comprovada. | Treinamento e Validação Cruzada (Notebook 05) |
| **2024** | ⏳ **PENDENTE_VALIDACAO** | Definitiva Bipartida | Mapeamento semântico resolvido e notas disponíveis, exigindo merge posicional seguro. | Reserva para Validação Out-of-Time no Airflow (Etapa 3) |
| **2025** | ⚠️ **PRELIMINAR_SEM_NOTAS** | Preliminar Cadastral | Cadastro pré-exame (apenas PARTICIPANTES). Inexistência de notas impede cálculo do TARGET_M4. | Teste Sintático de Inferência de Features X (Inapto p/ Benchmark) |"""

nb.cells[14].source = cell14_source

# 2. Update Cell 15 (Markdown - Seção 8 com discriminação dos 3 conjuntos)
cell15_source = """## 8. Exportação do Contrato Canônico de MLOps (`schema_mapping_historico.json`)

Para materializar o pipeline de MLOps de ponta a ponta, eliminar códigos *hardcoded* nos scripts de engenharia de dados e garantir **governança estrita sobre a maturidade e finalidade de cada edição**, exportamos abaixo o artefato canônico **`schema_mapping_historico.json`**. 

O contrato organiza as safras mapeadas em **três horizontes formalmente discriminados por maturidade**:

1. **Conjunto A — Treinamento e Benchmark (2014 a 2023 — Década de Ouro):**
   * **Situação:** `DEFINITIVA` (Status: `APROVADA`).
   * **Finalidade:** Microdados e notas $100\%$ consolidados para extração via `scripts/etl_parquet.py` e treinamento no **Notebook 05**.
2. **Conjunto B — Validação Temporal Out-of-Time com Notas (2024):**
   * **Situação:** `DEFINITIVA_BIPARTIDA` (Status: `PENDENTE_VALIDACAO`).
   * **Finalidade:** Conjunto cego de teste temporal com notas apuradas em `RESULTADOS_2024.csv`, aguardando concatenação no **Apache Airflow (Etapa 3)**.
3. **Conjunto C — Prévia Cadastral para Teste de Inferência sem Alvo (2025):**
   * **Situação:** `PRELIMINAR_CADASTRO` (Status: `PRELIMINAR_SEM_NOTAS`).
   * **Finalidade:** Base de inscritos pré-exame (`PARTICIPANTES_2025.csv`). Por não conter notas divulgadas, é **inapta para avaliação de erro preditivo**, servindo unicamente para testes de schema de variáveis preditoras ($X$)."""

nb.cells[15].source = cell15_source

# 3. Update Cell 16 (Code - Exportação do Contrato com classificacao_edicoes e _metadata)
cell16_source = """# 8. Geração, Validação Defensiva e Persistência do Contrato de Schema Mapping 
# com Classificação Específica de Maturidade das Edições (Blindagem N3, N4, N7, N8 e N9)
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

# ── 2. Montagem do Artefato Estruturado com Metadados e Retrocompatibilidade ──
contrato_mlops = {
    "_metadata": {
        "descricao": "Contrato Canônico de MLOps - Harmonização Semântica dos Microdados ENEM",
        "versao_contrato": "2.2 (Governança com Classificação de Maturidade)",
        "data_homologacao": datetime.date.today().isoformat(),
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
        }
    }
}

# Incorporar os mapeamentos preservando acesso direto por chave de ano
for ano_k in (edicoes_treinamento + edicoes_oot):
    contrato_mlops[ano_k] = schema_producao[ano_k]

with open(caminho_artefato, 'w', encoding='utf-8') as f:
    json.dump(contrato_mlops, f, indent=2, ensure_ascii=False)

print(f"\\n✅ Artefato de MLOps auditado e salvo com sucesso em: {caminho_artefato}")
print(f"  • Treinamento Definitivo (2014-2023): {len(edicoes_treinamento)} safras APROVADAS")
print(f"  • Validação Out-of-Time com Notas (2024): 1 safra PENDENTE DE JUNÇÃO")
print(f"  • Teste de Features sem Notas (2025): 1 safra PRELIMINAR CADASTRAL")

# Amostra do Contrato para 2014 comprovando a resolução de drift
print(\"\\nMapeamento Canônico Homologado para o ENEM 2014:\")
print(json.dumps(contrato_mlops.get('2014', {}), indent=2, ensure_ascii=False))"""

nb.cells[16].source = cell16_source

with open(nb_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print(f"✅ Notebook {nb_path} atualizado com sucesso com a Classificação de Maturidade (N9)!")
