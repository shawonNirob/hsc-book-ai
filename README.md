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

### Development Tools
- **Visual Studio Code**: Code editor used for development.

### Frameworks & Servers
- **FastAPI**: High-performance web framework for building APIs with Python.
- **Uvicorn**: ASGI server used to run the FastAPI app.

### Langchain Ecosystem
- **langchain**: Core Langchain framework for building LLM-based applications.
- **langchain_community**: Community integrations (e.g., vector stores, tools).
- **langchain_core**: Shared types and interfaces.
- **langchain_openai**: OpenAI integration for Langchain.

### AI and OCR
- **pytesseract**: Python wrapper for Google's Tesseract-OCR.
- **Pillow**: Imaging library used for image manipulation.
- **PyMuPDF**: PDF and document parsing.
- **langgraph**: Graph-based orchestration for LangChain components.

### Vector Database
- **Qdrant Client**: Client library for interacting with Qdrant, a vector similarity search engine.

### Data Validation
- **Pydantic**: Data validation using Python type hints.
- **pydantic-settings**: Manage application settings from `.env`.

### Utilities
- **Loguru**: Advanced logging for debugging and tracing.
- **requests**: HTTP requests for external APIs.
- **python-multipart**: Required by FastAPI to handle file uploads.

## Test Cases

- **অনুপমকে বিবাহ আসর থেকে ফিরিয়ে দেবার কারণ কী?**  
  গয়না নিয়ে মনোমালিন্যের কারণে

- **অনুপমের বাবা কী করে জীবিকা নির্বাহ করতেন?**  
  ওকালতি

- **অনুপম কাকে নিয়ে তীর্থযাত্রা শুরু করে?**  
  মাকে

- **Who is Anupam's friend in the story 'Aporichita'?**  
  Anupam's friend in the story 'Aporichita' is Harish.

- **In the story 'Aporichita', what color saree does Anupam imagine Kalyani wearing at her wedding?**  
  In the story 'Aporichita', Anupam imagines Kalyani wearing a red saree at her wedding.

## Screenshots

### Chatbot Interface
![alt text](image.png)
![alt text](image-1.png)

### Evaluation Matrix: Cosine Similarity API Response
![alt text](image-2.png)
![alt text](image-3.png)

## API Documentation

**Base URL:** `https://web-production-a06d.up.railway.app`

- **POST /agent/ask**  
  Accepts a query and optional thread ID. Returns a chatbot response.  
  Request body: `{ "query": "string", "thread_id": "string" }`

- **POST /agent/reset_memory**  
  Resets conversation memory for a given thread ID.  
  Request body: `{ "thread_id": "string" }`

- **POST /insert-vector**  
  Upload a PDF file; extracts chunks and inserts vectors into Qdrant.  
  Request: Multipart file upload.

- **POST /search_vector**  
  Search documents in Qdrant using a query string.  
  Request body: raw query string.

- **POST /matrix-evaluation/cosine-similarity**  
  Evaluation Matrix: Computes cosine similarity for the provided query.  
  Request body: `{ "query": "string" }`

## Screenshots
**API Documentation**: `https://web-production-a06d.up.railway.app/docs` or `https://web-production-a06d.up.railway.app/redoc`
![alt text](image-4.png)

## Follow Up Explanation
**What method or library did you use to extract the text, and why? Did you face any formatting challenges with the PDF content?**
I started by extracting text from PDFs using PyMuPDF, but it didn’t preserve the formatting well. So, I tried OCR with Tesseract and store page by page in vector database, which didn’t organize the content clearly.

Then, I used regex patterns to separate different parts like MCQs, creative questions, and notes. However, this wasn’t very reliable.

Then, I brought in LLM to clean and group the text, which helped accuracy but sometimes caused errors for the bigger documents.

So I use the mix solution, extract text page by page, then use the LLM to process each page separately. This balances accuracy and efficiency well, although some challenges with LLM limits still exist.

For file handling, I currently read the entire PDF file as bytes in FastAPI, which makes processing flexible. For storing PDFs, MinIO is good for production.


**What chunking strategy did you choose (e.g. paragraph-based, sentence-based, character limit)? Why do you think it works well for semantic retrieval?**
I separated the content into specific blocks such as:
MCQ questions with separate answer keys. MCQ questions with inline answers. Creative questions. Vocabulary and notes. Main content. Author information. Path Porichiti. 
This block based chunking, combined with page by page extraction, helps group related information meaningfully.
It works well for semantic retrieval because each chunk is thematically focused, reducing noise and improving the relevance of search results. By keeping related content together, the vector search can better capture context and meaning, leading to more accurate and useful retrieval.

