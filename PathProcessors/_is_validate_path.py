from pathlib import Path

def validate_path(base_path: str | Path, new_path: str | Path) -> bool:
    """
    验证路径是否合法
    """
    # 转换为Path对象以便于操作
    base_path = Path(base_path)
    new_path = Path(new_path)

    # 获取基础路径的绝对路径
    requested_path = (base_path.resolve() / new_path).resolve()
    
    # 检查路径是否在base_path的子目录内
    return requested_path.is_relative_to(base_path.resolve())