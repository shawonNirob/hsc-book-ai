import os
import fitz
import re
import json
import logging
import unicodedata
from typing import List, Dict, Any, Optional
from PIL import Image
import pytesseract
import io 

from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
llm = ChatOpenAI(model_name=settings.MODEL_ID, temperature=0.2)

def call_llm(prompt_messages: List[Any]) -> str:
    try:
        response = llm.invoke(prompt_messages)
        content = response.content.strip()

        if content.startswith('```json') and content.endswith('```'):
            content = content[len('```json'):-len('```')].strip()

        elif content.startswith('```') and content.endswith('```'):
            content = content[len('```'):-len('```')].strip()

        if not content.startswith('[') and not content.startswith('{'):
            logger.warning(f"LLM response, even after stripping markdown, does not look like JSON. Returning empty array. Response: {content[:100]}...")
            return "[]"
        
        return content
    except Exception as e:
        logger.error(f"LLM call failed: {e}", exc_info=True)
        return "[]"

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[^\u0980-\u09FFa-zA-Z0-9।॥.,:;()\[\]\{\}\-–—_?!\"'\n\s]", '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def extract_text_with_ocr(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    pages = []
    try:
        doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img, lang="ben", config="--oem 3 --psm 6")
            pages.append({"page_number": i + 1, "text": clean_text(ocr_text)})
        logger.info(f"Successfully extracted OCR text from {len(pages)} pages.")
    except Exception as e:
        logger.error(f"OCR extraction error: {e}", exc_info=True)
    return pages

def group_semantic_blocks(pages: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    blocks = {
        "mcq_questions_with_separate_answer_key": [],
        "mcq_questions_with_inline_answers": [],
        "creative_questions": [],
        "vocabulary_and_notes": [],
        "main_content": [],
        "author_info": [],
        "path_porichiti": []
    }
    pages.sort(key=lambda x: x["page_number"])

    for p in pages:
        pn = p["page_number"]
        if pn == 2 or pn == 20 or (23 <= pn <= 32):
            blocks["mcq_questions_with_inline_answers"].append(p)
        elif 3 <= pn <= 5:
            blocks["vocabulary_and_notes"].append(p)
        elif 6 <= pn <= 17:
            blocks["main_content"].append(p)
        elif pn == 18:
            blocks["author_info"].append(p)
        elif pn == 19:
            blocks["path_porichiti"].append(p)
        elif (21 <= pn <= 22) or (42 <= pn <= 49):
            blocks["creative_questions"].append(p)
        elif (33 <= pn <= 41): 
            blocks["mcq_questions_with_separate_answer_key"].append(p)
    logger.info(f"Grouped pages into {len([b for b in blocks.values() if b])} semantic blocks based on hardcoded ranges.")
    return blocks

def prompt_and_parse(text_for_llm: str, prompt_template_str: str) -> Any:

    system_message = SystemMessage(
        content="You are a highly accurate data extraction assistant. Your task is to extract information from the provided Bangla text based on the user's specific instructions and desired JSON schema. Your response MUST be a valid JSON array or object as specified in the prompt, with no additional text or explanation. If no data can be extracted, return an empty JSON array []."
    )
    
    human_message = HumanMessage(
        content=prompt_template_str
    )

    response_content = call_llm([system_message, human_message])
    
    logger.debug(f"Raw LLM response for current prompt (first 500 chars): {response_content[:500]}...")

    try:
        if not response_content:
            return []
        return json.loads(response_content)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}. Raw LLM output: {response_content[:500]}...")
        return []

def get_mcq_prompt(with_answer_key: bool, text_to_process: str, current_q_page: int, answer_page: Optional[int] = None) -> str:

    json_structure = """
        {{
          "content_type": "mcq",
          "question_number": <int>,
          "page": <int>,
          "question_text": "<str>",
          "options": {{
            "ক": "<str>",
            "খ": "<str>",
            "গ": "<str>",
            "ঘ": "<str>"
          }},
          "correct_answer_key": "<str>",
          "correct_answer_text": "<str>"
        }}
    """
    if with_answer_key:
        answer_key_info = f"2. A later section called 'উত্তরমালা' that contains correct answers. The answer key is on page {answer_page} and is provided within this text block. Match each question with its correct answer."
        page_context_info = f"This text block contains questions from page {current_q_page} and the answer key from page {answer_page}."
        
        return f"""
        The following Bangla text contains:
        1. A series of MCQs with options, without answers, primarily from page {current_q_page}.
        {answer_key_info}
        
        Return the structured output as a JSON array of objects. Each object should strictly follow this schema (replace <type> with actual values):
        [{json_structure.strip()}]

        Ensure the 'page' field accurately reflects the page number of the *question itself*.
        Do not include any other text or explanation in your response, only the JSON.

        {page_context_info}:
        ---
        {text_to_process}
        ---
        """
    else:
        return f"""
        The following Bangla text from page {current_q_page} contains a series of Multiple Choice Questions (MCQs) with options.
        Some questions might have answers provided immediately after the options or within the question text itself.

        Extract each MCQ and identify the question number, question text, options, and if an answer is clearly provided (e.g., marked with 'উত্তর:' or visually distinct), identify the correct option key (ক, খ, গ, ঘ) and its corresponding text.
        
        Return the structured output as a JSON array of objects. Each object should strictly follow this schema (replace <type> with actual values):
        [{json_structure.strip()}]

        Ensure the 'page' field accurately reflects the page number of the *question itself*.
        Do not include any other text or explanation in your response, only the JSON.

        Text from page {current_q_page}:
        ---
        {text_to_process}
        ---
        """

