from __future__ import annotations

import random
from pathlib import Path
from threading import Lock
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    import tensorflow as tf
    from tensorflow import keras
except ImportError as exc:  # pragma: no cover - startup guard for local installs
    raise RuntimeError(
        "TensorFlow is required to load the saved .keras attack detector. "
        "Install backend dependencies with: pip install -r requirements.txt"
    ) from exc


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
ATTACK_MODEL_PATH = MODEL_DIR / "attack_detector.keras"
EMBEDDING_DATA_PATH = MODEL_DIR / "test_embedding_df.csv"

FLOW_TYPES = [
    "Normal",
    "Port_Scan",
    "Web_Crwling",
    "Brute_Force",
    "HTTP_DDoS",
    "ICMP_Flood",
]

DISPLAY_FLOW_NAMES = {
    "Normal": "Normal",
    "Port_Scan": "Port Scan",
    "Web_Crwling": "Web Crawling",
    "Brute_Force": "Brute Force",
    "HTTP_DDoS": "HTTP DDoS",
    "ICMP_Flood": "ICMP Flood",
}

CLASS_NAMES = ["Scenario A", "Scenario B", "Neither"]
MAX_SEQUENCE_LENGTH = 100
EMBEDDING_DIM = 64


@keras.utils.register_keras_serializable(package="Custom")
class PositionalEncoding(keras.layers.Layer):
    def __init__(self, max_len: int = 100, d_model: int = 64, **kwargs: Any):
        super().__init__(**kwargs)
        self.max_len = max_len
        self.d_model = d_model

    def call(self, inputs: tf.Tensor) -> tf.Tensor:
        positions = np.arange(self.max_len)[:, np.newaxis]
        dimensions = np.arange(self.d_model)[np.newaxis, :]
        angle_rates = 1 / np.power(10000, (2 * (dimensions // 2)) / np.float32(self.d_model))
        angle_rads = positions * angle_rates
        angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])
        angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])
        positional_encoding = tf.cast(angle_rads[np.newaxis, ...], dtype=inputs.dtype)
        return inputs + positional_encoding[:, : tf.shape(inputs)[1], :]

    def get_config(self) -> dict[str, Any]:
        config = super().get_config()
        config.update({"max_len": self.max_len, "d_model": self.d_model})
        return config


