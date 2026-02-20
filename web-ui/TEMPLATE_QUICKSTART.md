# 模板管理快速开始

## 5分钟快速上手

### 第一步：启动应用

```bash
# 启动后端
cd web-ui/backend
python app.py

# 启动前端（新终端）
cd web-ui
npm run dev
```

访问：http://localhost:5173/template-management

### 第二步：创建第一个模板

1. 点击右上角"新建模板"按钮

2. 填写基本信息：
   ```
   名称：文件备份
   分类：自动化
   描述：将文件从源路径备份到目标路径
   关键词：backup, copy, 备份
   ```

3. 编写脚本（切换到"脚本编辑"标签）：
   ```powershell
   # 文件备份脚本
   # 将文件从源路径复制到目标路径
   
   $sourcePath = "{{sourcePath}}"
   $targetPath = "{{targetPath}}"
   $includeSubfolders = {{includeSubfolders}}
   
   if (-not (Test-Path $sourcePath)) {
       Write-Error "源路径不存在: $sourcePath"
       exit 1
   }
   
   if (-not (Test-Path $targetPath)) {
       New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
   }
   
   if ($includeSubfolders) {
       Copy-Item -Path $sourcePath -Destination $targetPath -Recurse -Force
   } else {
       Copy-Item -Path $sourcePath -Destination $targetPath -Force
   }
   
   Write-Host "备份完成！" -ForegroundColor Green
   ```

4. 配置参数（切换到"参数配置"标签）：
   
   点击"自动检测参数"，系统会自动识别脚本中的参数。
   
   或手动添加：
   
   **参数 1：**
   - 名称：`sourcePath`
   - 类型：字符串
   - 必填：是
   - 描述：源文件路径
   - 默认值：`C:\Data`
   
   **参数 2：**
   - 名称：`targetPath`
   - 类型：字符串
   - 必填：是
   - 描述：目标备份路径
   - 默认值：`D:\Backup`
   
   **参数 3：**
   - 名称：`includeSubfolders`
   - 类型：布尔值
   - 必填：否
   - 描述：是否包含子文件夹
   - 默认值：`true`

5. 预览和测试（切换到"预览测试"标签）：
   - 查看模板信息
   - 检查参数列表
   - 预览脚本内容
   - 点击"测试模板"验证

6. 保存模板：
   - 点击底部"保存"按钮
   - 等待保存成功提示

### 第三步：使用模板

1. 在模板列表中找到刚创建的"文件备份"模板

2. 点击"使用"按钮

3. 填写参数值：
   ```
   sourcePath: C:\MyDocuments
   targetPath: D:\Backup\Documents
   includeSubfolders: true
   ```

4. 点击"生成脚本"

5. 查看生成的脚本，确认无误后执行

## 常见场景示例

### 场景 1：系统监控脚本

```powershell
# 系统资源监控
$cpuThreshold = {{cpuThreshold}}
$memoryThreshold = {{memoryThreshold}}

$cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue
$memory = (Get-Counter '\Memory\% Committed Bytes In Use').CounterSamples.CookedValue

Write-Host "CPU使用率: $([math]::Round($cpu, 2))%"
Write-Host "内存使用率: $([math]::Round($memory, 2))%"

if ($cpu -gt $cpuThreshold) {
    Write-Warning "CPU使用率超过阈值！"
}

if ($memory -gt $memoryThreshold) {
    Write-Warning "内存使用率超过阈值！"
}
```

参数：
- `cpuThreshold` (数字, 默认: 80)
- `memoryThreshold` (数字, 默认: 85)

### 场景 2：批量文件重命名

```powershell
# 批量重命名文件
$path = "{{path}}"
$pattern = "{{pattern}}"
$replacement = "{{replacement}}"

Get-ChildItem -Path $path -File | ForEach-Object {
    $newName = $_.Name -replace $pattern, $replacement
    if ($newName -ne $_.Name) {
        Rename-Item -Path $_.FullName -NewName $newName
        Write-Host "重命名: $($_.Name) -> $newName"
    }
}

Write-Host "批量重命名完成！" -ForegroundColor Green
```

参数：
- `path` (字符串, 必填)
- `pattern` (字符串, 必填)
- `replacement` (字符串, 必填)

### 场景 3：定时任务创建

