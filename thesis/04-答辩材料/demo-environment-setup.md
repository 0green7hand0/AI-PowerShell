# 演示环境准备指南

## 概述

本文档详细说明如何准备答辩演示环境，包括系统配置、测试数据准备、环境验证和备用方案。

---

## 一、系统环境配置

### 1.1 硬件要求

**最低配置**：
- CPU: Intel i5 或同等性能
- 内存: 8GB RAM
- 存储: 20GB 可用空间
- 显示: 1920x1080 分辨率

**推荐配置**：
- CPU: Intel i7 或更高
- 内存: 16GB RAM
- 存储: 50GB SSD
- 显示: 1920x1080 或更高

### 1.2 软件环境

**操作系统**：
- ✅ Windows 10/11 (推荐)
- ✅ Linux (Ubuntu 20.04+)
- ✅ macOS (10.15+)

**必需软件**：
```bash
# Python 3.8+
python --version  # 应显示 3.8.0 或更高

# PowerShell Core 7.0+
pwsh --version    # 应显示 7.0.0 或更高

# Git (用于版本管理)
git --version

# Docker (可选，用于沙箱演示)
docker --version
```

### 1.3 项目安装

**步骤1：克隆项目**
```bash
cd ~/Desktop  # 或其他合适的位置
git clone https://github.com/your-repo/ai-powershell.git
cd ai-powershell
```

**步骤2：创建虚拟环境**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

**步骤3：安装依赖**
```bash
pip install -r requirements.txt
```

**步骤4：验证安装**
```bash
python -m src.main --version
# 应显示: AI PowerShell Assistant v1.0.0
```

### 1.4 AI模型配置

**选项A：使用Ollama（推荐）**
```bash
# 安装Ollama
# Windows: 下载安装包 https://ollama.ai/download
# Linux: curl https://ollama.ai/install.sh | sh
# macOS: brew install ollama

# 下载模型
ollama pull llama2

# 验证模型
ollama list
# 应显示 llama2
```

**选项B：使用本地LLaMA**
```bash
# 下载模型文件到 models/ 目录
# 配置 config/default.yaml 中的模型路径
```

### 1.5 配置文件设置

**编辑 config/default.yaml**：
```yaml
ai_engine:
  provider: "ollama"  # 或 "local"
  model: "llama2"
  temperature: 0.7
  max_tokens: 256
  cache_enabled: true
  cache_ttl: 3600

security_engine:
  whitelist_enabled: true
  permission_check_enabled: true
  sandbox_enabled: false  # 演示时设为false，除非要演示沙箱

execution_engine:
  timeout: 30
  encoding: "utf-8"
  platform_auto_detect: true

logging:
  level: "INFO"  # 演示时使用INFO级别
  format: "pretty"  # 使用美化格式
  file_enabled: false  # 演示时关闭文件日志
```

---

## 二、终端环境配置

### 2.1 Windows Terminal 配置（推荐）

**安装Windows Terminal**：
```powershell
# 从Microsoft Store安装
# 或使用 winget
winget install Microsoft.WindowsTerminal
```

**配置文件设置**：
```json
{
  "profiles": {
    "defaults": {
      "fontSize": 18,
      "fontFace": "Cascadia Code",
      "colorScheme": "One Half Dark",
      "cursorShape": "bar",
      "padding": "8, 8, 8, 8"
    }
  },
  "schemes": [
    {
      "name": "One Half Dark",
      "background": "#282C34",
      "foreground": "#DCDFE4"
    }
  ]
}
```

### 2.2 PowerShell 配置

