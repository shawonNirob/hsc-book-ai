# HSC BOOK AI

## Setup Guide
* Python 3.12 or higher installed
* `pip` package manager

## Installation Steps
1. **Clone the repository**
```bash
git clone git clone https://github.com/shawonNirob/hsc-book-ai.git
or,
git clone git@github.com:shawonNirob/hsc-book-ai.git
cd hsc-book-ai
```

2. **Create and activate a virtual environment**
On Linux/macOS:
```bash
python3 -m venv book-env
source book-env/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

7. **Environment Variables**
-Create a `.env` file and add your configuration:
```bash
OPENAI_API_KEY = " "
MODEL_ID =  "gpt-4o-2024-08-06"
QDRANT_API_KEY = " "
EMBEDDING_MODEL = "text-embedding-3-small"
```

4. **Run the FastAPI application**
```bash
uvicorn app.main:app --reload
```

5. **Access the API**
-Open your browser and go to:
```bash
http://127.0.0.1:8000
```

6. **Explore the interactive API docs**
* Swagger UI:
  `http://127.0.0.1:8000/docs`
* ReDoc:
  `http://127.0.0.1:8000/redoc`

## Used Tools, Libraries, and Packages

**Development Tools**
**Visual Studio Code:** Code editor used for development.

**Frameworks & Servers**
**FastAPI:** High-performance web framework for building APIs with Python.
**Uvicorn:** ASGI server used to run the FastAPI app.

**Langchain Ecosystem**
**langchain** – Core Langchain framework for building LLM-based applications.
**langchain_community** – Community integrations (e.g., vector stores, tools).
**langchain_core** – Shared types and interfaces.
**langchain_openai** – OpenAI integration for Langchain.

**AI and OCR**
**pytesseract:** Python wrapper for Google's Tesseract-OCR.
**Pillow:** Imaging library used for image manipulation.
**PyMuPDF:** PDF and document parsing.
**langgraph:** Graph-based orchestration for LangChain components.

**Vector Database**
**Qdrant Client:** Client library for interacting with Qdrant, a vector similarity search engine.

**Data Validation**
**Pydantic:** Data validation using Python type hints.
**pydantic-settings:** Manage application settings from `.env`.

### **Utilities**
**Loguru:** Advanced logging for debugging and tracing.
**requests:** HTTP requests for external APIs.
**python-multipart:** Required by FastAPI to handle file uploads.

