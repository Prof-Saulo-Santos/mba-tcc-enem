"""Agente RAG conversacional do TCC ENEM (TARGET_M4) para Hugging Face Spaces (Gradio)."""

import hashlib
import logging
import os
import re
import unicodedata
from pathlib import Path
from typing import Any

# ZeroGPU exige `import spaces` antes de carregar bibliotecas baseadas em PyTorch/CUDA.
try:
    import spaces  # type: ignore[import-not-found]
except ImportError:
    spaces = None

import gradio as gr  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from langchain_classic.chains import (  # noqa: E402
    create_history_aware_retriever,
    create_retrieval_chain,
)
from langchain_classic.chains.combine_documents import (  # noqa: E402
    create_stuff_documents_chain,
)
from langchain_community.vectorstores import FAISS  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # noqa: E402
from langchain_core.runnables import RunnableLambda  # noqa: E402
from langchain_google_genai import ChatGoogleGenerativeAI  # noqa: E402
from langchain_huggingface import HuggingFaceEmbeddings  # noqa: E402
from langchain_text_splitters import (  # noqa: E402
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tcc_enem_rag_space")

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base" / "tcc_enem_completo.md"
FAISS_INDEX_DIR = BASE_DIR / "faiss_index"
KB_HASH_FILE = FAISS_INDEX_DIR / "kb.sha256"

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
GEMINI_MODEL = "gemini-2.5-flash"

TOP_K_FINAL = 8
STOPWORDS_PT = {
    "a", "ao", "aos", "as", "com", "como", "da", "das", "de", "do", "dos",
    "e", "em", "entre", "essa", "esse", "esta", "este", "foi", "foram",
    "mais", "na", "nas", "no", "nos", "o", "os", "ou", "para", "pela",
    "pelas", "pelo", "pelos", "por", "quais", "qual", "que", "sao", "se",
    "sem", "ser", "sobre", "suas", "seus", "tinham", "sido", "um", "uma",
}

INITIAL_GREETING = (
    "Olá! Eu sou o Agente Especialista do TCC de MBA sobre Predição de Desempenho no ENEM "
    "(`TARGET_M4`) e Arquitetura MLOps. Posso responder dúvidas com base exclusiva no "
    "dossiê técnico do projeto: metodologia, prevenção de *data leakage*, engenharia das "
    "6 features, modelos avaliados (`DummyRegressor`, `Ridge`, `RandomForestRegressor` e "
    "`XGBRegressor`, além de `HistGradientBoostingRegressor` na seleção de alvo) e arquitetura "
    "MLOps na AWS. Como posso ajudar hoje?"
)

EXAMPLE_QUESTIONS = [
    "Quais modelos foram avaliados no TCC e por que o XGBoost foi escolhido para produção?",
    "Como é calculado o TARGET_M4 e por que ele é mais adequado para a TRI?",
    "Quais estratégias garantem ausência de data leakage nas 6 features?",
    "Como funciona a arquitetura MLOps com FastAPI, Docker, MLflow e AWS App Runner?",
]

CONTEXTUALIZE_Q_PROMPT = (
    "Dado o histórico da conversa e a última pergunta do usuário "
    "(que pode fazer referência ao contexto anterior), formule uma "
    "pergunta autônoma que possa ser compreendida sem o histórico. "
    "NÃO responda à pergunta; apenas reformule-a se necessário ou "
    "retorne-a exatamente como está."
)

QA_SYSTEM_PROMPT = (
    "Você é o Agente Especialista do TCC de MBA sobre Predição de Desempenho no ENEM "
    "(TARGET_M4) e Arquitetura MLOps. Responda sempre em Português do Brasil com rigor "
    "científico, clareza e objetividade.\n\n"
    "REGRAS OBRIGATÓRIAS DE FIDELIDADE (ATERRO AO CONTEXTO):\n"
    "1. Baseie sua resposta EXCLUSIVAMENTE nos trechos recuperados abaixo (`context`).\n"
    "2. É TERMINANTEMENTE PROIBIDO completar listas ou acrescentar algoritmos, métricas, "
    "etapas ou bibliotecas vindos do seu conhecimento geral prévio que não estejam "
    "escritos literalmente nos trechos abaixo.\n"
    "3. Ao citar algoritmos ou tecnologias, diferencie claramente o que foi **efetivamente "
    "avaliado/implementado** no experimento principal do que foi usado apenas em etapa "
    "auxiliar ou citado somente como **Trabalho Futuro**.\n"
    "4. Se algum dado solicitado não constar nos trechos recuperados, informe "
    "explicitamente que esse detalhe não está registrado no contexto recuperado.\n\n"
    "{context}"
)

if spaces is not None:

    @spaces.GPU(duration=1)
    def _zerogpu_startup_probe() -> str:
        """Mantém compatibilidade com a verificação de startup do ZeroGPU no HF Spaces."""
        return "ok"


_INDEX_CACHE: tuple[str, FAISS, list[Document]] | None = None
_RAG_CACHE: tuple[str, Any] | None = None


def _compute_kb_sha256(kb_path: Path = KNOWLEDGE_BASE_PATH) -> str:
    """Calcula SHA-256 da base de conhecimento para invalidar índice FAISS defasado."""
    if not kb_path.exists():
        raise FileNotFoundError(f"Base de conhecimento não encontrada em: {kb_path}")
    return hashlib.sha256(kb_path.read_bytes()).hexdigest()


def _split_knowledge_base(kb_path: Path = KNOWLEDGE_BASE_PATH) -> list[Document]:
    """Segmenta o Markdown por seções preservando cabeçalhos no texto e metadados."""
    if not kb_path.exists():
        raise FileNotFoundError(f"Base de conhecimento não encontrada em: {kb_path}")

    raw_text = kb_path.read_text(encoding="utf-8")
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "documento"),
            ("##", "secao"),
            ("###", "subsecao"),
        ],
        strip_headers=False,
    )
    section_docs = header_splitter.split_text(raw_text)

    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=220,
    )
    chunks = char_splitter.split_documents(section_docs)
    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = idx
        chunk.metadata["source"] = kb_path.name
        secao = chunk.metadata.get("secao", "Visão Geral")
        subsecao = chunk.metadata.get("subsecao")
        header_label = f"{secao} > {subsecao}" if subsecao else secao
        # Embute o título hierárquico no texto indexado para fortalecer busca vetorial e léxica.
        if not chunk.page_content.lstrip().startswith("#"):
            chunk.page_content = f"[Seção: {header_label}]\n{chunk.page_content}"
    return chunks


