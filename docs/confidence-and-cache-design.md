# 置信度与 LRU 缓存设计文档

本文档详细说明 AI PowerShell 智能助手中置信度（Confidence）和 LRU 缓存的设计原理与实现细节。

---

## 目录

1. [置信度设计](#一置信度设计)
2. [LRU 缓存设计](#二lru-缓存设计)
3. [代码实现参考](#三代码实现参考)

---

## 一、置信度设计

### 1.1 定义

置信度是一个 **0.0 ~ 1.0** 的浮点数，表示系统对生成命令的"确定程度"：

```
0.0 ────────────────────────────────────────── 1.0
完全不确定                                    完全确定
```

### 1.2 设计依据

置信度的设计基于三个核心维度：

#### 维度一：匹配方式的确定性

| 匹配方式 | 置信度范围 | 设计依据 |
|---------|-----------|---------|
| 精确规则匹配 | 0.95 | 用户输入完全符合预设规则，无歧义 |
| 模糊规则匹配 | 0.85-0.90 | 匹配到规则但需要提取参数 |
| AI 模型生成 | 0.80 | AI 理解语义生成，存在一定不确定性 |
| 关键词模糊匹配 | 0.60 | 只匹配到关键词，意图不明确 |
| 无法识别 | 0.30 | 完全无法理解，返回帮助命令 |

#### 维度二：信息完整度

| 识别结果 | 置信度 | 说明 |
|---------|--------|------|
| 操作类型识别成功 | 0.9 | 如"重命名"、"删除"、"查看" |
| 目标对象识别成功 | 0.9 | 如"文件"、"文件夹"、"进程" |
| 无法识别操作 | 0.3 | 返回 'unknown' |
| 无法识别目标 | 0.5 | 默认返回 'files' |

总体置信度计算公式：
```python
confidence = (action_confidence + target_confidence) / 2
```

#### 维度三：模板匹配权重

模板匹配采用加权评分机制：

| 匹配项 | 权重 | 说明 |
|-------|------|------|
| 操作类型匹配 | 10 | 最重要，决定命令类型 |
| 目标对象匹配 | 5 | 次重要，确定操作对象 |
| 参数匹配 | 3 | 辅助，提供具体参数 |
| 关键词部分匹配 | 2 | 补充，增强匹配精度 |

最终分数计算：
```python
score = (操作匹配×10 + 目标匹配×5 + 参数匹配×3 + 关键词匹配×2) × intent.confidence
```

### 1.3 置信度计算流程

```
用户输入
    │
    ▼
┌─────────────────────────────────────┐
│  阶段1: 意图识别                      │
│  - 识别操作类型 (action_confidence)   │
│  - 识别目标对象 (target_confidence)   │
│  - 计算总体置信度 = (a + t) / 2       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  阶段2: 模板匹配                      │
│  - 操作类型匹配 (+10)                 │
│  - 目标对象匹配 (+5)                  │
│  - 参数匹配 (+3)                      │
│  - 关键词匹配 (+2)                    │
│  - 最终分数 = 加权和 × 意图置信度     │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  阶段3: 命令生成                      │
│  - 精确规则匹配 → 0.95               │
│  - AI 生成 → 0.80                    │
│  - 模糊匹配 → 0.60                   │
└─────────────────────────────────────┘
```

### 1.4 具体示例

#### 示例1：精确匹配（高置信度 0.95）

```
输入: "C盘有什么"
匹配规则: r'([a-zA-Z])盘有什么$'
生成命令: Get-ChildItem C:\
置信度: 0.95

分析:
- 输入完全符合规则模式
- 无歧义，无需猜测
- 命令确定性强
```

#### 示例2：AI 生成（中等置信度 0.80）

```
输入: "帮我把昨天修改的文档整理一下"
匹配规则: 无精确匹配
生成命令: Get-ChildItem | Where-Object {$_.LastWriteTime -gt (Get-Date).AddDays(-1)}
置信度: 0.80

分析:
- 语义复杂，需要 AI 理解
- "昨天"、"文档"、"整理"需要综合理解
- 存在一定不确定性
```

#### 示例3：模糊匹配（低置信度 0.60）

```
输入: "文件"
匹配关键词: "文件"
生成命令: Get-ChildItem
置信度: 0.60

分析:
- 只有单个关键词
- 意图不明确
- 可能是"查看文件"、"删除文件"等
```

### 1.5 置信度的实际应用

```python
# 根据置信度给出不同提示
if confidence >= 0.90:
    提示 = "高置信度，可直接执行"
elif confidence >= 0.70:
    提示 = "中等置信度，建议确认后执行"
else:
    提示 = "低置信度，请仔细检查命令"
```

---

## 二、LRU 缓存设计

### 2.1 设计目的

LRU（Least Recently Used，最近最少使用）缓存用于：
- 提高响应速度，避免重复计算
- 减少对 AI 模型的调用次数
- 优化系统资源使用

### 2.2 核心数据结构

```python
class TranslationCache:
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        # 缓存字典：key=用户输入, value=(建议, 时间戳)
        self._cache: Dict[str, tuple[Suggestion, datetime]] = {}
        self._max_size = max_size           # 最大缓存条目数
        self._ttl = timedelta(seconds=ttl_seconds)  # 过期时间
```

### 2.3 LRU 淘汰策略

当缓存达到最大容量时，删除最旧的条目：

```python
def set(self, text: str, suggestion: Suggestion):
    # 缓存已满时，删除最旧的条目
    if len(self._cache) >= self._max_size:
        # 找到时间戳最小的 key（最旧）
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
        del self._cache[oldest_key]  # 删除最旧条目
    
    self._cache[text] = (suggestion, datetime.now())
```

### 2.4 TTL 过期机制

缓存条目在指定时间后自动失效：

```python
def get(self, text: str) -> Optional[Suggestion]:
    if text not in self._cache:
        return None
    
    suggestion, timestamp = self._cache[text]
    
    # 检查是否过期
    if datetime.now() - timestamp > self._ttl:
        del self._cache[text]  # 过期则删除
        return None
    
    return suggestion
```

### 2.5 缓存工作流程

```
用户输入
    │
    ▼
┌─────────────────────────────────────┐
│  检查缓存                            │
│  - 缓存命中且未过期 → 返回缓存结果   │
│  - 缓存未命中或已过期 → 继续        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  AI 翻译处理                         │
│  - 规则匹配或 AI 生成                │
│  - 生成命令建议                      │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  存入缓存                            │
│  - 检查缓存容量                      │
│  - 必要时淘汰最旧条目                │
│  - 存储新结果                        │
└─────────────────────────────────────┘
    │
    ▼
  返回结果
```

### 2.6 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `max_size` | 100 | 最大缓存条目数 |
| `ttl_seconds` | 3600 | 缓存过期时间（秒） |

### 2.7 特殊处理：重新生成

当用户对结果不满意并请求重新生成时，会清除对应缓存：

```python
# 检查是否是重新生成请求
is_regeneration = context.feedback is not None and context.feedback.get('feedback') == 'incorrect'

if is_regeneration:
    # 清除该文本的缓存
    if text in self.cache._cache:
        del self.cache._cache[text]
```

---

## 三、代码实现参考

### 3.1 相关文件

| 文件路径 | 说明 |
|---------|------|
| `src/ai_engine/engine.py` | TranslationCache 类实现 |
| `src/ai_engine/translation.py` | 规则匹配与置信度设置 |
| `src/template_engine/template_matcher.py` | 模板匹配加权计算 |
| `src/template_engine/intent_recognizer.py` | 意图识别与置信度计算 |
| `src/interfaces/base.py` | Suggestion 数据模型定义 |

### 3.2 关键代码片段

#### Suggestion 数据模型

```python
@dataclass
class Suggestion:
    original_input: str           # 原始用户输入
    generated_command: str        # 生成的 PowerShell 命令
    confidence_score: float       # 置信度分数 (0.0-1.0)
    explanation: str              # 命令解释说明
    alternatives: List[str]       # 备选命令列表
    timestamp: datetime           # 生成时间
```

#### 规则定义示例

```python
self.rules = {
    r'([a-zA-Z])盘有什么$': (
        'Get-ChildItem {drive}:\\',
        '列出指定盘符的文件和文件夹',
        0.95  # 置信度
    ),
    r'(显示|查看).*(进程|任务)': (
        'Get-Process',
        '列出所有运行中的进程',
        0.95
    ),
}
```

---

## 四、总结

### 置信度

| 特性 | 说明 |
|------|------|
| 目的 | 量化系统对生成命令的确定程度 |
| 范围 | 0.0 ~ 1.0 |
| 依据 | 匹配确定性 + 信息完整度 + 模板权重 |
| 用途 | 提示用户确认、排序备选命令 |

### LRU 缓存

| 特性 | 说明 |
|------|------|
| 目的 | 提高响应速度，减少重复计算 |
| 淘汰策略 | 删除最旧条目（基于时间戳） |
| 过期机制 | TTL 自动失效 |
| 容量 | 默认 100 条，可配置 |
