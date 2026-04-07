<!-- 文档类型: 运维指南 | 最后更新: 2025-01-17 | 维护者: 项目团队 -->

# 部署运维完整指南

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