def get_vectorstore_and_chunks() -> tuple[FAISS, list[Document]]:
    """Carrega ou reconstrói o índice FAISS em CPU e retorna também os chunks para RRF."""
    global _INDEX_CACHE
    kb_sha = _compute_kb_sha256()
    if _INDEX_CACHE is not None and _INDEX_CACHE[0] == kb_sha:
        return _INDEX_CACHE[1], _INDEX_CACHE[2]

    chunks = _split_knowledge_base()
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )

    index_file = FAISS_INDEX_DIR / "index.faiss"
    stored_sha = KB_HASH_FILE.read_text(encoding="utf-8").strip() if KB_HASH_FILE.exists() else ""
    if index_file.exists() and stored_sha == kb_sha:
        try:
            logger.info("Carregando índice FAISS atualizado de %s", FAISS_INDEX_DIR)
            vectorstore = FAISS.load_local(
                str(FAISS_INDEX_DIR),
                embeddings,
                allow_dangerous_deserialization=True,
            )
            _INDEX_CACHE = (kb_sha, vectorstore, chunks)
            return vectorstore, chunks
        except Exception:
            logger.warning("Falha ao carregar FAISS existente; reconstruindo índice.")

    logger.info("Indexando base %s (%d chunks) com %s", KNOWLEDGE_BASE_PATH, len(chunks), EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    try:
        FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(FAISS_INDEX_DIR))
        KB_HASH_FILE.write_text(kb_sha, encoding="utf-8")
    except OSError:
        logger.warning("Não foi possível persistir faiss_index em disco; mantendo em memória.")

    _INDEX_CACHE = (kb_sha, vectorstore, chunks)
    return vectorstore, chunks


def _tokenize_pt(text: str) -> list[str]:
    """Normaliza acentos e extrai termos relevantes para busca léxica complementar."""
    normalized = unicodedata.normalize("NFKD", text.lower())
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    tokens = re.findall(r"[a-z0-9_]{2,}", ascii_text)
    return [tok for tok in tokens if tok not in STOPWORDS_PT]


