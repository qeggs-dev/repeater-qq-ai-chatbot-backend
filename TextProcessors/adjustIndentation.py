def adjust_indentation(text, indent_length=4, min_indent_level=0):
    """
    基于缩进级别调整文本缩进
    
    参数:
    text (str): 输入文本
    indent_length (int): 单个缩进级别的空格数
    min_indent (int): 期望的最小缩进级别数
    
    返回:
    str: 调整后的文本
    
    异常:
    ValueError: 如果min_indent为负数或indent_length<=0
    """
    if min_indent_level < 0:
        raise ValueError("min_indent不能为负数")
    if indent_length <= 0:
        raise ValueError("indent_length必须大于0")
    
    lines = text.splitlines(keepends=True)
    if not lines:
        return text
    
    indent_levels = []  # 存储每行的缩进级别
    has_content = False  # 是否有非空行
    
    # 第一遍：分析缩进级别
    for line in lines:
        stripped = line.lstrip()
        is_empty = not stripped or stripped in ('\n', '\r\n')
        
        if is_empty:
            indent_levels.append(None)  # 空行标记
            continue
        
        has_content = True
        leading_spaces = len(line) - len(stripped)
        level = leading_spaces // indent_length
        indent_levels.append(level)
    
    # 如果没有有效内容，返回原文本
    if not has_content:
        return text
    
    # 找出最小缩进级别（忽略空行）
    min_level = min(lvl for lvl in indent_levels if lvl is not None)
    
    # 计算缩进偏移
    offset = min_indent_level - min_level
    
    # 第二遍：应用缩进调整
    result = []
    for i, line in enumerate(lines):
        level = indent_levels[i]
        
        if level is None:  # 空行
            result.append(line)
            continue
        
        # 计算新缩进级别
        new_level = level + offset
        if new_level < 0:
            new_level = 0  # 确保不小于0
            
        # 重建行内容
        stripped = line.lstrip()
        new_indent = ' ' * (new_level * indent_length)
        result.append(f"{new_indent}{stripped}")
    
    return ''.join(result)

if __name__ == "__main__":
    text = """
    Line 1
        Line 2
            Line 3

            Line 5
    """

    # 将最小缩进级别设为2（2*4=8空格）
    adjusted = adjust_indentation(text, indent_length=4, min_indent_level=2)
    print(adjusted)