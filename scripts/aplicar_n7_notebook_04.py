import os
import nbformat

nb_path = 'notebooks/04_varredura_semantica.ipynb'
print(f"Lendo {nb_path}...")

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# 1. Update Cell 14 (Markdown - Seção 7 Veredito Metodológico com os 3 Estados)
cell14_source = """## 7. Veredito Metodológico da Série Temporal: Os Três Estados de Homologação

Com base nos resultados matemáticos do pareamento vetorial e na auditoria semântica e física dos microdados, estabelecemos o veredito acadêmico oficial estruturado em **três estados formais de maturidade**:

| Edição do ENEM | Status de Governança | Justificativa Metodológica | Papel no Pipeline |
| :---: | :---: | :--- | :--- |
| **2009 e 2010** | ❌ **REPROVADA** | Ruptura estrutural insanável. Ausência de posse de computador (`Q024`) e escolaridade materna. | Descarte definitivo |
| **2011 a 2013** | ❌ **REPROVADA** | Volatilidade severa do questionário socioeconômico e risco de contaminação por ruído. | Descarte definitivo |
| **2014 a 2023** | ✅ **APROVADA** | Década de Ouro: estabilidade estrutural e cadastral dos microdados sob a escala da TRI, com 100% de presença física comprovada. | Treinamento e Validação Cruzada (Notebook 05) |
| **2024** | ⏳ **PENDENTE_VALIDACAO** | Mapeamento semântico resolvido (`Q024 -> Q021`), mas com formato bipartido que exige concatenação posicional segura. | Reserva para Validação Out-of-Time no Airflow (Etapa 3) |
| **2025** | ⏳ **PENDENTE_VALIDACAO** | Questionário preliminar mapeado, porém sem divulgação das notas oficiais pelo INEP. | Reserva para inferência futura |"""

nb.cells[14].source = cell14_source

# 2. Update Cell 16 (Code - Exportação do Contrato com Relatório de Governança)
cell16_source = """# 8. Geração, Validação Defensiva e Persistência do Contrato de Schema Mapping com Governança de Ciclo de Vida
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
caminho_artefato = os.path.join(PROCESSED_DATA_DIR, 'schema_mapping_historico.json')

# Filtrar o mapeamento para as edições de produção e modelagem (2014 a 2024)
schema_producao = {
    ano: mapa_schema_completo[ano] 
    for ano in sorted(mapa_schema_completo.keys()) 
    if int(ano) >= 2014
}

# ── Gatekeeper de Integridade e Governança (Blindagem N3, N4 e N7) ────────────
print("=" * 80)
print("AUDITORIA DE GOVERNANÇA E INTEGRIDADE DO CONTRATO DE MLOPS")
print("=" * 80)

relatorio_governanca = []
for ano_prod, mapa_prod in schema_producao.items():
    # Checagem de completude: todas as 15 variáveis canônicas devem estar resolvidas
    assert len(mapa_prod) == 15, f"Erro: apenas {len(mapa_prod)} variáveis mapeadas no ano {ano_prod}"
    # Checagem de unicidade: zero colisões
    assert len(set(mapa_prod.values())) == 15, f"Erro: colisão detectada no ano {ano_prod}"
    
    status_gov = "✅ APROVADA" if int(ano_prod) <= 2023 else "⏳ PENDENTE_VALIDACAO"
    papel = "Treinamento / Benchmark" if int(ano_prod) <= 2023 else "Reserva Out-of-Time (Airflow)"
    relatorio_governanca.append({
        'Edição': ano_prod,
        'Variáveis Mapeadas': len(mapa_prod),
        'Status de Homologação': status_gov,
        'Papel no Pipeline': papel
    })

df_gov = pd.DataFrame(relatorio_governanca)
display(df_gov)

with open(caminho_artefato, 'w', encoding='utf-8') as f:
    json.dump(schema_producao, f, indent=2, ensure_ascii=False)

print(f"\\n✅ Artefato de MLOps auditado e salvo com sucesso em: {caminho_artefato}")
print(f"Edições validadas no contrato de produção: {list(schema_producao.keys())}")

# Amostra do Contrato para 2014 comprovando a resolução de drift
print("\\nMapeamento Canônico Homologado para o ENEM 2014:")
print(json.dumps(schema_producao.get('2014', {}), indent=2, ensure_ascii=False))"""

nb.cells[16].source = cell16_source

with open(nb_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print(f"✅ Notebook {nb_path} atualizado com sucesso com o Framework de Três Estados (N7)!")