def _lexical_rank_chunks(query: str, chunks: list[Document]) -> list[int]:
    """Ordena chunks por correspondência léxica (exata + radical), priorizando títulos."""
    query_tokens = _tokenize_pt(query)
    if not query_tokens:
        return []

    scored: list[tuple[float, int]] = []
    for doc in chunks:
        chunk_id = int(doc.metadata.get("chunk_id", -1))
        if chunk_id < 0:
            continue
        header_text = " ".join(
            str(doc.metadata.get(k, "")) for k in ("documento", "secao", "subsecao")
        )
        header_tokens = set(_tokenize_pt(header_text))
        body_tokens = set(_tokenize_pt(doc.page_content))
        header_stems = {tok[:5] for tok in header_tokens if len(tok) >= 5}
        body_stems = {tok[:5] for tok in body_tokens if len(tok) >= 5}

        score = 0.0
        for q_tok in query_tokens:
            q_stem = q_tok[:5] if len(q_tok) >= 5 else q_tok
            if q_tok in header_tokens:
                score += 3.0
            elif q_tok in body_tokens:
                score += 1.5
            elif len(q_stem) >= 5 and q_stem in header_stems:
                score += 1.5
            elif len(q_stem) >= 5 and q_stem in body_stems:
                score += 0.75
        if score > 0.0:
            scored.append((score, chunk_id))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk_id for _, chunk_id in scored]


def hybrid_retrieve(query: str, k: int = TOP_K_FINAL) -> list[Document]:
    """Combina ranking vetorial (FAISS) e léxico via Reciprocal Rank Fusion (RRF)."""
    vectorstore, chunks = get_vectorstore_and_chunks()
    chunk_by_id = {int(doc.metadata["chunk_id"]): doc for doc in chunks}

    dense_docs = vectorstore.similarity_search(query, k=min(12, len(chunks)))
    lexical_ids = _lexical_rank_chunks(query, chunks)[: min(12, len(chunks))]

    rrf_scores: dict[int, float] = {}
    for rank, doc in enumerate(dense_docs, start=1):
        cid = int(doc.metadata.get("chunk_id", -1))
        if cid in chunk_by_id:
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (60.0 + rank)

    for rank, cid in enumerate(lexical_ids, start=1):
        if cid in chunk_by_id:
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.25 / (60.0 + rank)

    ranked_ids = sorted(rrf_scores, key=lambda cid: rrf_scores[cid], reverse=True)[:k]
    return [chunk_by_id[cid] for cid in ranked_ids]


def _get_rag_chain(api_key: str) -> Any:
    """Inicializa e reutiliza a cadeia RAG conversacional híbrida com Gemini 2.5 Flash."""
    global _RAG_CACHE
    if _RAG_CACHE is not None and _RAG_CACHE[0] == api_key:
        return _RAG_CACHE[1]

    get_vectorstore_and_chunks()
    hybrid_retriever = RunnableLambda(lambda query: hybrid_retrieve(str(query)))

    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0.0,
        api_key=api_key,
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CONTEXTUALIZE_Q_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm,
        hybrid_retriever,
        contextualize_q_prompt,
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", QA_SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    _RAG_CACHE = (api_key, rag_chain)
    return rag_chain


