# API Documentation

本文档描述了 AI PowerShell Assistant Web UI 与后端服务之间的 API 接口。

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **Authentication**: 暂不需要（可选功能）

## 通用响应格式

### 成功响应

```json
{
  "success": true,
  "data": {
    // Response data
  }
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "message": "Error message",
    "code": 400
  }
}
```

## API 端点

### 1. 命令 API

#### 1.1 翻译命令

将自然语言翻译为 PowerShell 命令。

**Endpoint**: `POST /api/command/translate`

**Request Body**:
```json
{
  "input": "显示CPU使用率最高的5个进程",
  "context": {
    "sessionId": "uuid-string",
    "history": []
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5",
    "confidence": 0.95,
    "explanation": "获取所有进程并按CPU使用率降序排序，选择前5个",
    "security": {
      "level": "safe",
      "warnings": [],
      "requiresConfirmation": false,
      "requiresElevation": false
    }
  }
}
```

**Security Levels**:
- `safe`: 安全命令
- `low`: 低风险
- `medium`: 中等风险
- `high`: 高风险
- `critical`: 危险命令

#### 1.2 执行命令

执行 PowerShell 命令。

**Endpoint**: `POST /api/command/execute`

**Request Body**:
```json
{
  "command": "Get-Process | Select-Object -First 5",
  "sessionId": "uuid-string",
  "timeout": 30
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "output": "Process output...",
    "error": null,
    "executionTime": 0.234,
    "returnCode": 0
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "message": "Command execution failed",
    "code": 500
  }
}
```

### 2. 历史记录 API

#### 2.1 获取历史记录列表

**Endpoint**: `GET /api/history`

**Query Parameters**:
- `page` (optional): 页码，默认 1
- `limit` (optional): 每页数量，默认 20
- `search` (optional): 搜索关键词

**Example**: `GET /api/history?page=1&limit=20&search=process`

**Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid-1",
        "userInput": "显示所有进程",
        "command": "Get-Process",
        "success": true,
        "output": "...",
        "error": null,
        "executionTime": 0.123,
        "timestamp": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

#### 2.2 获取单条历史记录

**Endpoint**: `GET /api/history/:id`

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-1",
    "userInput": "显示所有进程",
    "command": "Get-Process",
    "success": true,
    "output": "...",
    "error": null,
    "executionTime": 0.123,
    "timestamp": "2024-01-15T10:30:00Z",
    "security": {
      "level": "safe",
      "warnings": []
    }
  }
}
```

#### 2.3 删除历史记录

**Endpoint**: `DELETE /api/history/:id`

**Response**:
```json
{
  "success": true,
  "data": {
    "message": "History item deleted successfully"
  }
}
```

### 3. 模板 API

#### 3.1 获取模板列表

**Endpoint**: `GET /api/templates`

**Query Parameters**:
- `category` (optional): 模板分类
- `search` (optional): 搜索关键词

**Example**: `GET /api/templates?category=automation`

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "name": "备份脚本",
      "description": "备份指定目录到目标位置",
      "category": "automation",
      "scriptContent": "Copy-Item -Path {{sourcePath}} -Destination {{targetPath}} -Recurse",
      "parameters": [
        {
          "name": "sourcePath",
          "type": "string",
          "required": true,
          "default": null,
          "description": "源目录路径"
        },
        {
          "name": "targetPath",
          "type": "string",
          "required": true,
          "default": null,
          "description": "目标目录路径"
        }
      ],
      "keywords": ["backup", "copy", "备份"],
      "createdAt": "2024-01-15T10:00:00Z",
      "updatedAt": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### 3.2 获取单个模板

**Endpoint**: `GET /api/templates/:id`

**Response**: 同上单个模板对象

#### 3.3 创建模板

**Endpoint**: `POST /api/templates`

**Request Body**:
```json
{
  "name": "备份脚本",
  "description": "备份指定目录",
  "category": "automation",
  "scriptContent": "Copy-Item -Path {{sourcePath}} -Destination {{targetPath}} -Recurse",
  "parameters": [
    {
      "name": "sourcePath",
      "type": "string",
      "required": true,
      "description": "源目录路径"
    }
  ],
  "keywords": ["backup", "copy"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-1",
    "name": "备份脚本",
    // ... other fields
  }
}
```

#### 3.4 更新模板

**Endpoint**: `PUT /api/templates/:id`

**Request Body**: 同创建模板

**Response**: 同创建模板响应

#### 3.5 删除模板

**Endpoint**: `DELETE /api/templates/:id`

**Response**:
```json
{
  "success": true,
  "data": {
    "message": "Template deleted successfully"
  }
}
```

#### 3.6 生成脚本

使用模板生成脚本。

**Endpoint**: `POST /api/templates/:id/generate`

**Request Body**:
```json
{
  "parameters": {
    "sourcePath": "C:\\Data",
    "targetPath": "D:\\Backup"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "script": "Copy-Item -Path C:\\Data -Destination D:\\Backup -Recurse"
  }
}
```

### 4. 配置 API

#### 4.1 获取配置

**Endpoint**: `GET /api/config`

**Response**:
```json
{
  "success": true,
  "data": {
    "ai": {
      "provider": "ollama",
      "modelName": "llama2",
      "temperature": 0.7,
      "maxTokens": 2000
    },
    "security": {
      "whitelistMode": false,
      "requireConfirmation": true,
      "dangerousPatterns": ["Remove-Item", "Format-Volume"]
    },
    "execution": {
      "timeout": 30,
      "shellType": "powershell",
      "encoding": "utf-8"
    },
    "general": {
      "language": "zh-CN",
      "theme": "dark",
      "logLevel": "info"
    }
  }
}
```

#### 4.2 更新配置

**Endpoint**: `PUT /api/config`

**Request Body**: 同获取配置响应的 data 字段

**Response**:
```json
{
  "success": true,
  "data": {
    "message": "Configuration updated successfully"
  }
}
```

### 5. 日志 API

#### 5.1 获取日志列表

**Endpoint**: `GET /api/logs`

**Query Parameters**:
- `level` (optional): 日志级别 (INFO, WARNING, ERROR)
- `limit` (optional): 返回数量，默认 100
- `since` (optional): 起始时间戳

**Example**: `GET /api/logs?level=ERROR&limit=50`

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "level": "INFO",
      "message": "Command executed successfully",
      "context": {
        "command": "Get-Process"
      }
    }
  ]
}
```

