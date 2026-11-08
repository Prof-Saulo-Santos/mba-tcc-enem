# 📊 Roteiro de Slides: Capítulo 07 (Etapa 2) — Produtização FastAPI, Pytest, Docker Multi-Stage e CI/CD AWS

**Projeto de TCC:** MBA em Ciência de Dados / MLOps — Predição de Desempenho no ENEM  
**Autor:** Saulo Santos  
**Módulos de Referência:** [`src/api/`](file:///home/saulo/mba/tcc/enem/src/api/), [`tests/`](file:///home/saulo/mba/tcc/enem/tests/), [`Dockerfile`](file:///home/saulo/mba/tcc/enem/Dockerfile), [`.github/workflows/deploy.yml`](file:///home/saulo/mba/tcc/enem/.github/workflows/deploy.yml) e [`passo-a-passo-07-api-docker.md`](file:///home/saulo/mba/tcc/enem/passo-a-passo-07-api-docker.md)  
**Foco da Defesa:** Produtização do Modelo Campeão (`models/enem.pkl`), Governança de Contrato via **Pydantic v2**, Testes Automatizados (**Pytest 25/25**), Containerização Multi-Stage Enxuta (**FinOps `515 MB`**) e Esteira **CI/CD GitHub Actions $\rightarrow$ Amazon ECR / AWS App Runner**.

---

## 🧭 Visão Panorâmica da Apresentação (Arco Narrativo da Etapa 2 para a Banca)

1. **Do Notebook ao Microserviço (*Model as a Service*):** Como transformar o estimador `XGBRegressor` (`1,73 MB`) treinado em 37,59 milhões de alunos em uma API REST de baixíssima latência (`6,49 ms`).
2. **Governança e Defesa *Anti-Leakage* em Produção:** Uso do `models/enem_model_card.json` e do **Pydantic v2** (`extra="forbid"`) para bloquear em tempo real entradas fora de domínio ou variáveis proibidas como `NU_ANO` (`HTTP 422`).
3. **Engenharia de Testes em Machine Learning:** Auditoria automatizada com **25 testes no Pytest** cobrindo integridade criptográfica (`SHA-256`), fronteiras psicométricas, paridade numérica bit-a-bit e coerência sociológica de Bourdieu.
4. **Arquitetura FinOps em Contêineres:** Separação entre o plano pesado de laboratório (`>5 GB` com PyTorch/SBERT) e o plano leve de inferência (`requirements-api.txt` + `Dockerfile` *multi-stage* com `uv`), reduzindo a imagem OCI para **`515 MB`** sob usuário não-privilegiado (`appuser`).
5. **Automação CI/CD e Nuvem AWS:** Pipeline em 3 estágios no **GitHub Actions** com *Quality Gate*, *Smoke Test Docker E2E* e publicação automatizada no **Amazon ECR / AWS App Runner**.

---

## 🎯 Slide 1 — Arquitetura do Plano Leve de Inferência (*Model as a Service*)
> **Mapeamento no Repositório:** [`src/api/main.py`](file:///home/saulo/mba/tcc/enem/src/api/main.py) e [`src/api/model_loader.py`](file:///home/saulo/mba/tcc/enem/src/api/model_loader.py)

### Mensagem Central
> *"Um modelo de Machine Learning só gera valor público quando sai do Jupyter Notebook e se torna um serviço auditável, imutável e capaz de responder em milissegundos."*

### Layout Visual Recomendado
* **Topo (Diagrama da Etapa 2):**
  `models/enem.pkl (1,73 MB)` + `enem_model_card.json` $\longrightarrow$ `[ModelManager Singleton (Lifespan)]` $\longrightarrow$ `[FastAPI REST: /health | /info | /predict | /predict/batch]` $\longrightarrow$ `Respostas JSON na Escala TRI`.
* **Cards de Indicadores Técnicos na Base do Slide:**
  * **Pegada do Modelo:** `1,727 MB` (`SHA-256: 114f5195...`)
  * **Latência em Lote (Docker):** `6,49 ms` (3 perfis) / `< 82 ms` (10k alunos)
  * **Endpoints Expostos:** `4 rotas REST` + Documentação OpenAPI (`/docs`)

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Padrão *Singleton* no `lifespan`:** O artefato `enem.pkl` é carregado uma única vez na inicialização do servidor ASGI (`Uvicorn`), eliminando I/O de disco a cada requisição HTTP;
* **Verificação Criptográfica no Startup:** O [`ModelManager`](file:///home/saulo/mba/tcc/enem/src/api/model_loader.py#L19-L133) calcula o hash `SHA-256` em blocos de `64 KB` ao subir o serviço e o expõe na rota `/health`;
* **Inferência Dual (Pontual e Vetorial):** Suporte tanto para consulta individual em tempo real (`POST /predict`) quanto para escoragem vetorial de até `10.000` estudantes por requisição (`POST /predict/batch`);
* **Transparência Algorítmica (`GET /info`):** Exposição direta da linhagem do modelo (`MLflow Run ID`, tamanho do censo `37,59M` e métricas oficiais do Holdout e Out-of-Time).

### Trecho de Código para o Slide
```python
# src/api/model_loader.py — Carregamento Singleton e Downcasting Vetorial
df = pd.DataFrame([c.model_dump() for c in candidatos])[self.features_ordenadas]
df = df.astype({"RENDA_PER_CAPITA": "float32", "Q024": "int8", "TP_ANO_CONCLUIU": "int8",
                "TP_LINGUA": "int8", "TP_SEXO": "int8", "Q002": "int8"})
preds = self.model.predict(df)
```

### Roteiro de Fala do Apresentador
> *"Senhores membros da banca, iniciamos a Etapa 2 respondendo a um desafio clássico de MLOps: como colocar em produção um modelo treinado sobre 37,6 milhões de registros sem exigir servidores caros? Graças à parcimônia das 6 features de elite e à poda por Early Stopping no Notebook 06, nosso artefato `enem.pkl` pesa apenas 1,73 megabytes. Encapsulamos esse binário em um microserviço FastAPI com padrão Singleton, garantindo que o modelo permaneça aquecido em memória RAM e entregue predições em poucos milissegundos."*

---

## 🛡️ Slide 2 — Contrato Canônico Pydantic v2 e Defesa *Anti-Leakage* (`HTTP 422`)
> **Mapeamento no Repositório:** [`src/api/schemas.py`](file:///home/saulo/mba/tcc/enem/src/api/schemas.py) e [`models/enem_model_card.json`](file:///home/saulo/mba/tcc/enem/models/enem_model_card.json)

### Mensagem Central
> *"A API atua como um firewall estatístico: nenhum dado fora da escala sociológica do INEP ou variável de vazamento temporal consegue chegar ao motor do XGBoost."*

### Layout Visual Recomendado
* **Tabela do Contrato de Entrada (`CandidatoInput`):**

| Feature (Ordem Canônica) | Tipo Exigido | Domínio Permitido | Significado Sociológico |
| :--- | :---: | :---: | :--- |
| **`RENDA_PER_CAPITA`** | `float32` | `[0.0, 25.0]` | Renda familiar em Salários Mínimos por morador |
| **`Q024`** | `int8` | `{0, 1, 2, 3}` | Posse de computadores na residência (`0` a `3+`) |
| **`TP_ANO_CONCLUIU`** | `int8` | `{0 .. 9}` | Maturidade / Anos desde a conclusão do Ensino Médio |
| **`TP_LINGUA`** | `int8` | `{0, 1}` | Opção de língua estrangeira (`0=Inglês`, `1=Espanhol`) |
| **`TP_SEXO`** | `int8` | `{0, 1}` | Gênero do candidato (`0=Feminino`, `1=Masculino`) |
| **`Q002`** | `int8` | `{0 .. 7}` | Escolaridade materna (`0=Nunca estudou` a `7=Pós-grad.`) |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Validação Declarativa Estrita:** Limites `ge` (*greater or equal*) e `le` (*less or equal*) espelhados diretamente do [`models/enem_model_card.json`](file:///home/saulo/mba/tcc/enem/models/enem_model_card.json);
* **Cláusula `extra="forbid"` (Anti-Leakage em Produção):** Se um cliente tentar enviar `NU_ANO: 2023` ou a nota de redação no corpo do JSON, o Pydantic intercepta a requisição na camada HTTP e devolve **`422 Unprocessable Content`**;
* **Ordenação Determinística de Colunas:** Independentemente da ordem das chaves no JSON enviado pelo usuário, o `ModelManager` reorganiza o `DataFrame` na sequência exata exigida pelos nós das árvores do XGBoost.

### Trecho de Código para o Slide
```python
class CandidatoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Bloqueia NU_ANO e campos externos
    RENDA_PER_CAPITA: float = Field(..., ge=0.0, le=25.0)
    Q024: int = Field(..., ge=0, le=3)
    TP_ANO_CONCLUIU: int = Field(..., ge=0, le=9)
    TP_LINGUA: int = Field(..., ge=0, le=1)
    TP_SEXO: int = Field(..., ge=0, le=1)
    Q002: int = Field(..., ge=0, le=7)
```

### Roteiro de Fala do Apresentador
> *"Em sistemas de Machine Learning em produção, falhas silenciosas ocorrem quando a aplicação aceita categorias inexistentes ou permite a injeção acidental de variáveis vazadas. Nossa camada Pydantic funciona como um guardião de contrato: todas as 6 variáveis possuem travas estritas de intervalo e a diretiva `extra='forbid'` rejeita imediatamente com erro HTTP 422 qualquer campo não homologado, como o ano da prova."*

---

## 🧪 Slide 3 — Engenharia de Qualidade: Suíte Pytest (`25/25 PASSED`)
> **Mapeamento no Repositório:** [`tests/test_api_contract.py`](file:///home/saulo/mba/tcc/enem/tests/test_api_contract.py) e [`tests/test_model_inference.py`](file:///home/saulo/mba/tcc/enem/tests/test_model_inference.py)

### Mensagem Central
> *"Mais do que testar se a API responde HTTP 200, nossa suíte automatizada testa a integridade matemática, a direcionalidade sociológica e o SLA de latência do modelo."*

### Layout Visual Recomendado
* **Quadro de Cobertura dos 25 Testes Automatizados (`15,89s`):**

| Categoria de Teste | Nº de Testes | O que é Comprovado Cientificamente | Resultado |
| :--- | :---: | :--- | :---: |
| **Saúde, Governança e Rotas** | `3` | Redirecionamento `/docs`, hash `SHA-256` em `/health` e fidelidade do `/info` ao Model Card | ✅ `PASSED` |
| **Inferência Nominal e Fronteiras** | `3` | Predição individual (`547,12 pts`), limites extremos (`min`/`max`) e lote vetorial | ✅ `PASSED` |
| **Violação de Domínio e Anti-Leakage** | `14` | 12 testes parametrizados fora de faixa + campo ausente + injeção proibida de `NU_ANO` (`422`) | ✅ `PASSED` |
| **Paridade Matemática e Regressão** | `3` | Igualdade exata entre `API`, `ModelManager` e `joblib.load("models/enem.pkl")` puro | ✅ `PASSED` |
| **Sociologia (Bourdieu) & SLA** | `2` | Diferencial $> +100\text{ pts}$ entre extremos de capital + Lote de `1.000` alunos $< 500\text{ ms}$ | ✅ `PASSED` |

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Zero Divergência Treino-Serviço (*Zero Training-Serving Skew*):** O teste `test_parity_with_raw_xgboost_artifact` prova que o encapsulamento FastAPI não introduz nem um centésimo de ponto de distorção sobre o modelo treinado no Notebook 06;
* **Teste Unitário Sociológico (`test_sociological_directionality_bourdieu`):** Garante que futuras atualizações de código jamais invertam o sinal dos preditores de renda e escolaridade materna.

### Roteiro de Fala do Apresentador
> *"Implementamos 25 testes automatizados divididos em duas suítes. A primeira valida o contrato HTTP com 14 cenários de rejeição parametrizada. A segunda vai além da engenharia de software tradicional: ela executa testes de paridade matemática contra o binário puro do XGBoost, valida o SLA de latência para mil alunos simultâneos e inclui um teste de sanidade sociológica baseado em Bourdieu, garantindo zero distorção entre o laboratório e a nuvem."*

---

## 🐳 Slide 4 — Containerização Multi-Stage Enxuta (`515 MB`) e Homologação Real
> **Mapeamento no Repositório:** [`Dockerfile`](file:///home/saulo/mba/tcc/enem/Dockerfile), [`requirements-api.txt`](file:///home/saulo/mba/tcc/enem/requirements-api.txt) e [`passo-a-passo-07-api-docker.md`](file:///home/saulo/mba/tcc/enem/passo-a-passo-07-api-docker.md)

### Mensagem Central
> *"Isolando apenas os 8 pacotes de inferência em um build multi-stage com `uv`, reduzimos a imagem de >5 GB para 515 MB (OCI) e homologamos a resposta em 6,49 ms."*

### Layout Visual Recomendado
* **Comparativo FinOps de Arquitetura de Imagem:**
  * *Ambiente Completo (Etapa 1/3 com PyTorch + SBERT + Jupyter):* `> 5,0 GB` (Inviável para *cold start* serverless)
  * ***Imagem `enem-target-m4-api:v1` (Etapa 2 Multi-Stage):*** **`515 MB` Content Size** (`1,47 GB` em disco)
* **Log Real Homologado (`saulo@LeCun:enem` — 08/11/2026):**
```text
IMAGE                   ID             DISK USAGE   CONTENT SIZE
enem-target-m4-api:v1   fae92b51099c       1.47GB          515MB
CONTAINER ID   STATUS                    PORTS                    NAMES
3d14c5e44196   Up 27 seconds (healthy)   0.0.0.0:8000->8000/tcp   enem-target-m4-api
```

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Desacoplamento via `requirements-api.txt` e `.dockerignore`:** Bloqueio dos `>25 GB` de dados brutos no contexto de build e instalação exclusiva de `fastapi`, `uvicorn`, `pydantic`, `joblib`, `numpy`, `pandas`, `scikit-learn` e `xgboost` nas versões exatas do treino;
* **Detalhe Crítico de Engenharia Linux (`libgomp1`):** Inclusão explícita da biblioteca compartilhada OpenMP no `python:3.13-slim` para habilitar o multithreading nativo em C++ do XGBoost;
* **Segurança em Nuvem (`appuser`):** Execução sob UID/GID `1000` sem privilégios de `root` e `HEALTHCHECK` nativo em Python.

### Roteiro de Fala do Apresentador
> *"Para que o deploy no AWS App Runner seja rápido e econômico, aplicamos engenharia FinOps rigorosa no Docker. Separamos um manifesto exclusivo de inferência sem o peso do PyTorch e do SBERT, que pertencem ao processamento local da Etapa 3. Usando um Dockerfile multi-stage com o gerenciador `uv`, a biblioteca OpenMP `libgomp1` e usuário não-root, comprimimos a imagem para 515 megabytes. Os testes em container real confirmaram status healthy imediato e inferência em lote para três perfis socioeconômicos em apenas 6,49 milissegundos."*

---

## ☁️ Slide 5 — Esteira CI/CD no GitHub Actions, Amazon ECR e AWS App Runner
> **Mapeamento no Repositório:** [`.github/workflows/deploy.yml`](file:///home/saulo/mba/tcc/enem/.github/workflows/deploy.yml) e [`diagrama_deploy_aws.md`](file:///home/saulo/mba/tcc/enem/diagrama_deploy_aws.md)

### Mensagem Central
> *"Nenhuma imagem chega à nuvem AWS sem antes passar pelo crivo criptográfico do SHA-256, pelos 25 testes Pytest e por um Smoke Test real em container no GitHub Actions."*

### Layout Visual Recomendado
* **Fluxo dos 3 Jobs Encadeados em `.github/workflows/deploy.yml`:**
  `git push origin main` $\longrightarrow$ **`[Job 1: Quality Gate CI (SHA-256 + 25 Testes Pytest)]`** $\longrightarrow$ **`[Job 2: Docker Build & Smoke Test E2E (HTTP 200 & 422)]`** $\longrightarrow$ **`[Job 3: Push Amazon ECR + Deploy AWS App Runner (Trava FinOps)]`**.

### Conteúdo dos Tópicos no Slide (Bullets Curtos)
* **Job 1 (`quality-gate-ci`):** Verifica com `sha256sum` a integridade de `models/enem.pkl` e roda os 25 testes em ~15 segundos;
* **Job 2 (`docker-smoke-test`):** Constrói a imagem no runner Ubuntu, sobe o container e testa `/health`, `/predict` (`547,12 pts`) e o bloqueio `HTTP 422` antes de autorizar o envio para a nuvem;
* **Job 3 (`deploy-aws` com Governança FinOps):** Autentica via OIDC/IAM, envia a imagem taggeada com `$GITHUB_SHA` para o **Amazon ECR** (com *Scan on Push* ativo) e aciona o **AWS App Runner**. Possui trava condicional inteligente que mantém a esteira **100% verde** e a custo zero enquanto o ambiente de nuvem não está em apresentação.

### Roteiro de Fala do Apresentador
> *"Fechamos a Etapa 2 automatizando toda a entrega contínua no GitHub Actions. A esteira possui três barreiras de segurança: o Job 1 audita o hash SHA-256 do modelo e roda o Pytest; o Job 2 constrói o container e faz chamadas HTTP reais dentro do próprio GitHub; e somente após essa dupla aprovação o Job 3 publica a imagem no Amazon ECR e atualiza o AWS App Runner. Com isso, nosso plano leve de inferência está completo, homologado e pronto para interagir com a orquestração da Etapa 3."*

---

## ❓ Perguntas Prováveis da Banca sobre a Etapa 2 (e Respostas Blindadas)

**1. "Por que não colocar o modelo SBERT (NLP) e o Apache Airflow dentro dessa mesma imagem Docker na AWS?"**
> *Resposta:* "Por uma decisão arquitetural fundamentada em **FinOps e Separação de Responsabilidades (Plano Leve vs. Plano Pesado)**. A API de inferência recebe requisições online leves de 6 variáveis numéricas e precisa escalar horizontalmente rápido no AWS App Runner, exigindo uma imagem enxuta (`515 MB`) e *stateless*. Já o SBERT (PyTorch) e o retreinamento sobre 40 milhões de registros exigem gigabytes de bibliotecas neurais e alto processamento em lote (executado apenas uma vez por ano quando o INEP divulga uma nova safra). Manter o plano leve na nuvem e o plano pesado orquestrado em containers locais na Etapa 3 evita desperdício financeiro crônico na AWS sem abrir mão da automação ponta a ponta."

**2. "Por que travar versões exatas (`==`) no `requirements-api.txt` em vez de usar `>=`?"**
> *Resposta:* "Artefatos serializados em árvores binárias (`pickle`/`joblib`) dependem da estabilidade da ABI (*Application Binary Interface*) entre `xgboost`, `scikit-learn`, `numpy` e `pandas`. Travar na imagem Docker exatamente as mesmas versões registradas no `enem_model_card.json` durante o treinamento (`xgboost==3.4.1`, `scikit-learn==1.9.0`, `numpy==2.5.3`) garante reprodutibilidade determinística até a última casa decimal e elimina riscos de incompatibilidade em produção."

---

## 📋 Resumo Executivo — Fechamento Oficial da Etapa 2

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ SÍNTESE DE HOMOLOGAÇÃO DO CAPÍTULO 07 (FECHAMENTO DA ETAPA 2 DO TCC)                         │
├──────────────────────────────┬───────────────────────────────────────────────────────────────┤
│ Dimensão Auditada            │ Resultado Oficial Homologado                                  │
├──────────────────────────────┼───────────────────────────────────────────────────────────────┤
│ Framework de Serving         │ FastAPI 0.162.0 + Uvicorn 0.54.0 + Pydantic 2.13.5            │
│ Blindagem de Contrato        │ Domínios estritos + extra="forbid" (HTTP 422 contra Leakage)  │
│ Suíte Automatizada (Pytest)  │ 25/25 testes aprovados (Contrato, Paridade, Bourdieu e SLA)   │
│ Imagem Docker Multi-Stage    │ enem-target-m4-api:v1 (515 MB Content Size | appuser UID 1000)│
│ Latência Real em Container   │ 6,49 ms (lote vetorial de 3 perfis socioeconômicos)           │
│ Esteira CI/CD                │ .github/workflows/deploy.yml (3 Jobs -> ECR & App Runner)     │
└──────────────────────────────┴───────────────────────────────────────────────────────────────┘
```

