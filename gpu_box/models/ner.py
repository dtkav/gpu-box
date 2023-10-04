from .base import ModelRoute
from transformers import pipeline
from gpu_box.types import JSONType


def get_val(d):
    if isinstance(d, (list, tuple)):
        return [get_val(item) for item in d]
    if isinstance(d, dict):
        return {k: get_val(v) for k, v in d.items()}
    if hasattr(d, "item") and callable(d.item):
        return d.item()
    return d


class NER(ModelRoute):
    """Named Entity Recognition using dbmdz/bert-large-cased-finetuned-conll03-english"""

    name = "ner"

    def load(self):
        return pipeline(
            "ner",
            aggregation_strategy="simple",
            model="dbmdz/bert-large-cased-finetuned-conll03-english",
        )

    async def run(self, data: str) -> JSONType:
        return get_val(self.model(data))
