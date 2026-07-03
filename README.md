```` 
brew install uv
uv init
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

uv add fastapi
uv add uvicorn
uv add pydantic
uv add pydantic-settings
uv add python-dotenv
uv add loguru
uv add langgraph
uv add langchain
uv add langchain-community
uv add ollama
uv add pymupdf
uv add moviepy
uv add pillow
uv add typer
uv add pymupdf

uv add --dev pytest
uv add --dev pytest-asyncio
uv add --dev ruff
uv add --dev mypy

uv run python main.py books/atomic_habits.pdf
python main.py load books/atomic_habits.pdf
python main.py summarize books/atomic_habits.pdf
python main.py blueprint books/atomic_habits.pdf
python main.py render-images books/atomic_habits.pdf
python main.py render-images books/atomic_habits.pdf --limit 1

uv run pytest
````

#### COMFY

````
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python main.py
````

#### OLLAMA

````
ollama serve
````