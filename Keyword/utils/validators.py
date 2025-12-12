# utils/validators.py

from config.settings import MIN_KEYWORDS, MAX_KEYWORDS, DEFAULT_NUM_KEYWORDS

def validate_num_keywords(num: int) -> int:
    """Đảm bảo số từ khóa nằm trong giới hạn hợp lệ."""
    if num < MIN_KEYWORDS:
        return MIN_KEYWORDS
    if num > MAX_KEYWORDS:
        return MAX_KEYWORDS
    return num if num > 0 else DEFAULT_NUM_KEYWORDS
