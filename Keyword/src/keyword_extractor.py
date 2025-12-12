# from config.settings import EXTRACTION_PROMPT_TEMPLATE, DEFAULT_NUM_KEYWORDS
# from utils.validators import validate_num_keywords
# from utils.logger import logger
# from src.api_client import GeminiClient
# from src.file_handler import FileHandler
# import docx 
# from pathlib import Path

# class KeywordExtractor:
#     def __init__(self):
#         self.client = GeminiClient()
#         self.file_handler = FileHandler(self.client)
    
#     def extract(self, file_path: str, num_keywords: int = DEFAULT_NUM_KEYWORDS):
#         """Xử lý trích xuất cho 1 file duy nhất"""
#         num_keywords = validate_num_keywords(num_keywords)
        
#         logger.info("="*60)
#         logger.info(f"🚀 EXTRACTING: {Path(file_path).name}")
#         logger.info("="*60)

#         # Kiểm tra loại file
#         path = Path(file_path)
#         suffix = path.suffix.lower()
        
#         # Danh sách các file nên đọc text trực tiếp thay vì upload
#         text_based_files = ['.docx', '.txt', '.md', '.json']

#         try:
#             # TRƯỜNG HỢP 1: Xử lý file DOCX hoặc Text (Không upload, chỉ đọc nội dung)
#             if suffix in text_based_files:
#                 logger.info(f"📄 Detected text-based file ({suffix}). Reading content locally...")
                
#                 # 1. Đọc nội dung file thành chữ
#                 content_text = self._read_file_content(file_path)
                
#                 # 2. Tạo prompt (gắn nội dung file vào prompt)
#                 base_prompt = EXTRACTION_PROMPT_TEMPLATE.format(
#                     experience_years=10,
#                     num_keywords=num_keywords
#                 )
#                 full_prompt = f"{base_prompt}\n\n---\nNỘI DUNG VĂN BẢN CẦN XỬ LÝ:\n{content_text}"
                
#                 # 3. Gửi request (truyền file_obj=None)
#                 result = self.client.generate_content(full_prompt, file_obj=None)

#             # TRƯỜNG HỢP 2: Xử lý PDF hoặc Ảnh (Upload file)
#             else:
#                 logger.info(f"📎 Detected binary file ({suffix}). Uploading to Gemini...")
#                 file_obj = self.file_handler.prepare_file(file_path)
                
#                 prompt = EXTRACTION_PROMPT_TEMPLATE.format(
#                     experience_years=10,
#                     num_keywords=num_keywords
#                 )
                
#                 result = self.client.generate_content(prompt, file_obj)
            
#             logger.info("✅ Completed file extraction")
#             return result

#         except Exception as e:
#             logger.error(f"❌ Extraction failed for {path.name}: {str(e)}")
#             return f"ERROR: {str(e)}"

#         finally:
#             # Chỉ cleanup nếu đã từng upload file
#             if suffix not in text_based_files:
#                 self.file_handler.cleanup()

#     # --- HÀM MỚI THÊM ĐỂ SỬA LỖI BATCH ---
#     def extract_batch(self, file_paths: list, num_keywords: int = DEFAULT_NUM_KEYWORDS):
#         """Xử lý danh sách nhiều file"""
#         results = {}
#         total = len(file_paths)
        
#         for index, file_path in enumerate(file_paths, 1):
#             logger.info(f"\nProcessing file {index}/{total}...")
#             try:
#                 # Gọi lại hàm extract đơn lẻ
#                 result = self.extract(file_path, num_keywords)
#                 results[file_path] = result
#             except Exception as e:
#                 logger.error(f"Failed to process batch item {file_path}: {e}")
#                 results[file_path] = f"ERROR: {str(e)}"
                
#         return results
#     # -------------------------------------

#     def _read_file_content(self, file_path: str) -> str:
#         """Đọc nội dung text từ file .txt, .md hoặc .docx"""
#         path = Path(file_path)
#         suffix = path.suffix.lower()

#         # Xử lý file Word (.docx)
#         if suffix == '.docx':
#             try:
#                 doc = docx.Document(file_path)
#                 full_text = [para.text for para in doc.paragraphs if para.text.strip()]
#                 return '\n'.join(full_text)
#             except Exception as e:
#                 raise ValueError(f"Lỗi đọc file Word: {e}")
        
