def limit_blank_lines(base_str:str, minimum_consecutive_blank_lines:int = 1) -> str:
    """
    将输入字符串中的连续空行压缩到不超过n个
    
    参数:
    base_str (str): 输入字符串
    minimum_consecutive_blank_lines (int): 允许的最大连续空行数量
    
    返回:
    str: 处理后的字符串
    """
    lines = base_str.splitlines(keepends=True)
    if not lines:
        return base_str
    
    result = []
    blank_count = 0
    
    for line in lines:
        # 检查是否为空行（只包含空白字符）
        if line.strip():
            # 非空行：重置计数器并保留该行
            blank_count = 0
            result.append(line)
        else:
            # 空行：如果当前连续空行数小于n则保留
            if blank_count < minimum_consecutive_blank_lines:
                result.append(line)
            blank_count += 1
    
    return ''.join(result)

if __name__ == "__main__":
    textstr = """
第一行


第四行
"""
    print(limit_blank_lines(textstr, 1))