**创建配置文件**：
```powershell
# 编辑 PowerShell 配置
notepad $PROFILE

# 添加以下内容
$PSStyle.OutputRendering = 'PlainText'  # 避免颜色问题
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### 2.3 字体和颜色设置

**字体设置**：
- 字体：Cascadia Code 或 Consolas
- 大小：18-20pt（确保投影时清晰可见）
- 粗细：Regular 或 Bold

**配色方案**：
- 背景：深色（#282C34 或类似）
- 前景：亮色（#DCDFE4 或类似）
- 高对比度，确保投影时清晰

### 2.4 窗口设置

**窗口大小**：
- 宽度：120 列
- 高度：30 行
- 位置：屏幕中央或左上角

**其他设置**：
- 关闭滚动条（可选）
- 启用透明度：0%（演示时不要透明）
- 光标：闪烁的竖线

---

## 三、测试数据准备

### 3.1 基本测试数据

**创建测试目录**：
```bash
mkdir ~/demo-test
cd ~/demo-test

# 创建一些测试文件
echo "Test file 1" > file1.txt
echo "Test file 2" > file2.txt
mkdir subdir
echo "Test file 3" > subdir/file3.txt
```

### 3.2 进程测试数据

**启动一些进程**（用于演示进程查询）：
```bash
# Windows
notepad.exe
calc.exe

# Linux/macOS
gedit &
gnome-calculator &
```

### 3.3 历史记录准备

**预先执行一些命令**（用于演示历史功能）：
```bash
python -m src.main interactive

# 在交互模式中执行
>>> 显示当前时间
>>> 列出所有进程
>>> 查看磁盘空间
>>> exit
```

### 3.4 配置文件备份

**备份当前配置**：
```bash
cp config/default.yaml config/default.yaml.backup
cp config/templates.yaml config/templates.yaml.backup
```

---

## 四、演示场景测试

### 4.1 场景1测试：基本翻译功能

**测试步骤**：
```bash
python -m src.main interactive
>>> 显示当前时间
>>> y
>>> exit
```

**预期结果**：
- ✅ 系统正常启动
- ✅ 翻译为 "Get-Date"
- ✅ 置信度 > 0.9
- ✅ 执行成功，显示时间
- ✅ 无错误或警告

**检查清单**：
- [ ] 启动时间 < 3秒
- [ ] 翻译时间 < 2秒
- [ ] 中文显示正常
- [ ] 输出格式清晰

### 4.2 场景2测试：复杂命令处理

**测试步骤**：
```bash
python -m src.main interactive
>>> 显示CPU使用率最高的5个进程
>>> y
>>> exit
```

**预期结果**：
- ✅ 翻译为包含管道的复杂命令
- ✅ 置信度 > 0.85
- ✅ 执行成功，显示进程列表
- ✅ 表格格式清晰

**检查清单**：
- [ ] 命令包含 Get-Process | Sort-Object | Select-Object
- [ ] 返回5个进程
- [ ] 表格对齐正确
- [ ] CPU数据显示正确

### 4.3 场景3测试：安全机制

**测试步骤**：
```bash
python -m src.main interactive
>>> 删除所有文件
>>> 重启计算机
>>> n
>>> exit
```

**预期结果**：
- ✅ "删除所有文件" 被拒绝执行
- ✅ 显示风险等级 CRITICAL
- ✅ 提供安全建议
- ✅ "重启计算机" 提示需要管理员权限
- ✅ 用户可以取消

**检查清单**：
- [ ] 危险命令被正确识别
- [ ] 风险等级显示正确
- [ ] 警告信息清晰
- [ ] 建议内容有用

### 4.4 场景4测试：配置自定义

**测试步骤**：
```bash
python -m src.main interactive
>>> config show
>>> config add-rule "查看网络" "Get-NetAdapter"
>>> 查看网络
>>> y
>>> exit
```

**预期结果**：
- ✅ 显示当前配置
- ✅ 成功添加规则
- ✅ 新规则立即生效
- ✅ 使用规则匹配（不是AI生成）

**检查清单**：
- [ ] 配置显示完整
- [ ] 规则添加成功
- [ ] 规则匹配工作正常
- [ ] 置信度为0.95

### 4.5 完整流程测试

**执行完整演示流程**：
```bash
# 按照 demo-script-summary.md 中的脚本
# 完整执行一遍所有场景
# 记录每个场景的实际耗时
```

**时间记录**：
- 场景1：____秒（目标30秒）
- 场景2：____秒（目标30秒）
- 场景3：____秒（目标2分钟）
- 场景4：____秒（目标1分钟）
- 总计：____秒（目标5分钟）

---

## 五、备用方案准备

### 5.1 演示视频录制

**录制工具**：
- Windows: OBS Studio 或 Camtasia
- Linux: SimpleScreenRecorder 或 OBS Studio
- macOS: QuickTime Player 或 OBS Studio

**录制设置**：
```
分辨率: 1920x1080
帧率: 30fps
格式: MP4 (H.264)
音频: 可选（背景音乐或旁白）
时长: 3-4分钟
```

**录制步骤**：
1. 清理桌面，关闭不必要的程序
2. 打开终端，调整字体大小
3. 启动录制软件
4. 按照演示脚本执行
5. 停止录制，保存文件
6. 添加字幕和说明（可选）

**视频文件**：
```
thesis/04-答辩材料/videos/
├── system-demo-full.mp4      # 完整演示（3-4分钟）
├── system-demo-short.mp4     # 精简版（2分钟）
└── system-demo-backup.mp4    # 备用版本
```

### 5.2 截图准备

**关键截图列表**：
```
thesis/04-答辩材料/screenshots/
├── 01-startup.png              # 系统启动界面
├── 02-basic-translation.png   # 基本翻译
├── 03-complex-command.png      # 复杂命令
├── 04-danger-block.png         # 危险命令拦截
├── 05-permission-check.png     # 权限检查
├── 06-config-show.png          # 配置显示
├── 07-config-add-rule.png      # 添加规则
└── 08-history.png              # 历史记录
```

**截图要求**：
- 格式：PNG
- 分辨率：1920x1080
- 清晰度：高清，无模糊
- 内容：包含完整的输入和输出

**截图工具**：
- Windows: Snipping Tool 或 Snagit
- Linux: GNOME Screenshot 或 Flameshot
- macOS: Command+Shift+4

### 5.3 备用U盘准备

**U盘1（主要）**：
```
AI-PowerShell-Demo/
├── system/                    # 完整系统文件
│   ├── src/
│   ├── config/
│   ├── requirements.txt
│   └── README.md
├── videos/                    # 演示视频
│   └── system-demo-full.mp4
├── screenshots/               # 关键截图
│   └── *.png
├── presentation/              # PPT文件
│   └── defense-presentation.pptx
└── README.txt                 # 使用说明
```

**U盘2（备份）**：
- 与U盘1内容完全相同
- 用于应急情况

**README.txt 内容**：
```
AI PowerShell 智能助手 - 答辩演示材料

