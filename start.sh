#!/bin/bash
# AI PowerShell 智能助手 - 启动脚本 (Linux/macOS)
# 自动检测并启动所有必要的服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 输出函数
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${CYAN}ℹ $1${NC}"; }

# 显示标题
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   AI PowerShell 智能助手 - 启动检测脚本       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
echo ""

# 1. 检查 Python
print_info "检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python 已安装: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    print_success "Python 已安装: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    print_error "Python 未安装或不在 PATH 中"
    print_warning "请安装 Python 3.8+ 后重试"
    exit 1
fi

# 2. 检查 Node.js (用于 Web UI)
print_info "检查 Node.js 环境..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js 已安装: $NODE_VERSION"
    SKIP_WEB_UI=false
else
    print_warning "Node.js 未安装，Web UI 将无法启动"
    SKIP_WEB_UI=true
fi

# 3. 检查 Ollama 服务
print_info "检查 Ollama AI 服务..."
if curl -s --connect-timeout 3 http://localhost:11434/api/version > /dev/null 2>&1; then
    OLLAMA_VERSION=$(curl -s http://localhost:11434/api/version | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    print_success "Ollama 服务运行中 (版本: $OLLAMA_VERSION)"
    
    # 检查模型
    print_info "检查已安装的 AI 模型..."
    MODELS=$(curl -s http://localhost:11434/api/tags)
    MODEL_COUNT=$(echo "$MODELS" | grep -o '"name"' | wc -l)
    
    if [ "$MODEL_COUNT" -gt 0 ]; then
        print_success "已安装 $MODEL_COUNT 个模型:"
        echo "$MODELS" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | while read -r model; do
            echo -e "  ${NC}• $model"
        done
        
        # 检查配置的模型
        CONFIG_MODEL="qwen3:30b"
        if echo "$MODELS" | grep -q "\"name\":\"$CONFIG_MODEL\""; then
            print_success "配置的模型 '$CONFIG_MODEL' 已就绪"
        else
            print_warning "配置的模型 '$CONFIG_MODEL' 未找到"
        fi
    else
        print_warning "未安装任何模型，请先安装模型"
        print_info "示例: ollama pull qwen3:30b"
    fi
else
    print_error "Ollama 服务未运行"
    print_warning "请先启动 Ollama 服务"
    print_info "macOS: 从应用程序启动 Ollama"
    print_info "Linux: systemctl start ollama 或 ollama serve"
    print_info "或访问: https://ollama.ai/download"
    
    read -p "是否继续启动项目? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${CYAN}════════════════════════════════════════════════${NC}"
echo ""

# 4. 询问启动模式
print_info "请选择启动模式:"
echo "  1. 仅启动命令行界面 (CLI)"
echo "  2. 仅启动 Web 界面"
echo "  3. 同时启动 CLI 和 Web 界面"
echo ""

read -p "请输入选项 (1-3): " choice

case $choice in
    1)
        # 启动 CLI
        print_info "启动命令行界面..."
        $PYTHON_CMD run.py
        ;;
    2)
        if [ "$SKIP_WEB_UI" = true ]; then
            print_error "Node.js 未安装，无法启动 Web UI"
            exit 1
        fi
        
        # 检查依赖
        print_info "检查 Web UI 依赖..."
        if [ ! -d "web-ui/node_modules" ]; then
            print_warning "Web UI 依赖未安装，正在安装..."
            cd web-ui
            npm install
            cd ..
        fi
        
        # 启动后端
        print_info "启动后端服务..."
        cd web-ui/backend
        $PYTHON_CMD app.py &
        BACKEND_PID=$!
        cd ../..
        sleep 3
        
        # 启动前端
        print_info "启动前端服务..."
        cd web-ui
        npm run dev
        
        # 清理
        kill $BACKEND_PID 2>/dev/null || true
        ;;
    3)
        if [ "$SKIP_WEB_UI" = true ]; then
            print_error "Node.js 未安装，无法启动 Web UI"
            print_info "将仅启动 CLI 模式"
            $PYTHON_CMD run.py
            exit 0
        fi
        
        # 检查依赖
        print_info "检查 Web UI 依赖..."
        if [ ! -d "web-ui/node_modules" ]; then
            print_warning "Web UI 依赖未安装，正在安装..."
            cd web-ui
            npm install
            cd ..
        fi
        
        # 启动后端
        print_info "启动后端服务..."
        cd web-ui/backend
        $PYTHON_CMD app.py &
        BACKEND_PID=$!
        cd ../..
        sleep 3
        
        # 启动前端
        print_info "启动前端服务..."
        cd web-ui
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        sleep 3
        
        # 启动 CLI
        print_info "启动命令行界面..."
        $PYTHON_CMD run.py
        
        # 清理
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
        ;;
    *)
        print_error "无效的选项"
        exit 1
        ;;
esac
