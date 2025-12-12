# import sys
# import argparse
# from pathlib import Path

# from src.keyword_extractor import KeywordExtractor
# from src.output_manager import OutputManager
# from utils.logger import logger
# from utils.validators import ValidationError
# from src.api_client import GeminiAPIError
# from config.settings import (
#     DEFAULT_NUM_KEYWORDS, 
#     MIN_KEYWORDS, 
#     MAX_KEYWORDS,
#     INPUT_DIR
# )

# def parse_arguments():
#     """Parse command line arguments"""
#     parser = argparse.ArgumentParser(
#         description="🔍 Trích xuất từ khóa từ file sử dụng Gemini AI",
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         epilog="""
# Ví dụ sử dụng:
#   python main.py document.pdf
#   python main.py document.pdf -n 20 -f md
#   python main.py document.pdf --no-save
#   python main.py file1.pdf file2.txt --batch
#         """
#     )
    
#     parser.add_argument(
#         'files',
#         nargs='+',
#         help='Đường dẫn đến file(s) cần xử lý'
#     )
    
#     parser.add_argument(
#         '-n', '--num-keywords',
#         type=int,
#         default=DEFAULT_NUM_KEYWORDS,
#         help=f'Số lượng từ khóa (mặc định: {DEFAULT_NUM_KEYWORDS}, min: {MIN_KEYWORDS}, max: {MAX_KEYWORDS})'
#     )
    
#     parser.add_argument(
#         '-f', '--format',
#         choices=['txt', 'md', 'json'],
#         default='txt',
#         help='Định dạng output (mặc định: txt)'
#     )
    
#     parser.add_argument(
#         '--no-save',
#         action='store_true',
#         help='Chỉ hiển thị kết quả, không lưu file'
#     )
    
#     parser.add_argument(
#         '--batch',
#         action='store_true',
#         help='Xử lý nhiều file cùng lúc'
#     )
    
#     parser.add_argument(
#         '--output-dir',
#         type=str,
#         help='Thư mục lưu output (tùy chọn)'
#     )
    
#     return parser.parse_args()

# def process_single_file(
#     file_path: str,
#     num_keywords: int,
#     output_format: str,
#     save_output: bool,
#     output_manager: OutputManager
# ):
#     """
#     Xử lý một file đơn lẻ
    
#     Args:
#         file_path: Đường dẫn file
#         num_keywords: Số lượng từ khóa
#         output_format: Format output
#         save_output: Có lưu file không
#         output_manager: OutputManager instance
#     """
#     try:
#         # Khởi tạo extractor
#         extractor = KeywordExtractor()
        
#         # Trích xuất từ khóa
#         result = extractor.extract(
#             file_path=file_path,
#             num_keywords=num_keywords
#         )
        
#         # In kết quả ra console
#         output_manager.print_result(result)
        
#         # Lưu file nếu cần
#         if save_output:
#             file_info = extractor.file_handler.get_info()
#             base_name = Path(file_path).stem
            
#             saved_path = output_manager.save(
#                 content=result,
#                 base_name=base_name,
#                 format=output_format,
#                 file_info=file_info
#             )
            
#             logger.info(f"✅ Hoàn thành! Output: {saved_path}")
        
#         return True
        
#     except ValidationError as e:
#         logger.error(f"Validation error: {e}")
#         return False
#     except GeminiAPIError as e:
#         logger.error(f"API error: {e}")
#         return False
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")
#         return False

# def process_batch_files(
#     file_paths: list,
#     num_keywords: int,
#     output_format: str,
#     save_output: bool,
#     output_manager: OutputManager
# ):
#     """
#     Xử lý nhiều file
    
#     Args:
#         file_paths: Danh sách đường dẫn
#         num_keywords: Số lượng từ khóa
#         output_format: Format output
#         save_output: Có lưu file không
#         output_manager: OutputManager instance
#     """
#     extractor = KeywordExtractor()
    
#     logger.info(f"🔄 Batch processing {len(file_paths)} files...")
    
#     results = extractor.extract_batch(
#         file_paths=file_paths,
#         num_keywords=num_keywords
#     )
    
#     # Xử lý kết quả
#     success_count = 0
#     for file_path, result in results.items():
#         if not result.startswith("ERROR"):
#             success_count += 1
            
#             if save_output:
#                 base_name = Path(file_path).stem
#                 output_manager.save(
#                     content=result,
#                     base_name=base_name,
#                     format=output_format
#                 )
    
#     logger.info(f"✅ Batch completed: {success_count}/{len(file_paths)} successful")

# def main():
#     """Main entry point"""
#     # Parse arguments
#     args = parse_arguments()
    
#     # Bắt đầu session
#     logger.info(f"🚀 Starting Gemini Keyword Extractor")
#     logger.info(f"💻 Device: MacBook Air 13-inch M4 2025")
    
#     # Khởi tạo output manager
#     if args.output_dir:
#         output_manager = OutputManager(Path(args.output_dir))
#     else:
#         output_manager = OutputManager()
    