目录说明：
- system/: 完整系统代码，可直接运行
- videos/: 演示视频，如果现场演示失败可播放
- screenshots/: 关键截图，可用于讲解
- presentation/: 答辩PPT

运行系统：
1. 确保已安装 Python 3.8+ 和 PowerShell Core 7.0+
2. cd system
3. pip install -r requirements.txt
4. python -m src.main interactive

播放视频：
- 使用 VLC Player 或系统默认播放器
- 视频时长约3-4分钟

联系方式：
- 姓名：[你的姓名]
- 邮箱：[你的邮箱]
- 电话：[你的电话]
```

---

## 六、现场设备测试

### 6.1 投影仪测试

**测试清单**：
- [ ] 连接投影仪，确保信号正常
- [ ] 调整分辨率为1920x1080或投影仪支持的最高分辨率
- [ ] 测试颜色显示，确保对比度足够
- [ ] 测试字体大小，确保后排能看清
- [ ] 测试视频播放，确保流畅无卡顿

**常见问题处理**：
- **分辨率不匹配**：降低到1024x768，增大字体
- **颜色失真**：调整投影仪设置或更换配色方案
- **字体太小**：增大到24pt或更大
- **视频卡顿**：使用更低分辨率的视频

### 6.2 音频测试（如果需要）

**测试清单**：
- [ ] 连接音响，测试音量
- [ ] 播放演示视频，检查音频同步
- [ ] 调整音量到合适水平
- [ ] 准备备用音频设备

### 6.3 网络测试（如果需要）

**测试清单**：
- [ ] 测试WiFi连接
- [ ] 测试网络速度
- [ ] 准备离线版本（推荐）
- [ ] 准备移动热点作为备用

---

## 七、演示前检查清单

### 7.1 系统检查（答辩前1天）

**软件环境**：
- [ ] Python版本正确（3.8+）
- [ ] PowerShell版本正确（7.0+）
- [ ] 所有依赖已安装
- [ ] AI模型已下载并可用
- [ ] 配置文件正确

**系统功能**：
- [ ] 基本翻译功能正常
- [ ] 复杂命令处理正常
- [ ] 安全机制工作正常
- [ ] 配置管理功能正常
- [ ] 历史记录功能正常

**性能检查**：
- [ ] 启动时间 < 3秒
- [ ] 翻译响应 < 2秒
- [ ] 命令执行正常
- [ ] 内存占用正常
- [ ] 无内存泄漏

### 7.2 环境检查（答辩前1小时）

**硬件设备**：
- [ ] 笔记本电脑充满电
- [ ] 电源适配器准备好
- [ ] 投影仪连接线准备好
- [ ] 鼠标和激光笔准备好
- [ ] U盘x2准备好

**软件环境**：
- [ ] 关闭所有不必要的程序
- [ ] 关闭通知和弹窗
- [ ] 关闭自动更新
- [ ] 关闭屏幕保护
- [ ] 设置电源为高性能模式

**演示材料**：
- [ ] PPT文件已打开
- [ ] 演示系统已启动
- [ ] 演示视频已准备
- [ ] 截图已准备
- [ ] 演讲稿已打印

### 7.3 最后检查（答辩前10分钟）

**设备测试**：
- [ ] 投影仪显示正常
- [ ] 字体大小合适
- [ ] 颜色对比度足够
- [ ] 音频正常（如需要）
- [ ] 网络连接正常（如需要）

**材料准备**：
- [ ] PPT在第一页
- [ ] 演示系统在就绪状态
- [ ] 备用视频可以播放
- [ ] U盘插入电脑
- [ ] 演讲稿在手边

**个人准备**：
- [ ] 着装得体
- [ ] 精神状态良好
- [ ] 熟悉演示流程
- [ ] 准备好回答问题
- [ ] 保持自信和冷静

---

## 八、应急预案

### 8.1 系统无法启动

**症状**：运行 `python -m src.main` 报错

**可能原因**：
1. Python环境问题
2. 依赖包缺失
3. 配置文件错误
4. AI模型未加载

**解决方案**：
1. 检查Python版本：`python --version`
2. 重新安装依赖：`pip install -r requirements.txt`
3. 检查配置文件：`config/default.yaml`
4. 使用备用视频演示

### 8.2 AI模型响应慢

**症状**：翻译时间超过5秒

**可能原因**：
1. 模型首次加载
2. 系统资源不足
3. 模型配置问题

**解决方案**：
1. 提前启动系统，预热模型
2. 关闭其他程序，释放资源
3. 使用规则匹配的示例（更快）
4. 说明"这是AI模型在思考"

### 8.3 中文显示乱码

**症状**：输出中文显示为乱码或问号

**可能原因**：
1. 终端编码设置错误
2. PowerShell编码问题
3. 系统区域设置问题

**解决方案**：
1. 设置终端编码为UTF-8
2. 在PowerShell中运行：`chcp 65001`
3. 检查系统区域设置
4. 使用备用截图展示

### 8.4 投影仪问题

**症状**：投影仪无信号或显示异常

**可能原因**：
1. 连接线松动
2. 分辨率不匹配
3. 投影仪设置问题

**解决方案**：
1. 重新连接线缆
2. 调整分辨率：Windows+P
3. 切换投影模式：复制或扩展
4. 使用笔记本屏幕演示

### 8.5 时间不够

**症状**：演示时间超过预定时间

**解决方案**：
1. 跳过可选场景（场景5、6）
2. 减少讲解，只展示结果
3. 使用视频快速播放
4. 重点展示核心功能

---

## 九、演示环境验收标准

### 9.1 功能验收

**必须通过**：
- ✅ 系统能正常启动
- ✅ 基本翻译功能正常
- ✅ 安全机制工作正常
- ✅ 命令能正常执行
- ✅ 中文显示正常

**推荐通过**：
- ✅ 复杂命令处理正常
- ✅ 配置管理功能正常
- ✅ 历史记录功能正常
- ✅ 性能指标达标

### 9.2 性能验收

**响应时间**：
- 启动时间 < 3秒 ✅
- 规则匹配 < 10ms ✅
- AI翻译 < 2秒 ✅
- 命令执行 < 1秒 ✅

**资源占用**：
- 内存 < 512MB ✅
- CPU < 30% ✅
- 磁盘 < 100MB ✅

### 9.3 显示验收

**字体清晰度**：
- 后排能看清 ✅
- 对比度足够 ✅
- 无模糊或重影 ✅

**颜色显示**：
- 颜色准确 ✅
- 高亮明显 ✅
- 背景舒适 ✅

---

## 十、演示环境文档

### 10.1 环境配置文档

**创建文档**：`thesis/04-答辩材料/environment-config.txt`

**内容**：
```
AI PowerShell 智能助手 - 演示环境配置

