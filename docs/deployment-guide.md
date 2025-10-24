<!-- 文档类型: 运维指南 | 最后更新: 2025-01-17 | 维护者: 项目团队 -->

# 部署运维完整指南

> **文档类型**: 运维指南 | **最后更新**: 2025-01-17 | **维护者**: 项目团队

📍 [首页](../README.md) > [文档中心](README.md) > 部署运维完整指南

## 📋 目录

- [安装部署](#安装部署)
- [Docker 部署](#docker-部署)
- [CI/CD 配置](#cicd-配置)
- [发布流程](#发布流程)
- [AI 模型配置](#ai-模型配置)
- [部署检查清单](#部署检查清单)
- [许可证说明](#许可证说明)

---

## 安装部署

### 系统要求

**最低配置**:
- Python 3.8+
- PowerShell Core 7.0+
- 2GB RAM
- 5GB 磁盘空间

**推荐配置**:
- Python 3.11+
- PowerShell Core 7.4+
- 4GB RAM
- 10GB 磁盘空间

### 快速安装

#### Linux/macOS

```bash
# 克隆仓库
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell

# 运行安装脚本
chmod +x scripts/install.sh
./scripts/install.sh

# 验证安装
python scripts/verify_installation.py
```

#### Windows

```powershell
# 克隆仓库
git clone https://github.com/0green7hand0/AI-PowerShell.git
cd AI-PowerShell

# 运行安装脚本
.\scripts\install.ps1

# 验证安装
python scripts\verify_installation.py
```

### 手动安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装开发依赖（可选）
pip install -r requirements-dev.txt

# 3. 配置环境
cp config/default.yaml config/user.yaml
# 编辑 config/user.yaml 进行自定义配置

# 4. 验证安装
python scripts/verify_installation.py

# 5. 运行应用
python src/main.py --interactive
```

### 依赖说明

**核心依赖**:
- PyYAML >= 6.0.1 - 配置文件解析
- pydantic >= 2.0.0 - 数据验证
- structlog >= 23.1.0 - 结构化日志

**UI 依赖**:
- rich >= 13.7.0 - 终端 UI
- click >= 8.1.7 - 命令行接口
- prompt-toolkit >= 3.0.43 - 交互式输入
- colorama >= 0.4.6 - 跨平台颜色支持

**可选依赖**:
- ollama >= 0.1.0 - 本地 AI 模型
- docker >= 6.1.0 - 沙箱执行环境

---

## Docker 部署

### 前置要求

- Docker 20.10+ 已安装
- Docker Compose 1.29+ (或 Docker Compose V2)
- 至少 2GB 可用内存
- 5GB 可用磁盘空间

### 快速启动

#### 使用 Docker

```bash
# 构建镜像
docker build -t ai-powershell:2.0.0 .

# 运行容器
docker run -it --rm \
  -v $(pwd)/config:/app/config:ro \
  -v ai-powershell-logs:/app/logs \
  -v ai-powershell-data:/app/data \
  ai-powershell:2.0.0
```

#### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 使用 Makefile

```bash
# 构建 Docker 镜像
make docker-build

# 运行容器
make docker-run

# 使用 docker-compose 启动
make docker-compose-up

# 查看日志
make docker-compose-logs

# 停止服务
make docker-compose-down
```

### Docker 配置

#### 环境变量

在 `docker-compose.yml` 中配置环境变量：

```yaml
environment:
  # AI 引擎
  - AI_ENGINE_PROVIDER=local
  - AI_ENGINE_MODEL=llama
  - AI_ENGINE_TEMPERATURE=0.7
  
  # 安全设置
  - SECURITY_SANDBOX_ENABLED=false
  - SECURITY_REQUIRE_CONFIRMATION=true
  
  # 执行设置
  - EXECUTION_TIMEOUT=30
  - EXECUTION_ENCODING=utf-8
```

#### 数据卷

Docker 配置使用多个数据卷实现数据持久化：

- **配置文件**: `./config:/app/config:ro` (只读)
- **日志文件**: `ai-powershell-logs:/app/logs` (持久化)
- **数据文件**: `ai-powershell-data:/app/data` (持久化)
- **用户目录**: `ai-powershell-home:/home/appuser` (持久化)

#### 自定义配置

1. 创建自定义配置文件：

```bash
cp config/default.yaml config/user.yaml
# 编辑 config/user.yaml 进行自定义设置
```

2. 更新 docker-compose.yml 使用自定义配置：

```yaml
environment:
  - AI_POWERSHELL_CONFIG=/app/config/user.yaml
```

### Docker 架构

#### 多阶段构建

Dockerfile 使用多阶段构建进行优化：

1. **构建阶段**: 编译依赖并创建虚拟环境
2. **运行阶段**: 最小化运行时镜像，仅包含必要组件

**优势**:
- 更小的镜像体积 (~500MB vs ~1.5GB)
- 更快的部署速度
- 减少攻击面

#### 安全特性

- **非 root 用户**: 以 `appuser` (UID 1000) 运行
- **只读文件系统**: 可选的只读根文件系统
- **资源限制**: 配置 CPU 和内存限制
- **网络隔离**: 沙箱容器无网络访问
- **安全选项**: 启用 `no-new-privileges`

### 资源管理

#### 资源限制

docker-compose.yml 中的默认资源限制：

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

根据工作负载调整：

- **轻度使用**: 0.5 CPU, 512MB RAM
- **正常使用**: 1.0 CPU, 1GB RAM
- **重度使用**: 2.0 CPU, 2GB RAM
- **AI 模型推理**: 4.0 CPU, 4GB RAM

#### 存储管理

监控数据卷使用情况：

```bash
# 列出数据卷
docker volume ls | grep ai-powershell

# 检查数据卷详情
docker volume inspect ai-powershell-logs

# 检查数据卷大小
docker system df -v
```

清理旧数据：

```bash
# 删除所有数据卷（警告：会删除所有数据）
docker-compose down -v

# 清理前备份数据卷
docker run --rm -v ai-powershell-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/data-backup.tar.gz -C /data .
```

### 健康检查

容器包含健康检查：

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app'); from src.main import PowerShellAssistant; print('healthy')" || exit 1
```

检查健康状态：

```bash
# 查看健康状态
docker ps

# 检查健康详情
docker inspect ai-powershell-assistant | jq '.[0].State.Health'

# 手动执行健康检查
docker exec ai-powershell-assistant \
  python -c "from src.main import PowerShellAssistant; print('healthy')"
```

### 日志管理

#### 日志配置

配置日志轮转：

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

#### 查看日志

```bash
# 查看所有日志
docker-compose logs

# 跟踪日志
docker-compose logs -f

# 查看特定服务
docker-compose logs ai-powershell

# 查看最后 100 行
docker-compose logs --tail=100
```

### Docker 故障排除

#### 容器无法启动

1. 检查日志：
```bash
docker-compose logs ai-powershell
```

2. 验证配置：
```bash
docker-compose config
```

3. 检查资源可用性：
```bash
docker system df
docker stats
```

#### PowerShell 未找到

验证容器中的 PowerShell 安装：

```bash
docker exec ai-powershell-assistant pwsh --version
```

如果缺失，重新构建镜像：

```bash
docker-compose build --no-cache
```

#### 权限问题

确保数据卷具有正确的权限：

```bash
# 修复数据卷权限
docker exec -u root ai-powershell-assistant \
  chown -R appuser:appuser /app/logs /app/data
```

#### 内存不足

在 docker-compose.yml 中增加内存限制：

```yaml
deploy:
  resources:
    limits:
      memory: 4G  # 从 2G 增加
```

---

## CI/CD 配置

### 概述

本项目实施了完整的持续集成和持续部署（CI/CD）流程，确保代码质量、测试覆盖率和安全性。

### GitHub Actions 工作流

#### 主 CI 工作流

**文件**: `.github/workflows/ci.yml`

**功能**:
- 多平台测试（Ubuntu、Windows、macOS）
- 多 Python 版本测试（3.8、3.9、3.10、3.11）
- 自动安装 PowerShell Core
- 运行完整测试套件
- 生成覆盖率报告
- 上传到 Codecov

**触发条件**:
- 推送到 `main` 或 `develop` 分支
- 针对 `main` 或 `develop` 的 Pull Request