def _extract_text(content: Any) -> str:
    """Extrai texto limpo de payloads string ou blocos multimodais do Gradio."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return str(content)


def _to_langchain_history(history: list[dict[str, Any]] | None) -> list[HumanMessage | AIMessage]:
    """Converte histórico `messages` do Gradio em objetos de mensagem do LangChain."""
    lc_messages: list[HumanMessage | AIMessage] = []
    for entry in history or []:
        role = entry.get("role") if isinstance(entry, dict) else getattr(entry, "role", None)
        raw_content = (
            entry.get("content") if isinstance(entry, dict) else getattr(entry, "content", "")
        )
        text = _extract_text(raw_content).strip()
        if not text:
            continue
        if role == "assistant" and text == INITIAL_GREETING:
            continue
        if role == "user":
            lc_messages.append(HumanMessage(content=text))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=text))
    return lc_messages


def _format_sources_markdown(context_docs: list[Document]) -> str:
    """Formata os trechos recuperados do TCC para exibição transparente ao avaliador."""
    if not context_docs:
        return "Nenhum trecho recuperado para esta consulta."

    lines: list[str] = []
    for idx, doc in enumerate(context_docs, start=1):
        source = doc.metadata.get("source", KNOWLEDGE_BASE_PATH.name)
        secao = doc.metadata.get("secao", "Visão Geral")
        subsecao = doc.metadata.get("subsecao")
        header = f"{secao} → {subsecao}" if subsecao else secao
        excerpt = " ".join(doc.page_content.strip().split())
        if len(excerpt) > 360:
            excerpt = f"{excerpt[:357]}..."
        lines.append(f"**Trecho {idx}** (`{source}` — *{header}*)\n> {excerpt}")
    return "\n\n---\n\n".join(lines)


def respond(
    user_message: str,
    history: list[dict[str, Any]] | None,
) -> tuple[str, list[dict[str, str]], str]:
    """Processa uma pergunta no chat mantendo memória conversacional e citando fontes."""
    cleaned = user_message.strip()
    updated_history: list[dict[str, str]] = [
        {
            "role": str(item.get("role") if isinstance(item, dict) else getattr(item, "role", "")),
            "content": _extract_text(
                item.get("content") if isinstance(item, dict) else getattr(item, "content", "")
            ),
        }
        for item in (history or [])
    ]
    if not cleaned:
        return "", updated_history, "Digite uma pergunta para consultar os documentos do TCC."

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        updated_history.append({"role": "user", "content": cleaned})
        updated_history.append(
            {
                "role": "assistant",
                "content": (
                    "⚠️ Chave `GOOGLE_API_KEY` não configurada neste Space.\n\n"
                    "No Hugging Face Spaces, acesse **Settings → Variables and secrets → "
                    "New secret**, defina `GOOGLE_API_KEY` com sua chave do Google AI Studio "
                    "e reinicie o Space."
                ),
            }
        )
        return "", updated_history, "Aguardando configuração do segredo `GOOGLE_API_KEY`."

    lc_history = _to_langchain_history(updated_history)
    updated_history.append({"role": "user", "content": cleaned})

    try:
        rag_chain = _get_rag_chain(api_key)
        result = rag_chain.invoke({"input": cleaned, "chat_history": lc_history})
        answer = str(result.get("answer", "")).strip() or "Não foi possível gerar resposta."
        sources_md = _format_sources_markdown(result.get("context", []))
    except Exception:
        logger.exception("Erro ao consultar a cadeia RAG.")
        answer = (
            "❌ Ocorreu um erro ao consultar o modelo Gemini ou o índice FAISS. "
            "Verifique se a chave `GOOGLE_API_KEY` está válida e tente novamente."
        )
        sources_md = "Consulta interrompida por erro de execução."

    updated_history.append({"role": "assistant", "content": answer})
    return "", updated_history, sources_md


def clear_conversation() -> tuple[str, list[dict[str, str]], str]:
    """Reinicia o histórico de chat preservando a saudação inicial."""
    return (
        "",
        [{"role": "assistant", "content": INITIAL_GREETING}],
        "Nenhuma consulta realizada após a limpeza do histórico.",
    )


def build_demo() -> gr.Blocks:
    """Constrói a interface Gradio do Agente Especialista do TCC."""
    with gr.Blocks(title="Agente TCC ENEM - TARGET_M4", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "# 🎓 Agente Especialista do TCC — Predição ENEM (`TARGET_M4`)\n"
            "Faça perguntas sobre a metodologia científica, prevenção de *data leakage*, "
            "engenharia das 6 features, comparação de modelos (`DummyRegressor`, `Ridge`, "
            "`RandomForestRegressor`, `XGBRegressor` e `HistGradientBoostingRegressor` na seleção "
            "de alvo) e arquitetura MLOps na AWS."
        )

        chatbot = gr.Chatbot(
            value=[{"role": "assistant", "content": INITIAL_GREETING}],
            type="messages",
            height=460,
            show_label=False,
        )

        with gr.Accordion("📚 Ver Documentos Fonte (última consulta)", open=False):
            sources_output = gr.Markdown("Nenhuma consulta realizada ainda.")

        with gr.Row():
            prompt_input = gr.Textbox(
                placeholder="Digite sua dúvida sobre o TCC aqui...",
                show_label=False,
                scale=7,
            )
            send_btn = gr.Button("Enviar", variant="primary", scale=1)
            clear_btn = gr.Button("Limpar", variant="secondary", scale=1)

        gr.Examples(
            examples=[[question] for question in EXAMPLE_QUESTIONS],
            inputs=[prompt_input],
            label="Perguntas sugeridas para a banca",
        )

        prompt_input.submit(
            fn=respond,
            inputs=[prompt_input, chatbot],
            outputs=[prompt_input, chatbot, sources_output],
        )
        send_btn.click(
            fn=respond,
            inputs=[prompt_input, chatbot],
            outputs=[prompt_input, chatbot, sources_output],
        )
        clear_btn.click(
            fn=clear_conversation,
            inputs=[],
            outputs=[prompt_input, chatbot, sources_output],
        )

    return demo


demo = build_demo()


if __name__ == "__main__":
    # Pré-carrega o índice vetorial em CPU antes de abrir o servidor para respostas rápidas.
    try:
        get_vectorstore_and_chunks()
    except Exception:
        logger.exception("Pré-carregamento do FAISS falhou; será tentado novamente na 1ª pergunta.")
    demo.launch()
