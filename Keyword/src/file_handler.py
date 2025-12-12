# src/file_handler.py
import google.generativeai as genai
import mimetypes
from pathlib import Path
from utils.logger import logger
from config.settings import GOOGLE_API_KEY

class FileHandler:
    def __init__(self, client=None):
        self.client = client
        genai.configure(api_key=GOOGLE_API_KEY)   # 🔥 thiếu dòng này nên lỗi
        self.uploaded_files = []

    def prepare_file(self, file_path: str):
        """
        Chuẩn bị file pdf/ảnh để upload lên Gemini
        """
        path = Path(file_path)
        mime_type, _ = mimetypes.guess_type(path)
        mime_type = mime_type or "application/pdf"

        logger.info(f"📎 Uploading file to Gemini: {path.name}")

        try:
            uploaded = genai.upload_file(path, mime_type=mime_type)
            self.uploaded_files.append(uploaded)
            return uploaded
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            raise e


    def cleanup(self):
        """
        Xóa file tạm trên Gemini (tránh tốn quota)
        """
        for f in self.uploaded_files:
            try:
                f.delete()
            except:
                pass
        
        logger.info("🧹 Temp files cleared!")
