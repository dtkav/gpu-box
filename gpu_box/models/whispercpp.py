from .base import ModelRoute
from gpu_box.types import JSONType, File
from whispercpp import Whisper

class WhisperCppBase(ModelRoute):
    """ Whisper.cpp (base)
    """
    name = "whispercpp-base"
    model_size = "base"

    def load(self):
        return Whisper(self.model_size)

    async def run(self, file: File) -> str:
        print(f"running model on {file.name} (@{file.path})")
        result = self.model.transcribe(file.path)
        return "\n\n".join(self.model.extract_text(result))


class WhisperCppTiny(WhisperCppBase):
    """ Whisper.cpp (tiny)
    """
    name = "whispercpp-tiny"
    model_size = "tiny"


class WhisperCppLarge(WhisperCppBase):
    """ Whisper.cpp (large)
    """
    name = "whispercpp-large"
    model_size = "large"
