from gpu_box.models.base import ModelRouteRegistry
from gpu_box.models import ner, whisper
model_instances = ModelRouteRegistry.create_model_instances()
print(model_instances)


