"""Cliente HTTP isolado e gerador de candidatos sintéticos para a API ENEM TARGET_M4.

Consome os endpoints REST `/health`, `/info`, `/predict` e `/predict/batch` sem
nenhum acoplamento de importação com `src/api/`.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

import httpx

MEDIA_HISTORICA_DECADA = 511.05
MAX_CANDIDATOS_LOTE = 10_000

OPCOES_Q024: Dict[int, str] = {
    0: "0 — Nenhum computador no domicílio",
    1: "1 — 1 computador",
    2: "2 — 2 computadores",
    3: "3 — 3 ou mais computadores",
}

OPCOES_TP_ANO_CONCLUIU: Dict[int, str] = {
    0: "0 — Não informado / concluinte no ano",
    1: "1 — Concluiu há 1 ano",
    2: "2 — Concluiu há 2 anos",
    3: "3 — Concluiu há 3 anos",
    4: "4 — Concluiu há 4 anos",
    5: "5 — Concluiu há 5 anos",
    6: "6 — Concluiu há 6 anos",
    7: "7 — Concluiu há 7 anos",
    8: "8 — Concluiu há 8 anos",
    9: "9 — Concluiu há 9 ou mais anos",
}

OPCOES_TP_LINGUA: Dict[int, str] = {
    0: "0 — Inglês",
    1: "1 — Espanhol",
}

OPCOES_TP_SEXO: Dict[int, str] = {
    0: "0 — Feminino (F)",
    1: "1 — Masculino (M)",
}

OPCOES_Q002: Dict[int, str] = {
    0: "0 — Nunca estudou",
    1: "1 — Ensino Fundamental I incompleto",
    2: "2 — Ensino Fundamental I completo / II incompleto",
    3: "3 — Ensino Fundamental completo / Médio incompleto",
    4: "4 — Ensino Médio completo / Superior incompleto",
    5: "5 — Ensino Superior completo",
    6: "6 — Pós-graduação",
    7: "7 — Não sei informar",
}


class EnemApiError(RuntimeError):
    """Erro amigável para falhas de conexão ou resposta HTTP da API ENEM."""


def gerar_alunos_aleatorios(
    quantidade: int,
    seed: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Gera `quantidade` perfis sintéticos válidos segundo o contrato da API.

    Todas as 6 variáveis respeitam estritamente os intervalos do modelo Pydantic
    (`RENDA_PER_CAPITA` em `[0.0, 25.0]`, `Q024` em `{0..3}`, `TP_ANO_CONCLUIU`
    em `{0..9}`, `TP_LINGUA` em `{0, 1}`, `TP_SEXO` em `{0, 1}`, `Q002` em `{0..7}`).
    """
    if not 1 <= quantidade <= MAX_CANDIDATOS_LOTE:
        raise ValueError(
            f"A quantidade deve estar entre 1 e {MAX_CANDIDATOS_LOTE} candidatos."
        )

    rng = random.Random(seed)
    candidatos: List[Dict[str, Any]] = []

    # Pesos levemente realistas para renda (concentração maior em faixas baixas/médias,
    # mantendo amostras em faixas altas até 25 SM para exercitar amplitude completa).
    for _ in range(quantidade):
        faixa = rng.random()
        if faixa < 0.55:
            renda = round(rng.uniform(0.0, 1.5), 2)
        elif faixa < 0.88:
            renda = round(rng.uniform(1.5, 5.0), 2)
        else:
            renda = round(rng.uniform(5.0, 25.0), 2)

        candidatos.append(
            {
                "RENDA_PER_CAPITA": renda,
                "Q024": rng.choices([0, 1, 2, 3], weights=[40, 38, 15, 7], k=1)[0],
                "TP_ANO_CONCLUIU": rng.randint(0, 9),
                "TP_LINGUA": rng.choice([0, 1]),
                "TP_SEXO": rng.choice([0, 1]),
                "Q002": rng.randint(0, 7),
            }
        )

    return candidatos


class EnemApiClient:
    """Cliente HTTP síncrono para comunicação com a API FastAPI do ENEM."""

    def __init__(self, base_url: str, timeout_seconds: float = 30.0) -> None:
        self.base_url = base_url.strip().rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _request(
        self,
        method: str,
        path: str,
        json_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.request(method, url, json=json_payload)
        except httpx.ConnectError as exc:
            raise EnemApiError(
                f"Não foi possível conectar em `{self.base_url}`. "
                "Verifique se a API FastAPI está em execução."
            ) from exc
        except httpx.TimeoutException as exc:
            raise EnemApiError(
                f"Tempo limite ({self.timeout_seconds:.0f}s) excedido ao chamar `{url}`."
            ) from exc
        except httpx.HTTPError as exc:
            raise EnemApiError(f"Erro HTTP ao chamar `{url}`: {exc}") from exc

        if response.status_code >= 400:
            try:
                detalhe = response.json()
            except ValueError:
                detalhe = response.text
            raise EnemApiError(
                f"A API retornou HTTP {response.status_code} em `{path}`: {detalhe}"
            )

        data: Dict[str, Any] = response.json()
        return data

    def check_health(self) -> Dict[str, Any]:
        """Consulta `GET /health`."""
        return self._request("GET", "/health")

    def get_model_info(self) -> Dict[str, Any]:
        """Consulta `GET /info`."""
        return self._request("GET", "/info")

    def predict_single(self, candidato: Dict[str, Any]) -> Dict[str, Any]:
        """Envia 1 candidato para `POST /predict`."""
        return self._request("POST", "/predict", json_payload=candidato)

    def predict_batch(self, candidatos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Envia lote de candidatos para `POST /predict/batch`."""
        return self._request(
            "POST",
            "/predict/batch",
            json_payload={"candidatos": candidatos},
        )
