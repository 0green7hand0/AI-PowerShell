# 源代码目录

本目录用于存放整理后的项目源代码。

## 目录说明

此目录将包含:
1. 完整的项目源代码
2. 配置文件
3. 测试代码
4. 文档
5. 示例代码

## 整理步骤

### 自动整理 (推荐)

运行整理脚本:
```bash
python scripts/prepare_source_code.py
```

脚本会自动:
- 复制所有必要的源代码文件
- 排除临时文件和缓存
- 清理调试代码
- 更新README
- 创建压缩包
- 创建Git标签

### 手动整理

如果需要手动整理，请按以下步骤:

#### 1. 清理代码

- 删除调试代码 (print语句、断点等)
- 删除注释掉的废弃代码
- 确保代码格式规范
- 更新注释和文档字符串

#### 2. 更新README

确保README.md包含:
- 项目简介
- 功能特性
- 安装步骤
- 使用方法
- 项目结构
- 开发指南
- 许可证信息

#### 3. 检查依赖

- 更新requirements.txt
- 确保版本号正确
- 移除未使用的依赖

#### 4. 复制文件

复制以下目录和文件:

**目录:**
- src/ (源代码)
- tests/ (测试代码)
- config/ (配置文件)
- templates/ (模板)
- scripts/ (脚本)
- examples/ (示例)
- docs/ (文档)
- web-ui/ (Web界面)

**根目录文件:**
- README.md
- requirements.txt
- requirements-dev.txt
- pyproject.toml
- Makefile
- Dockerfile
- docker-compose.yml
- .gitignore
- LICENSE
- CHANGELOG.md
- run.py
- 中文项目说明.md
- 快速开始.md

**排除:**
- __pycache__/
- *.pyc, *.pyo, *.pyd
- .pytest_cache/
- .coverage, htmlcov/
- .git/
- .vscode/, .idea/
- node_modules/
- *.log
- venv/, env/
- .env.local

#### 5. 打包压缩

创建压缩包:
```bash
# Windows PowerShell
Compress-Archive -Path "源代码\*" -DestinationPath "AI-PowerShell-源代码-20240101.zip"

# Linux/macOS
zip -r AI-PowerShell-源代码-20240101.zip 源代码/
```

#### 6. 创建Git标签

```bash
# 创建标签
git tag -a submission-20240101 -m "提交版本"

# 推送标签
git push origin submission-20240101
```

## 验证清单

整理完成后，请验证:

### 代码质量
- [ ] 无调试代码
- [ ] 无废弃代码
- [ ] 代码格式规范
- [ ] 注释完整清晰

### 文档完整性
- [ ] README.md完整
- [ ] 安装步骤清晰
- [ ] 使用说明详细
- [ ] API文档完整

### 依赖管理
- [ ] requirements.txt准确
- [ ] 版本号明确
- [ ] 无多余依赖

### 文件结构
- [ ] 目录结构清晰
- [ ] 文件命名规范
- [ ] 无临时文件
- [ ] 无敏感信息

### 功能测试
- [ ] 代码可以运行
- [ ] 测试可以通过
- [ ] 示例可以执行
- [ ] 文档可以访问

## 压缩包内容

压缩包应包含:
```
AI-PowerShell/
├── src/                    # 源代码
├── tests/                  # 测试
├── config/                 # 配置
├── templates/              # 模板
├── scripts/                # 脚本
├── examples/               # 示例
├── docs/                   # 文档
├── web-ui/                 # Web界面
├── README.md               # 说明
├── requirements.txt        # 依赖
├── LICENSE                 # 许可证
└── run.py                  # 运行脚本
```

## 提交格式

### 文件命名
- 格式: `AI-PowerShell-源代码-YYYYMMDD.zip`
- 示例: `AI-PowerShell-源代码-20240101.zip`

### 文件大小
- 建议: < 50MB
- 如果过大，考虑:
  - 移除大型测试数据
  - 压缩图片资源
  - 排除不必要的文件

### Git标签
- 格式: `submission-YYYYMMDD`
- 示例: `submission-20240101`
- 说明: 标记提交版本

## 常见问题

### Q1: 如何清理Python缓存?

```bash
# 删除所有__pycache__目录
find . -type d -name __pycache__ -exec rm -rf {} +

# 删除所有.pyc文件
find . -type f -name "*.pyc" -delete
```

### Q2: 如何检查代码规范?

```bash
# 使用flake8检查
flake8 src/

# 使用black格式化
black src/
```

### Q3: 如何更新依赖列表?

```bash
# 生成当前环境的依赖
pip freeze > requirements.txt

# 或使用pipreqs扫描项目
pipreqs . --force
```

### Q4: 如何验证压缩包?

```bash
# 解压到临时目录
unzip AI-PowerShell-源代码-*.zip -d /tmp/test

# 进入目录测试
cd /tmp/test/AI-PowerShell
python run.py --help
```

### Q5: 如何处理敏感信息?

- 移除.env文件
- 检查配置文件中的密钥
- 移除日志文件
- 检查代码中的硬编码信息

## 注意事项

1. **备份**: 整理前先备份原始代码
2. **测试**: 整理后测试代码是否可运行
3. **文档**: 确保文档与代码同步
4. **版本**: 记录当前版本号
5. **许可**: 确认许可证信息正确

## 获取帮助

如遇到问题:
1. 查看脚本输出的错误信息
2. 检查文件权限
3. 确认Python环境正确
4. 查看项目文档

## 更新记录

- 2024-XX-XX: 创建源代码目录
- 待更新: 整理并打包源代码