```powershell
# 创建定时任务
$taskName = "{{taskName}}"
$scriptPath = "{{scriptPath}}"
$scheduleType = "{{scheduleType}}"
$startTime = "{{startTime}}"

$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File `"$scriptPath`""

switch ($scheduleType) {
    "daily" {
        $trigger = New-ScheduledTaskTrigger -Daily -At $startTime
    }
    "weekly" {
        $trigger = New-ScheduledTaskTrigger -Weekly -At $startTime -DaysOfWeek Monday
    }
    "hourly" {
        $trigger = New-ScheduledTaskTrigger -Once -At $startTime -RepetitionInterval (New-TimeSpan -Hours 1)
    }
}

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger

Write-Host "定时任务创建成功！" -ForegroundColor Green
```

参数：
- `taskName` (字符串, 必填)
- `scriptPath` (字符串, 必填)
- `scheduleType` (选择项: daily/weekly/hourly)
- `startTime` (字符串, 默认: "09:00")

## 编辑器快捷操作

### 脚本编辑器
- **插入参数**：点击工具栏"插入参数"按钮，快速插入 `{{参数名}}` 占位符
- **格式化**：自动格式化脚本，移除多余空行
- **验证**：检查脚本中的参数是否都已定义

### 参数配置
- **自动检测**：自动扫描脚本，提取所有参数占位符
- **快速添加**：点击"添加参数"快速创建新参数
- **拖拽排序**：（计划中）拖拽调整参数顺序

### 预览测试
- **实时预览**：编辑时实时更新预览
- **测试模板**：验证模板完整性和正确性

## 视图模式选择

### 卡片视图
- 适合：浏览和选择模板
- 特点：直观、美观、信息丰富
- 推荐：日常使用

### 列表视图
- 适合：快速查看多个模板
- 特点：紧凑、高效
- 推荐：模板较多时使用

### 表格视图
- 适合：详细对比模板
- 特点：信息完整、便于排序
- 推荐：需要详细信息时使用

## 搜索技巧

### 按名称搜索
```
输入：backup
结果：所有名称包含"backup"的模板
```

### 按描述搜索
```
输入：文件
结果：描述中包含"文件"的模板
```

### 按关键词搜索
```
输入：monitor
结果：关键词包含"monitor"的模板
```

### 组合筛选
```
搜索：backup
分类：自动化
结果：自动化分类中名称/描述/关键词包含"backup"的模板
```

## 最佳实践

### 1. 模板命名规范
✅ 好的命名：
- "文件备份脚本"
- "系统资源监控"
- "批量重命名工具"

❌ 不好的命名：
- "脚本1"
- "test"
- "新建模板"

### 2. 参数设计原则
- 使用清晰的参数名
- 提供合理的默认值
- 添加详细的描述
- 标记必填参数

### 3. 脚本编写建议
- 添加注释说明功能
- 包含错误处理
- 提供友好的输出信息
- 使用参数验证

### 4. 关键词优化
- 包含中英文关键词
- 添加常用别名
- 考虑搜索习惯

## 常见问题

### Q: 如何修改已保存的模板？
A: 在模板列表中找到模板，点击"编辑"按钮即可修改。

### Q: 参数占位符格式是什么？
A: 使用双花括号包裹参数名：`{{参数名}}`，例如 `{{sourcePath}}`

### Q: 如何删除模板？
A: 点击模板的"删除"按钮，确认后即可删除。注意：删除操作不可恢复。

### Q: 自动检测参数不准确怎么办？
A: 可以手动添加或修改参数。确保脚本中使用正确的占位符格式。

### Q: 如何导出模板？
A: 当前版本暂不支持导出，该功能在开发计划中。

### Q: 模板保存在哪里？
A: 模板保存在后端的 `config/templates.yaml` 文件中。

## 下一步

- 探索更多模板示例
- 学习 PowerShell 脚本编写
- 创建自己的模板库
- 分享模板给团队

## 获取帮助

- 查看完整文档：[TEMPLATE_MANAGEMENT.md](./TEMPLATE_MANAGEMENT.md)
- 查看 API 文档：[API.md](./API.md)
- 提交问题：GitHub Issues
- 联系支持：开发团队

---

**提示**：建议先从简单的模板开始，逐步掌握各项功能。
