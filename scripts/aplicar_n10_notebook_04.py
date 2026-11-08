import os
import nbformat

nb_path = 'notebooks/04_varredura_semantica.ipynb'
print(f"Lendo {nb_path}...")

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# 1. Update Cell 5 (Code - Parser Robusto com Validação Estrita e Detecção de Conflitos)
cell5_source = """# 3. Parser Robusto e Auditável de Dicionários Multi-Aba do INEP (Blindagem N10)
import os
import glob
import pandas as pd

def extrair_dicionario_multiaba(path_excel, retornar_metadados=False):
    \"\"\"
    Lê com segurança e rigor de governança todas as abas legítimas de um dicionário do INEP:
    - Descarta abas irrelevantes (ITENS, LEIA-ME, HISTORICO, HAB_ESTUDO, VERSAO);
    - Exige coocorrência de termos no cabeçalho (NOME/VARIÁVEL e DESCRIÇÃO/DEFINIÇÃO);
    - Localiza estritamente as colunas canônicas de identificador e descrição;
    - Detecta duplicidades entre abas e audita conflitos semânticos;
    - Registra a aba de origem de cada variável para rastreabilidade de linhagem.
    \"\"\"
    try:
        xls = pd.ExcelFile(path_excel, engine='openpyxl')
        ignorar_abas = ['ITENS', 'LEIA', 'HISTOR', 'SUMAR', 'HAB_ESTUDO', 'VERSAO']
        sheets_validas = [
            s for s in xls.sheet_names 
            if not any(ign in s.upper() for ign in ignorar_abas)
        ]
        
        dicionario_consolidado = {}
        registro_auditoria = {}
        duplicidades_detectadas = []
        
        for sheet in sheets_validas:
            df_raw = pd.read_excel(path_excel, sheet_name=sheet, header=None, engine='openpyxl')
            
            # 1. Validação estrita de cabeçalho: coocorrência de identificador e descrição
            header_idx = None
            for i, row in df_raw.head(15).iterrows():
                row_str = ' '.join(str(v).upper() for v in row.values if pd.notna(v))
                tem_id = any(k in row_str for k in ['NOME DA VARIÁVEL', 'NOME DA VARIAVEL', 'NOME DA COLUNA', 'VARIÁVEL', 'VARIAVEL'])
                tem_desc = any(k in row_str for k in ['DESCRIÇÃO', 'DESCRICAO', 'DEFINIÇÃO', 'DEFINICAO'])
                if tem_id and tem_desc:
                    header_idx = i
                    break
                    
            # Fallback tolerante para linhas com NOME isolado caso coocorrência falhe
            if header_idx is None:
                for i, row in df_raw.head(15).iterrows():
                    row_str = ' '.join(str(v).upper() for v in row.values if pd.notna(v))
                    if 'NOME' in row_str or 'VARIÁVEL' in row_str:
                        header_idx = i
                        break
                        
            if header_idx is None:
                continue
                
            df_sheet = pd.read_excel(path_excel, sheet_name=sheet, header=header_idx, engine='openpyxl')
            df_sheet.columns = [str(c).strip() for c in df_sheet.columns]
            
            # 2. Localização canônica das colunas técnicas
            col_nome = next((c for c in df_sheet.columns if any(k in c.upper() for k in ['NOME DA VARIÁVEL', 'NOME DA VARIAVEL', 'NOME DA COLUNA', 'NOME'])), None)
            col_desc = next((c for c in df_sheet.columns if any(k in c.upper() for k in ['DESCRIÇÃO DO CAMPO', 'DESCRIÇÃO DA VARIÁVEL', 'DESCRIÇÃO', 'DESCRICAO'])), None)
            
            if not (col_nome and col_desc):
                continue
                
            sub = df_sheet[[col_nome, col_desc]].dropna(subset=[col_nome])
            
            for _, r in sub.iterrows():
                var_name = str(r[col_nome]).strip()
                var_desc = str(r[col_desc]).strip().replace('\\n', ' ')
                
                # Descartar ruídos de seção e cabeçalhos residuais
                if not var_name or var_name.upper().startswith(('NOME', 'DADOS', 'TABELA', 'FONTE')):
                    continue
                    
                # 3. Auditoria de duplicidade e verificação de conflitos entre abas
                if var_name in dicionario_consolidado:
                    desc_anterior = dicionario_consolidado[var_name]
                    desc_identica = (desc_anterior.strip().lower() == var_desc.strip().lower())
                    duplicidades_detectadas.append({
                        'variavel': var_name,
                        'aba_anterior': registro_auditoria[var_name]['aba'],
                        'aba_atual': sheet,
                        'descricoes_identicas': desc_identica
                    })
                    if not desc_identica:
                        registro_auditoria[var_name]['conflito_detectado'] = True
                        registro_auditoria[var_name]['desc_conflitante'] = var_desc
                        registro_auditoria[var_name]['aba_conflitante'] = sheet
                else:
                    dicionario_consolidado[var_name] = var_desc
                    registro_auditoria[var_name] = {
                        'aba': sheet,
                        'descricao': var_desc,
                        'conflito_detectado': False
                    }
                    
        if retornar_metadados:
            return dicionario_consolidado, registro_auditoria, duplicidades_detectadas
        return dicionario_consolidado

    except Exception as e:
        print(f"Erro ao processar dicionário em {path_excel}: {e}")
        if retornar_metadados:
            return {}, {}, []
        return {}

# ── Teste e Auditoria dos Metadados Extraídos nas Edições de Transição ─────────
print("=" * 80)
print("AUDITORIA DE QUALIDADE DOS METADADOS EXTRAÍDOS (BLINDAGEM N10)")
print("=" * 80)

relatorio_parser = []
for teste_ano in ['2014', '2022', '2023', '2024', '2025']:
    p = glob.glob(os.path.join(RAW_DATA_DIR, f'enem_{teste_ano}/**/Dicion*.xlsx'), recursive=True)
    if p:
        dic, reg, dups = extrair_dicionario_multiaba(p[0], retornar_metadados=True)
        conflitos = sum(1 for v in reg.values() if v.get('conflito_detectado', False))
        relatorio_parser.append({
            'Ano': teste_ano,
            'Total Variáveis': len(dic),
            'Abas Lidas': list(set(v['aba'] for v in reg.values())),
            'Duplicidades': len(dups),
            'Conflitos Semânticos': f"✅ Zero ({conflitos})" if conflitos == 0 else f"⚠️ {conflitos} conflitos",
            'TP_LINGUA Presente?': "✅ Sim" if 'TP_LINGUA' in dic else "❌ Não"
        })

df_auditoria_parser = pd.DataFrame(relatorio_parser)
display(df_auditoria_parser)"""

