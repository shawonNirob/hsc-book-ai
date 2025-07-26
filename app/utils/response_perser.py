import json
import logging
from typing import Any, Dict
from langchain_core.messages import BaseMessage, AIMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_ai_message(message: BaseMessage) -> Dict[str, Any]:
    if isinstance(message, AIMessage):
        content = message.content
        logger.info(f"Raw content from AIMessage: {content}")

        if content.startswith("```json"):
            content = content.strip("```json").strip("```").strip()

        try:
            parsed = json.loads(content)
            logger.info(f"process response: {parsed}")
            return parsed

        except json.JSONDecoderError as e:
            logger.error(f"Failed to parse content as JSON: {e}")
            return {"error": "Invalid JSON returned by model", "raw": content}

    return {"error": "Unexpectd response format", "raw": str(message)}