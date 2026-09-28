"""Preprocessing Pipeline Module for AssureX Claim Engine.

Constructs and manages scikit-learn preprocessing ColumnTransformers and LabelEncoders
for tabular warranty claim features. Handles persistence and loading of preprocessor artifacts.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import List, Optional, Tuple, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

from src.ml.feature_engineering import (
    BOOLEAN_FEATURES,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
)


DEFAULT_PREPROCESSOR_PATH = Path("model/python/preprocessor.joblib")
DEFAULT_LABEL_ENCODER_PATH = Path("model/python/label_encoder.joblib")


def build_preprocessor(
    numeric_features: Optional[List[str]] = None,
    categorical_features: Optional[List[str]] = None,
) -> ColumnTransformer:
    """Constructs a scikit-learn ColumnTransformer for numeric and categorical features.
    
    Numeric features (including boolean 0/1 flags) are median-imputed and standardized.
    Categorical features are constant-imputed ('missing') and one-hot encoded with unknown handling.
    
    Args:
        numeric_features: List of numeric and boolean feature column names.
        categorical_features: List of categorical feature column names.
        
    Returns:
        Unfitted ColumnTransformer instance.
    """
    if numeric_features is None:
        numeric_features = NUMERIC_FEATURES + BOOLEAN_FEATURES
    if categorical_features is None:
        categorical_features = CATEGORICAL_FEATURES

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ],
        remainder="drop",
    )

    return preprocessor


def build_label_encoder() -> LabelEncoder:
    """Instantiates a LabelEncoder for claim classification targets."""
    return LabelEncoder()


def save_preprocessor(
    preprocessor: ColumnTransformer,
    path: Union[str, Path] = DEFAULT_PREPROCESSOR_PATH,
) -> Path:
    """Saves the fitted ColumnTransformer to disk using joblib.
    
    Args:
        preprocessor: Fitted ColumnTransformer instance.
        path: Target file path.
        
    Returns:
        Path to the saved artifact.
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(preprocessor, path_obj)
    return path_obj


def load_preprocessor(
    path: Union[str, Path] = DEFAULT_PREPROCESSOR_PATH,
) -> ColumnTransformer:
    """Loads a fitted ColumnTransformer from disk.
    
    Args:
        path: Path to the joblib artifact.
        
    Returns:
        Loaded ColumnTransformer instance.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Preprocessor artifact not found at {path_obj.resolve()}")
    return joblib.load(path_obj)


def save_label_encoder(
    label_encoder: LabelEncoder,
    path: Union[str, Path] = DEFAULT_LABEL_ENCODER_PATH,
) -> Path:
    """Saves the fitted LabelEncoder to disk using joblib.
    
    Args:
        label_encoder: Fitted LabelEncoder instance.
        path: Target file path.
        
    Returns:
        Path to the saved artifact.
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(label_encoder, path_obj)
    return path_obj


def load_label_encoder(
    path: Union[str, Path] = DEFAULT_LABEL_ENCODER_PATH,
) -> LabelEncoder:
    """Loads a fitted LabelEncoder from disk.
    
    Args:
        path: Path to the joblib artifact.
        
    Returns:
        Loaded LabelEncoder instance.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Label encoder artifact not found at {path_obj.resolve()}")
    return joblib.load(path_obj)


def fit_and_save_pipeline(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    preprocessor_path: Union[str, Path] = DEFAULT_PREPROCESSOR_PATH,
    label_encoder_path: Union[str, Path] = DEFAULT_LABEL_ENCODER_PATH,
) -> Tuple[ColumnTransformer, LabelEncoder, np.ndarray, np.ndarray]:
    """Fits and persists preprocessor and label encoder on training data.
    
    Args:
        X_train: Engineered training features DataFrame.
        y_train: Training labels Series.
        preprocessor_path: Destination path for preprocessor artifact.
        label_encoder_path: Destination path for label encoder artifact.
        
    Returns:
        Tuple of (fitted_preprocessor, fitted_label_encoder, X_train_transformed, y_train_encoded).
    """
    preprocessor = build_preprocessor()
    label_encoder = build_label_encoder()

    X_train_transformed = preprocessor.fit_transform(X_train)
    y_train_encoded = label_encoder.fit_transform(y_train)

    save_preprocessor(preprocessor, preprocessor_path)
    save_label_encoder(label_encoder, label_encoder_path)

    return preprocessor, label_encoder, X_train_transformed, y_train_encoded