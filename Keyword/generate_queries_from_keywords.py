# #!/usr/bin/env python3
# """
# Sinh câu hỏi từ kho từ khóa (Phiên bản Clean Output - Chỉ lấy câu hỏi)
# """
# import sys
# import json
# import time
# from pathlib import Path
# from typing import List
# import re

# # Import module của bạn
# from src.api_client import GeminiClient
# from utils.logger import logger, create_session_log

# class KeywordQueryGenerator:
    
#     def __init__(self):
#         self.client = GeminiClient()
    
#     def load_keywords_from_file(self, file_path: str) -> List[str]:
#         """Đọc từ khóa từ file"""
#         path = Path(file_path)
#         keywords = []
#         try:
#             if path.suffix == '.json':
#                 with open(path, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     keywords = data.get('keywords', [])
#             else:
#                 with open(path, 'r', encoding='utf-8') as f:
#                     content = f.read()
#                     # Parse đơn giản các dòng có chứa từ khóa
#                     for line in content.split('\n'):
#                         clean_line = line.strip()
#                         if len(clean_line) > 3 and not clean_line.startswith('=='):
#                             # Logic lọc từ khóa đơn giản
#                             if '🔑' in clean_line:
#                                 match = re.search(r'🔑\s*([^|]+)', clean_line)
#                                 if match: keywords.append(match.group(1).strip())
#                             elif clean_line.startswith('- ') or clean_line.startswith('• '):
#                                 keywords.append(clean_line[1:].split(':')[0].strip())
                            
#             # Lọc trùng và làm sạch
#             keywords = list(set([k for k in keywords if k]))
#             logger.info(f"✅ Loaded {len(keywords)} unique keywords")
#             return keywords
#         except Exception as e:
#             logger.error(f"Load keywords failed: {e}")
#             return []

#     def generate_queries(self, keywords: List[str], num_queries: int = 30, context: str = None) -> List[str]:
#         """Điều phối sinh câu hỏi - Trả về List[String]"""
#         if not keywords: return []

#         # --- CHẾ ĐỘ MAX (BATCHING) ---
#         if num_queries == -1:
#             logger.info("🚀 MODE: MAXIMUM GENERATION (Batch Processing)")
#             return self._generate_queries_in_batches(keywords, context)

#         # --- CHẾ ĐỘ THƯỜNG ---
#         return self._call_gemini_api(keywords[:25], num_queries, context)

#     def _generate_queries_in_batches(self, keywords: List[str], context: str) -> List[str]:
#         """Chia nhỏ để sinh tối đa câu hỏi"""
#         BATCH_SIZE = 5
#         QUERIES_PER_KEYWORD = 8 
#         all_queries = []
        
#         for i in range(0, len(keywords), BATCH_SIZE):
#             batch_keywords = keywords[i : i + BATCH_SIZE]
#             logger.info(f"⚡ Processing batch: {batch_keywords}")
            
#             target_num = len(batch_keywords) * QUERIES_PER_KEYWORD
            
#             batch_results = self._call_gemini_api(
#                 batch_keywords, 
#                 num_queries=target_num, 
#                 context=context,
#                 is_strict_batch=True
#             )
            
#             if batch_results:
#                 all_queries.extend(batch_results)
            
#             time.sleep(1) # Tránh rate limit

#         return list(set(all_queries)) # Lọc trùng lần cuối

#     def _call_gemini_api(self, keywords: List[str], num_queries: int, context: str, is_strict_batch: bool = False) -> List[str]:
#         """Gọi API và chỉ trả về danh sách string câu hỏi"""
        
#         if not context: context = f"Tin học"
#         keywords_str = '\n'.join(f"- {kw}" for kw in keywords)
        
#         prompt = f"""
# Bạn là trợ lý AI hỗ trợ sinh dữ liệu huấn luyện.
# Ngữ cảnh: {context}
# Từ khóa:
# {keywords_str}

# Nhiệm vụ: Sinh ra {num_queries} câu hỏi tìm kiếm (query) tự nhiên nhất mà học sinh có thể hỏi liên quan đến các từ khóa trên.
# Yêu cầu:
# 1. Câu hỏi phải đa dạng (định nghĩa, cách làm, sửa lỗi, so sánh).
# 2. Trả về kết quả dưới dạng JSON Array chứa các chuỗi string (List of Strings).
# 3. KHÔNG trả về object phức tạp, chỉ cần danh sách câu hỏi.

# Ví dụ output mong muốn:
# ["Câu hỏi A là gì?", "Làm sao để sửa lỗi B?", "So sánh C và D"]
# """

#         try:
#             response = self.client.generate_content(prompt=prompt, file_obj=None)
#             result_text = response.strip()
            
