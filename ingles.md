# 🇺🇸 Guia Estratégico e Plano de Ação: Processo Seletivo AI Coding Evaluator (EUA)

Este documento foi elaborado para guiar a preparação, seleção e estruturação do projeto de software exigido para a oportunidade de trabalho como avaliador de assistentes de codificação de IA (*AI Coding Assistant Evaluator / RLHF / Side-by-Side Reviewer*).

---

## 🚨 1. Alerta Crítico de Elegibilidade (Por que NÃO usar o TCC ENEM)

As diretrizes do programa estabelecem regras rígidas sobre projetos elegíveis e inelegíveis:

### ❌ O que é PROIBIDO pelo regulamento:
* **"Work for an employer, client or university":** O projeto do ENEM é um Trabalho de Conclusão de Curso (TCC) de um MBA universitário.
* **"AI model training or evaluation; ML infrastructure":** O projeto do ENEM é essencialmente treinamento de modelos (XGBoost/Random Forest), validação de métricas de ML e infraestrutura de MLOps (MLflow/Airflow).
* **"Projects that process other people’s personal data":** Os microdados do ENEM tratam de dados individuais de milhões de estudantes brasileiros (notas, raça, renda familiar).

> [!CAUTION]
> **Veredito:** Submeter o projeto do ENEM levará à **desqualificação imediata** por violar 3 regras fundamentais de elegibilidade. Você precisa de um **projeto de Engenharia de Software clássica**, de sua autoria exclusiva, sem relação com universidade, sem dados pessoais e sem modelos de Machine Learning.

---

## 🎯 2. O que a Empresa Norte-Americana Realmente Espera

A dinâmica da vaga é de avaliação comparativa **Side-by-Side (SxS)**:
1. Você trabalha no seu projeto usando a plataforma proprietária da empresa com um assistente de IA;
2. A cada instrução que você dá, a plataforma gera **duas respostas concorrentes** (Modelo A vs. Modelo B);
3. Você escolhe a melhor resposta e escreve uma justificativa técnica concisa em **Inglês** explicando o porquê.

### O Projeto Ideal Deve:
* Ser 100% seu (*solely owned*);
* Conter licença de código aberto aprovada (**MIT License**);
* Ter arquitetura limpa, modular e moderna (ex.: Python com `FastAPI`, `Pydantic`, `pytest`, `Click` ou `Typer`);
* Ter tarefas naturais a realizar: novas funcionalidades, correção de bugs, criação de testes unitários, refatoração de código e documentação.

---

## 💡 3. Sugestões de Projetos "Prontos para Aprovação"

Recomendo criar um projeto novo em um diretório à parte (ex.: `/home/saulo/projects/`). Escolha uma das 3 opções abaixo:

### 🏆 Opção Recomendada: `dev-doc-audit` (CLI de Auditoria de Documentação e Código)
* **O que é:** Uma ferramenta de linha de comando em Python para desenvolvedores que analisa um repositório git, checa se funções possuem docstrings no padrão Google/Sphinx, valida links quebrados em arquivos Markdown e calcula cobertura de documentação.
* **Por que é perfeita:**
  * Não usa dados de ninguém (apenas lê arquivos locais);
  * É 100% engenharia de software pura;
  * Gera tarefas infinitas para pedir à IA (adicionar novas regras, gerar relatórios em JSON/HTML, criar testes com `pytest`, criar CLI com `Typer`).

### Opção B: `fast-vault-api` (API REST Assíncrona de Armazenamento Seguro de Snippets)
* **O que é:** Um microsserviço leve construído com FastAPI, SQLite e SQLAlchemy para salvar, categorizar e buscar snippets de código e notas com autenticação JWT.
* **Tarefas para a IA:** Criar endpoints CRUD, implementar paginação, adicionar validações no Pydantic, escrever suíte de testes assíncronos com `httpx`.

### Opção C: `pysql-sanitizer` (Biblioteca Open-Source de Sanitização e Lint de SQL)
* **O que é:** Um pacote Python leve que analisa queries SQL procurando anti-padrões, ausência de cláusulas WHERE em deletes/updates e formata o código SQL.

---

## 📋 4. Plano de Ação Passo a Passo para o Novo Chat

Ao abrir o novo chat, siga esta sequência ordenada:

