# 常见问题解答 (FAQ)

## 目录

- [入门问题](#入门问题)
- [功能使用](#功能使用)
- [安全相关](#安全相关)
- [性能优化](#性能优化)
- [故障排除](#故障排除)
- [高级配置](#高级配置)

---

## 入门问题

### 如何安装和启动 Web UI？

**开发环境：**

```bash
# 前端
cd web-ui
npm install
npm run dev

# 后端
cd web-ui/backend
pip install -r requirements.txt
python app.py
```

**生产环境：**

```bash
# 使用 Docker
docker-compose up -d

# 或使用构建脚本
./build.sh
./start-production.sh
```

详细说明请参考 [QUICK_START.md](./QUICK_START.md)

### 首次访问需要做什么配置？

1. 访问设置页面（⚙️ 图标）
2. 配置 AI 设置：
   - 选择 Provider（OpenAI/Azure/Ollama）
   - 设置 API Key（如需要）
   - 选择模型名称
3. 配置安全设置（推荐保持默认）
4. 点击"保存"

### 支持哪些操作系统？

Web UI 是跨平台的，支持：
- Windows 10/11
- macOS 10.15+
- Linux（Ubuntu、CentOS、Debian 等）

后端需要 PowerShell 支持（Windows 自带，Linux/macOS 需安装 PowerShell Core）

### 需要什么权限？

- **普通命令**：无需特殊权限
- **系统管理命令**：需要管理员权限
- **文件操作**：需要相应目录的读写权限

建议以普通用户身份运行，需要时再提升权限。

---

## 功能使用

### Chat 功能

#### Q: AI 翻译的命令不准确怎么办？

**A:** 尝试以下方法：

1. **更详细的描述**
   ```
   ❌ "显示进程"
   ✅ "显示 CPU 使用率最高的 5 个进程，包含进程名、PID 和 CPU 百分比"
   ```

2. **提供上下文**
   ```
   "在 C:\Projects 目录下，查找所有 .log 文件，按修改时间排序"
   ```

3. **调整 Temperature**
   - 降低 Temperature（0.3-0.5）：更保守、更准确
   - 提高 Temperature（0.7-0.9）：更有创造性

4. **使用编辑功能**
   - 点击"编辑"按钮修改命令
   - 保存修改后的命令供以后参考

#### Q: 如何输入多行命令？

**A:** 使用 `Shift+Enter` 换行，`Enter` 发送。

```
Get-Process |
  Where-Object {$_.CPU -gt 10} |
  Sort-Object CPU -Descending |
  Select-Object -First 5
```

#### Q: 置信度是什么意思？

**A:** 置信度表示 AI 对翻译结果的信心程度：

- **90-100%**：非常确定，可以直接执行
- **70-89%**：比较确定，建议检查后执行
- **50-69%**：不太确定，需要仔细检查
- **<50%**：不确定，建议重新描述或手动编写

#### Q: 如何复制命令？

**A:** 点击命令卡片上的"复制"按钮，或手动选择文本复制。

### 历史记录

#### Q: 历史记录保存在哪里？

**A:** 保存在后端的存储引擎中，默认位置：
- 开发环境：`test_data/sessions/`
- 生产环境：配置文件中指定的路径

#### Q: 如何导出历史记录？

**A:** 当前版本暂不支持直接导出。可以通过以下方式：

1. 查看历史详情，手动复制
2. 访问后端存储文件（JSON 格式）
3. 使用 API 获取历史数据

计划在未来版本中添加导出功能。

#### Q: 可以批量删除历史记录吗？

**A:** 可以。在历史记录页面：
1. 使用过滤器筛选要删除的记录
2. 选择多条记录
3. 点击"批量删除"按钮

或者直接清空所有历史：设置 → 高级 → 清空历史记录

#### Q: 历史记录会占用多少空间？

**A:** 每条记录约 1-5KB，1000 条记录约 1-5MB。建议定期清理不需要的记录。

### 模板管理

#### Q: 如何创建参数化模板？

**A:** 使用 `{{参数名}}` 语法：

```powershell
# 备份脚本模板
$source = "{{sourcePath}}"
$target = "{{targetPath}}"
$date = Get-Date -Format "yyyyMMdd"

Copy-Item -Path $source -Destination "$target\backup_$date" -Recurse
Write-Host "备份完成：$source -> $target\backup_$date"
```

然后在模板编辑器中定义参数：
- 参数名：sourcePath
- 类型：string
- 必填：是
- 描述：源目录路径

#### Q: 模板支持哪些参数类型？

**A:** 支持以下类型：

1. **string**：文本输入
2. **number**：数字输入
3. **boolean**：是/否选择
4. **select**：下拉选择（需定义选项）

示例：
```json
{
  "name": "logLevel",
  "type": "select",
  "options": ["INFO", "WARNING", "ERROR"],
  "default": "INFO"
}
```

#### Q: 可以导入/导出模板吗？

**A:** 可以。

**导出模板：**
1. 在模板详情页点击"导出"
2. 保存为 JSON 文件

**导入模板：**
1. 点击"导入"按钮
2. 选择 JSON 文件
3. 确认导入

#### Q: 模板可以嵌套吗？

**A:** 当前版本不支持模板嵌套。可以通过以下方式实现类似功能：
1. 创建多个独立模板
2. 在脚本中调用其他脚本
3. 使用函数库

### 日志和监控

#### Q: 实时日志不更新怎么办？

**A:** 检查以下几点：

1. **WebSocket 连接状态**
   - 查看系统状态指示器
   - 如果显示"离线"，点击"重新连接"

2. **网络连接**
   - 检查网络是否正常
   - 检查防火墙设置

3. **后端服务**
   - 确认后端服务正在运行
   - 查看后端日志是否有错误

4. **浏览器兼容性**
   - 尝试刷新页面
   - 尝试其他浏览器

#### Q: 如何查看历史日志？

**A:** 日志页面默认显示最近的日志。要查看更早的日志：
1. 向上滚动加载更多
2. 使用日期过滤器
3. 或直接查看后端日志文件

#### Q: 日志级别有什么区别？

**A:** 

- **DEBUG**：详细的调试信息（开发用）
- **INFO**：一般信息（正常操作）
- **WARNING**：警告信息（需要注意）
- **ERROR**：错误信息（操作失败）

建议生产环境设置为 INFO 或 WARNING。

### 设置和配置

#### Q: 修改配置后需要重启吗？

**A:** 大部分配置会立即生效，但以下配置需要刷新页面或重启服务：

**需要刷新页面：**
- 主题设置
- 语言设置

**需要重启后端：**
- AI Provider 更改
- 安全引擎配置
- 执行引擎配置

#### Q: 配置文件在哪里？

**A:** 

- **前端配置**：`.env` 文件
- **后端配置**：`backend/config.py` 和 `config/default.yaml`
- **用户配置**：通过 Web UI 设置页面修改

#### Q: 如何重置为默认配置？

**A:** 

1. 在设置页面点击"重置为默认"
2. 或删除配置文件，重启服务
3. 或通过 API：`DELETE /api/config`

---

## 安全相关

### Q: 什么命令会被标记为危险？

**A:** 以下类型的命令会被标记：

1. **删除操作**
   - `Remove-Item`
   - `Delete`
   - `rm -rf`

2. **系统修改**
   - 注册表修改
   - 系统服务操作
   - 防火墙规则修改

3. **网络操作**
   - 下载文件
   - 网络连接
   - 端口扫描

4. **权限提升**
   - `sudo`
   - `runas`
   - UAC 提升

### Q: 如何自定义安全规则？

**A:** 在设置 → 安全设置中：

1. **添加危险模式**
   ```
   Remove-Item.*-Recurse.*-Force
   Format-Volume
   Clear-Disk
   ```

2. **配置白名单**
   - 启用白名单模式
   - 添加允许的命令模式

3. **设置确认级别**
   - 所有命令都需要确认
   - 仅高风险命令需要确认
   - 不需要确认（不推荐）

### Q: 白名单模式如何工作？

**A:** 启用白名单模式后：

1. 只有白名单中的命令可以执行
2. 其他命令会被阻止
3. 适合生产环境或受限环境

示例白名单：
```
Get-*
Select-Object
Where-Object
Sort-Object
```

### Q: 如何处理需要管理员权限的命令？

**A:** 

1. **方法一：以管理员身份运行后端**
   ```bash
   # Windows
   以管理员身份运行 PowerShell
   python app.py
   ```

2. **方法二：使用 RunAs**
   ```powershell
   Start-Process powershell -Verb RunAs -ArgumentList "命令"
   ```

3. **方法三：配置 UAC**
   - 在安全设置中启用"自动提升权限"
   - 需要时会弹出 UAC 提示

---

## 性能优化

### Q: 界面加载很慢怎么办？

**A:** 

1. **清除缓存**
   ```
   Ctrl+Shift+Delete → 清除缓存和 Cookie
   ```

2. **检查网络**
   - 使用浏览器开发者工具（F12）
   - 查看 Network 标签
   - 找出慢的请求

3. **优化配置**
   - 减少历史记录加载数量
   - 禁用不需要的功能
   - 使用生产构建

4. **升级硬件**
   - 增加内存
   - 使用 SSD
   - 升级网络

### Q: 命令执行很慢怎么办？

**A:** 

1. **优化命令**
   ```powershell
   # 慢
   Get-ChildItem -Recurse | Where-Object {$_.Length -gt 1MB}
   
   # 快
   Get-ChildItem -Recurse -File | Where-Object Length -gt 1MB
   ```

2. **增加超时时间**
   - 设置 → 执行设置 → Timeout

3. **使用异步执行**
   - 对于长时间运行的命令
   - 使用后台作业

4. **分批处理**
   - 将大任务分成小任务
   - 使用模板批量处理

### Q: 如何减少内存占用？

**A:** 

1. **限制历史记录**
   - 定期清理历史
   - 设置自动清理策略

2. **关闭实时日志**
   - 不使用时关闭日志页面
   - 减少日志级别

3. **优化模板**
   - 删除不用的模板
   - 简化复杂模板

4. **使用生产模式**
   - 禁用调试功能
   - 启用压缩和缓存

---

## 故障排除

### Q: 无法连接到后端服务？

**A:** 

1. **检查服务状态**
   ```bash
   # 查看进程
   ps aux | grep python
   
   # 查看端口
   netstat -an | grep 5000
   ```

2. **检查配置**
   - 前端 `.env` 文件中的 `VITE_API_BASE_URL`
   - 后端监听地址和端口

3. **检查防火墙**
   ```bash
   # Windows
   netsh advfirewall firewall add rule name="Flask" dir=in action=allow protocol=TCP localport=5000
   
   # Linux
   sudo ufw allow 5000
   ```

4. **查看日志**
   - 后端日志：`logs/assistant.log`
   - 浏览器控制台（F12）

### Q: 命令执行失败？

**A:** 

1. **查看错误信息**
   - 在执行结果中查看详细错误
   - 在日志页面查看系统日志

2. **常见错误**
   
   **权限不足：**
   ```
   Access denied
   → 以管理员身份运行或修改权限
   ```
   
   **命令不存在：**
   ```
   Command not found
   → 检查 PowerShell 版本和模块
   ```
   
   **语法错误：**
   ```
   Syntax error
   → 检查命令语法，使用编辑功能修正
   ```

3. **手动测试**
   - 在 PowerShell 中直接运行命令
   - 确认命令本身是否正确

### Q: 配置保存失败？

**A:** 

1. **检查权限**
   - 确保有写入配置文件的权限
   - Windows：右键 → 属性 → 安全

2. **验证配置值**
   - 检查是否符合格式要求
   - 查看错误提示信息

3. **查看后端日志**
   ```bash
   tail -f logs/assistant.log
   ```

4. **手动编辑配置**
   - 直接编辑 `config/default.yaml`
   - 重启后端服务

### Q: 主题切换不生效？

**A:** 

1. **清除缓存**
   - Ctrl+Shift+Delete
   - 清除站点数据

2. **检查 localStorage**
   - F12 → Application → Local Storage
   - 查看 `theme` 键值

3. **强制刷新**
   - Ctrl+F5（Windows）
   - Cmd+Shift+R（Mac）

---

## 高级配置

### Q: 如何配置反向代理？

**A:** 使用 Nginx 示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Q: 如何配置 HTTPS？

**A:** 

1. **获取 SSL 证书**
   - Let's Encrypt（免费）
   - 商业 CA

2. **配置 Nginx**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       # ... 其他配置
   }
   ```

3. **更新前端配置**
   ```env
   VITE_API_BASE_URL=https://your-domain.com
   ```

### Q: 如何配置多用户？

**A:** 

1. **启用认证**
   - 在 `backend/config.py` 中设置 `AUTH_ENABLED = True`

2. **配置用户数据库**
   - 使用 SQLite/PostgreSQL/MySQL

3. **设置用户权限**
   - 管理员：所有权限
   - 普通用户：受限权限

4. **配置会话**
   - 设置会话超时时间
   - 配置 JWT 密钥

### Q: 如何集成其他 AI 模型？

**A:** 

1. **OpenAI 兼容 API**
   ```yaml
   ai:
     provider: openai
     api_base: https://your-api.com/v1
     api_key: your-key
     model: your-model
   ```

2. **自定义 Provider**
   - 在 `src/ai_engine/providers/` 添加新 provider
   - 实现 `BaseProvider` 接口
   - 在配置中注册

3. **本地模型（Ollama）**
   ```yaml
   ai:
     provider: ollama
     api_base: http://localhost:11434
     model: llama2
   ```

### Q: 如何备份和恢复数据？

**A:** 

**备份：**
```bash
# 备份配置
cp -r config config.backup

# 备份历史记录
cp -r test_data test_data.backup

# 备份模板
cp -r templates templates.backup
```

**恢复：**
```bash
# 恢复配置
cp -r config.backup/* config/

# 恢复历史记录
cp -r test_data.backup/* test_data/

# 恢复模板
cp -r templates.backup/* templates/
```

**自动备份脚本：**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup_$DATE.tar.gz config test_data templates
```

---

## 获取更多帮助

### 文档资源

- [用户指南](./USER_GUIDE.md)
- [快速开始](./QUICK_START.md)
- [开发者文档](./DEVELOPER_GUIDE.md)
- [API 文档](./API.md)
- [故障排除](./TROUBLESHOOTING.md)

### 社区支持

- GitHub Issues
- 讨论区
- Stack Overflow（标签：ai-powershell-assistant）

### 联系方式

- 邮件支持
- 技术论坛
- 在线聊天

---

**最后更新**: 2025-10-08  
**版本**: 1.0.0
