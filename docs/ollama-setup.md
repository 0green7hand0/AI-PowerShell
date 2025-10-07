# Ollama 本地模型配置指南

本指南说明如何配置和使用 Ollama 本地 AI 模型。

## 📋 前置要求

- Ollama 已安装并运行
- 已下载 qwen3:30b 模型（或其他支持的模型）
- Python 3.8+

## 🔧 配置步骤

### 1. 安装 Ollama

访问 [Ollama 官网](https://ollama.ai) 下载并安装。

### 2. 下载模型

```bash
# 下载千问3 30B模型
ollama pull qwen3:30b

# 验证模型已下载
ollama list
```

### 3. 启动 Ollama 服务

```bash
# 启动服务（默认端口 11434）
ollama serve
```

### 4. 配置项目

编辑 `config/default.yaml`:

```yaml
ai:
  provider: ollama              # 使用 Ollama
  model_name: qwen3:30b         # 模型名称
  ollama_url: http://localhost:11434  # 服务地址
  use_ai_provider: true         # 启用 AI
  temperature: 0.7              # 创造性参数
  max_tokens: 256               # 最大生成长度
```

## 🎯 使用方法

### 测试连接

```bash
# 测试 Ollama 连接
python -c "import ollama; print(ollama.list())"
```

### 使用助手

```bash
# 启动交互模式
python src/main.py --interactive

# 输入命令
> 显示CPU使用率最高的5个进程
```

## 🔍 工作原理

项目使用三层翻译策略：

1. **规则匹配**（最快）
   - 正则表达式匹配常见命令
   - 响应时间 < 0.1秒

2. **AI 模型**（智能）
   - 规则匹配失败时调用 Ollama
   - 响应时间 1-5秒

3. **回退策略**（保底）
   - AI 不可用时的关键词匹配
   - 保证基本可用

## ⚙️ 性能优化

### CPU 优化

```yaml
ai:
  threads: 8              # CPU 线程数
  batch_size: 4           # 批处理大小
```

### GPU 优化

```yaml
ai:
  gpu_layers: 32          # GPU 层数
  context_length: 2048    # 上下文长度
```

### 内存优化

```yaml
ai:
  temperature: 0.7        # 降低可减少内存
  max_tokens: 256         # 限制生成长度
```

## 🐛 故障排除

### 问题1：Ollama 服务未运行

**症状**：连接错误

**解决方案**：
```bash
# 启动服务
ollama serve

# 检查状态
curl http://localhost:11434/api/tags
```

### 问题2：模型未找到

**症状**：模型不存在错误

**解决方案**：
```bash
# 列出已安装模型
ollama list

# 下载模型
ollama pull qwen3:30b
```

### 问题3：响应慢

**症状**：AI 响应时间过长

**解决方案**：
1. 使用更小的模型（如 qwen3:7b）
2. 增加 GPU 层数
3. 减少 max_tokens

## 📊 性能指标

| 操作 | 响应时间 | 说明 |
|------|---------|------|
| 规则匹配 | < 0.1秒 | 最快 |
| AI 生成 | 1-5秒 | 取决于硬件 |
| 命令执行 | 0.1-30秒 | 取决于命令 |

## 🔒 隐私保护

✅ 所有 AI 处理在本地完成  
✅ 不向外部服务发送数据  
✅ 完全离线可用  

## 📚 相关文档

- [快速开始](../快速开始.md)
- [配置参考](configuration.md)
- [开发者指南](developer-guide.md)

## 💡 最佳实践

1. 使用合适大小的模型
2. 根据硬件调整参数
3. 启用缓存提高性能
4. 定期更新模型

## 🎓 进阶配置

### 使用多个模型

```yaml
ai:
  models:
    - name: qwen3:30b
      use_for: complex
    - name: qwen3:7b
      use_for: simple
```

### 自定义提示词

```yaml
ai:
  system_prompt: |
    你是一个 PowerShell 专家...
```

## 📞 获取帮助

- 查看 [Ollama 文档](https://ollama.ai/docs)
- 提交 [GitHub Issue](https://github.com/0green7hand0/AI-PowerShell/issues)
- 参与 [讨论](https://github.com/0green7hand0/AI-PowerShell/discussions)
