import re
import types
import shlex
from .Exceptions import *

class PromptVP:
    '''
    ## PromptVP: Prompt Variable Processor

    ---

    #### Zh-CN:

    提示词变量处理器

    一个面向大模型System Prompt文本处理的变量处理器
    
    提示词变量格式：
    {variable_name}

    敏感块的使用：
    :::
    敏感块内容
    :::

    条件块的使用：
    {var}->```...```
    当变量var存在且其值不为空、不为False、执行后内容非空时，显示后面的内容块
    否则整个内容块将被去除

    变量可以被传参，格式：
    {variable_name arg1 arg2 arg3}

    PromptVP支持两种变量注册方式：
    1. 直接注册变量值
    2. 注册变量函数，函数参数为kwargs，返回变量值
    
    PromptVP 允许在文本中使用敏感块(用:::包裹的文本)，敏感块中的变量一旦没有命中，整个敏感块将被删除。

    没有命中的变量不会被取值，函数变量也不会被执行。

    ---

    #### En-US:

    a variable processor for large model system prompt text processing

    Prompt variable format:
    {variable_name}

    Sensitive block usage:
    :::
    sensitive block content
    :::

    Conditional block usage:
    {var}->```...```
    When the variable var exists and its value is not empty, not False, and not empty after execution, 
    the content block is displayed. Otherwise, the entire content block is removed.

    Variables can be passed in the format:
    {variable_name arg1 arg2 arg3}

    PromptVP supports two ways to register variables:
    1. Register variable values directly
    2. Register variable functions, the function parameter is kwargs, and the return value is the variable value

    PromptVP allows sensitive blocks (text wrapped in :::) to be used in the text. Once a variable in a sensitive block is not hit, the entire sensitive block will be deleted.

    Variables that are not hit will not be taken, and function variables will not be executed.
    '''

    # 预编译正则表达式
    _SENSITIVE_BLOCK_PATTERN = re.compile(r'(\s*:::.*?:::\s*)', re.DOTALL)
    _SENSITIVE_BLOCK_START_PATTERN = re.compile(r'\s*:::')
    _STRIP_SENSITIVE_BLOCK_PATTERN = re.compile(r'\s*:::(.*?):::\s*', re.DOTALL)
    # 变量正则，匹配变量前的反斜杠和变量块
    _VAR_PATTERN = re.compile(r'(\\*)\{([^{}]+)\}')
    _INDENT_PATTERN = re.compile(r'(\s*)')
    # 变量提取正则添加转义变量的忽略
    _VAR_EXTRACT_PATTERN = re.compile(r'(?<!\\)(?:\\\\)*\{([a-zA-Z0-9_]+)')
    # 条件块正则表达式保持不变
    _CONDITIONAL_BLOCK_PATTERN = re.compile(
        r'\{([a-zA-Z0-9_]+)\}\s*->\s*```(.*?)```',
        re.DOTALL
    )

    def __init__(self):
        self.variables = {}
        # 命中计数器
        self.discovered_variable = 0
        self.hit_variable = 0

    def register_variable(self, name: str, value: str | types.FunctionType):
        '''注册变量'''
        if ' ' in name:
            raise InvalidVariableName(f'Variable name cannot contain spaces, but got "{name}"')
        self.variables[name] = value

    def bulk_register_variable(self, **kwargs):
        '''批量注册变量'''
        for name, value in kwargs.items():
            self.register_variable(name, value)
    
    def process(self, text: str, **kwargs) -> str:
        '''处理文本中的变量'''

        # 先处理条件块
        text = self._process_conditional_blocks(text, **kwargs)

        # 分割敏感块和普通内容
        parts = self._SENSITIVE_BLOCK_PATTERN.split(text)

        processed = []
        for part in parts:
            if self._SENSITIVE_BLOCK_START_PATTERN.match(part):
                # 提取内容和缩进
                indent_match = self._INDENT_PATTERN.match(part)
                indent = indent_match.group(1) if indent_match else ''

                # 去除包围的冒号和空白
                content = self._STRIP_SENSITIVE_BLOCK_PATTERN.sub(r'\1', part)

                # 提取变量时忽略转义变量
                variables = set()
                for match in self._VAR_EXTRACT_PATTERN.finditer(content):
                    var_name = match.group(1)
                    variables.add(var_name)

                # 检查变量是否存在
                if all(var in self.variables for var in variables):
                    # 替换变量并保留原缩进
                    replaced = self._replace_vars(content, check_exists=False, **kwargs)
                    processed.append(f"{indent}{replaced}")
                else:
                    # 完全删除整个块
                    processed.append('')
            else:
                # 处理普通内容
                processed.append(self._replace_vars(part, check_exists=True, **kwargs))

        return ''.join(processed)

    
    def _process_conditional_blocks(self, text: str, **kwargs) -> str:
        '''处理条件块'''
        def replacer(match):
            var_name = match.group(1)
            content_block = match.group(2).strip()
            
            # 检查变量是否存在
            if var_name in self.variables:
                value = self.variables[var_name]
                
                # 如果是函数变量，执行函数获取值
                if isinstance(value, types.FunctionType):
                    value = value(**kwargs)
                
                # 检查值是否应该显示内容块
                if self._should_display(value):
                    return self._replace_vars(content_block, check_exists=False, **kwargs)
            
            # 条件不满足，返回空字符串
            return ''
        
        return self._CONDITIONAL_BLOCK_PATTERN.sub(replacer, text)
    
    def _should_display(self, value) -> bool:
        '''检查值是否应该显示内容块'''
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value.strip() != ''
        if isinstance(value, (list, tuple, dict, set)):
            return len(value) > 0
        return True
    
    def _parse_var_and_args(self, s: str) -> tuple:
        '''解析变量名和参数列表 - 使用shlex改进'''
        try:
            tokens = shlex.split(s)
            if not tokens:
                return None, []
            var_name = tokens[0].strip()
            args = [arg.strip() for arg in tokens[1:]]
            return var_name, args
        except Exception:
            # 解析失败时回退到简单方法
            tokens = [t.strip() for t in s.split(' ') if t.strip()]
            return (tokens[0], tokens[1:]) if tokens else (None, [])
    
    def discover_var(self) -> int:
        '''返回发现变量的数量'''
        return self.discovered_variable
    
    def hit_var(self) -> int:
        '''返回命中的变量数量'''
        return self.hit_variable
    
    def reset_counter(self):
        '''重置计数器'''
        self.discovered_variable = 0
        self.hit_variable = 0

    def size(self) -> int:
        '''返回变量数量'''
        return len(self.variables)

    def _replace_vars(self, text, check_exists=True, **kwargs) -> str:
        '''替换变量（带参数解析）'''
        def replacer(match):
            slashes = match.group(1)  # 捕获的反斜杠
            full_var = match.group(2)  # 变量内容
            
            # 计算反斜杠数量
            num_slashes = len(slashes)
            
            # 处理反斜杠转义
            if num_slashes > 0:
                # 保留 N//2 个反斜杠
                preserved_slashes = slashes[:num_slashes // 2]
                
                # 如果反斜杠数量为奇数，转义变量（不展开）
                if num_slashes % 2 == 1:
                    return preserved_slashes + '{' + full_var + '}'
            else:
                preserved_slashes = ''

            # 正常处理变量替换
            self.discovered_variable += 1
            var_name, args = self._parse_var_and_args(full_var)
            if not var_name:
                return preserved_slashes  # 无效变量名

            if check_exists and var_name not in self.variables:
                return preserved_slashes  # 变量不存在

            value = self.variables.get(var_name)
            if value is None:
                return preserved_slashes  # 变量不存在

            self.hit_variable += 1

            # 处理函数变量
            if callable(value):
                try:
                    return preserved_slashes + str(value(*args, **kwargs))
                except Exception as e:
                    return preserved_slashes + f"[PromptPV Error | {var_name}]: {e}"
            else:
                return preserved_slashes + str(value)

        # 使用更新后的正则表达式
        return self._VAR_PATTERN.sub(replacer, text)
    
if __name__ == '__main__':
    # === 测试代码 ===
    processor = PromptVP()
    processor.register_variable("model_name", "GPT-4")
    
    # 测试含下划线的变量名
    text = "欢迎使用{model_name}，未定义变量{undefined}"
    print(processor.process(text)) 
    # 输出："欢迎使用GPT-4，未定义变量"
    
    # 测试敏感块
    text = '''
    :::
    模型名称：{model_name}
    开发团队：{dev_team}
    :::
    '''
    answer = processor.process(text)
    print(f'{answer}')  # 输出空字符串（因为 dev_team 未注册）
    
    processor.register_variable("dev_team", "OpenAI")
    answer = processor.process(text)
    print(f"{answer}")
    '''
    输出：
    模型名称：GPT-4
    开发团队：OpenAI
    '''
    # 测试函数变量
    import time
    processor.register_variable("time", lambda **kw: time.strftime(kw.get("format"), kw.get("t")))
    text = "当前时间：{time}"
    answer = processor.process(text, format="%Y-%m-%d %H:%M:%S", t = time.localtime())
    print(f"{answer}")

    print(f'Hit: {processor.hit_var()}/{processor.discover_var()}') # 输出：Hit: 2/5
    processor.reset_counter()

    # 测试多个敏感块
    text ='''
    :::
    模型名称：{model_name}
    开发团队：{dev_team}
    :::
    :::
    CPU使用率：{CPU_Percent}
    未定义变量：{Undefined}
    :::
    '''
    answer = processor.process(text)
    print(f"{answer}")
    
    # 测试条件块
    processor = PromptVP()
    processor.register_variable("show_details", True)
    processor.register_variable("show_advanced", False)
    processor.register_variable("empty_value", "")
    processor.register_variable("zero_value", 0)
    
    text = '''
    基本配置：
    {show_details}->```
    详细设置：
    - 选项1: 值1
    - 选项2: 值2
    ```
    
    {show_advanced}->```
    高级设置：
    - 高级选项1
    - 高级选项2
    ```
    
    {empty_value}->```
    这个块不应该显示
    ```
    
    {zero_value}->```
    这个块也不应该显示
    ```
    
    {undefined}->```
    未定义变量块不应该显示
    ```
    '''
    
    print("\n条件块测试结果:")
    print(processor.process(text))
    
    # 测试条件块中的变量替换
    processor.register_variable("user_name", "Alice")
    text = '''
    {show_details}->```
    用户信息：
    - 姓名: {user_name}
    - 等级: {user_level}
    ```
    '''
    print("\n条件块中的变量替换:")
    # 由于user_level未定义，但在条件块中，整个块会被保留但user_level会被替换为空
    print(processor.process(text))
    
    # 测试条件块中的函数变量
    processor.register_variable("get_count", lambda: 5)
    text = '''
    {get_count}->```
    项目数量: {get_count}
    ```
    '''
    print("\n条件块中的函数变量:")
    print(processor.process(text))

    # 测试带参数的变量
    processor.register_variable("greet", lambda name: f"Hello, {name}!")
    processor.register_variable("add", lambda a, b: f"Result: {int(a)+int(b)}")
    processor.register_variable("info", lambda *args, **kwargs: "System Information")
    text = "1. {greet 'John Doe'} 2. {add 5 3} 3. {info} 4. {info extra param}"
    print(processor.process(text))
    # 输出: 
    # 1. Hello, John Doe! 2. Result: 8 3. System Information 4. System Information
    
    # 测试引号内的特殊字符
    text = "Data: {add '5 3', '2 4'}"
    print(processor.process(text))  # 输出: Data: Result: 9
    
    # 测试未注册变量
    text = "Test {undefined arg1 arg2}"
    print(processor.process(text))  # 输出: Test 
    
    # 测试解析错误（保留原文本）
    text = "Test {unclosed  'quote}"
    print(processor.process(text))  # 输出: Test 
    
    # 测试函数调用异常
    processor.register_variable("div", lambda a, b: int(a)/int(b))
    text = "Division: {div 10 0}"
    print(processor.process(text))  # 输出: Division: (并打印错误信息)
    
    # 测试敏感块中的带参变量
    processor.register_variable("model", "GPT-4")
    text = '''
    ::: 
    Model: {model}
    Calculation: {add 7 8}
    ::: 
    '''
    print(processor.process(text))
    # 输出:
    # Model: GPT-4
    # Calculation: Result: 15
    
    # 测试条件块中的带参变量
    processor.register_variable("show", True)
    text = '''
    {show}->```
    Generated: {add 3 4}
    ```
    '''
    print(processor.process(text))
    # 输出:
    # Generated: Result: 7

    # 测试转义功能
    processor = PromptVP()
    processor.register_variable("var", "value")

    # 测试偶数个反斜杠（正常替换）
    text = r"1. \\{var} 2. \\\\{var}"
    print(processor.process(text)) 
    # 输出: "1. \value 2. \\value"

    # 测试奇数个反斜杠（转义变量）
    text = r"1. \{var} 2. \\\{var}"
    print(processor.process(text)) 
    # 输出: "1. {var} 2. \\{var}"

    # 测试混合情况
    text = r"正常: {var}, 转义: \{var}, 双重转义: \\{var}"
    print(processor.process(text))
    # 输出: "正常: value, 转义: {var}, 双重转义: \value"