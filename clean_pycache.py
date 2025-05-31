import os
import re
import shutil

def find_and_remove_pycache(start_dir='.', exclude_pattern=None, ask_confirmation=True):
    """
    递归查找并删除__pycache__文件夹，可排除符合正则的路径
    
    :param start_dir: 开始搜索的目录，默认为当前目录
    :param exclude_pattern: 要排除路径的正则表达式（如 r'/venv/'）
    :param ask_confirmation: 是否询问确认删除
    """
    pycache_dirs = []
    exclude_re = re.compile(exclude_pattern) if exclude_pattern else None
    
    # 递归查找所有__pycache__文件夹
    for root, dirs, files in os.walk(start_dir):
        if '__pycache__' in dirs:
            full_path = os.path.join(root, '__pycache__')
            
            # 检查是否在排除路径中
            if exclude_re and exclude_re.search(full_path):
                print(f"[排除] {full_path} (匹配排除规则)")
                continue
                
            pycache_dirs.append(full_path)
    
    if not pycache_dirs:
        print("没有找到任何可删除的__pycache__文件夹。")
        return
    
    print("\n找到以下__pycache__文件夹:")
    for i, dir_path in enumerate(pycache_dirs, 1):
        print(f"{i}. {dir_path}")
    
    if ask_confirmation:
        print(f"\n共找到 {len(pycache_dirs)} 个__pycache__文件夹。")
        if exclude_pattern:
            print(f"排除规则: {exclude_pattern}")
        
        answer = input("是否要删除所有这些文件夹? [y/N]: ").strip().lower()
        
        if answer != 'y':
            print("取消删除操作。")
            return
    
    # 删除文件夹
    deleted_count = 0
    for dir_path in pycache_dirs:
        try:
            shutil.rmtree(dir_path)
            print(f"已删除: {dir_path}")
            deleted_count += 1
        except Exception as e:
            print(f"删除 {dir_path} 时出错: {e}")
    
    print(f"\n操作完成，共删除 {deleted_count} 个__pycache__文件夹")

if __name__ == '__main__':
    print("=== __pycache__ 清理工具（增强版） ===")
    print("提示：可以输入正则表达式来排除特定路径（如 venv 目录）")
    
    exclude_pat = input("输入要排除路径的正则表达式（直接回车跳过）: ").strip()
    if exclude_pat:
        try:
            re.compile(exclude_pat)  # 验证正则表达式
        except re.error as e:
            print(f"错误的正则表达式: {e}")
            exit(1)
    
    find_and_remove_pycache(exclude_pattern=exclude_pat if exclude_pat else None)