#             # Xử lý Markdown JSON nếu có
#             if '```' in result_text:
#                 match = re.search(r'```(?:json)?\s*(.*?)\s*```', result_text, re.DOTALL)
#                 if match: result_text = match.group(1)
            
#             data = json.loads(result_text)
            
#             # --- XỬ LÝ QUAN TRỌNG: LỌC DỮ LIỆU ---
#             clean_queries = []
            
#             if isinstance(data, list):
#                 for item in data:
#                     if isinstance(item, str):
#                         # Trường hợp 1: API trả về ["Câu 1", "Câu 2"] (Đúng mong đợi)
#                         clean_queries.append(item)
#                     elif isinstance(item, dict) and 'query' in item:
#                         # Trường hợp 2: API lỡ trả về [{"query": "Câu 1"}, ...] (Fallback)
#                         clean_queries.append(item['query'])
            
#             return clean_queries
            
#         except Exception as e:
#             logger.error(f"API Error: {e}")
#             return []

#     def save_queries(self, queries: List[str], output_file: str):
#         """Lưu file sạch"""
#         output_path = Path(output_file)
#         try:
#             # Loại bỏ trùng lặp và dòng trống
#             queries = sorted(list(set([q.strip() for q in queries if q.strip()])))
            
#             if output_path.suffix == '.json':
#                 # Lưu dạng JSON List đơn giản: ["q1", "q2"]
#                 with open(output_path, 'w', encoding='utf-8') as f:
#                     json.dump(queries, f, ensure_ascii=False, indent=2)
#             else:
#                 # Lưu dạng Text: Mỗi câu 1 dòng
#                 with open(output_path, 'w', encoding='utf-8') as f:
#                     f.write('\n'.join(queries))
                    
#             logger.info(f"💾 Saved {len(queries)} clean queries to: {output_path}")
#         except Exception as e:
#             logger.error(f"Save failed: {e}")

# def main():
#     # Phần xử lý tham số dòng lệnh giữ nguyên hoặc đơn giản hóa
#     if len(sys.argv) < 2:
#         print("Usage: python generate.py <keywords_file> [-n max]")
#         return

#     keywords_file = sys.argv[1]
#     num_queries = 30
#     # Check flag max
#     if '-n' in sys.argv and ('max' in sys.argv or '-1' in sys.argv):
#         num_queries = -1
        
#     output_file = f"data/output/{Path(keywords_file).stem}_queries.txt" # Mặc định lưu .txt cho dễ dùng

#     create_session_log()
#     gen = KeywordQueryGenerator()
#     kws = gen.load_keywords_from_file(keywords_file)
    
#     results = gen.generate_queries(kws, num_queries)
    
#     if results:
#         gen.save_queries(results, output_file)
#         print(f"\n✅ Đã tạo xong file sạch: {output_file}")
#     else:
#         print("❌ Không tạo được câu hỏi nào.")

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
"""
Sinh câu hỏi từ kho từ khóa (Hỗ trợ Batch Folder & Clean Output)
Input: File đơn hoặc Folder chứa các file keywords
Output: File text chứa danh sách câu hỏi (Clean)
"""
import sys
import json
import time
from pathlib import Path
from typing import List
import re

# Import module của bạn
from src.api_client import GeminiClient
from utils.logger import logger, create_session_log

