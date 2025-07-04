# 预定义的非法字符集（使用集合，提高可读性和查找效率）
WINDOWS_INVALID_CHARS = {'<', '>', ':', '"', '/', '\\', '|', '?', '*'}
UNIX_INVALID_CHARS = {'/', '\0'}  # Unix 主要限制 '/' 和空字符
CONTROL_CHARS = {chr(i) for i in range(32)}  # ASCII 控制字符（0-31）
DEFAULT_INVALID_CHARS = WINDOWS_INVALID_CHARS | CONTROL_CHARS  # 默认合并 Windows + 控制字符