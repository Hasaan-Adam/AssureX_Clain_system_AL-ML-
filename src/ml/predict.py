"""Inference and Prediction Interface for AssureX Claim Engine.

Provides high-performance, validated prediction functions for single claim records
and batch claims using the trained Python ML model pipeline.
"""

from __future__ import annotations

import functools
import logging
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd

from src.ml.feature_engineering import extract_features
from src.ml.preprocess_pipeline import (
    DEFAULT_LABEL_ENCODER_PATH,
    DEFAULT_PREPROCESSOR_PATH,
    load_label_encoder,
    load_preprocessor,
)
from src.ml.registry import get_latest_version


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_MODEL_PATH = Path("model/python/claim_classifier.joblib")


class ClaimPredictor:
    """Thread-safe singleton predictor for the AssureX Claim Classifier."""

    _instance: Optional[ClaimPredictor] = None

    def __init__(
        self,
        model_path: Union[str, Path] = DEFAULT_MODEL_PATH,
        preprocessor_path: Union[str, Path] = DEFAULT_PREPROCESSOR_PATH,
        label_encoder_path: Union[str, Path] = DEFAULT_LABEL_ENCODER_PATH,
    ):
        self.model_path = Path(model_path)
        self.preprocessor_path = Path(preprocessor_path)
        self.label_encoder_path = Path(label_encoder_path)

        self._model = None
        self._preprocessor = None
        self._label_encoder = None
        self._model_version = "v1.0.0"

        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Loads model, preprocessor, label encoder, and version metadata from disk."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {self.model_path.resolve()}")

        logger.info(f"Loading ClaimPredictor artifacts from {self.model_path.parent}...")
        self._model = joblib.load(self.model_path)
        self._preprocessor = load_preprocessor(self.preprocessor_path)
        self._label_encoder = load_label_encoder(self.label_encoder_path)

        try:
            latest = get_latest_version()
            if latest and "version" in latest:
                self._model_version = latest["version"]
        except Exception:
            self._model_version = "v1.0.0"

    @classmethod
    def get_instance(cls) -> ClaimPredictor:
        """Get or initialize singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reload_instance(cls) -> ClaimPredictor:
        """Forces reloading the singleton instance from disk."""
        cls._instance = cls()
        return cls._instance

    def predict(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs inference for a single claim dictionary.
        
        Args:
            claim_data: Raw or pre-extracted claim record dictionary.
            
        Returns:
            Dictionary containing:
                - `predicted_class`: string ('Valid Claim' / 'Invalid Claim' / 'Manual Review')
                - `confidence`: float (confidence score of the winning class, between 0.0 and 1.0)
                - `probabilities`: dict mapping each class to its probability
                - `model_version`: string version identifier
        """
        features_df = extract_features(claim_data)
        
        X_trans = self._preprocessor.transform(features_df)
        
        if hasattr(self._model, "predict_proba"):
            probs = self._model.predict_proba(X_trans)[0]
        else:
            pred_idx = self._model.predict(X_trans)[0]
            probs = np.zeros(len(self._label_encoder.classes_))
            probs[pred_idx] = 1.0

        classes = list(self._label_encoder.classes_)
        prob_dict = {str(c): float(np.round(probs[i], 4)) for i, c in enumerate(classes)}

        best_idx = int(np.argmax(probs))
        predicted_class = str(classes[best_idx])
        confidence = float(np.round(probs[best_idx], 4))

        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "probabilities": prob_dict,
            "model_version": self._model_version,
        }

    def batch_predict(
        self, claims_data: Union[List[Dict[str, Any]], pd.DataFrame]
    ) -> List[Dict[str, Any]]:
        """Runs batch inference for a list of claim dictionaries or a DataFrame.
        
        Args:
            claims_data: List of claim dicts or pandas DataFrame.
            
        Returns:
            List of prediction result dictionaries.
        """
        if isinstance(claims_data, pd.DataFrame):
            df_in = claims_data
        elif isinstance(claims_data, list):
            df_in = pd.DataFrame(claims_data)
        else:
            raise TypeError(f"Unsupported data type for batch prediction: {type(claims_data)}")

        features_df = extract_features(df_in)
        X_trans = self._preprocessor.transform(features_df)
        classes = list(self._label_encoder.classes_)

        if hasattr(self._model, "predict_proba"):
            all_probs = self._model.predict_proba(X_trans)
        else:
            pred_indices = self._model.predict(X_trans)
            all_probs = np.zeros((len(df_in), len(classes)))
            for row_i, p_idx in enumerate(pred_indices):
                all_probs[row_i, p_idx] = 1.0

        results = []
        for probs in all_probs:
            prob_dict = {str(c): float(np.round(probs[i], 4)) for i, c in enumerate(classes)}
            best_idx = int(np.argmax(probs))
            results.append({
                "predicted_class": str(classes[best_idx]),
                "confidence": float(np.round(probs[best_idx], 4)),
                "probabilities": prob_dict,
                "model_version": self._model_version,
            })

        return results


def predict_claim(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean functional prediction interface for single claim inference.
    
    Args:
        claim_data: Dictionary representing a single claim.
        
    Returns:
        Dict with keys: 'predicted_class', 'confidence', 'probabilities', 'model_version'.
    """
    predictor = ClaimPredictor.get_instance()
    return predictor.predict(claim_data)


def batch_predict_claims(
    claims_data: Union[List[Dict[str, Any]], pd.DataFrame]
) -> List[Dict[str, Any]]:
    """Clean functional batch prediction interface.
    
    Args:
        claims_data: List of claim dicts or pandas DataFrame.
        
    Returns:
        List of prediction result dicts.
    """
    predictor = ClaimPredictor.get_instance()
    return predictor.batch_predict(claims_data)