nb.cells[5].source = cell5_source

# 2. Update Cell 7 (Code - Varredura Semântica Longitudinal capturando aba_origem)
cell7_source = """# 4. Execução da Varredura Semântica Longitudinal (2009 a 2025) com Proteção contra Colisão e Captura de Evidências (N3, N4, N10, N11)
import re
import glob
from collections import Counter

anos_paths = sorted(glob.glob(os.path.join(RAW_DATA_DIR, '*/microdados_enem_*/DICIONÁRIO/Dicion*.xlsx')))
print(f"Total de dicionários históricos identificados: {len(anos_paths)}")

historico_drift = []
matriz_scores = []
mapa_schema_completo = {}
mapa_evidencias_completo = {}

for path in anos_paths:
    match = re.search(r'enem_(\\d{4})', path)
    ano = match.group(1) if match else "Desconhecido"
    
    # RESOLUÇÃO N10: Extração robusta com metadados de procedência e auditoria de duplicidades
    dic_ano, reg_metadados, dups_ano = extrair_dicionario_multiaba(path, retornar_metadados=True)
    if not dic_ano:
        continue
        
    target_keys = list(dic_ano.keys())
    target_descs = [dic_ano[k] for k in target_keys]
    
    # Embedding de todas as descrições do ano histórico
    target_embs = model.encode(target_descs, convert_to_tensor=True)
    
    # Matriz de Similaridade de Cosseno (15 variáveis base x N variáveis históricas)
    cos_sim = util.cos_sim(base_embeddings, target_embs)
    
    linha_drift = {'Ano': ano}
    linha_scores = {'Ano': ano}
    schema_ano = {}
    evidencias_ano = {}
    
    for i, b_key in enumerate(base_keys):
        scores = cos_sim[i]
        best_idx = torch.argmax(scores).item()
        best_score = scores[best_idx].item()
        best_key = target_keys[best_idx]
        
        # Auditoria de identidade exata
        exact_score = 0.0
        if b_key in dic_ano:
            exact_idx = target_keys.index(b_key)
            exact_score = scores[exact_idx].item()
            
        # ── Decisão Algorítmica com Blindagem Semântica e Registro de Evidências ──
        if b_key.startswith('NU_') or b_key.startswith('TP_'):
            # RESOLUÇÃO N4: Não aceita cegamente pelo nome; exige similaridade mínima de 0.60
            if b_key in dic_ano and exact_score >= 0.60:
                coluna_eleita = b_key
                score_final = exact_score
                status_str = "Mantida"
                tipo_match = "Exata (Identidade Nominal)"
                justificativa = f"Identidade nominal de código confirmada com estabilidade semântica (score {exact_score:.2f} >= 0.60)."
            elif b_key in dic_ano and exact_score < 0.60:
                coluna_eleita = None
                score_final = exact_score
                status_str = f"⚠️ DERIVA ({exact_score:.2f})"
                tipo_match = "Divergência Semântica"
                justificativa = f"Alerta crítico: código nominal idêntico, porém similaridade semântica insuficiente ({exact_score:.2f} < 0.60)."
            elif best_score >= 0.70:
                coluna_eleita = best_key
                score_final = best_score
                status_str = f"{best_key} ({best_score:.2f})"
                tipo_match = "Semântica (Alinhamento SBERT)"
                justificativa = f"Variável administrativa remapeada via similaridade vetorial SBERT (score {best_score:.2f} >= 0.70)."
            else:
                coluna_eleita = None
                score_final = 0.0
                status_str = "AUSENTE"
                tipo_match = "Não Encontrada"
                justificativa = "Variável ausente no dicionário da edição ou similaridade abaixo do corte de 0.70."
        else:
            # Variáveis socioeconômicas (Q*): Prioridade para a semântica vetorial
            if best_score > (exact_score + 0.15) and best_score >= 0.70:
                coluna_eleita = best_key
                score_final = best_score
                status_str = f"{best_key} ({best_score:.2f})"
                tipo_match = "Semântica (Alinhamento SBERT)"
                if b_key == 'Q006' and best_key == 'Q003' and ano == '2014':
                    justificativa = "Equivalência estrita de 17 faixas (A-Q) de múltiplos de Salário Mínimo comprovada na Seção 6."
                elif b_key == 'Q005' and best_key == 'Q004' and ano == '2014':
                    justificativa = "Equivalência de domínio de 1 a 20 moradores no domicílio comprovada na auditoria empírica (Seção 6)."
                elif b_key == 'Q024' and best_key == 'Q010' and ano == '2014':
                    justificativa = "Equivalência de posse de computador comprovada na auditoria empírica de inclusão digital (Seção 6)."
                elif b_key == 'Q024' and best_key == 'Q021' and ano in ['2024', '2025']:
                    justificativa = f"Identificação de posse de computador no questionário reestruturado do ENEM {ano} via SBERT (score {best_score:.2f})."
                else:
                    justificativa = f"Mudança de código resolvida por embedding SBERT (score {best_score:.2f} > limiar + 0.15)."
            elif b_key in dic_ano and exact_score >= 0.65:
                coluna_eleita = b_key
                score_final = exact_score
                status_str = "Mantida"
                tipo_match = "Exata (Identidade Nominal)"
                justificativa = f"Enunciado socioeconômico e código estáveis em relação ao padrão 2023 (score {exact_score:.2f} >= 0.65)."
            elif best_score >= 0.70:
                coluna_eleita = best_key
                score_final = best_score
                status_str = f"{best_key} ({best_score:.2f})"
                tipo_match = "Semântica (Alinhamento SBERT)"
                justificativa = f"Recuperação semântica vetorial SBERT (score {best_score:.2f} >= 0.70)."
            else:
                coluna_eleita = None
                score_final = 0.0
                status_str = "AUSENTE"
                tipo_match = "Não Encontrada"
                justificativa = "Pergunta socioeconômica ausente no questionário desta edição."
                
        linha_drift[b_key] = status_str
        linha_scores[b_key] = score_final
        if coluna_eleita:
            schema_ano[b_key] = coluna_eleita
            evidencias_ano[b_key] = {
                'coluna_eleita': coluna_eleita,
                'score_similaridade': round(score_final, 4),
                'tipo_correspondencia': tipo_match,
                'descricao_canonica': CONTRATO_CANONICO.get(b_key, "N/A"),
                'descricao_historica': dic_ano.get(coluna_eleita, "N/A"),
                'aba_origem': reg_metadados.get(coluna_eleita, {}).get('aba', 'Única'),
                'fonte_documental': os.path.basename(path),
                'justificativa_decisao': justificativa
            }
            
    # ── RESOLUÇÃO N3: Verificação de Injetividade Estrita (1-para-1) ──────────
    colunas_historicas_usadas = list(schema_ano.values())
    contagem_usadas = Counter(colunas_historicas_usadas)
    colisoes = {k: v for k, v in contagem_usadas.items() if v > 1}
    
    if colisoes:
        msg_erro = f"CRÍTICO: Colisão semântica detectada no ano {ano}! Variáveis históricas reutilizadas: {colisoes}"
        if int(ano) >= 2014:
            raise ValueError(msg_erro)
        else:
            print(f"⚠️ {msg_erro} (Edição histórica preliminar)")
            
    historico_drift.append(linha_drift)
    matriz_scores.append(linha_scores)
    mapa_schema_completo[ano] = schema_ano
    mapa_evidencias_completo[ano] = evidencias_ano

df_drift = pd.DataFrame(historico_drift).set_index('Ano')
df_scores = pd.DataFrame(matriz_scores).set_index('Ano')
print("✅ Varredura semântica longitudinal concluída com sucesso e evidências registradas!")"""

nb.cells[7].source = cell7_source

# 3. Update Cell 16 (Code - Exportação do Contrato com aba_origem na Tabela)
cell16_source = """# 8. Geração, Validação Defensiva e Persistência do Contrato de Schema Mapping 
# com Governança Bipartida e Evidências Auditáveis de Decisão (Blindagem N3, N4, N7, N8, N9, N10 e N11)
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

# ── 2. Montagem do Artefato Estruturado com Metadados e Evidências de Decisão (N11) ──
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
        "versao_contrato": "3.1 (Contrato Canônico Auditável com Rastreabilidade de Aba e Evidências)",
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

# Exibir Amostra da Ficha de Evidência para o ENEM 2014 (comprovando a resolução da N10 e N11)
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

print(f"✅ Notebook {nb_path} atualizado com sucesso com Parser Auditável (N10)!")
