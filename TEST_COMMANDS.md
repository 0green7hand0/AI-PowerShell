# 测试命令列表

## ✅ 已修复的问题

### 问题1: 创建文件夹命令不完整
- **输入**: "在桌面新建两个文件夹"
- **旧命令**: `New-Item -ItemType Directory` ❌
- **新命令**: `New-Item -ItemType Directory -Path "C:\Users\...\Desktop\NewFolder1"; New-Item -ItemType Directory -Path "C:\Users\...\Desktop\NewFolder2"` ✅

### 问题2: 删除文件夹命令不完整
- **输入**: "删除桌面NewFolder文件夹"
- **旧命令**: `Remove-Item .` ❌
- **新命令**: `Remove-Item -Path "C:\Users\...\Desktop\NewFolder" -Recurse -Force` ✅
- **沙箱**: ✅ 自动在沙箱中执行（包含Remove-Item关键词）

## 🧪 测试用例

### 1. 低风险命令（正常执行）

#### 查询类命令
```
输入: "显示当前进程"
预期命令: Get-Process
风险等级: Safe
执行方式: 正常执行
```

```
输入: "查看当前时间"
预期命令: Get-Date
风险等级: Safe
执行方式: 正常执行
```

```
输入: "显示当前目录"
预期命令: Get-Location
风险等级: Safe
执行方式: 正常执行
```

#### 创建类命令
```
输入: "在桌面新建一个文件夹"
预期命令: New-Item -ItemType Directory -Path "C:\Users\...\Desktop\NewFolder"
风险等级: Low/Medium
执行方式: 正常执行
```

```
输入: "在桌面新建两个文件夹"
预期命令: New-Item -ItemType Directory -Path "...\NewFolder1"; New-Item -ItemType Directory -Path "...\NewFolder2"
风险等级: Low/Medium
执行方式: 正常执行
```

```
输入: "在文档创建三个目录"
预期命令: New-Item -ItemType Directory -Path "...\NewFolder1"; ... (3个)
风险等级: Low/Medium
执行方式: 正常执行
```

### 2. 高风险命令（沙箱执行）🔒

#### 删除类命令
```
输入: "删除桌面NewFolder文件夹"
预期命令: Remove-Item -Path "C:\Users\...\Desktop\NewFolder" -Recurse -Force
风险等级: High
执行方式: 🔒 沙箱执行
后端日志: [沙箱执行] 命令: Remove-Item ...
```

```
输入: "删除桌面上的临时文件"
预期命令: Remove-Item -Path "C:\Users\...\Desktop\temp*" -Recurse -Force
风险等级: High
执行方式: 🔒 沙箱执行
```

```
输入: "删除文档中的test文件夹"
预期命令: Remove-Item -Path "C:\Users\...\Documents\test" -Recurse -Force
风险等级: High
执行方式: 🔒 沙箱执行
```

#### 进程管理命令
```
输入: "停止记事本进程"
预期命令: Stop-Process -Name notepad
风险等级: High
执行方式: 🔒 沙箱执行
```

```
输入: "强制结束chrome进程"
预期命令: Stop-Process -Name chrome -Force
风险等级: High
执行方式: 🔒 沙箱执行
```

### 3. 严重风险命令（沙箱执行）🛑

```
输入: "格式化D盘"
预期命令: Format-Volume -DriveLetter D
风险等级: Critical
执行方式: 🔒 沙箱执行
状态: 应该被安全引擎阻止
```

```
输入: "关闭计算机"
预期命令: Stop-Computer
风险等级: Critical
执行方式: 🔒 沙箱执行
状态: 应该被安全引擎阻止
```

## 📊 预期结果

### 正常执行的命令
- ✅ 直接在本地PowerShell中执行
- ✅ 执行速度快（<1秒）
- ✅ 可以访问本地文件系统
- ✅ 后端日志显示: `✅ 命令执行成功`

### 沙箱执行的命令
- ✅ 在Docker容器中隔离执行
- ✅ 执行速度较慢（1-3秒，包含容器启动时间）
- ❌ 无法访问宿主机文件系统
- ✅ 后端日志显示: `[沙箱执行]` 和 `🔒 命令在沙箱中执行`
- ✅ 响应中包含: `"sandbox": true`

## 🔍 验证方法

### 1. 查看后端日志

**正常执行**:
```
⚡ 开始执行命令: Get-Process
✅ 命令执行成功 (耗时: 0.80秒)
```

**沙箱执行**:
```
[沙箱执行] 命令: Remove-Item -Path "..." -Recurse -Force
⚡ 开始执行命令: Remove-Item -Path "..." -Recurse -Force
🔒 使用沙箱执行高危命令...
✅ 命令执行成功 (耗时: 2.34秒)
🔒 命令在沙箱中执行
```

### 2. 查看前端响应

在浏览器开发者工具的Network标签中，查看 `/api/command/execute` 的响应：

**正常执行**:
```json
{
  "success": true,
  "data": {
    "output": "...",
    "executionTime": 0.8,
    "sandbox": false
  }
}
```

**沙箱执行**:
```json
{
  "success": true,
  "data": {
    "output": "...",
    "executionTime": 2.3,
    "sandbox": true
  }
}
```

### 3. 查看历史记录

在Web界面的历史记录页面，沙箱执行的命令会有特殊标记。

## 🐛 已知限制

### 沙箱执行的限制

1. **无法访问宿主机文件系统**
   - 删除命令在沙箱中执行时，实际上不会删除宿主机的文件
   - 这是沙箱的安全特性，防止误操作

2. **网络隔离**
   - 沙箱中的命令默认无法访问网络
   - 需要网络的命令会失败

3. **性能开销**
   - 每次沙箱执行需要启动Docker容器
   - 首次执行较慢（1-3秒）

### 解决方案

如果需要真正执行删除等高危操作：

**方法1**: 临时禁用沙箱
```yaml
# config/default.yaml
security:
  sandbox_enabled: false
```

**方法2**: 只对特定命令禁用沙箱
```yaml
security:
  sandbox_for_high_risk_only: false  # 所有命令都不使用沙箱
```

**方法3**: 使用CLI模式
```bash
# CLI模式不使用沙箱
python src/main.py
```

## 💡 测试建议

1. **先测试低风险命令**
   - 确保基本功能正常
   - 验证命令生成是否完整

2. **再测试高危命令**
   - 验证沙箱是否启用
   - 检查后端日志中的沙箱标记

3. **检查Docker状态**
   ```bash
   docker ps
   ```
   - 执行高危命令后，应该能看到短暂的PowerShell容器

4. **查看容器日志**（如果需要调试）
   ```bash
   docker logs <container_id>
   ```

## 🎯 成功标准

- ✅ 低风险命令正常执行，速度快
- ✅ 高危命令在沙箱中执行，有明确标记
- ✅ 命令生成完整，包含所有必要参数
- ✅ 后端日志清晰显示执行方式
- ✅ 前端响应包含沙箱标记
- ✅ Docker容器正常启动和清理

现在可以在Web界面中测试了！🚀
