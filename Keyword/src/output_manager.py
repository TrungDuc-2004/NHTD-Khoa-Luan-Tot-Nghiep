# import json
# from pathlib import Path
# from datetime import datetime
# from config.settings import OUTPUT_DIR
# from utils.logger import logger

# class OutputManager:
#     def __init__(self, output_dir=OUTPUT_DIR):
#         # Đảm bảo output_dir là đối tượng Path
#         self.output_dir = Path(output_dir) if output_dir else Path("output")
#         self.output_dir.mkdir(parents=True, exist_ok=True)
    
#     # --- ĐÂY LÀ HÀM BẠN ĐANG THIẾU ---
#     def save(self, content: str, base_name: str, format: str = 'txt', file_info: dict = None) -> str:
#         """
#         Hàm chính để lưu file. Nó sẽ tự chọn cách lưu dựa trên format.
#         """
#         if format == 'json':
#             return self.save_json(content, base_name, file_info)
#         else:
#             # Mặc định dùng save_text cho txt và md
#             return self.save_text(content, base_name, file_info, extension=format)

#     def save_text(self, content: str, base_name: str, file_info=None, extension='txt'):
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         output_path = self.output_dir / f"{base_name}_keywords_{timestamp}.{extension}"
        
#         try:
#             with open(output_path, 'w', encoding='utf-8') as f:
#                 f.write("="*70 + "\n")
#                 f.write("KEYWORD EXTRACTION REPORT\n")
#                 f.write("="*70 + "\n\n")
#                 if file_info:
#                     # Dùng .get() để tránh lỗi nếu thiếu key
#                     f.write(f"📄 Source: {file_info.get('name', 'Unknown')}\n")
#                     f.write(f"📦 Size: {file_info.get('size_kb', 0)} KB\n\n")
#                 f.write(content)
            
#             logger.info(f"💾 Saved: {output_path}")
#             return str(output_path)
#         except Exception as e:
#             logger.error(f"❌ Lỗi khi lưu file text: {e}")
#             return ""

#     def save_json(self, content: str, base_name: str, file_info=None):
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         output_path = self.output_dir / f"{base_name}_keywords_{timestamp}.json"
        
#         data = {
#             "meta": file_info if file_info else {},
#             "extracted_at": datetime.now().isoformat(),
#             "keywords": content  # Có thể cần xử lý thêm nếu muốn keywords dạng list
#         }

#         try:
#             with open(output_path, 'w', encoding='utf-8') as f:
#                 json.dump(data, f, ensure_ascii=False, indent=2)
            
#             logger.info(f"💾 Saved JSON: {output_path}")
#             return str(output_path)
#         except Exception as e:
#             logger.error(f"❌ Lỗi khi lưu file JSON: {e}")
#             return ""
    
#     def print_result(self, content: str):
#         print("\n" + "="*70)
#         print("📊 KẾT QUẢ")
#         print("="*70 + "\n")
#         print(content)
#         print("\n" + "="*70 + "\n")

import json
from pathlib import Path
from datetime import datetime
from config.settings import OUTPUT_DIR
from utils.logger import logger


class OutputManager:
    def __init__(self, output_dir=OUTPUT_DIR):
        # Nếu không truyền OUTPUT_DIR thì mặc định dùng data/output
        self.output_dir = Path(output_dir) if output_dir else Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, data, base_name: str, format: str = 'txt', file_info: dict = None) -> str:
        """
        Lưu kết quả trích xuất ra file.

        - format = 'json' -> lưu dạng JSON đầy đủ (meta + result)
        - format khác     -> lưu dạng report .txt chỉ chứa keywords
        """
        # Làm sạch tên file (chỉ giữ chữ, số, space, -, _)
        safe_base_name = "".join([c for c in base_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        
        if format == 'json':
            return self._save_json_file(data, safe_base_name, file_info)
        else:
            return self._save_text_report(data, safe_base_name, file_info)

    def _save_json_file(self, data, base_name, file_info):
        """
        Lưu file JSON:
        {
          "meta": {...},
          "extracted_at": "...",
          "result": { ...data gốc... }
        }
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"{base_name}_keywords_{timestamp}.json"
        
        final_data = {
            "meta": file_info if file_info else {},
            "extracted_at": datetime.now().isoformat(),
            "result": data
        }
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2)
            logger.info(f" Saved JSON: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f" Save JSON failed: {e}")
            return ""

    def _save_text_report(self, data, base_name, file_info):
        """
        Lưu file .txt dạng REPORT, nhưng:
        🔹 CHỈ in mỗi keyword (term)
        🔹 KHÔNG in description
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"{base_name}_keywords_{timestamp}.txt"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # HEADER
                f.write("="*80 + "\n")
                f.write("KEYWORD EXTRACTION REPORT\n")
                f.write("="*80 + "\n\n")
                
                # Kiểm tra dữ liệu hợp lệ
                if isinstance(data, dict) and 'keywords' in data:
                    keywords = data['keywords']
                    count = len(keywords)
                    
                    # Câu dẫn nhập
                    f.write(f"Dưới đây là {count} từ khóa quan trọng nhất được trích xuất từ tài liệu:\n\n")
                    
                    # CHỈ GHI TERM, MỖI KEYWORD MỘT DÒNG
                    for item in keywords:
                        term = item.get('term', 'N/A').strip()
                        f.write(f"{term}\n")
                else:
                    # Trường hợp lỗi / không đúng format
                    f.write("Không tìm thấy dữ liệu từ khóa hợp lệ.\n")
                    if isinstance(data, dict) and 'error' in data:
                        f.write(f"Lỗi chi tiết: {data['error']}\n")
                    else:
                        f.write(f"Raw Data: {str(data)}")
                    
            logger.info(f"💾 Saved Report: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"❌ Save Text failed: {e}")
            return ""
            
    def print_result(self, data):
        """
        In ra console kết quả trích xuất:
        keyword1
        keyword2
        ...
        (Không in description)
        """
        print("\n" + "="*70)
        if isinstance(data, dict) and 'keywords' in data:
            print(f" Tìm thấy {len(data['keywords'])} từ khóa:\n")
            for item in data['keywords']:
                term = item.get('term', 'N/A')
                print(f"🔑 {term}")
        else:
            print(f"⚠️ Raw result: {data}")
        print("="*70 + "\n")
