# GPU Box API Framework 🚀

An easy-to-use API framework for serving machine learning models via a REST API. Built on the robust foundation of Starlette, Uvicorn, and Asyncio.

## Features
- 🚄 Fast and Asynchronous: Leverages the power of Starlette and Uvicorn for high-performance operations.
- 📦 Model Agnostic: Add any model seamlessly without any additional setup.
- 🔐 Secure: Choose between OAuth or basic authentication for secure endpoint access.
- 🔄 Automatic API Generation: API endpoints are generated based on the type signature of your model's `run` function.
- 🎒 Built-In Tunneling: With `pyngrok` integration, expose your local server to the world without any hassles.

## Quick Start

### Setup

Make sure you have `poetry` installed. If not, install it using:

``` bash
pip install poetry
```

Then, clone the repository and install dependencies:

```bash
git clone https://github.com/dtkav/gpu-box
cd gpu-box
poetry install
```

### Load Environment Variables

You can store environment variables set in a file called `.auth.env`.
```
NGROK_DOMAIN=your.domain.here
NGROK_TOKEN=<your token goes here>
NGROK_AUTH_PAIRS=user:pass,user2:pass2
NGROK_ALLOWED_EMAILS=butts@gmail.com,butts2@gmail.com
NGROK_OAUTH_PROVIDER=google
```

Use the provided `do` script to source the environment from this file.
```bash
./do python cli.py oauth
```

### Running the Server Locally

You can start the server using:

```bash
python cli.py serve
```

### Ngrok Tunneling

To expose your local server with ngrok, you can either use OAuth or basic authentication:

1. OAuth2:
```bash
python cli.py oauth --token YOUR_NGROK_TOKEN --oauth-provider=google --allowed-emails=butts@gmail.com
```

2. Basic Authentication:
```bash
python cli.py password --token YOUR_NGROK_TOKEN --auth-pairs username:password
```

### Adding New Models

Adding new models is a breeze! Here's a simple step-by-step guide:

1. Define a new class that inherits from `ModelRoute`.
2. Set the `name` attribute (this becomes the API endpoint).
3. Implement the `load` method to load your model.
4. Implement the `run` method. The API for the model is generated based on the type signature of this function.

For instance:

```python
from .base import ModelRoute
from gpu_box.types import JSONType, File
from whispercpp import Whisper

class WhisperCppBase(ModelRoute):
    name = "whispercpp-base"
    model_size = "base"

    def load(self):
        return Whisper(self.model_size)

    async def run(self, file: File) -> str:
        print(f"running model on {file.name} (@{file.path})")
        result = self.model.transcribe(file.path)
        return "\n\n".join(self.model.extract_text(result))
```

This will create an API endpoint at `/whispercpp-base` that accepts file uploads and outputs text.

## License
[MIT](LICENSE)
