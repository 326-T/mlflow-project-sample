import argparse
import logging
from typing import Any, AsyncIterator, Dict, Union

from kserve import Model, ModelServer, model_server
from kserve.model import PredictorConfig, PredictorProtocol
from kserve.protocol.grpc.grpc_predict_v2_pb2 import ModelInferRequest
from kserve.protocol.infer_type import InferOutput, InferRequest, InferResponse
from mlflow.environment_variables import _EnvironmentVariable
from mlflow.sentence_transformers import load_model
from sentence_transformers import SentenceTransformer


class SentenceTransformerModel(Model):
    def __init__(
        self, name: str, model_uri: str, predictor_host: str, predictor_protocol: str
    ):
        super().__init__(
            name,
            PredictorConfig(
                predictor_host=predictor_host, predictor_protocol=predictor_protocol
            ),
            return_response_headers=True,
        )
        self.model_uri = model_uri
        self.load()

    def load(self):
        self.model: SentenceTransformer = load_model(model_uri=self.model_uri)
        self.model.eval()
        self.ready = True
        logging.info(f"Model loaded from {self.model_uri}")

    async def predict(
        self,
        payload: Union[Dict, InferRequest, ModelInferRequest],
        headers: Dict[str, str] = None,
        response_headers: Dict[str, str] = None,
    ) -> Union[Dict, InferResponse, AsyncIterator[Any]]:
        if isinstance(payload, InferRequest):
            return self._predict_rest_v2(payload)
        elif isinstance(payload, ModelInferRequest):
            return self._predict_grpc_v2(payload)
        return self._predict_rest_v1(payload)

    def _predict_rest_v1(self, payload: Dict) -> Dict:
        """
        Predicts the embeddings of the input text data using REST V1 protocol.

        Args:
            payload (Dict): The input payload containing text data.
                It should follow the V1 protocol format with an "instances" key.
                Example:
                {
                    "instances": [
                        "This is a test.",
                        "Another test."
                    ]
                }

        Returns:
            Dict: The response containing the embeddings of the input text data.
                Example:
                {
                    "predictions": [[0.1, 0.2, ..., 0.8], [0.3, 0.4, ..., 0.9]]
                }
        """
        instances = payload.get("instances")
        texts = []
        for instance in instances:
            if isinstance(instance, list):
                texts.extend(instance)
            elif isinstance(instance, dict) and "text" in instance:
                texts.append(instance)

        embeddings = self.model.encode(texts)
        return {"predictions": embeddings.tolist()}

    def _predict_rest_v2(self, payload: InferRequest = None) -> InferResponse:
        """
        Predicts the embeddings of the input text data using REST V2 protocol.

        Args:
            payload (InferRequest): The input payload containing text data.
                It should follow the V2 protocol format with an "inputs" key.
                Example:
                {
                    "inputs": [
                        {
                            "name": "text",
                            "shape": [2],
                            "datatype": "BYTES",
                            "data": ["This is a test.", "Another test."]
                        }
                    ]
                }

        Returns:
            InferResponse: The response containing the embeddings of the input text data.
                Example:
                {
                    "id": "1",
                    "model_name": "sentence-transformer",
                    "model_version": "1.0",
                    "parameters": {},
                    "outputs": [
                        {
                            "name": "embeddings",
                            "shape": [2, 1024],
                            "datatype": "FP32",
                            "parameters": {},
                            "data": [[0.1, 0.2, ..., 0.8], [0.3, 0.4, ..., 0.9]]
                        }
                    ]
                }
        """
        texts = []
        for input_data in payload.inputs:
            data = input_data.to_dict().get("data")
            if isinstance(data, list):
                texts.extend(data)
            elif isinstance(data, str):
                texts.append(data)

        embeddings = self.model.encode(texts)
        return InferResponse(
            response_id=payload.id or "none",
            model_name=self.name,
            infer_outputs=[
                InferOutput(
                    name="embeddings",
                    shape=embeddings.shape,
                    datatype="FP32",
                    data=embeddings.tolist(),
                )
            ],
        )

    def _predict_grpc_v2(self, payload: ModelInferRequest) -> AsyncIterator[Any]:
        raise NotImplementedError("gRPC V2 protocol is not supported.")


MODELS_DIR = _EnvironmentVariable("MODELS_DIR", str, "/mnt/models")
parser = argparse.ArgumentParser(parents=[model_server.parser])

args, _ = parser.parse_known_args()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    model = SentenceTransformerModel(
        name=args.model_name,
        model_uri=MODELS_DIR.get(),
        predictor_host=args.predictor_host,
        predictor_protocol=PredictorProtocol(args.predictor_protocol),
    )
    ModelServer(workers=1).start([model])