系统信息：
- 操作系统: Windows 11 Pro
- Python版本: 3.10.5
- PowerShell版本: 7.3.0
- 内存: 16GB
- CPU: Intel i7-10700

软件配置：
- AI提供商: Ollama
- AI模型: llama2
- 终端: Windows Terminal
- 字体: Cascadia Code 18pt
- 配色: One Half Dark

网络配置：
- 模式: 离线（本地AI）
- 备用: 移动热点

备用方案：
- 演示视频: videos/system-demo-full.mp4
- 关键截图: screenshots/*.png
- U盘: 2个（主备）

联系方式：
- 姓名: [你的姓名]
- 邮箱: [你的邮箱]
- 电话: [你的电话]

最后更新: 2024-01-15
```

### 10.2 测试报告

**创建文档**：`thesis/04-答辩材料/demo-test-report.md`

**内容**：
```markdown
# 演示环境测试报告

## 测试时间
2024-01-15 14:00-16:00

## 测试环境
- 操作系统: Windows 11 Pro
- Python: 3.10.5
- PowerShell: 7.3.0

## 测试结果

### 场景1：基本翻译功能
- 状态: ✅ 通过
- 耗时: 25秒
- 问题: 无

### 场景2：复杂命令处理
- 状态: ✅ 通过
- 耗时: 28秒
- 问题: 无

### 场景3：安全机制演示
- 状态: ✅ 通过
- 耗时: 1分50秒
- 问题: 无

### 场景4：配置自定义
- 状态: ✅ 通过
- 耗时: 55秒
- 问题: 无

### 总体评估
- 所有核心功能正常
- 性能指标达标
- 显示效果良好
- 准备就绪，可以答辩

## 测试人员
[你的姓名]

## 审核人员
[指导教师姓名]
```

---

## 总结

演示环境准备是答辩成功的关键。请按照本指南逐项检查，确保：

1. ✅ 系统环境配置正确
2. ✅ 所有功能测试通过
3. ✅ 备用方案准备充分
4. ✅ 现场设备测试完成
5. ✅ 应急预案准备就绪

**最后提醒**：
- 提前1天完成所有准备
- 提前1小时到达现场
- 保持冷静和自信
- 相信自己的准备

**祝答辩成功！** 🎓
