import argparse
import logging
from typing import Dict, List

from kserve import Model, ModelServer, model_server
from kserve.model import PredictorConfig, PredictorProtocol
from mlflow.environment_variables import _EnvironmentVariable
from mlflow.sentence_transformers import load_model
from sentence_transformers import SentenceTransformer


class SentenceTransformerModel(Model):
    def __init__(self, name: str, model_uri: str, predictor_protocol: str):
        super().__init__(
            name,
            PredictorConfig(predictor_protocol=predictor_protocol),
            return_response_headers=True,
        )
        self.model_uri = model_uri
        self.load()

    def load(self):
        self.model: SentenceTransformer = load_model(model_uri=self.model_uri)
        self.model.eval()
        self.ready = True
        logging.info(f"Model loaded from {self.model_uri}")

    def predict(self, payload: Dict[str, str] = None) -> Dict:
        """
        Embed text data using the SentenceTransformer model.

        This method processes the input payload, extracts text data, and computes
        embeddings for the provided text using a pre-trained SentenceTransformer model.

        Args:
            payload (Dict[str, Any]): The input payload containing text data.
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
            Dict: The output payload containing embeddings in the V2 protocol format.
                Example:
                {
                    "outputs": [
                        {
                            "name": "embeddings",
                            "shape": [2, 1024],
                            "datatype": "FP32",
                            "data": [[...], [...]]  # Embedding vectors for each input text.
                        }
                    ]
                }

        Raises:
            ValueError: If the input payload does not contain valid text data.
        """
        try:
            texts = self._extract_texts_v2(payload)
        except ValueError as e:
            return {"error": str(e)}
        embeddings = self.model.encode(texts)
        result = {
            "outputs": [
                {
                    "name": "embeddings",
                    "shape": embeddings.shape,
                    "datatype": "FP32",
                    "data": embeddings.tolist(),
                }
            ]
        }
        return result

    def _extract_texts_v2(self, payload: Dict[str, str] = None) -> List[str]:
        """Extract text data from the input payload following the V2 protocol.

        Args:
            payload (Dict[str, Any]): The input payload containing text data.
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

        Raises:
            ValueError: If the input payload does not contain valid text data.
            ValueError: If the input payload does not contain any data.

        Returns:
            List[str]: A list of text data extracted from the input payload.
                Example:
                [
                    "This is a test.",
                    "Another test."
                ]
        """
        inputs = payload.get("inputs", [])
        if not inputs:
            logging.error("入力データが見つかりません。")
            raise ValueError("No input data found in the payload.")

        # Extract text data from the input payload
        texts = []
        for input_data in inputs:
            data = input_data.get("data")
            if data is None:
                logging.warning("データが見つかりませんでした。")
                continue
            if isinstance(data, list):
                texts.extend(data)
            elif isinstance(data, str):
                texts.append(data)
            else:
                logging.warning(f"無効なデータ形式: {data}")

        if not texts:
            logging.error("有効なテキストデータがありません。")
            raise ValueError("No valid text data found in the payload.")
        return texts


MODELS_DIR = _EnvironmentVariable("MODELS_DIR", str, "/mnt/models")
parser = argparse.ArgumentParser(parents=[model_server.parser])
parser.add_argument(
    "--model_name",
    help="The name that the model is served under.",
    default="sentence-transformer",
)
parser.add_argument("--protocol", help="The protocol for the predictor", default="v2")
args, _ = parser.parse_known_args()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    model = SentenceTransformerModel(
        name=args.model_name,
        model_uri=MODELS_DIR.get(),
        predictor_protocol=PredictorProtocol(args.predictor_protocol),
    )
    ModelServer(workers=1).start([model])
