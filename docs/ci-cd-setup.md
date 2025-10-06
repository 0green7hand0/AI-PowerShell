# CI/CD 配置文档

## 概述

本文档描述了 AI PowerShell 智能助手项目的持续集成和持续部署（CI/CD）配置。

## 实施的配置

### 1. GitHub Actions 工作流

#### 1.1 主 CI 工作流 (`.github/workflows/ci.yml`)

**功能：**
- 多平台测试（Ubuntu、Windows、macOS）
- 多 Python 版本测试（3.8、3.9、3.10、3.11）
- 自动安装 PowerShell Core
- 运行完整测试套件
- 生成覆盖率报告
- 上传到 Codecov

**触发条件：**
- 推送到 `main` 或 `develop` 分支
- 针对 `main` 或 `develop` 的 Pull Request

**作业：**
1. **test**: 跨平台和跨版本测试
2. **code-quality**: 代码质量检查
3. **integration-tests**: 集成测试
4. **security-scan**: 安全扫描

#### 1.2 代码质量工作流 (`.github/workflows/code-quality.yml`)

**功能：**
- Black 代码格式化检查
- Flake8 代码检查
- MyPy 类型检查
- Pylint 代码分析
- isort 导入排序检查

**独立运行：** 可以快速反馈代码质量问题

#### 1.3 覆盖率工作流 (`.github/workflows/coverage.yml`)

**功能：**
- 生成详细的覆盖率报告
- 强制执行 80% 覆盖率阈值
- PR 覆盖率差异分析
- 模块级覆盖率检查
- 上传 HTML、XML、JSON 报告

**覆盖率目标：**
- 整体覆盖率：≥ 80%
- 每个模块：≥ 80%

### 2. 代码质量配置文件

#### 2.1 `.flake8`

Flake8 代码检查配置：

```ini
max-line-length = 127
max-complexity = 10
exclude = .git, __pycache__, backup, venv
ignore = E203, W503, E501
```

#### 2.2 `pyproject.toml`

统一配置文件，包含：

**Black 配置：**
- 行长度：127
- 目标版本：Python 3.8-3.11

**MyPy 配置：**
- 忽略缺失的导入
- 警告未使用的配置
- 检查未类型化的定义

**Pytest 配置：**
- 测试路径：`tests/`
- 覆盖率报告：term、HTML、XML、JSON
- 标记：slow、integration、unit

**Coverage 配置：**
- 源目录：`src/`
- 精度：2 位小数
- 失败阈值：80%

**isort 配置：**
- 配置文件：black
- 行长度：127

**Bandit 配置：**
- 排除：tests、backup

**Pylint 配置：**
- 最大行长度：127
- 禁用：C0111、R0903、R0913、W0212

#### 2.3 `.coveragerc`

Coverage.py 配置：

```ini
[run]
source = src
branch = True
fail_under = 80

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

#### 2.4 `.pre-commit-config.yaml`

Pre-commit 钩子配置：

**钩子：**
1. 通用文件检查（尾随空格、文件结尾、大文件）
2. Black 代码格式化
3. isort 导入排序
4. Flake8 代码检查
5. MyPy 类型检查
6. Bandit 安全检查
7. YAML 格式化

### 3. 开发依赖

#### 3.1 `requirements-dev.txt`

开发环境依赖：

**代码格式化：**
- black >= 23.0.0
- isort >= 5.12.0

**代码检查：**
- flake8 >= 6.0.0
- flake8-docstrings >= 1.7.0
- flake8-bugbear >= 23.0.0
- pylint >= 2.17.0

**类型检查：**
- mypy >= 1.5.0
- types-PyYAML >= 6.0.0

**测试：**
- pytest >= 7.4.0
- pytest-cov >= 4.1.0
- pytest-asyncio >= 0.21.0
- pytest-mock >= 3.11.0
- pytest-timeout >= 2.1.0

**覆盖率：**
- coverage[toml] >= 7.3.0

**安全：**
- safety >= 2.3.0
- bandit >= 1.7.5

**文档：**
- sphinx >= 7.0.0
- sphinx-rtd-theme >= 1.3.0

**工具：**
- pre-commit >= 3.3.0
- build >= 0.10.0
- twine >= 4.0.0

### 4. 本地开发脚本

#### 4.1 `scripts/run-coverage.sh` (Linux/macOS)

Bash 脚本，用于本地运行覆盖率测试：

```bash
./scripts/run-coverage.sh
```

**功能：**
- 清理旧的覆盖率数据
- 运行测试并生成覆盖率报告
- 检查 80% 阈值
- 显示覆盖率摘要
- 生成 HTML、XML、JSON 报告

#### 4.2 `scripts/run-coverage.ps1` (Windows)

PowerShell 脚本，功能同上：

```powershell
.\scripts\run-coverage.ps1
```

#### 4.3 `Makefile`

便捷的开发命令：

**安装：**
```bash
make install          # 安装生产依赖
make install-dev      # 安装开发依赖
```

**测试：**
```bash
make test             # 运行所有测试
make test-unit        # 运行单元测试
make test-integration # 运行集成测试
make coverage         # 运行覆盖率测试
```

**代码质量：**
```bash
make format           # 格式化代码
make format-check     # 检查格式
make lint             # 运行 linter
make type-check       # 类型检查
make quality          # 运行所有质量检查
```

**维护：**
```bash
make clean            # 清理构建产物
make docs             # 生成文档
make security         # 安全检查
make ci               # 模拟 CI 流程
```

## 使用指南

### 本地开发设置

1. **安装开发依赖：**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **安装 pre-commit 钩子：**
   ```bash
   pre-commit install
   ```

3. **运行测试：**
   ```bash
   make test
   # 或
   pytest
   ```

4. **检查覆盖率：**
   ```bash
   make coverage
   # 或
   ./scripts/run-coverage.sh  # Linux/macOS
   .\scripts\run-coverage.ps1 # Windows
   ```

5. **格式化代码：**
   ```bash
   make format
   # 或
   black src/ tests/
   isort src/ tests/
   ```

6. **运行所有质量检查：**
   ```bash
   make quality
   ```

### 提交代码前

1. **运行 pre-commit 钩子：**
   ```bash
   pre-commit run --all-files
   ```

2. **确保测试通过：**
   ```bash
   make test
   ```

3. **检查覆盖率：**
   ```bash
   make coverage
   ```

4. **运行质量检查：**
   ```bash
   make quality
   ```

### Pull Request 流程

1. **创建分支：**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **开发并提交：**
   ```bash
   # 开发代码
   git add .
   git commit -m "feat: your feature"
   # pre-commit 钩子会自动运行
   ```

3. **推送并创建 PR：**
   ```bash
   git push origin feature/your-feature
   ```

4. **CI 检查：**
   - 所有平台和版本的测试
   - 代码质量检查
   - 覆盖率检查
   - 安全扫描

5. **查看覆盖率报告：**
   - PR 会自动添加覆盖率评论
   - 可以下载 HTML 报告查看详情

## 覆盖率要求

### 整体覆盖率

- **最低要求：** 80%
- **目标：** 85%+
- **优秀：** 90%+

### 模块覆盖率

每个模块都应达到 80% 以上：

- `src/ai_engine/` - AI 引擎
- `src/security/` - 安全引擎
- `src/execution/` - 执行引擎
- `src/config/` - 配置管理
- `src/log_engine/` - 日志引擎
- `src/storage/` - 存储引擎
- `src/context/` - 上下文管理

### 覆盖率报告

**生成位置：**
- HTML: `htmlcov/index.html`
- XML: `coverage.xml`
- JSON: `coverage.json`

**查看方式：**
```bash
# Linux/macOS
open htmlcov/index.html