### Passo 1: Inicialização do Repositório Limpo
1. Criar o diretório isolado: `mkdir -p /home/saulo/projects/dev-doc-audit && cd /home/saulo/projects/dev-doc-audit`;
2. Inicializar o git com branch `main`;
3. Criar o arquivo `LICENSE` com a licença **MIT** em seu nome;
4. Criar `.gitignore` para Python e `pyproject.toml` (usando `uv`).

### Passo 2: Construção da Base Funcional Mínima (MVP em 15 minutos)
1. Criar o módulo principal `src/doc_audit/core.py`;
2. Criar o ponto de entrada CLI `src/doc_audit/cli.py` utilizando `typer` ou `argparse`;
3. Implementar uma funcionalidade básica funcional (ex.: varrer arquivos `.md` e reportar contagem de linhas e seções).

### Passo 3: Criação de um "Backlog de Avaliação" (10 Tasks Prontas)
Planejar as instruções que você dará na plataforma americana para gerar comparações ricas entre os modelos A e B:
* *Task 1 (Feature):* "Implement a parser to detect missing docstrings in Python functions with AST."
* *Task 2 (Refactor):* "Refactor the Markdown scanner to run asynchronously using asyncio for multi-file repositories."
* *Task 3 (Bugfix):* "Fix an edge case where empty markdown files cause an unexpected IndexError."
* *Task 4 (Testing):* "Write a comprehensive pytest suite with at least 8 test cases and fixtures."
* *Task 5 (Documentation):* "Write a professional README.md with installation, usage examples, badges, and CLI arguments."

---

## ✍️ 5. Guia Prático para Escrever Justificativas Técnicas em Inglês (SxS Feedback)

A empresa avaliará a sua capacidade técnica de discernir o melhor código e justificar com precisão. Evite respostas vagas como *"Response A is better"* ou *"I like B"*.

### Critérios de Avaliação e Frases-Modelo:

#### 1. Correção e Robustez (Correctness & Edge Cases)
* *"Response A is significantly better because it handles edge cases (such as empty input lists and None values) using explicit guard clauses, whereas Response B raises an unhandled `TypeError`."*
* *"Model B correctly identified the off-by-one error in the slicing logic and avoided mutating the original dictionary."*

#### 2. Padrões de Projeto e Estilo (Code Quality & Idiomatic Style)
* *"Response B adheres strictly to PEP8 standards, provides accurate type hints (`dict[str, Any]`), and writes clean docstrings. Response A used legacy string formatting and lacked type annotations."*
* *"Model A used list comprehensions idiomatically, improving performance, while Model B wrote redundant nested loops."*

#### 3. Completude e Executabilidade (Completeness vs Hallucination)
* *"Response A provided fully runnable, drop-in replacement code. Response B left `pass` and `# TODO` comments inside the core logic, requiring extra manual implementation."*
* *"Model B hallucinated a non-existent parameter `strict=True` for the parser method, which causes a runtime `ValueError`."*

#### 4. Qualidade de Testes (Test Coverage & Fixtures)
* *"Response A included parameterized `pytest` unit tests covering both positive and negative scenarios, while Response B only wrote a single trivial test assertion."*

---

## 🔒 6. Checklist de Segurança antes de Iniciar as Sessões
* [ ] Nenhuma chave de API (OpenAI, AWS, Google) commitada ou exibida no terminal;
* [ ] Nenhum arquivo `.env` enviado no chat;
* [ ] Nenhum dado real de pessoas, clientes ou empresas;
* [ ] Todo o feedback escrito diretamente por você em inglês fluente e técnico.

---

## 🚀 Como Proceder Agora:

1. Este arquivo [ingles.md](file:///home/saulo/mba/tcc/enem/ingles.md) está salvo na raiz e servirá de roteiro completo;
2. **Abra um novo chat** e inicie dizendo:
   > *"Estou iniciando a preparação do meu projeto de software para a vaga internacional de AI Coding Evaluator, conforme planejado no arquivo `ingles.md`. Vamos construir o projeto `dev-doc-audit` do zero em `/home/saulo/projects/`."*
3. Quando concluir a submissão desse projeto na empresa, retornaremos a este chat para construirmos o **Notebook 05** e finalizar seu TCC!
