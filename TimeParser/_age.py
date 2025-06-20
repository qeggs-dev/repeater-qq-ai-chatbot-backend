from datetime import datetime, timedelta

def calculate_age(birth_year:int, birth_month:int, birth_day:int, current_timestamp:int|float=None, offset_timezone=0):
    """
    计算一个人的年龄（整型）
    
    参数:
    birth_year -- 出生年份
    birth_month -- 出生月份
    birth_day -- 出生日
    current_timestamp -- 当前时间的UNIX秒级时间戳（可选，默认为当前系统时间）
    offset_timezone -- 时区偏移量（小时，可选，默认为0）
    
    返回:
    整型的年龄
    """
    today = datetime.now() if current_timestamp is None else datetime.fromtimestamp(current_timestamp)
    age = today.year - birth_year
    
    # 如果今年还没过生日，年龄减1
    if (today.month, today.day) < (birth_month, birth_day):
        age -= 1
    return age