"""Aplicação cliente Streamlit (desacoplada) para consumir a API ENEM TARGET_M4."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from api_client import (
    MAX_CANDIDATOS_LOTE,
    MEDIA_HISTORICA_DECADA,
    OPCOES_Q002,
    OPCOES_Q024,
    OPCOES_TP_ANO_CONCLUIU,
    OPCOES_TP_LINGUA,
    OPCOES_TP_SEXO,
    EnemApiClient,
    EnemApiError,
    gerar_alunos_aleatorios,
)
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parent
load_dotenv(FRONTEND_DIR / ".env")

DEFAULT_API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DEFAULT_HF_RAG_URL = os.getenv("HF_RAG_SPACE_URL", "").strip()
KB_PATH = FRONTEND_DIR / "knowledge_base" / "tcc_enem_completo.md"

st.set_page_config(
    page_title="ENEM TARGET_M4 — Simulador & Governança",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 ENEM `TARGET_M4` — Cliente de Inferência Socioeconômica")
st.caption(
    "Front-end desacoplado em Streamlit consumindo a API FastAPI (`XGBRegressor`, "
    "censo 2014–2023). As chamadas feitas aqui alimentam normalmente o Prometheus e o Grafana."
)

# ------------------------------------------------------------------------------
# Barra lateral: Conexão com a API e Link Externo do RAG no Hugging Face
# ------------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuração da API")
    api_url = st.text_input(
        "URL base da API FastAPI",
        value=DEFAULT_API_URL,
        help="Local: http://localhost:8000 | Nuvem: URL HTTPS do AWS App Runner.",
    )
    timeout_s = st.number_input(
        "Timeout HTTP (segundos)",
        min_value=5,
        max_value=120,
        value=30,
        step=5,
    )
    client = EnemApiClient(base_url=api_url, timeout_seconds=float(timeout_s))

    if st.button("🩺 Verificar saúde da API (/health)", use_container_width=True):
        try:
            health = client.check_health()
            st.success(
                f"Status: `{health.get('status')}` | Modelo: `{health.get('model_version')}`"
            )
            st.caption(f"SHA-256: `{str(health.get('artifact_sha256', ''))[:16]}...`")
        except EnemApiError as exc:
            st.error(str(exc))

    st.divider()
    st.header("🤖 Assistente RAG do TCC (Hugging Face)")
    hf_rag_url = st.text_input(
        "URL do Space RAG/LLM no Hugging Face",
        value=DEFAULT_HF_RAG_URL,
        placeholder="https://huggingface.co/spaces/usuario/space-rag",
        help="Cole a URL do seu Space publicado no Hugging Face para abrir em nova aba.",
    ).strip()

    if hf_rag_url and not hf_rag_url.endswith(("SEU_SPACE_RAG", "SEU_USUARIO/SEU_SPACE_RAG")):
        st.link_button(
            "🔗 Abrir RAG/LLM no Hugging Face",
            url=hf_rag_url,
            use_container_width=True,
        )
    else:
        st.info(
            "Informe a URL pública do seu Space RAG/LLM acima (ou em `HF_RAG_SPACE_URL` no `.env`) "
            "para habilitar o botão de acesso direto."
        )

    if KB_PATH.exists():
        kb_bytes = KB_PATH.read_bytes()
        st.download_button(
            "📥 Baixar Dossiê do TCC (.md)",
            data=kb_bytes,
            file_name="tcc_enem_completo.md",
            mime="text/markdown",
            use_container_width=True,
            help="Arquivo consolidado para alimentar/consultar no seu RAG do Hugging Face.",
        )

    st.divider()
    st.caption(
        "📊 **Observabilidade local:** se estiver rodando `docker compose --profile monitoring up -d`, "
        "acompanhe Prometheus (`:9090`) e Grafana (`:3000`)."
    )

# ------------------------------------------------------------------------------
# Abas principais
# ------------------------------------------------------------------------------
tab_simulador, tab_governanca, tab_rag = st.tabs(
    [
        "🎯 Simulador (1 Aluno & Lote N)",
        "🛡️ Governança & Métricas (/health & /info)",
        "📚 Dossiê do TCC & Acesso ao RAG",
    ]
)

with tab_simulador:
    col_ind, col_lote = st.columns([1, 1.15], gap="large")

    # ── COLUNA ESQUERDA: BOTÃO 1 — CONSULTAR 1 ALUNO (/predict) ───────────────
    with col_ind:
        st.subheader("1️⃣ Consultar 1 Aluno (`POST /predict`)")
        st.write(
            "Selecione os 6 atributos do *Esquadrão de Elite* e dispare a inferência pontual."
        )

        renda_per_capita = st.slider(
            "Renda familiar per capita (`RENDA_PER_CAPITA`, em Salários Mínimos)",
            min_value=0.0,
            max_value=25.0,
            value=1.5,
            step=0.25,
        )
        q024 = st.selectbox(
            "Posse de computador no domicílio (`Q024`)",
            options=list(OPCOES_Q024.keys()),
            index=1,
            format_func=lambda k: OPCOES_Q024[k],
        )
        q002 = st.selectbox(
            "Escolaridade da mãe / mulher responsável (`Q002`)",
            options=list(OPCOES_Q002.keys()),
            index=4,
            format_func=lambda k: OPCOES_Q002[k],
        )
        tp_lingua = st.selectbox(
            "Língua estrangeira escolhida (`TP_LINGUA`)",
            options=list(OPCOES_TP_LINGUA.keys()),
            index=0,
            format_func=lambda k: OPCOES_TP_LINGUA[k],
        )
        tp_ano_concluiu = st.selectbox(
            "Anos desde conclusão do Ensino Médio (`TP_ANO_CONCLUIU`)",
            options=list(OPCOES_TP_ANO_CONCLUIU.keys()),
            index=0,
            format_func=lambda k: OPCOES_TP_ANO_CONCLUIU[k],
        )
        tp_sexo = st.selectbox(
            "Sexo informado (`TP_SEXO`)",
            options=list(OPCOES_TP_SEXO.keys()),
            index=0,
            format_func=lambda k: OPCOES_TP_SEXO[k],
        )

        payload_individual: Dict[str, Any] = {
            "RENDA_PER_CAPITA": float(renda_per_capita),
            "Q024": int(q024),
            "TP_ANO_CONCLUIU": int(tp_ano_concluiu),
            "TP_LINGUA": int(tp_lingua),
            "TP_SEXO": int(tp_sexo),
            "Q002": int(q002),
        }

        with st.expander("Ver payload JSON enviado ao `/predict`"):
            st.json(payload_individual)

        if st.button(
            "🔍 Consultar 1 Aluno",
            type="primary",
            use_container_width=True,
            key="btn_predict_single",
        ):
            try:
                resp = client.predict_single(payload_individual)
                nota = float(resp["target_m4"])
                delta = nota - MEDIA_HISTORICA_DECADA
                st.metric(
                    label="Nota Prevista TARGET_M4 (Média das 4 Provas Objetivas)",
                    value=f"{nota:.2f} pts",
                    delta=f"{delta:+.2f} pts vs. média da década ({MEDIA_HISTORICA_DECADA})",
                )
                st.caption(
                    f"Modelo: `{resp.get('modelo')}` | Unidade: `{resp.get('unidade')}`"
                )
            except EnemApiError as exc:
                st.error(str(exc))

    # ── COLUNA DIREITA: BOTÃO 2 — GERAR E CONSULTAR N ALUNOS (/predict/batch) ─
    with col_lote:
        st.subheader("2️⃣ Gerar e Consultar `N` Alunos Aleatórios (`POST /predict/batch`)")
        st.write(
            "Gera perfis sintéticos dentro das faixas válidas da API, executa inferência vetorial "
            "em lote e envia métricas reais para o Prometheus/Grafana."
        )

        c_n, c_seed = st.columns([2, 1])
        with c_n:
            n_alunos = st.number_input(
                f"Quantidade de alunos (`N`, de 1 a {MAX_CANDIDATOS_LOTE:,})",
                min_value=1,
                max_value=MAX_CANDIDATOS_LOTE,
                value=100,
                step=50,
            )
        with c_seed:
            usar_seed = st.checkbox("Fixar semente (seed)", value=False)
            seed_valor: Optional[int] = None
            if usar_seed:
                seed_valor = int(
                    st.number_input("Seed", min_value=0, max_value=999_999, value=42, step=1)
                )

        if st.button(
            "🎲 Gerar e Consultar N Alunos Aleatórios",
            type="primary",
            use_container_width=True,
            key="btn_predict_batch",
        ):
            try:
                candidatos = gerar_alunos_aleatorios(
                    quantidade=int(n_alunos),
                    seed=seed_valor,
                )
                resp_lote = client.predict_batch(candidatos)
                st.session_state["ultimo_lote_df"] = pd.DataFrame(candidatos).assign(
                    TARGET_M4_PREVISTO=resp_lote["predicoes"]
                )
                st.session_state["ultimo_lote_meta"] = {
                    "total_candidatos": resp_lote["total_candidatos"],
                    "tempo_inferencia_ms": resp_lote["tempo_inferencia_ms"],
                    "modelo": resp_lote["modelo"],
                }
            except EnemApiError as exc:
                st.error(str(exc))

        if "ultimo_lote_df" in st.session_state:
            df_lote: pd.DataFrame = st.session_state["ultimo_lote_df"]
            meta: Dict[str, Any] = st.session_state["ultimo_lote_meta"]

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Alunos consultados", f"{meta['total_candidatos']:,}")
            m2.metric("Média prevista", f"{df_lote['TARGET_M4_PREVISTO'].mean():.2f} pts")
            m3.metric(
                "Faixa (Min–Máx)",
                f"{df_lote['TARGET_M4_PREVISTO'].min():.1f}–{df_lote['TARGET_M4_PREVISTO'].max():.1f}",
            )
            m4.metric("Latência API", f"{meta['tempo_inferencia_ms']:.2f} ms")

            if len(df_lote) > 1 and df_lote["TARGET_M4_PREVISTO"].nunique() > 1:
                st.caption("Distribuição das notas previstas (`TARGET_M4`) por faixa no lote:")
                n_bins = min(10, int(df_lote["TARGET_M4_PREVISTO"].nunique()))
                faixas = pd.cut(df_lote["TARGET_M4_PREVISTO"], bins=n_bins)
                contagens = faixas.value_counts().sort_index()
                dist = pd.DataFrame(
                    {
                        "Faixa TRI": [
                            f"{iv.left:.0f}–{iv.right:.0f}" for iv in contagens.index
                        ],
                        "Quantidade": contagens.values,
                    }
                )
                st.bar_chart(dist, x="Faixa TRI", y="Quantidade")

            with st.expander("📋 Ver tabela completa dos alunos gerados e predições", expanded=True):
                st.dataframe(df_lote, use_container_width=True, height=280)
                st.download_button(
                    "📥 Exportar lote simulado (.csv)",
                    data=df_lote.to_csv(index=False).encode("utf-8"),
                    file_name="simulacao_lote_enem_target_m4.csv",
                    mime="text/csv",
                )

# ------------------------------------------------------------------------------
# Aba 2: Governança & Saúde (/health e /info)
# ------------------------------------------------------------------------------
with tab_governanca:
    st.subheader("🛡️ Auditoria Criptográfica & Linhagem MLflow da API")
    st.write(
        "Consulta ao vivo aos endpoints `GET /health` e `GET /info` da API conectada."
    )

    if st.button("🔄 Atualizar dados de governança da API", key="btn_refresh_info"):
        st.session_state.pop("cache_api_health", None)
        st.session_state.pop("cache_api_info", None)

    try:
        if (
            st.session_state.get("cache_api_url") != client.base_url
            or "cache_api_health" not in st.session_state
            or "cache_api_info" not in st.session_state
        ):
            st.session_state["cache_api_health"] = client.check_health()
            st.session_state["cache_api_info"] = client.get_model_info()
            st.session_state["cache_api_url"] = client.base_url

        health_data = st.session_state["cache_api_health"]
        info_data = st.session_state["cache_api_info"]

        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Estado API", str(health_data.get("status", "-")).upper())
        g2.metric("Modelo", str(info_data.get("classe_modelo_campeao", "-")))
        g3.metric("Registros Censo", f"{int(info_data.get('n_total_censo', 0)):,}")
        g4.metric("Holdout Cego", f"{int(info_data.get('n_holdout_cego', 0)):,}")

        st.markdown(
            f"""
