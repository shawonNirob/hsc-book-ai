import fitz
import io

def extract_chunks_by_page(file_bytes: bytes):
    doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
    chunks = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        page_text = page.get_text().strip()

        if len(page_text.split()) <= 500:
            chunks.append({
                "page": page_number +1,
                "text": page_text
            })

        else:
            paragraphs = page_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    chunks.append({
                        "page": page_number + 1,
                        "text": page_text
                    })

    return chunks