#### 5.2 实时日志流 (WebSocket)

**Endpoint**: `ws://localhost:5000/ws/logs`

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:5000/ws/logs')

ws.onopen = () => {
  console.log('Connected to log stream')
}

ws.onmessage = (event) => {
  const log = JSON.parse(event.data)
  console.log(log)
}

ws.onerror = (error) => {
  console.error('WebSocket error:', error)
}

ws.onclose = () => {
  console.log('Disconnected from log stream')
}
```

**Message Format**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Command executed successfully",
  "context": {}
}
```

### 6. 健康检查 API

#### 6.1 健康检查

**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 3600,
    "services": {
      "ai": "online",
      "security": "online",
      "execution": "online"
    }
  }
}
```

## 错误代码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

## 使用示例

### JavaScript/TypeScript

```typescript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 翻译命令
async function translateCommand(input: string) {
  try {
    const response = await apiClient.post('/command/translate', {
      input,
      context: {
        sessionId: 'session-123'
      }
    })
    return response.data.data
  } catch (error) {
    console.error('Translation failed:', error)
    throw error
  }
}

// 执行命令
async function executeCommand(command: string) {
  try {
    const response = await apiClient.post('/command/execute', {
      command,
      sessionId: 'session-123'
    })
    return response.data.data
  } catch (error) {
    console.error('Execution failed:', error)
    throw error
  }
}

// 获取历史记录
async function getHistory(page = 1, limit = 20) {
  try {
    const response = await apiClient.get('/history', {
      params: { page, limit }
    })
    return response.data.data
  } catch (error) {
    console.error('Failed to fetch history:', error)
    throw error
  }
}
```

### cURL

```bash
# 翻译命令
curl -X POST http://localhost:5000/api/command/translate \
  -H "Content-Type: application/json" \
  -d '{"input": "显示所有进程"}'

# 执行命令
curl -X POST http://localhost:5000/api/command/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "Get-Process", "sessionId": "test"}'

# 获取历史记录
curl http://localhost:5000/api/history?page=1&limit=20

# 获取配置
curl http://localhost:5000/api/config

# 健康检查
curl http://localhost:5000/api/health
```

## 速率限制

目前没有实施速率限制，但建议：
- 命令翻译：每分钟不超过 60 次
- 命令执行：每分钟不超过 30 次
- 其他 API：每分钟不超过 100 次

## 版本控制

API 版本通过 URL 路径管理：
- 当前版本：`/api/...`
- 未来版本：`/api/v2/...`

## 安全建议

1. 在生产环境中启用 HTTPS
2. 实施认证和授权机制
3. 验证所有输入参数
4. 限制命令执行权限
5. 记录所有敏感操作
6. 实施速率限制
7. 定期更新依赖包

## 相关文档

- [开发指南](./DEVELOPMENT.md)
- [项目说明](./README.md)
- [后端 API 实现](./backend/README.md)