* **Artefato carregado:** `{info_data.get('nome_artefato')}` (`{health_data.get('model_version')}`)
* **SHA-256 ativo:** `{health_data.get('artifact_sha256')}`
* **Modelo MLflow:** `{info_data.get('modelo_registrado_mlflow')}` | **Run ID campeão:** `{info_data.get('mlflow_run_id_campeao')}`
* **Treinamento (UTC):** `{info_data.get('data_treinamento_utc')}` | **Janela:** `{info_data.get('janela_historica')}`
"""
        )

        st.subheader("📊 Métricas Oficiais Registradas no Model Card")
        st.json(info_data.get("metricas_oficiais", {}))
    except EnemApiError as exc:
        st.warning(str(exc))

# ------------------------------------------------------------------------------
# Aba 3: Base de Conhecimento & Link para o RAG/LLM no Hugging Face
# ------------------------------------------------------------------------------
with tab_rag:
    st.subheader("📚 Base de Conhecimento Unificada do TCC & Assistente RAG Externo")
    st.write(
        "Conforme decisão arquitetural, o motor RAG/LLM permanece hospedado de forma independente "
        "no seu Space gratuito do **Hugging Face**, desacoplado da API de inferência e deste cliente."
    )

    c_link, c_dl = st.columns(2)
    with c_link:
        if hf_rag_url and not hf_rag_url.endswith(("SEU_SPACE_RAG", "SEU_USUARIO/SEU_SPACE_RAG")):
            st.link_button(
                "🚀 Acessar Assistente RAG/LLM no Hugging Face",
                url=hf_rag_url,
                type="primary",
                use_container_width=True,
            )
        else:
            st.info(
                "Cole a URL do seu Space RAG/LLM na barra lateral esquerda (ou defina "
                "`HF_RAG_SPACE_URL` em `frontend/.env`) para exibir o botão de redirecionamento."
            )
    with c_dl:
        if KB_PATH.exists():
            st.download_button(
                "📥 Baixar `tcc_enem_completo.md` para o RAG",
                data=KB_PATH.read_bytes(),
                file_name="tcc_enem_completo.md",
                mime="text/markdown",
                use_container_width=True,
            )

    if KB_PATH.exists():
        kb_text = KB_PATH.read_text(encoding="utf-8")
        with st.expander("📖 Pré-visualizar `frontend/knowledge_base/tcc_enem_completo.md`"):
            st.markdown(kb_text)