#         # Xử lý file Text (.txt, .md, .json, ...)
#         else:
#             try:
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     return f.read()
#             except UnicodeDecodeError:
#                 with open(file_path, 'r', encoding='latin-1') as f:
#                     return f.read()

import json
import re
import docx
from pathlib import Path
from config.settings import EXTRACTION_PROMPT_TEMPLATE, DEFAULT_NUM_KEYWORDS
from utils.validators import validate_num_keywords
from utils.logger import logger
from src.api_client import GeminiClient
from src.file_handler import FileHandler

class KeywordExtractor:
    def __init__(self):
        self.client = GeminiClient()
        self.file_handler = FileHandler(self.client)
    
    def extract(self, file_path: str, num_keywords: int = DEFAULT_NUM_KEYWORDS):
        """Xử lý trích xuất cho 1 file duy nhất"""
        num_keywords = validate_num_keywords(num_keywords)
        
        logger.info("="*60)
        logger.info(f"🚀 EXTRACTING: {Path(file_path).name}")
        logger.info("="*60)

        path = Path(file_path)
        suffix = path.suffix.lower()
        text_based_files = ['.docx', '.txt', '.md', '.json']

        try:
            response_text = ""
            
            # Tạo base prompt với tham số
            full_prompt_content = EXTRACTION_PROMPT_TEMPLATE.format(
                experience_years=10,
                num_keywords=num_keywords
            )

            # TRƯỜNG HỢP 1: File Text/Word (Đọc tại chỗ)
            if suffix in text_based_files:
                logger.info(f"📄 Reading local content ({suffix})...")
                content_text = self._read_file_content(file_path)
                full_prompt = f"{full_prompt_content}\n\n---\nNỘI DUNG VĂN BẢN:\n{content_text}"
                response_text = self.client.generate_content(full_prompt, file_obj=None)

            # TRƯỜNG HỢP 2: File PDF/Ảnh (Upload)
            else:
                logger.info(f"📎 Uploading binary file ({suffix})...")
                file_obj = self.file_handler.prepare_file(file_path)
                response_text = self.client.generate_content(full_prompt_content, file_obj)
            
            logger.info("🔄 Parsing response to JSON...")
            parsed_result = self._parse_json_response(response_text)
            
            logger.info(f"✅ Found {len(parsed_result.get('keywords', []))} keywords")
            return parsed_result

        except Exception as e:
            logger.error(f"❌ Extraction failed for {path.name}: {str(e)}")
            return {"keywords": [], "error": str(e)}

        finally:
            if suffix not in text_based_files:
                self.file_handler.cleanup()

    def extract_batch(self, file_paths: list, num_keywords: int = DEFAULT_NUM_KEYWORDS):
        results = {}
        for index, file_path in enumerate(file_paths, 1):
            logger.info(f"--- Batch {index}/{len(file_paths)} ---")
            try:
                results[file_path] = self.extract(file_path, num_keywords)
            except Exception as e:
                results[file_path] = {"keywords": [], "error": str(e)}
        return results

    def _read_file_content(self, file_path: str) -> str:
        path = Path(file_path)
        if path.suffix.lower() == '.docx':
            try:
                doc = docx.Document(file_path)
                return '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
            except Exception as e:
                raise ValueError(f"Docx error: {e}")
        else:
            # Thử nhiều encoding để tránh lỗi font
            for enc in ['utf-8', 'utf-8-sig', 'latin-1']:
                try:
                    with open(file_path, 'r', encoding=enc) as f: return f.read()
                except: continue
            return ""

    def _parse_json_response(self, text: str) -> dict:
        """Hàm làm sạch và parse JSON từ phản hồi của Gemini"""
        try:
            clean_text = text.strip()
            # Tìm chuỗi JSON trong markdown code block nếu có
            json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(clean_text)
        except Exception:
            # Nếu lỗi parse JSON, trả về dict rỗng để không crash chương trình
            logger.warning("⚠️ Could not parse JSON. Returning raw text in error field.")
            return {"keywords": [], "raw_text": text}