import re
import types

__all__=['PromptVP']

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

    PromptVP supports two ways to register variables:
    1. Register variable values directly
    2. Register variable functions, the function parameter is kwargs, and the return value is the variable value

    PromptVP allows sensitive blocks (text wrapped in :::) to be used in the text. Once a variable in a sensitive block is not hit, the entire sensitive block will be deleted.

    Variables that are not hit will not be taken, and function variables will not be executed.
    '''
    def __init__(self):
        self.variables = {}

        # 预编译正则表达式
        self._sensitive_block_pattern = re.compile(r'(\s*:::.*?:::\s*)', re.DOTALL)
        self._sensitive_block_start_pattern = re.compile(r'\s*:::')
        self._strip_sensitive_block_pattern = re.compile(r'\s*:::(.*?):::\s*', re.DOTALL)
        self._var_pattern = re.compile(r'\{([a-zA-Z0-9_]+)\}')
        self._indent_pattern = re.compile(r'(\s*)')
        
        # 条件块正则表达式
        self._conditional_block_pattern = re.compile(
            r'\{([a-zA-Z0-9_]+)\}\s*->\s*```(.*?)```',
            re.DOTALL
        )

        # 命中计数器
        self.discovered_variable = 0
        self.hit_variable = 0

    def register_variable(self, name:str, value:str|types.FunctionType):
        '''注册变量'''
        # if not isinstance(name, str):
        #     raise ValueError(f'Variable name {name} must be a string')
        # if not isinstance(value, str) and not callable(value):
        #     raise ValueError(f'Variable {name} must be a string or a function')
        self.variables[name] = value

    def bulk_register_variable(self, **kwargs):
        '''批量注册变量'''
        for name, value in kwargs.items():
            self.register_variable(name, value)

    def process(self, text:str, **kwargs) -> str:
        '''处理文本中的变量'''
        # 先处理条件块
        text = self._process_conditional_blocks(text, **kwargs)
        
        # 分割敏感块和普通内容
        parts = self._sensitive_block_pattern.split(text)
        
        processed = []
        for part in parts:
            # 判断是否为敏感块（包含:::）
            if self._sensitive_block_start_pattern.match(part):
                # 提取内容和缩进
                indent_match = self._indent_pattern.match(part)
                indent = indent_match.group(1) if indent_match else ''
                
                # 去除包围的冒号和空白
                content = self._strip_sensitive_block_pattern.sub(r'\1', part)
                
                # 变量提取（允许变量名包含字母数字和下划线）
                variables = set(self._var_pattern.findall(content))
                
                # 检查变量是否存在
                if all(var in self.variables for var in variables):
                    # 替换变量并保留原缩进
                    replaced = self._replace_vars(content, check_exists=False, **kwargs)
                    processed.append(f"{indent}{replaced}")
                else:
                    # 完全删除整个块（包括缩进和换行）
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
                    return content_block
            
            # 条件不满足，返回空字符串
            return ''
        
        return self._conditional_block_pattern.sub(replacer, text)
    
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
        '''替换变量'''
        def replacer(match):
            self.discovered_variable += 1
            var_name = match.group(1)
            if check_exists:
                if var_name in self.variables:
                    self.hit_variable += 1
                    if isinstance(self.variables[var_name], types.FunctionType):
                        return str(self.variables[var_name](**kwargs))
                    else:
                        return str(self.variables[var_name])
                else:
                    return ''
            else:
                if isinstance(self.variables[var_name], types.FunctionType):
                    return str(self.variables[var_name](**kwargs))
                else:
                    return str(self.variables[var_name])

        return self._var_pattern.sub(replacer, text)
    
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