---
title: Agente TCC ENEM - TARGET_M4
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.49.1
python_version: "3.13"
app_file: app.py
short_description: Agente RAG do TCC Predição ENEM (TARGET_M4)
license: mit
pinned: false
---

# Agente Especialista do TCC — Predição de Desempenho no ENEM (`TARGET_M4`)

Este Hugging Face Space hospeda o **Agente RAG (Retrieval-Augmented Generation) com memória conversacional** do Trabalho de Conclusão de Curso (MBA), permitindo consultar em linguagem natural toda a metodologia científica, engenharia de atributos, resultados comparativos e arquitetura MLOps do projeto.

## Arquitetura do Agente

- **Interface Web:** Gradio (`sdk: gradio`, compatível com `ZeroGPU Free` no Hugging Face Spaces).
- **Base de Conhecimento:** `knowledge_base/tcc_enem_completo.md` indexada semanticamente por seções Markdown.
- **Embeddings:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (em CPU, alinhado ao Notebook 04 do TCC).
- **Índice Vetorial:** `FAISS` criado automaticamente na inicialização caso `faiss_index/` ainda não exista.
- **LLM + Memória Conversacional:** `gemini-2.5-flash` via `langchain-google-genai`, com `create_history_aware_retriever` e `create_retrieval_chain`.

## Configuração no Hugging Face Spaces

1. No Space **`Prof-Saulo-Santos/agente-tcc-enem-gemini`**, acesse **Settings → Variables and secrets**.
2. Clique em **New secret**:
   - **Name:** `GOOGLE_API_KEY`
   - **Value:** sua chave do Google AI Studio (Gemini).
3. O Space lê automaticamente a variável de ambiente `GOOGLE_API_KEY` (sem armazenar segredos no repositório).

## Execução Local (Opcional)

```bash
cd hf_rag_space
python -m venv .venv
source .venv/bin/activate
pip install gradio==5.49.1 -r requirements.txt
cp .env.example .env  # preencha GOOGLE_API_KEY=...
python app.py
```