class KeywordQueryGenerator:
    
    def __init__(self):
        self.client = GeminiClient()
    
    def load_keywords_from_file(self, file_path: str) -> List[str]:
        """
        Đọc từ khóa từ file.
        Hỗ trợ: JSON (mới/cũ) và TXT (regex)
        """
        path = Path(file_path)
        keywords = []
        try:
            # --- XỬ LÝ JSON ---
            if path.suffix == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Trường hợp 1: JSON cấu trúc mới {keywords: [{term: "A", desc: "B"}]}
                    if isinstance(data, dict) and 'keywords' in data:
                        raw_list = data['keywords']
                        if raw_list and isinstance(raw_list[0], dict):
                            keywords = [item.get('term') for item in raw_list if 'term' in item]
                        else:
                            keywords = raw_list # Trường hợp list string cũ
                    
                    # Trường hợp 2: JSON là list thuần ["A", "B"]
                    elif isinstance(data, list):
                        keywords = data

            # --- XỬ LÝ TXT ---
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        clean_line = line.strip()
                        if len(clean_line) > 3 and not clean_line.startswith('=='):
                            # Regex bắt pattern: 🔑 **Từ khóa** – Mô tả
                            if '🔑' in clean_line:
                                # Lấy phần text nằm giữa 🔑 và dấu – (hoặc hết dòng)
                                # Xử lý cả dấu * nếu có
                                clean_line = clean_line.replace('*', '')
                                match = re.search(r'🔑\s*([^–-]+)', clean_line)
                                if match: 
                                    keywords.append(match.group(1).strip())
                            elif clean_line.startswith('- ') or clean_line.startswith('• '):
                                keywords.append(clean_line[1:].split(':')[0].strip())
                            
            # Lọc trùng và làm sạch
            keywords = list(set([k.strip() for k in keywords if k and len(k.strip()) > 1]))
            logger.info(f"✅ Loaded {len(keywords)} keywords from {path.name}")
            return keywords

        except Exception as e:
            logger.error(f"Load keywords failed for {path.name}: {e}")
            return []

    def generate_queries(self, keywords: List[str], num_queries: int = 30, context: str = None) -> List[str]:
        """Điều phối sinh câu hỏi"""
        if not keywords: return []

        # --- CHẾ ĐỘ MAX (BATCHING) ---
        if num_queries == -1:
            logger.info(f"🚀 MODE: MAX GENERATION (Batching {len(keywords)} keywords)")
            return self._generate_queries_in_batches(keywords, context)

        # --- CHẾ ĐỘ THƯỜNG ---
        return self._call_gemini_api(keywords[:25], num_queries, context)

    def _generate_queries_in_batches(self, keywords: List[str], context: str) -> List[str]:
        BATCH_SIZE = 5
        QUERIES_PER_KEYWORD = 8 
        all_queries = []
        
        total_batches = (len(keywords) + BATCH_SIZE - 1) // BATCH_SIZE
        
        for i in range(0, len(keywords), BATCH_SIZE):
            batch_keywords = keywords[i : i + BATCH_SIZE]
            current_batch = (i // BATCH_SIZE) + 1
            
            logger.info(f"⚡ Batch {current_batch}/{total_batches}: Processing {len(batch_keywords)} keywords...")
            
            target_num = len(batch_keywords) * QUERIES_PER_KEYWORD
            
            batch_results = self._call_gemini_api(
                batch_keywords, 
                num_queries=target_num, 
                context=context,
                is_strict_batch=True
            )
            
            if batch_results:
                all_queries.extend(batch_results)
            
            time.sleep(1) # Tránh rate limit

        return list(set(all_queries))

    # def _call_gemini_api(self, keywords: List[str], num_queries: int, context: str, is_strict_batch: bool = False) -> List[str]:
    #     if not context: context = "Tin học THPT"
    #     keywords_str = '\n'.join(f"- {kw}" for kw in keywords)
        
    #     prompt = f"""
    #     Bạn là trợ lý AI giáo dục.
    #     Ngữ cảnh: {context}
    #     Từ khóa:
    #     {keywords_str}

    #     Nhiệm vụ: Sinh ra {num_queries} câu hỏi tìm kiếm (search queries) tự nhiên mà học sinh có thể dùng.
    #     Yêu cầu:
    #     1. Câu hỏi ngắn gọn, đa dạng (hỏi định nghĩa, cách làm, lỗi sai).
    #     2. KHÔNG đánh số thứ tự (1., 2.).
    #     3. OUTPUT FORMAT: Chỉ trả về JSON Array chứa danh sách các chuỗi string.
    #     Ví dụ: ["Câu 1?", "Câu 2?", "Câu 3?"]
    #     """

    #     try:
    #         response = self.client.generate_content(prompt=prompt, file_obj=None)
    #         result_text = response.strip()
            
    #         if '```' in result_text:
    #             match = re.search(r'```(?:json)?\s*(.*?)\s*```', result_text, re.DOTALL)
    #             if match: result_text = match.group(1)
            
    #         data = json.loads(result_text)
            
    #         clean_queries = []
    #         if isinstance(data, list):
    #             for item in data:
    #                 if isinstance(item, str): clean_queries.append(item)
    #                 elif isinstance(item, dict) and 'query' in item: clean_queries.append(item['query'])
            
    #         return clean_queries
    #     except Exception:
    #         return []

    def _call_gemini_api(self, keywords: List[str], num_queries: int, context: str, is_strict_batch: bool = False) -> List[str]:
        if not context: context = "Tin học THPT"
        keywords_str = '\n'.join(f"- {kw}" for kw in keywords)
        
        prompt = f"""
        Bạn là trợ lý AI giáo dục.
        Ngữ cảnh: {context}
        Từ khóa:
        {keywords_str}

        Nhiệm vụ: Sinh ra {num_queries} câu hỏi tìm kiếm (search queries) tự nhiên mà học sinh có thể dùng.
        Yêu cầu:
        1. Câu hỏi ngắn gọn, đa dạng (hỏi định nghĩa, cách làm, lỗi sai).
        2. KHÔNG đánh số thứ tự (1., 2.).
        3. OUTPUT FORMAT: Chỉ trả về JSON Array chứa danh sách các chuỗi string.
        Ví dụ: ["Câu 1?", "Câu 2?", "Câu 3?"]
        """

        result_text = "" # Khởi tạo biến để tránh lỗi reference

        try:
            response = self.client.generate_content(prompt=prompt, file_obj=None)
            result_text = response.strip()
            
            # 1. Cố gắng làm sạch JSON (tìm đoạn nằm giữa ```json ... ```)
            if '```' in result_text:
                match = re.search(r'```(?:json)?\s*(.*?)\s*```', result_text, re.DOTALL)
                if match: result_text = match.group(1)
            
            # 2. Parse JSON
            try:
                data = json.loads(result_text)
            except json.JSONDecodeError as e:
                logger.error(f"⚠️ JSON Decode Error. Raw output was:\n{result_text}")
                return []

            # 3. Trích xuất dữ liệu (Làm mềm dẻo hơn để bắt mọi trường hợp)
            clean_queries = []
            
            # Trường hợp A: Trả về List trực tiếp ["Q1", "Q2"]
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, str): 
                        clean_queries.append(item)
                    elif isinstance(item, dict) and 'query' in item: 
                        clean_queries.append(item['query'])
            
            # Trường hợp B: Trả về Dict {"queries": ["Q1", "Q2"]}
            elif isinstance(data, dict):
                # Tìm bất kỳ key nào chứa list
                for key, value in data.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, str):
                                clean_queries.append(item)
                            elif isinstance(item, dict) and 'query' in item:
                                clean_queries.append(item['query'])
                        break # Lấy list đầu tiên tìm thấy
            
            if not clean_queries:
                logger.warning("⚠️ Parsed JSON but found no queries inside.")

            return clean_queries

        except Exception as e:
            # --- ĐÂY LÀ PHẦN QUAN TRỌNG ĐỂ BIẾT LỖI ---
            logger.error(f"❌ API Error Details: {str(e)}")
            if result_text:
                logger.error(f"🔍 Context (Raw Response): {result_text[:200]}...") # In 200 ký tự đầu để check
            return []

    def save_queries(self, queries: List[str], output_file: str):
        output_path = Path(output_file)
        try:
            queries = sorted(list(set([q.strip() for q in queries if q.strip()])))
            
            # Luôn đảm bảo thư mục tồn tại
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_path.suffix == '.json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(queries, f, ensure_ascii=False, indent=2)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(queries))
                    
            logger.info(f"💾 Saved {len(queries)} clean queries to: {output_path.name}")
        except Exception as e:
            logger.error(f"Save failed: {e}")

