import asyncio
import hashlib
import os
from ._charset import DEFAULT_INVALID_CHARS

def sanitize_filename(
    filename: str,
    prefix: str = "",
    max_length: int = 255,
    invalid_chars: set[str] | None = None,
    replacement: str = "_",
) -> str:
    """
    转义文件名中的非法字符，支持自定义字符集和替换字符。

    Args:
        filename: 原始文件名（可含路径和扩展名）
        prefix: 可选前缀
        max_length: 文件名最大长度（不含扩展名）
        invalid_chars: 自定义非法字符集（None 时使用默认集）
        replacement: 替换字符（默认 '_'）

    Returns:
        处理后的安全文件名
    """
    if filename is None:
        return None

    # 初始化静态翻译表（仅在第一次调用时计算）
    if not hasattr(sanitize_filename, "_trans_cache"):
        sanitize_filename._trans_cache = {}

    # 获取或生成当前字符集的翻译表
    if invalid_chars is None:
        invalid_chars = DEFAULT_INVALID_CHARS
    cache_key = (frozenset(invalid_chars), replacement)  # 用 frozenset 作为字典键

    if cache_key not in sanitize_filename._trans_cache:
        # 生成新的翻译表
        trans_map = {ord(c): replacement for c in invalid_chars}
        sanitize_filename._trans_cache[cache_key] = str.maketrans(trans_map)

    trans_table = sanitize_filename._trans_cache[cache_key]

    # 处理文件名
    name, ext = os.path.splitext(filename)
    sanitized_name = name.translate(trans_table)

    # 处理超长文件名（哈希缩短）
    if len(sanitized_name) > max_length:
        hash_hex = hashlib.sha256(sanitized_name.encode()).hexdigest()[:16]
        sanitized_name = hash_hex

    # 添加前缀
    if prefix:
        sanitized_name = f"{prefix}_{sanitized_name}"

    return f"{sanitized_name}{ext}"

async def sanitize_filename_async(
        filename,
        prefix="",
        max_length=255
    ) -> str:
    """
    异步版本的sanitize_filename函数。
    """
    return await asyncio.to_thread(sanitize_filename, filename, prefix, max_length)

# 示例用法
if __name__ == "__main__":
    # 测试文件名转义和缩短
    test_filename = 'my/illegal:file?.name*with<long>path.txt'
    print(sanitize_filename(test_filename, prefix="doc"))  # 输出: doc_my_illegal_file_name_with_long_path.txt

    # 测试文件名过长的情况
    long_filename = 'a' * 300 + '.txt'
    print(sanitize_filename(long_filename))  # 输出: 类似 "9835fa6bf4e20a9b.txt"