def get_creative_prompt(text_to_process: str, page_number: int) -> str:
    json_structure = """
        {{
          "content_type": "creative_question",
          "question_number": <int>,
          "page": <int>,
          "stem_text": "<str>",
          "sub_questions": {{
            "ক": "<str>",
            "খ": "<str>",
            "গ": "<str>",
            "ঘ": "<str>"
          }}
        }}
    """
    return f"""
    The following Bangla text from page {page_number} contains 'সৃজনশীল প্রশ্ন' (Creative Questions).
    Each creative question typically starts with "প্রশ্ন-" followed by a number, and includes a stem/scenario and multiple sub-questions (ক, খ, গ, ঘ).

    Extract each complete creative question block.
    Return the structured output as a JSON array of objects. Each object should strictly follow this schema (replace <type> with actual values):
    [{json_structure.strip()}]

    Ensure the 'page' field accurately reflects the page number of the *question itself*.
    Do not include any other text or explanation in your response, only the JSON.

    Text from page {page_number}:
    ---
    {text_to_process}
    ---
    """

def get_prose_prompt(section: str, text_to_process: str, page_number: int) -> str:
    json_structure = """
        {{
          "content_type": "prose",
          "section": "<str>",
          "page": <int>,
          "text": "<str>"
        }}
    """
    return f"""
    The following Bangla text is from the '{section}' section, specifically from page {page_number}.
    Clean and logically break it down into semantically meaningful chunks (e.g., paragraphs, distinct sub-sections).
    Remove any garbage characters, join broken words, and ensure consistent formatting.
    Do NOT translate. Return only cleaned Bangla text.

    Return the structured output as a JSON array of objects. Each object should strictly follow this schema (replace <type> with actual values):
    [{json_structure.strip()}]

    Ensure the 'page' field accurately reflects the page number of the *text itself*.
    Do not include any other text or explanation in your response, only the JSON.

    Text from page {page_number}:
    ---
    {text_to_process}
    ---
    """

def process_pdf_semantically(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    logger.info("Starting semantic PDF processing...")
    pages = extract_text_with_ocr(pdf_bytes)
    if not pages:
        logger.error("OCR failed or empty PDF. Aborting.")
        return []

    blocks = group_semantic_blocks(pages)
    all_chunks = []

    if blocks["mcq_questions_with_separate_answer_key"]:
        sep_ans_pages = blocks["mcq_questions_with_separate_answer_key"]
        
        answer_key_page_obj = next((p for p in sep_ans_pages if p["page_number"] == 41), None)
        answer_key_text = answer_key_page_obj["text"] if answer_key_page_obj else ""
        answer_key_page_num = answer_key_page_obj["page_number"] if answer_key_page_obj else 0

        q_pages = [p for p in sep_ans_pages if p["page_number"] != 41]

        for q_page in q_pages:
            text_for_llm = q_page["text"]
            if answer_key_text:
                text_for_llm += f"\n\n--- উত্তরমালা (Page {answer_key_page_num}) ---\n" + answer_key_text

            logger.info(f"Processing MCQs with separate answer key from page {q_page['page_number']} (with answer key from page {answer_key_page_num})")
            
            prompt_str = get_mcq_prompt(True, text_for_llm, q_page["page_number"], answer_key_page_num)
            mcq_data = prompt_and_parse(text_for_llm, prompt_str) 
            all_chunks.extend(mcq_data)
    
    if blocks["mcq_questions_with_inline_answers"]:
        for p in blocks["mcq_questions_with_inline_answers"]:
            logger.info(f"Processing MCQs with inline answers from page {p['page_number']}")
            prompt_str = get_mcq_prompt(False, p["text"], p["page_number"])
            mcq_data = prompt_and_parse(p["text"], prompt_str)
            all_chunks.extend(mcq_data)

    if blocks["creative_questions"]:
        for p in blocks["creative_questions"]:
            logger.info(f"Processing Creative Questions from page {p['page_number']}")
            prompt_str = get_creative_prompt(p["text"], p["page_number"])
            creative_data = prompt_and_parse(p["text"], prompt_str)
            all_chunks.extend(creative_data)

    prose_labels = {
        "vocabulary_and_notes": "শব্দার্থ ও টীকা",
        "main_content": "মূল আলোচ্য বিষয়",
        "author_info": "লেখক পরিচিতি",
        "path_porichiti": "পাঠ পরিচিতি"
    }

    for key, label in prose_labels.items():
        if blocks[key]:
            for p in blocks[key]:
                logger.info(f"Processing prose section '{label}' from page {p['page_number']}")
                prompt_str = get_prose_prompt(label, p["text"], p["page_number"])
                prose_data = prompt_and_parse(p["text"], prompt_str)
                all_chunks.extend(prose_data)

    logger.info(f"Total structured chunks: {len(all_chunks)}")
    return all_chunks