@keras.utils.register_keras_serializable(package="Custom")
class TransformerBlock(keras.layers.Layer):
    def __init__(
        self,
        embed_dim: int = 64,
        num_heads: int = 4,
        ff_dim: int = 256,
        dropout: float = 0.1,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.dropout = dropout
        self.attn = keras.layers.MultiHeadAttention(
            num_heads=num_heads,
            key_dim=embed_dim // num_heads,
        )
        self.ffn = keras.Sequential(
            [
                keras.layers.Dense(ff_dim, activation="relu"),
                keras.layers.Dense(embed_dim),
            ]
        )
        self.norm1 = keras.layers.LayerNormalization(epsilon=1e-6)
        self.norm2 = keras.layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = keras.layers.Dropout(dropout)
        self.dropout2 = keras.layers.Dropout(dropout)

    def call(self, inputs: tf.Tensor, training: bool = False) -> tf.Tensor:
        attn_output = self.attn(inputs, inputs, use_causal_mask=True)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.norm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.norm2(out1 + ffn_output)

    def get_config(self) -> dict[str, Any]:
        config = super().get_config()
        config.update(
            {
                "embed_dim": self.embed_dim,
                "num_heads": self.num_heads,
                "ff_dim": self.ff_dim,
                "dropout": self.dropout,
            }
        )
        return config


class InjectRequest(BaseModel):
    flow_type: str


class CampaignState:
    def __init__(self) -> None:
        self.embeddings: list[np.ndarray] = []
        self.history: list[dict[str, Any]] = []
        self.current_prediction: dict[str, Any] | None = None
        self.lock = Lock()

    def reset(self) -> None:
        with self.lock:
            self.embeddings.clear()
            self.history.clear()
            self.current_prediction = None


app = FastAPI(title="AI Multi-Step Attack Detector API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state = CampaignState()
attack_model: keras.Model | None = None
embedding_groups: dict[str, np.ndarray] = {}


@app.on_event("startup")
def load_assets() -> None:
    global attack_model, embedding_groups

    if not ATTACK_MODEL_PATH.exists():
        raise RuntimeError(f"Missing attack model: {ATTACK_MODEL_PATH}")
    if not EMBEDDING_DATA_PATH.exists():
        raise RuntimeError(f"Missing embedding dataset: {EMBEDDING_DATA_PATH}")

    attack_model = keras.models.load_model(
        ATTACK_MODEL_PATH,
        custom_objects={
            "PositionalEncoding": PositionalEncoding,
            "TransformerBlock": TransformerBlock,
        },
        compile=False,
    )

    df = pd.read_csv(EMBEDDING_DATA_PATH)
    missing_columns = [str(index) for index in range(EMBEDDING_DIM) if str(index) not in df.columns]
    if missing_columns or "Label" not in df.columns:
        raise RuntimeError("test_embedding_df.csv must contain columns 0..63 and Label.")

    embedding_groups = {
        label: group[[str(index) for index in range(EMBEDDING_DIM)]].to_numpy(dtype=np.float32)
        for label, group in df.groupby("Label")
    }

    missing_labels = sorted(set(FLOW_TYPES) - set(embedding_groups))
    if missing_labels:
        raise RuntimeError(f"Embedding dataset is missing labels: {', '.join(missing_labels)}")


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "AI Multi-Step Attack Detector API"}


@app.post("/reset")
def reset() -> dict[str, str]:
    state.reset()
    return {"status": "ok"}


@app.post("/inject")
def inject_flow(payload: InjectRequest) -> dict[str, Any]:
    flow_type = payload.flow_type
    if flow_type not in FLOW_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported flow_type '{flow_type}'. Expected one of: {', '.join(FLOW_TYPES)}",
        )

    if attack_model is None:
        raise HTTPException(status_code=503, detail="Model is still loading.")

    with state.lock:
        sampled_embedding = random.choice(embedding_groups[flow_type]).astype(np.float32)
        state.embeddings.append(sampled_embedding)
        prediction = run_prediction(state.embeddings)

        event = {
            "step": len(state.history) + 1,
            "flow_type": flow_type,
            "flow_name": DISPLAY_FLOW_NAMES[flow_type],
            "prediction": prediction["prediction"],
            "confidence": prediction["confidence"],
            "probabilities": prediction["probabilities"],
        }
        state.history.append(event)
        state.current_prediction = prediction

        return {
            **prediction,
            "campaign_length": len(state.embeddings),
            "history": state.history,
        }


@app.get("/history")
def history() -> dict[str, Any]:
    with state.lock:
        return {"history": state.history, "campaign_length": len(state.embeddings)}


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    with state.lock:
        prediction = state.current_prediction or empty_prediction()
        return {
            **prediction,
            "campaign_length": len(state.embeddings),
        }


def run_prediction(sequence: list[np.ndarray]) -> dict[str, Any]:
    active_sequence = sequence[-MAX_SEQUENCE_LENGTH:]
    sequence_length = len(active_sequence)

    padded = np.zeros((1, MAX_SEQUENCE_LENGTH, EMBEDDING_DIM), dtype=np.float32)
    padded[0, :sequence_length, :] = np.asarray(active_sequence, dtype=np.float32)

    predictions = attack_model.predict(padded, verbose=0)
    latest_probabilities = predictions[0, sequence_length - 1]
    class_index = int(np.argmax(latest_probabilities))

    probabilities = {
        class_name: round(float(latest_probabilities[index]), 6)
        for index, class_name in enumerate(CLASS_NAMES)
    }

    return {
        "prediction": CLASS_NAMES[class_index],
        "confidence": round(float(latest_probabilities[class_index]), 6),
        "probabilities": probabilities,
    }


def empty_prediction() -> dict[str, Any]:
    return {
        "prediction": "Neither",
        "confidence": 0.0,
        "probabilities": {class_name: 0.0 for class_name in CLASS_NAMES},
    }
