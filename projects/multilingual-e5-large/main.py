from typing import List

from mlflow import start_run, log_param, log_metric
from mlflow.models import infer_signature
from mlflow.models.signature import ModelSignature
from mlflow.sentence_transformers import log_model
from sentence_transformers import SentenceTransformer


class Project:
    def __init__(self) -> None:
        # load model with tokenizer
        self.model = SentenceTransformer(
            model_name_or_path="intfloat/multilingual-e5-large",
        )

    def load_data(self):
        pass

    def train(self):
        log_param("model_name", "intfloat/multilingual-e5-large")
        log_param("batch_size", 64)

        log_metric("loss", 0.1)

    def save(self):
        sample_input: List[str] = ["日本語の文章をembeddingします。"]
        signature: ModelSignature = infer_signature(
            model_input=sample_input,
            model_output=self.model.encode(sentences=sample_input),
        )
        log_model(
            model=self.model,
            artifact_path="multilingual-e5-large",
            signature=signature,
            input_example=sample_input,
        )


project = Project()
project.load_data()

with start_run():
    project.train()
    project.save()