#     try:
#         # Xử lý batch hoặc single file
#         if args.batch and len(args.files) > 1:
#             process_batch_files(
#                 file_paths=args.files,
#                 num_keywords=args.num_keywords,
#                 output_format=args.format,
#                 save_output=not args.no_save,
#                 output_manager=output_manager
#             )
#         else:
#             # Xử lý từng file một
#             for file_path in args.files:
#                 logger.info(f"\n{'='*70}")
#                 logger.info(f"Processing: {file_path}")
#                 logger.info(f"{'='*70}")
                
#                 success = process_single_file(
#                     file_path=file_path,
#                     num_keywords=args.num_keywords,
#                     output_format=args.format,
#                     save_output=not args.no_save,
#                     output_manager=output_manager
#                 )
                
#                 if not success:
#                     logger.warning(f"⚠️  Failed to process: {file_path}")
        
#         logger.info("\n🎉 All tasks completed!")
#         return 0
        
#     except KeyboardInterrupt:
#         logger.warning("\n⚠️  Process interrupted by user")
#         return 130
#     except Exception as e:
#         logger.error(f"\n❌ Fatal error: {e}")
#         return 1

# if __name__ == "__main__":
#     sys.exit(main())

import sys
import argparse
import glob
import os
from pathlib import Path

# Import các module
from src.keyword_extractor import KeywordExtractor
from src.output_manager import OutputManager
from utils.logger import logger
from config.settings import DEFAULT_NUM_KEYWORDS

def parse_arguments():
    parser = argparse.ArgumentParser(description="🔍 Trích xuất từ khóa Gemini AI")
    parser.add_argument('files', nargs='+', help='Đường dẫn file (hỗ trợ wildcard *)')
    parser.add_argument('--batch', action='store_true', help='Chế độ xử lý hàng loạt')
    parser.add_argument('--no-save', action='store_true', help='Không lưu file kết quả')
    parser.add_argument('-n', '--num-keywords', type=int, default=DEFAULT_NUM_KEYWORDS, help='Số lượng từ khóa')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Khởi tạo
    output_manager = OutputManager()
    extractor = KeywordExtractor()

    logger.info(f"🚀 Starting Gemini Keyword Extractor")

    # 1. Xử lý danh sách file đầu vào (Hỗ trợ cả dấu * trong ngoặc kép)
    files_to_process = []
    for path_arg in args.files:
        if '*' in path_arg:
            files_to_process.extend(glob.glob(path_arg))
        else:
            files_to_process.append(path_arg)
            
    # Lọc bỏ các file không tồn tại hoặc folder
    files_to_process = [f for f in files_to_process if os.path.isfile(f)]

    if not files_to_process:
        logger.error("❌ Không tìm thấy file nào hợp lệ. Vui lòng kiểm tra đường dẫn!")
        return

    logger.info(f"🔎 Tìm thấy {len(files_to_process)} file để xử lý.")

    # 2. Chạy vòng lặp xử lý từng file
    # Dùng extractor.extract() trực tiếp trong vòng lặp để dễ kiểm soát lỗi hơn là dùng extract_batch
    for idx, file_path in enumerate(files_to_process, 1):
        file_name = Path(file_path).name
        logger.info(f"\n--- Processing {idx}/{len(files_to_process)}: {file_name} ---")
        
        try:
            # --- BƯỚC A: TRÍCH XUẤT ---
            # Kết quả trả về bây giờ là Dictionary (JSON)
            result = extractor.extract(file_path, num_keywords=args.num_keywords)
            
            # --- BƯỚC B: KIỂM TRA LỖI (Logic mới) ---
            is_success = False
            
            # Trường hợp 1: Kết quả là Dictionary (Code mới)
            if isinstance(result, dict):
                if result.get('error'):
                    logger.warning(f"⚠️ Lỗi từ API: {result.get('error')}")
                elif not result.get('keywords'):
                     logger.warning(f"⚠️ Không tìm thấy từ khóa nào trong file.")
                else:
                    is_success = True
            
            # Trường hợp 2: Kết quả là String (Code cũ hoặc lỗi crash)
            elif isinstance(result, str):
                if result.startswith("ERROR"):
                    logger.warning(f"⚠️ Lỗi hệ thống: {result}")
                else:
                    # Nếu là string bình thường thì coi như thành công (tương thích ngược)
                    is_success = True

            # --- BƯỚC C: LƯU KẾT QUẢ ---
            if is_success:
                # In ra màn hình console
                output_manager.print_result(result)
                
                if not args.no_save:
                    base_name = Path(file_path).stem
                    # Gọi hàm save với tham số chuẩn
                    saved_path = output_manager.save(result, base_name, format='txt')
                    if saved_path:
                        logger.info(f"✅ Đã lưu: {saved_path}")

        except Exception as e:
            logger.error(f"❌ Lỗi khi xử lý file {file_name}: {e}")

    logger.info("\n🎉 Tất cả tác vụ đã hoàn tất!")

if __name__ == "__main__":
    sys.exit(main())