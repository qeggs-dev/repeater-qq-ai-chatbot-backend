from decimal import Decimal, localcontext

def format_deltatime(
    delta_time: float,
    offset: float = 0.0,
    format_str: str = "%Y-%m-%d_%H:%M:%S"
) -> str:
    '''
    将时间差转换为指定格式的字符串（默认每年365天，每月30天）
    
    当更高级别的格式化符号不存在时，最高级别的单位不会进位

    Args:
        delta_time (float): 时间差（秒），可以包含小数部分表示毫秒
        offset (float, optional): 偏移量（秒）。默认为0.0
        format_str (str, optional): 格式化字符串。支持以下占位符：
            %Y - 年
            %m - 月
            %d - 日
            %H - 小时
            %M - 分钟
            %S - 秒
            %f - 毫秒（3位）
            默认为"%Y-%m-%d_%H:%M:%S"

    Returns: 
        str: 格式化后的时间字符串
    '''
    DeltaTime = delta_time + offset

    # 定义时间常数（假设每年365天，每月30天）
    SECONDS_PER_YEAR = 365 * 86400    # 31536000
    SECONDS_PER_MONTH = 30 * 86400    # 2592000
    SECONDS_PER_DAY = 86400
    SECONDS_PER_HOUR = 3600
    SECONDS_PER_MINUTE = 60

    # 检查哪些时间单位需要计算
    has_year = "%Y" in format_str
    has_month = "%m" in format_str
    has_day = "%d" in format_str
    has_hour = "%H" in format_str
    has_minute = "%M" in format_str
    has_second = "%S" in format_str
    has_millisecond = "%f" in format_str

    def _calculate_unit(remaining: float, unit_seconds: float, higher_units_exist: bool) -> tuple[int, float]:
        '''
        计算时间单位的值和剩余时间
        
        Args:
            remaining: 剩余时间（秒）
            unit_seconds: 当前单位的秒数（如3600表示小时）
            higher_units_exist: 更高阶的单位是否存在
        
        Returns:
            (单位值, 新的剩余时间)
        '''
        if higher_units_exist:
            # 如果高阶单位存在，则正常计算当前单位
            unit_value = int(remaining // unit_seconds)
            remaining -= unit_value * unit_seconds
        else:
            # 如果高阶单位不存在，则当前单位包含所有更高阶的时间
            unit_value = int(remaining // unit_seconds)
            remaining = remaining % unit_seconds  # 只保留更小单位的时间
        return unit_value, remaining

    remaining = DeltaTime

    # 计算各时间单位
    years, remaining = _calculate_unit(remaining, SECONDS_PER_YEAR, False) if has_year else (0, remaining)
    months, remaining = _calculate_unit(remaining, SECONDS_PER_MONTH, has_year) if has_month else (0, remaining)
    days, remaining = _calculate_unit(remaining, SECONDS_PER_DAY, has_year or has_month) if has_day else (0, remaining)
    hours, remaining = _calculate_unit(remaining, SECONDS_PER_HOUR, has_year or has_month or has_day) if has_hour else (0, remaining)
    minutes, remaining = _calculate_unit(remaining, SECONDS_PER_MINUTE, has_year or has_month or has_day or has_hour) if has_minute else (0, remaining)
    
    # 秒和毫秒不需要考虑进位
    seconds = int(remaining) if has_second else 0
    milliseconds = int((remaining - seconds) * 1000) if has_millisecond else 0

    # 处理转义的%%
    temp_placeholder = "___TEMP_PERCENT___"
    formatted = format_str.replace("%%", temp_placeholder)

    # 替换占位符
    replacements = {
        "%Y": f"{years:04}",
        "%m": f"{months:02}",
        "%d": f"{days:02}",
        "%H": f"{hours:02}",
        "%M": f"{minutes:02}",
        "%S": f"{seconds:02}",
        "%f": f"{milliseconds:03}",
    }
    for placeholder, value in replacements.items():
        formatted = formatted.replace(placeholder, value)

    # 恢复转义的%%
    formatted = formatted.replace(temp_placeholder, "%")
    return formatted

def format_deltatime_ns(
    delta_ns: int,
    format_str: str = "%Y-%m-%d_%H:%M:%S.%n"
) -> str:
    """
    将纳秒级时间差转换为指定格式的字符串（默认每年365天，每月30天）
    当更高级别的格式化符号不存在时，最高级别的单位不会进位
    
    Args:
        delta_ns (int): 时间差（纳秒）
        format_str (str, optional): 格式化字符串。支持占位符：
            %Y - 年
            %m - 月
            %d - 日
            %H - 小时
            %M - 分钟
            %S - 秒
            %f - 毫秒（3位）
            %u - 微秒（3位）
            %n - 纳秒（3位）
            默认为"%Y-%m-%d_%H:%M:%S.%n"
            
    Returns: 
        str: 格式化后的时间字符串
    """
    # 定义时间常数（纳秒）
    NS_PER_YEAR = 365 * 24 * 60 * 60 * 10**9
    NS_PER_MONTH = 30 * 24 * 60 * 60 * 10**9
    NS_PER_DAY = 24 * 60 * 60 * 10**9
    NS_PER_HOUR = 60 * 60 * 10**9
    NS_PER_MINUTE = 60 * 10**9
    NS_PER_SECOND = 10**9
    NS_PER_MILLISECOND = 10**6
    NS_PER_MICROSECOND = 10**3

    # 检查需要计算的单位
    has_year = "%Y" in format_str
    has_month = "%m" in format_str
    has_day = "%d" in format_str
    has_hour = "%H" in format_str
    has_minute = "%M" in format_str
    has_second = "%S" in format_str
    has_millisecond = "%f" in format_str
    has_microsecond = "%u" in format_str
    has_nanosecond = "%n" in format_str

    # 时间单位计算函数
    def calculate_unit(remaining: int, unit_ns: int, higher_exists: bool) -> tuple[int, int]:
        if higher_exists:
            unit_value = remaining // unit_ns
            return unit_value, remaining - unit_value * unit_ns
        else:
            unit_value = remaining // unit_ns
            return unit_value, remaining % unit_ns

    remaining = delta_ns
    
    # 计算各时间单位
    years, remaining = calculate_unit(remaining, NS_PER_YEAR, False) if has_year else (0, remaining)
    months, remaining = calculate_unit(remaining, NS_PER_MONTH, has_year) if has_month else (0, remaining)
    days, remaining = calculate_unit(remaining, NS_PER_DAY, has_year or has_month) if has_day else (0, remaining)
    hours, remaining = calculate_unit(remaining, NS_PER_HOUR, has_year or has_month or has_day) if has_hour else (0, remaining)
    minutes, remaining = calculate_unit(remaining, NS_PER_MINUTE, has_year or has_month or has_day or has_hour) if has_minute else (0, remaining)
    
    # 秒及以下单位计算
    seconds = remaining // NS_PER_SECOND if has_second else 0
    subsecond_ns = remaining % NS_PER_SECOND
    
    # 毫秒、微秒、纳秒计算
    milliseconds = subsecond_ns // NS_PER_MILLISECOND if has_millisecond else 0
    microsecond_remainder = subsecond_ns % NS_PER_MILLISECOND
    
    microseconds = microsecond_remainder // NS_PER_MICROSECOND if has_microsecond else 0
    nanoseconds = microsecond_remainder % NS_PER_MICROSECOND if has_nanosecond else 0

    # 处理转义的%%
    temp_placeholder = "___TEMP_PERCENT___"
    formatted = format_str.replace("%%", temp_placeholder)

    # 替换占位符
    replacements = {
        "%Y": f"{years:04}",
        "%m": f"{months:02}",
        "%d": f"{days:02}",
        "%H": f"{hours:02}",
        "%M": f"{minutes:02}",
        "%S": f"{seconds:02}",
        "%f": f"{milliseconds:03}",
        "%u": f"{microseconds:03}",
        "%n": f"{nanoseconds:03}",
    }
    
    for placeholder, value in replacements.items():
        formatted = formatted.replace(placeholder, value)
    
    # 恢复转义的%%
    formatted = formatted.replace(temp_placeholder, "%")
    return formatted


if __name__ == "__main__":
    # 测试用例
    test_cases = [
        (1_000_000_000, "%S", "01", "1秒"),
        (1_500_000_000, "%S", "01", "1.5秒（只显示秒）"),
        (1_500_000_000, "%S.%n", "01.500000000", "1.5秒（秒+纳秒）"),
        (1_234_567, "%S.%f", "00.001", "1234567纳秒（毫秒）"),
        (1_234_567, "%S.%u", "00.001", "1234567纳秒（微秒）"),
        (1_234_567, "%S.%n", "00.1234567", "1234567纳秒（纳秒）"),
        (3_660_000_000_000, "%H:%M:%S", "01:01:00", "1小时1分钟"),
        (365 * 24 * 60 * 60 * 10**9, "%Y", "0001", "1年"),
        (30 * 24 * 60 * 60 * 10**9, "%m", "0001", "1个月"),
        (2 * 30 * 24 * 60 * 60 * 10**9 + 1_234_567, "%m %d %H:%M:%S.%n", "02 00 00:00:00.1234567", "2个月+1234567纳秒"),
    ]
    
    print("纳秒级时间格式化测试：")
    for delta_ns, fmt, expected, desc in test_cases:
        result = format_deltatime_ns(delta_ns, format_str=fmt)
        status = "✓" if result == expected else "✗"
        print(f"{status} {desc:30} {fmt:20} 输入: {delta_ns:<15} 输出: {result:<15} 预期: {expected}")

def format_deltatime_high_precision(
    delta_time: float,
    offset: float = 0.0,
    format_str: str = "%Y-%m-%d_%H:%M:%S"
) -> str:
    '''
    将时间差转换为指定格式的字符串（默认每年365天，每月30天）

    当更高级别的格式化符号不存在时，最高级别的单位不会进位

    此版本使用了高精度浮点数，适用于需要高精度时间差的情况

    Args:
        delta_time (float): 时间差（秒），可以包含小数部分表示毫秒
        offset (float, optional): 偏移量（秒）。默认为0.0
        format_str (str, optional): 格式化字符串。支持以下占位符：
            %Y - 年
            %m - 月
            %d - 日
            %H - 小时
            %M - 分钟
            %S - 秒
            %f - 毫秒（3位）
            默认为"%Y-%m-%d_%H:%M:%S"

    Returns: 
        str: 格式化后的时间字符串
    '''
    with localcontext() as ctx:
        ctx.prec = 20
        DeltaTime = Decimal(str(delta_time)) + Decimal(str(offset))

        SECONDS_PER_YEAR = Decimal(365 * 86400)
        SECONDS_PER_MONTH = Decimal(30 * 86400)
        SECONDS_PER_DAY = Decimal(86400)
        SECONDS_PER_HOUR = Decimal(3600)
        SECONDS_PER_MINUTE = Decimal(60)

        has_year = "%Y" in format_str
        has_month = "%m" in format_str
        has_day = "%d" in format_str
        has_hour = "%H" in format_str
        has_minute = "%M" in format_str
        has_second = "%S" in format_str
        has_millisecond = "%f" in format_str

        def _calculate_unit(remaining: Decimal, unit_seconds: Decimal, higher_units_exist: bool) -> tuple[int, Decimal]:
            if higher_units_exist:
                unit_value = int(remaining // unit_seconds)
                remaining -= unit_value * unit_seconds
            else:
                unit_value = int(remaining // unit_seconds)
                remaining = remaining % unit_seconds
            return unit_value, remaining

        remaining = DeltaTime
        years, remaining = _calculate_unit(remaining, SECONDS_PER_YEAR, False) if has_year else (0, remaining)
        months, remaining = _calculate_unit(remaining, SECONDS_PER_MONTH, has_year) if has_month else (0, remaining)
        days, remaining = _calculate_unit(remaining, SECONDS_PER_DAY, has_year or has_month) if has_day else (0, remaining)
        hours, remaining = _calculate_unit(remaining, SECONDS_PER_HOUR, has_year or has_month or has_day) if has_hour else (0, remaining)
        minutes, remaining = _calculate_unit(remaining, SECONDS_PER_MINUTE, has_year or has_month or has_day or has_hour) if has_minute else (0, remaining)
        
        seconds = int(remaining) if has_second else 0
        milliseconds = int((remaining - Decimal(seconds)) * Decimal(1000)) if has_millisecond else 0

        temp_placeholder = "___TEMP_PERCENT___"
        formatted = format_str.replace("%%", temp_placeholder)
        replacements = {
            "%Y": f"{years:04}",
            "%m": f"{months:02}",
            "%d": f"{days:02}",
            "%H": f"{hours:02}",
            "%M": f"{minutes:02}",
            "%S": f"{seconds:02}",
            "%f": f"{milliseconds:03}",
        }
        for placeholder, value in replacements.items():
            formatted = formatted.replace(placeholder, value)
        return formatted.replace(temp_placeholder, "%")


if __name__ == "__main__":
    # 测试用例
    test_cases = [
        (3661, "%H:%M:%S", "01:01:01", "小时:分钟:秒（正常进位）"),
        (3661, "%M:%S", "61:01", "分钟:秒（小时不进位）"),
        (90061, "%d %H:%M:%S", "01 01:01:01", "天 小时:分钟:秒（正常进位）"),
        (90061, "%H:%M:%S", "25:01:01", "小时:分钟:秒（天不进位）"),
        (90061, "%M:%S", "1501:01", "分钟:秒（小时和天不进位）"),
        (123.456, "%S.%f", "123.456", "秒.毫秒"),
        (123.456, "%M:%S.%f", "02:03.456", "分钟:秒.毫秒"),
        (123.456, "%H:%M:%S.%f", "00:02:03.456", "小时:分钟:秒.毫秒"),
        (86400 + 3600 + 60 + 1.234, "%d %H:%M:%S.%f", "01 01:01:01.234", "天 小时:分钟:秒.毫秒（完整测试）"),
    ]

    print("测试结果：")
    for delta, fmt, expected, desc in test_cases:
        result = format_deltatime_high_precision(delta, format_str=fmt)
        status = "✓" if result == expected else "✗"
        print(f"{status} {desc:40} {fmt:15} 输入: {delta:<10} 输出: {result:<15} 预期: {expected}")
    
    # 测试用例对比
    test_cases = [
        (3661, "%H:%M:%S", "01:01:01"),
        (90061.234, "%d %H:%M:%S.%f", "01 01:01:01.234"),
    ]

    print("测试结果对比：")
    for delta, fmt, expected in test_cases:
        r1 = format_deltatime(delta, format_str=fmt)
        r2 = format_deltatime_high_precision(delta, format_str=fmt)
        status = "✓" if r2 == expected else "✗"
        print(f"普通版: {r1:<18} 高精度版: {r2:<18} {status} {fmt:15} 输入: {delta}")