"""Esquemas Pydantic para validação e serialização da API de inferência do ENEM.

Baseado estritamente no contrato canônico formalizado em models/enem_model_card.json.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class CandidatoInput(BaseModel):
    """Esquema de entrada para um candidato individual.

    Representa o Esquadrão de Elite de 6 variáveis socioeconômicas
    homologadas para a previsão do TARGET_M4 (TRI).
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "RENDA_PER_CAPITA": 1.5,
                "Q024": 1,
                "TP_ANO_CONCLUIU": 0,
                "TP_LINGUA": 0,
                "TP_SEXO": 0,
                "Q002": 4,
            }
        },
    )

    RENDA_PER_CAPITA: float = Field(
        ...,
        ge=0.0,
        le=25.0,
        description="Renda familiar per capita em salários mínimos por morador (0.0 a 25.0).",
    )
    Q024: int = Field(
        ...,
        ge=0,
        le=3,
        description="Posse de computador no domicílio: 0=Não tem, 1=Sim (um), 2=Sim (dois), 3=Sim (três ou mais).",
    )
    TP_ANO_CONCLUIU: int = Field(
        ...,
        ge=0,
        le=9,
        description="Ano de conclusão do Ensino Médio: 0=Não informado/concluinte no ano, 1=1 ano atrás ... 9=9 ou mais anos atrás.",
    )
    TP_LINGUA: int = Field(
        ...,
        ge=0,
        le=1,
        description="Língua estrangeira escolhida: 0=Inglês, 1=Espanhol.",
    )
    TP_SEXO: int = Field(
        ...,
        ge=0,
        le=1,
        description="Sexo do candidato: 0=Feminino, 1=Masculino.",
    )
    Q002: int = Field(
        ...,
        ge=0,
        le=7,
        description="Escolaridade da mãe / mulher responsável: 0=Nunca estudou a 7=Pós-graduação.",
    )


class BatchCandidatosInput(BaseModel):
    """Esquema de entrada para lote de candidatos."""

    candidatos: List[CandidatoInput] = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Lista de candidatos para inferência vetorial (máximo de 10.000 por requisição).",
    )


class PredictionOutput(BaseModel):
    """Resultado da inferência para um candidato individual."""

    target_m4: float = Field(
        ...,
        description="Nota prevista TARGET_M4 (média das 4 provas objetivas na escala TRI).",
    )
    unidade: str = Field(
        default="pontos_escala_tri_0_a_1000",
        description="Unidade psicométrica da predição.",
    )
    modelo: str = Field(
        default="enem_target_m4_producao:v1",
        description="Identificador e versão do modelo de produção.",
    )


class BatchPredictionOutput(BaseModel):
    """Resultado da inferência em lote."""

    total_candidatos: int = Field(
        ...,
        description="Quantidade total de candidatos processados no lote.",
    )
    predicoes: List[float] = Field(
        ...,
        description="Lista de notas previstas TARGET_M4 na ordem de entrada.",
    )
    tempo_inferencia_ms: float = Field(
        ...,
        description="Tempo de execução da inferência em milissegundos.",
    )
    unidade: str = Field(
        default="pontos_escala_tri_0_a_1000",
        description="Unidade psicométrica da predição.",
    )
    modelo: str = Field(
        default="enem_target_m4_producao:v1",
        description="Identificador e versão do modelo de produção.",
    )


class HealthResponse(BaseModel):
    """Resposta do healthcheck da API."""

    status: str = Field(default="healthy", description="Estado de integridade do serviço.")
    model_loaded: bool = Field(..., description="Indica se o modelo está carregado na memória.")
    model_version: str = Field(..., description="Versão do modelo carregado.")
    artifact_sha256: str = Field(..., description="Hash SHA-256 do arquivo enem.pkl.")


class ModelInfoResponse(BaseModel):
    """Metadados e métricas oficiais de governança do modelo."""

    nome_artefato: str
    modelo_registrado_mlflow: str
    mlflow_run_id_campeao: str
    classe_modelo_campeao: str
    data_treinamento_utc: str
    sha256_enem_pkl: str
    janela_historica: str
    n_total_censo: int
    n_holdout_cego: int
    features_ordenadas: List[str]
    metricas_oficiais: Dict[str, Any]

