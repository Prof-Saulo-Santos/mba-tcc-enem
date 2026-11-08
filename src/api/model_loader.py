"""Carregador e gerenciador de inferência do modelo do ENEM (Singleton).

Gerencia o ciclo de vida do modelo serializado `models/enem.pkl` e do
contrato de governança `models/enem_model_card.json`.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pandas as pd

from src.api.schemas import CandidatoInput


class ModelManager:
    """Singleton responsável pelo carregamento e execução de inferências."""

    _instance: Optional["ModelManager"] = None

    def __init__(
        self,
        model_path: Optional[str] = None,
        model_card_path: Optional[str] = None,
    ) -> None:
        project_root = Path(__file__).resolve().parent.parent.parent

        self.model_path = Path(
            model_path or os.getenv("MODEL_PATH", project_root / "models" / "enem.pkl")
        )
        self.model_card_path = Path(
            model_card_path
            or os.getenv("MODEL_CARD_PATH", project_root / "models" / "enem_model_card.json")
        )

        self.model = None
        self.model_card: Dict[str, Any] = {}
        self.sha256: str = ""
        self.features_ordenadas: List[str] = [
            "RENDA_PER_CAPITA",
            "Q024",
            "TP_ANO_CONCLUIU",
            "TP_LINGUA",
            "TP_SEXO",
            "Q002",
        ]

    @classmethod
    def get_instance(cls) -> "ModelManager":
        """Retorna a instância única do gerenciador de modelo."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self) -> None:
        """Carrega o modelo serializado e o cartão de governança."""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Artefato do modelo não encontrado no caminho: {self.model_path}"
            )

        # Cálculo do SHA256 do arquivo em disco
        sha256_hash = hashlib.sha256()
        with open(self.model_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        self.sha256 = sha256_hash.hexdigest()

        # Carregamento do estimador (XGBRegressor puro)
        self.model = joblib.load(self.model_path)

        # Carregamento do Model Card
        if self.model_card_path.exists():
            with open(self.model_card_path, "r", encoding="utf-8") as f:
                self.model_card = json.load(f)

            card_features = (
                self.model_card.get("contrato_inferencia_api", {}).get("features_ordenadas")
            )
            if card_features:
                self.features_ordenadas = card_features

    def is_loaded(self) -> bool:
        """Verifica se o modelo está pronto na memória."""
        return self.model is not None

    def _preparar_dataframe(self, candidatos: List[CandidatoInput]) -> pd.DataFrame:
        """Converte uma lista de Pydantic models em DataFrame otimizado para o XGBoost."""
        dados = [c.model_dump() for c in candidatos]
        df = pd.DataFrame(dados)[self.features_ordenadas]

        # Tipagem compatível com o treinamento consolidado
        df = df.astype(
            {
                "RENDA_PER_CAPITA": "float32",
                "Q024": "int8",
                "TP_ANO_CONCLUIU": "int8",
                "TP_LINGUA": "int8",
                "TP_SEXO": "int8",
                "Q002": "int8",
            }
        )
        return df

    def predict_single(self, candidato: CandidatoInput) -> float:
        """Executa a predição para um único candidato."""
        if not self.is_loaded():
            raise RuntimeError("O modelo ainda não foi carregado na memória.")

        df = self._preparar_dataframe([candidato])
        pred = self.model.predict(df)[0]
        # Arredondamento psicométrico com 2 casas decimais na escala TRI
        return round(float(pred), 2)

    def predict_batch(self, candidatos: List[CandidatoInput]) -> List[float]:
        """Executa a predição vetorial para um lote de candidatos."""
        if not self.is_loaded():
            raise RuntimeError("O modelo ainda não foi carregado na memória.")

        df = self._preparar_dataframe(candidatos)
        preds = self.model.predict(df)
        return [round(float(p), 2) for p in preds]

    def get_info(self) -> Dict[str, Any]:
        """Retorna informações estruturadas de governança."""
        linhagem = self.model_card.get("linhagem_dados", {})
        return {
            "nome_artefato": self.model_card.get("nome_artefato", self.model_path.name),
            "modelo_registrado_mlflow": self.model_card.get(
                "modelo_registrado_mlflow", "enem_target_m4_producao"
            ),
            "mlflow_run_id_campeao": self.model_card.get("mlflow_run_id_campeao", "desconhecido"),
            "classe_modelo_campeao": self.model_card.get("classe_modelo_campeao", "XGBRegressor"),
            "data_treinamento_utc": self.model_card.get("data_treinamento_utc", "desconhecida"),
            "sha256_enem_pkl": self.sha256,
            "janela_historica": linhagem.get("janela_historica", "2014-2023"),
            "n_total_censo": linhagem.get("n_total_censo", 37593629),
            "n_holdout_cego": linhagem.get("n_holdout_cego", 7518726),
            "features_ordenadas": self.features_ordenadas,
            "metricas_oficiais": self.model_card.get("metricas_oficiais", {}),
        }

