# AI PowerShell 沙箱功能指南

## 📋 概述

沙箱功能已成功集成到Web端，实现了**智能沙箱策略**：只有高危命令才会在Docker容器中隔离执行，低风险命令正常执行以保证性能。

## 🎯 当前配置

### 配置文件 (`config/default.yaml`)

```yaml
security:
  sandbox_enabled: true                    # ✅ 沙箱已启用
  sandbox_for_high_risk_only: true        # ✅ 只对高危命令使用沙箱
  require_confirmation: true               # 需要用户确认
  whitelist_mode: strict                   # 严格白名单模式
```

## 🔒 智能沙箱策略

### 执行策略

| 风险等级 | 执行方式 | 说明 |
|---------|---------|------|
| **Safe** (安全) | 🟢 正常执行 | Get-*, Show-*, Test-* 等只读命令 |
| **Low** (低风险) | 🟢 正常执行 | 基本的文件操作，如 New-Item |
| **Medium** (中等) | 🟢 正常执行 | 修改系统状态但影响有限 |
| **High** (高危) | 🔒 **沙箱执行** | Remove-Item, Stop-Process 等 |
| **Critical** (严重) | 🔒 **沙箱执行** | Format-*, Stop-Computer 等 |

### 高危命令关键词

以下命令会自动在沙箱中执行：

- `Remove-Item` - 删除文件/目录
- `Delete` - 删除操作
- `Format-*` - 格式化操作
- `Clear-*` - 清除操作
- `Stop-Computer` - 关机
- `Restart-Computer` - 重启
- `Stop-Process` - 停止进程
- `Set-ExecutionPolicy` - 修改执行策略
- `Invoke-Expression` / `iex` - 执行表达式
- `rd`, `del`, `rmdir` - 删除命令

## 🐳 Docker 要求

### 前置条件

1. **Docker Desktop 已安装** ✅
   - 版本: Docker 28.0.4
   - 路径: `C:\Program Files\Docker\Docker\Docker Desktop.exe`

2. **Docker 服务运行中** ⏳
   - 启动命令: `Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"`
   - 检查命令: `docker ps`

3. **PowerShell 镜像**
   - 镜像: `mcr.microsoft.com/powershell:latest`
   - 首次使用时会自动拉取

### 启动 Docker Desktop

```powershell
# 方法1: 通过开始菜单启动 Docker Desktop

# 方法2: 命令行启动
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# 等待30-60秒让Docker完全启动

# 验证Docker是否运行
docker ps
```

## 🚀 使用方式

### 自动模式（推荐）

系统会自动判断命令风险等级，高危命令自动使用沙箱：

```bash
# 低风险命令 - 正常执行
用户输入: "在桌面新建文件夹"
生成命令: New-Item -ItemType Directory -Path "C:\Users\...\Desktop\NewFolder"
执行方式: 🟢 正常执行

# 高危命令 - 沙箱执行
用户输入: "删除桌面上的临时文件"
生成命令: Remove-Item "C:\Users\...\Desktop\temp*" -Recurse
执行方式: 🔒 沙箱执行
```

### 手动指定风险等级

前端可以在执行请求中指定风险等级：

```javascript
// 执行命令时传递风险等级
const response = await executeCommand({
  command: "Remove-Item temp.txt",
  riskLevel: "high"  // 强制使用沙箱
});

// 检查是否在沙箱中执行
if (response.data.sandbox) {
  console.log("命令在沙箱中安全执行");
}
```

## 🛡️ 沙箱安全特性

### 资源限制

- **内存限制**: 512MB
- **CPU限制**: 0.5核心
- **进程数限制**: 100个
- **超时时间**: 30秒（可配置）

### 隔离措施

- ✅ **网络隔离**: 默认禁用网络访问
- ✅ **只读文件系统**: 防止修改容器文件系统
- ✅ **临时目录**: 提供100MB临时空间
- ✅ **权限限制**: 禁止权限提升

### 安全选项

```python
{
    'security_opt': ['no-new-privileges:true'],
    'network_mode': 'none',
    'read_only': True,
    'tmpfs': {'/tmp': 'rw,noexec,nosuid,size=100m'}
}
```

## 📊 执行日志

### 后端日志示例

```
[沙箱执行] 命令: Remove-Item temp.txt
⚡ 开始执行命令: Remove-Item temp.txt
🔍 风险等级: high
🔒 使用沙箱执行高危命令...
✅ 命令执行成功 (耗时: 2.34秒)
🔒 命令在沙箱中执行
```

### 历史记录

执行历史会标记是否在沙箱中执行：

```json
{
  "id": "hist_1777539184158",
  "command": "Remove-Item temp.txt",
  "success": true,
  "sandbox": true,
  "execution_time": 2.34
}
```

## ⚙️ 配置选项

### 完整配置

```yaml
security:
  # 是否启用沙箱功能
  sandbox_enabled: true
  
  # 是否只对高危命令使用沙箱（推荐）
  # true: 只有high和critical级别的命令使用沙箱
  # false: 所有命令都使用沙箱
  sandbox_for_high_risk_only: true
  
  # 沙箱Docker配置
  docker_image: mcr.microsoft.com/powershell:latest
  memory_limit: 512m
  cpu_limit: 0.5
  timeout: 30
  network_disabled: true
  read_only: true
```

## 🔧 故障排除

### Docker 未运行

**问题**: `error during connect: ... dockerDesktopLinuxEngine`

**解决方案**:
1. 启动 Docker Desktop
2. 等待30-60秒
3. 运行 `docker ps` 验证

### 镜像不存在

**问题**: `Image not found: mcr.microsoft.com/powershell:latest`

**解决方案**:
```powershell
# 手动拉取镜像
docker pull mcr.microsoft.com/powershell:latest
```

### 沙箱执行失败

**问题**: 命令在沙箱中执行失败

**解决方案**:
1. 检查Docker日志
2. 临时禁用沙箱: `sandbox_enabled: false`
3. 查看后端日志获取详细错误信息

## 📈 性能对比

| 执行方式 | 启动时间 | 执行时间 | 隔离性 | 适用场景 |
|---------|---------|---------|--------|---------|
| **正常执行** | ~0ms | 快 | 无 | 低风险命令 |
| **沙箱执行** | ~1-2s | 慢 | 完全隔离 | 高危命令 |

## 💡 最佳实践

### 推荐配置

✅ **开发环境**:
```yaml
sandbox_enabled: true
sandbox_for_high_risk_only: true  # 平衡性能和安全
```

✅ **生产环境**:
```yaml
sandbox_enabled: true
sandbox_for_high_risk_only: false  # 所有命令都使用沙箱
```

✅ **测试环境**:
```yaml
sandbox_enabled: false  # 快速测试
```

### 注意事项

1. **首次使用**: Docker会自动拉取PowerShell镜像，需要几分钟
2. **网络命令**: 沙箱默认禁用网络，需要网络的命令会失败
3. **文件访问**: 沙箱无法访问宿主机文件系统
4. **性能影响**: 沙箱启动需要1-2秒，频繁执行会影响体验

## 🎉 总结

✅ **已实现功能**:
- 智能沙箱策略（只对高危命令使用沙箱）
- 自动风险等级判断
- Docker容器隔离
- 资源限制和超时控制
- 执行日志和历史记录

✅ **安全保护层级**:
1. **第一层**: 命令白名单验证
2. **第二层**: 权限检查
3. **第三层**: 沙箱隔离执行（高危命令）

现在你的Web端已经具备完整的三层安全保护，并且采用智能策略，只对真正危险的命令使用沙箱，既保证了安全性，又不影响日常使用的性能！
