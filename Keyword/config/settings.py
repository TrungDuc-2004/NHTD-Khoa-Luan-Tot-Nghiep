# import os
# from pathlib import Path
# from dotenv import load_dotenv

# load_dotenv()

# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

# if not GOOGLE_API_KEY:
#     raise ValueError("❌ Thiếu GOOGLE_API_KEY trong file .env")

# SUPPORTED_FORMATS = {'.pdf', '.txt', '.docx', '.doc', '.csv', '.md'}
# MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
# FILE_PROCESSING_TIMEOUT = 120

# DEFAULT_NUM_KEYWORDS = 15
# MIN_KEYWORDS = 5
# MAX_KEYWORDS = 30

# BASE_DIR = Path(__file__).parent.parent
# DATA_DIR = BASE_DIR / "data"
# INPUT_DIR = DATA_DIR / "input"
# OUTPUT_DIR = DATA_DIR / "output"
# LOGS_DIR = BASE_DIR / "logs"

# for directory in [INPUT_DIR, OUTPUT_DIR, LOGS_DIR]:
#     directory.mkdir(parents=True, exist_ok=True)

# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# LOG_FILE = LOGS_DIR / "app.log"

# # --- ĐÃ SỬA PHẦN NÀY ĐỂ CHỈ LẤY TỪ KHÓA ---
# EXTRACTION_PROMPT_TEMPLATE = """
# Bạn là một chuyên gia SEO và phân tích nội dung.
# Nhiệm vụ: Trích xuất {num_keywords} từ khóa (keywords) quan trọng nhất từ văn bản được cung cấp dưới đây.

# YÊU CẦU QUAN TRỌNG VỀ ĐỊNH DẠNG OUTPUT:
# 1. CHỈ liệt kê các từ khóa, TUYỆT ĐỐI KHÔNG kèm theo định nghĩa hay giải thích phía sau.
# 2. KHÔNG sử dụng các ký tự đánh dấu như 🔑, -, hay dấu gạch đầu dòng ở đầu dòng.
# 3. KHÔNG in đậm (bỏ dấu **).
# 4. Mỗi từ khóa nằm trên một dòng riêng biệt.

# Ví dụ output mong muốn (Format chuẩn):
# Thiết kế đồ họa
# Truyền thông đa phương tiện
# Adobe Photoshop
# Marketing
# Sáng tạo nội dung

# Kinh nghiệm chuyên gia: {experience_years} năm.
# Hãy bắt đầu trích xuất từ nội dung dưới đây:
# """

# OUTPUT_FORMATS = {'txt': 'text/plain', 'md': 'text/markdown', 'json': 'application/json'}
# DEFAULT_OUTPUT_FORMAT = 'txt'

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Lưu ý: Hiện tại model ổn định là gemini-1.5-flash hoặc gemini-1.5-pro
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

if not GOOGLE_API_KEY:
    raise ValueError("❌ Thiếu GOOGLE_API_KEY trong file .env")

SUPPORTED_FORMATS = {'.pdf', '.txt', '.docx', '.doc', '.csv', '.md', '.json'}
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
FILE_PROCESSING_TIMEOUT = 120

DEFAULT_NUM_KEYWORDS = 15
MIN_KEYWORDS = 5
MAX_KEYWORDS = 50

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

for directory in [INPUT_DIR, OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"

# --- CẬP NHẬT PROMPT ĐỂ LẤY CẢ MÔ TẢ (JSON FORMAT) ---
EXTRACTION_PROMPT_TEMPLATE = """
Bạn là một chuyên gia SEO và phân tích nội dung với {experience_years} năm kinh nghiệm.
Nhiệm vụ: Đọc hiểu tài liệu và trích xuất {num_keywords} từ khóa quan trọng nhất.

YÊU CẦU ĐẦU RA (JSON FORMAT):
Hãy phân tích tài liệu và trả về kết quả dưới dạng JSON Object hợp lệ (RFC 8259).
Không thêm bất kỳ lời dẫn hay markdown nào (như ```json) ngoài JSON thuần.

1. "keywords": Một danh sách chứa đúng {num_keywords} từ khóa.
2. Mỗi từ khóa PHẢI có 2 trường: 
   - "term": Tên từ khóa.
   - "description": Giải thích ngắn gọn, súc tích (1-2 câu) ý nghĩa của nó trong văn bản.

Cấu trúc JSON mẫu bắt buộc:
{{
    "keywords": [
        {{
            "term": "Tên từ khóa 1",
            "description": "Giải thích ý nghĩa..."
        }},
        {{
            "term": "Tên từ khóa 2",
            "description": "Giải thích ý nghĩa..."
        }}
    ]
}}
"""

OUTPUT_FORMATS = {'txt': 'text/plain', 'md': 'text/markdown', 'json': 'application/json'}
DEFAULT_OUTPUT_FORMAT = 'txt'