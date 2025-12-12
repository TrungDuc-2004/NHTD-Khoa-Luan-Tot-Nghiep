# src/api_client.py

import google.generativeai as genai
from config.settings import GOOGLE_API_KEY, MODEL_NAME
from utils.logger import logger


class GeminiClient:
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)

    def generate_content(self, prompt, file_obj=None):
        """
        Gửi prompt tới Gemini, hỗ trợ cả dạng text và upload file.
        """
        logger.info("🔗 Sending request to Gemini API...")

        try:
            if file_obj:
                response = self.model.generate_content([prompt, file_obj])
            else:
                response = self.model.generate_content(prompt)

            result = response.text
            logger.info("📥 Response received.")
            return result

        except Exception as e:
            logger.error(f"❌ Gemini API Error: {e}")
            return f'{{"keywords": [], "error": "{e}"}}'
