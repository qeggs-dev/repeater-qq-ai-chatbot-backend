from datetime import datetime, timezone, timedelta

def format_timestamp(timestamp, offset_timezone, format="%Y-%m-%d %H:%M:%S"):
    """
    格式化时间戳为指定时区的日期时间字符串
    
    参数:
        timestamp (float): 时间戳（秒数，可以是整数或浮点数）
        offset_timezone (float): 时区偏移量（小时数，如东八区为8，西五区为-5）
        format (str): 日期时间格式，默认为"%Y-%m-%d %H:%M:%S"
    
    返回:
        str: 格式化后的日期时间字符串 (YYYY-MM-DD HH:MM:SS)
    """
    # 创建固定偏移的时区
    tz_offset = timedelta(hours=offset_timezone)
    custom_tz = timezone(tz_offset)
    
    # 将时间戳转换为带时区信息的datetime对象
    utc_time = datetime.fromtimestamp(timestamp, timezone.utc)
    local_time = utc_time.astimezone(custom_tz)
    
    # 格式化为字符串
    return local_time.strftime(format)

if __name__ == "__main__":
    # 示例1: UTC时间戳0在UTC时区
    print(format_timestamp(0, 0))  # 输出: 1970-01-01 00:00:00
    
    # 示例2: UTC时间戳0在东八区
    print(format_timestamp(0, 8))  # 输出: 1970-01-01 08:00:00
    
    # 示例3: UTC时间戳0在纽约时区(西五区)
    print(format_timestamp(0, -5))  # 输出: 1969-12-31 19:00:00
    
    # 示例4: 小数时区(印度时区UTC+5.5)
    print(format_timestamp(0, 5.5))  # 输出: 1970-01-01 05:30:00
    
    # 示例5: 带毫秒的时间戳
    ts = 1691417235.678  # 2023-08-07 12:07:15.678 UTC
    print(format_timestamp(ts, 8))  # 输出: 2023-08-07 20:07:15