from typing import List

from mlflow import start_run, log_param, log_metric
from mlflow.models import infer_signature
from mlflow.models.signature import ModelSignature
from mlflow.sentence_transformers import log_model
from sentence_transformers import SentenceTransformer

sample_input: List[str] = ["日本語の文章をembeddingします。"]

# load model with tokenizer
model = SentenceTransformer(
    model_name_or_path="intfloat/multilingual-e5-large",
)
signature: ModelSignature = infer_signature(
    model_input=sample_input, model_output=model.encode(sentences=sample_input)
)

with start_run():
    log_param("model_name", "intfloat/multilingual-e5-large")
    log_param("batch_size", 64)
    log_model(
        model=model,
        artifact_path="multilingual-e5-large",
        signature=signature,
        input_example=sample_input,
    )
    log_metric("loss", 0.1)