# --- LOGIC XỬ LÝ ĐƠN VÀ ĐA FILE ---
def process_single_path(generator, file_path, num_queries, output_dir_base):
    """Hàm xử lý 1 file cụ thể"""
    input_path = Path(file_path)
    
    # Bỏ qua file output để tránh vòng lặp
    if "_queries" in input_path.name:
        return

    logger.info(f"\n📂 PROCESSING: {input_path.name}")
    
    # Load keywords
    keywords = generator.load_keywords_from_file(str(input_path))
    if not keywords:
        logger.warning(f"⚠️  No keywords found in {input_path.name}")
        return

    # Generate
    # Lấy tên file làm context (ví dụ: bai_01_thong_tin...)
    context = f"Bài học: {input_path.stem.replace('_', ' ')}"
    results = generator.generate_queries(keywords, num_queries, context)
    
    if results:
        # Save vào thư mục riêng biệt cho gọn
        out_dir = output_dir_base / "generated_queries"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = out_dir / f"{input_path.stem}_queries.txt"
        generator.save_queries(results, str(output_file))
    else:
        logger.error(f"❌ Failed to generate for {input_path.name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate.py <file_or_folder> [-n max]")
        return

    input_arg = sys.argv[1]
    num_queries = 30
    
    # Parse Args đơn giản
    if '-n' in sys.argv:
        idx = sys.argv.index('-n')
        if idx + 1 < len(sys.argv):
            val = sys.argv[idx+1]
            if val.lower() in ['max', '-1']: num_queries = -1
            else: num_queries = int(val)

    create_session_log()
    gen = KeywordQueryGenerator()
    
    input_path = Path(input_arg)
    
    # --- LOGIC QUAN TRỌNG: FOLDER vs FILE ---
    if input_path.is_dir():
        logger.info(f"📁 DIRECTORY MODE detected: {input_path}")
        # Tìm tất cả file txt và json
        files = sorted(list(input_path.glob("*.txt")) + list(input_path.glob("*.json")))
        logger.info(f"Found {len(files)} files to process.")
        
        for f in files:
            process_single_path(gen, f, num_queries, input_path.parent)
            
    elif input_path.is_file():
        logger.info(f"📄 SINGLE FILE MODE detected.")
        process_single_path(gen, input_path, num_queries, input_path.parent)
        
    else:
        logger.error("❌ Path does not exist.")

    logger.info("\n🎉 ALL DONE.")

if __name__ == "__main__":
    main()