# Windows
Start-Process htmlcov\index.html
```

## 代码质量标准

### Black 格式化

- 行长度：127
- 自动格式化
- 强制执行

### Flake8 检查

- 最大复杂度：10
- 最大行长度：127
- 忽略：E203、W503、E501

### MyPy 类型检查

- 忽略缺失的导入
- 检查未类型化的定义
- 警告冗余的类型转换

### Pylint 分析

- 最大行长度：127
- 禁用某些规则（如缺失文档字符串）

## 安全扫描

### Safety

检查依赖项的已知漏洞：

```bash
safety check
```

### Bandit

扫描 Python 代码的安全问题：

```bash
bandit -r src/
```

## 故障排除

### 测试失败

1. **检查 Python 版本：**
   ```bash
   python --version
   ```

2. **更新依赖：**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **清理缓存：**
   ```bash
   make clean
   ```

### 覆盖率不足

1. **查看未覆盖的行：**
   ```bash
   pytest --cov=src --cov-report=term-missing
   ```

2. **添加测试：**
   - 为未覆盖的代码添加测试
   - 确保边界情况被覆盖

3. **使用 pragma：**
   ```python
   # pragma: no cover
   ```
   用于不需要测试的代码

### Pre-commit 钩子失败

1. **查看所有问题：**
   ```bash
   pre-commit run --all-files
   ```

2. **自动修复格式：**
   ```bash
   make format
   ```

3. **更新钩子：**
   ```bash
   pre-commit autoupdate
   ```

## 最佳实践

### 编写测试

1. **测试命名：**
   ```python
   def test_function_name_should_do_something():
       pass
   ```

2. **使用标记：**
   ```python
   @pytest.mark.slow
   @pytest.mark.integration
   def test_slow_integration():
       pass
   ```

3. **参数化测试：**
   ```python
   @pytest.mark.parametrize("input,expected", [
       (1, 2),
       (2, 4),
   ])
   def test_multiply(input, expected):
       assert multiply(input, 2) == expected
   ```

### 代码质量

1. **保持函数简单：**
   - 复杂度 ≤ 10
   - 行数 ≤ 50

2. **添加类型注解：**
   ```python
   def function(param: str) -> int:
       return len(param)
   ```

3. **编写文档字符串：**
   ```python
   def function(param: str) -> int:
       """Calculate the length of a string.
       
       Args:
           param: The input string
           
       Returns:
           The length of the string
       """
       return len(param)
   ```

### 提交消息

使用约定式提交（Conventional Commits）：

```
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
style: 代码格式化
refactor: 重构代码
test: 添加测试
chore: 构建/工具更改
```

## 参考资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [pytest 文档](https://docs.pytest.org/)
- [Coverage.py 文档](https://coverage.readthedocs.io/)
- [Black 文档](https://black.readthedocs.io/)
- [Flake8 文档](https://flake8.pycqa.org/)
- [MyPy 文档](https://mypy.readthedocs.io/)
- [Pre-commit 文档](https://pre-commit.com/)

## 总结

本 CI/CD 配置提供了：

✅ 自动化测试（多平台、多版本）
✅ 代码质量检查（格式化、检查、类型检查）
✅ 覆盖率报告和强制执行（80% 阈值）
✅ 安全扫描（依赖和代码）
✅ 本地开发工具（脚本、Makefile、pre-commit）
✅ 详细的文档和故障排除指南

这确保了代码质量、测试覆盖率和安全性，同时提供了良好的开发体验。
