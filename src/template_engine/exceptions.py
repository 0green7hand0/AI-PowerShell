"""
模板引擎异常类定义
"""


class TemplateError(Exception):
    """
    模板相关错误的基类
    
    所有模板引擎相关的异常都应该继承此类。
    这允许调用者捕获所有模板相关的错误。
    
    Attributes:
        message: 错误消息
        details: 额外的错误详情（可选）
    """
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class TemplateValidationError(TemplateError):
    """
    模板验证错误
    
    当模板内容、参数配置或占位符验证失败时抛出此异常。
    
    常见场景:
    - PowerShell 语法错误
    - 参数类型与默认值不匹配
    - 占位符与参数定义不一致
    - 必需参数缺失
    
    Attributes:
        message: 验证错误的描述
        details: 包含验证失败的具体信息，如:
            - field: 验证失败的字段名
            - expected: 期望的值或格式
            - actual: 实际的值或格式
            - line_number: 错误所在行号（如果适用）
    """
    pass


class TemplateNotFoundError(TemplateError):
    """
    模板不存在错误
    
    当尝试访问、编辑或删除不存在的模板时抛出此异常。
    
    常见场景:
    - 使用无效的模板 ID 查询模板
    - 模板文件已被外部删除
    - 配置文件中引用的模板文件不存在
    
    Attributes:
        message: 错误描述
        details: 包含模板标识信息，如:
            - template_id: 请求的模板 ID
            - template_name: 请求的模板名称
            - search_path: 搜索的路径
    """
    pass


class TemplateConflictError(TemplateError):
    """
    模板冲突错误
    
    当模板操作导致冲突时抛出此异常。
    
    常见场景:
    - 创建模板时名称已存在
    - 导入模板时与现有模板冲突
    - 并发修改同一模板
    - 分类名称冲突
    
    Attributes:
        message: 冲突描述
        details: 包含冲突的详细信息，如:
            - conflict_type: 冲突类型（name, file, category）
            - existing_template: 现有模板的信息
            - new_template: 新模板的信息
            - resolution_options: 可用的解决方案列表
    """
    pass


class TemplateSyntaxError(TemplateError):
    """
    模板语法错误
    
    当模板脚本包含语法错误时抛出此异常。
    这通常是 PowerShell 语法验证失败的结果。
    
    常见场景:
    - PowerShell 脚本语法错误
    - 占位符格式错误
    - 参数块格式错误
    - 无效的命令或函数调用
    
    Attributes:
        message: 语法错误描述
        details: 包含语法错误的详细信息，如:
            - line_number: 错误所在行号
            - column_number: 错误所在列号
            - error_code: PowerShell 错误代码
            - suggestion: 修复建议
            - context: 错误上下文（前后几行代码）
    """
    pass


class TemplateIOError(TemplateError):
    """
    模板文件 I/O 错误
    
    当模板文件读写操作失败时抛出此异常。
    
    常见场景:
    - 文件权限不足
    - 磁盘空间不足
    - 文件被其他进程锁定
    - 路径不存在
    
    Attributes:
        message: I/O 错误描述
        details: 包含文件操作的详细信息，如:
            - file_path: 操作的文件路径
            - operation: 操作类型（read, write, delete）
            - os_error: 操作系统错误信息
    """
    pass


class TemplateConfigError(TemplateError):
    """
    模板配置错误
    
    当模板配置文件操作失败时抛出此异常。
    
    常见场景:
    - YAML 格式错误
    - 配置文件损坏
    - 必需配置项缺失
    - 配置值类型错误
    
    Attributes:
        message: 配置错误描述
        details: 包含配置错误的详细信息，如:
            - config_file: 配置文件路径
            - config_key: 错误的配置键
            - expected_type: 期望的配置类型
            - actual_value: 实际的配置值
    """
    pass
