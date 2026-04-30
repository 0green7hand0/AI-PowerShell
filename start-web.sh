#!/bin/bash
# AI PowerShell Web UI 启动脚本 (Linux/macOS)
# 同时启动前端和后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 显示标题
echo -e "${CYAN}========================================"
echo -e "  AI PowerShell Web UI 启动脚本"
echo -e "========================================${NC}\n"

# 检查是否在项目根目录
if [ ! -d "web-ui" ]; then
    echo -e "${RED}❌ 错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 1. 检查 Python
echo -e "${YELLOW}📋 检查 Python 环境...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ 错误: 未找到 Python，请先安装 Python 3.8+${NC}"
    exit 1
fi

# 2. 检查 Node.js
echo -e "\n${YELLOW}📋 检查 Node.js 环境...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ 错误: 未找到 Node.js，请先安装 Node.js${NC}"
    exit 1
fi

# 3. 检查 Docker (可选)
echo -e "\n${YELLOW}📋 检查 Docker 状态...${NC}"
if command -v docker &> /dev/null; then
    if docker ps &> /dev/null; then
        echo -e "${GREEN}✅ Docker: 运行中 (沙箱功能可用)${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker: 未运行 (沙箱功能不可用)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Docker: 未安装 (沙箱功能不可用)${NC}"
fi

# 4. 检查后端依赖
echo -e "\n${YELLOW}📋 检查后端依赖...${NC}"
if [ ! -d "web-ui/backend/venv" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    cd web-ui/backend
    $PYTHON_CMD -m venv venv
    cd ../..
fi

# 5. 检查前端依赖
echo -e "\n${YELLOW}📋 检查前端依赖...${NC}"
if [ ! -d "web-ui/node_modules" ]; then
    echo -e "${YELLOW}⚠️  前端依赖未安装，正在安装...${NC}"
    cd web-ui
    npm install
    cd ..
    echo -e "${GREEN}✅ 前端依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ 前端依赖已安装${NC}"
fi

# 创建日志目录
mkdir -p logs

# 6. 启动后端服务
echo -e "\n${CYAN}🚀 启动后端服务...${NC}"
cd web-ui/backend
source venv/bin/activate
$PYTHON_CMD app.py > ../../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ../..
echo -e "${GREEN}✅ 后端服务启动中... (PID: $BACKEND_PID)${NC}"
echo -e "   后端地址: http://localhost:5000"

# 等待后端启动
echo -e "\n${YELLOW}⏳ 等待后端服务启动...${NC}"
sleep 5

# 检查后端是否启动成功
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务启动成功${NC}"
else
    echo -e "${YELLOW}⚠️  后端服务可能还在启动中...${NC}"
fi

# 7. 启动前端服务
echo -e "\n${CYAN}🚀 启动前端服务...${NC}"
cd web-ui
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✅ 前端服务启动中... (PID: $FRONTEND_PID)${NC}"
echo -e "   前端地址: http://localhost:5173"

# 等待前端启动
echo -e "\n${YELLOW}⏳ 等待前端服务启动...${NC}"
sleep 8

# 8. 显示启动信息
echo -e "\n${CYAN}========================================"
echo -e "  🎉 服务启动完成！"
echo -e "========================================${NC}"
echo -e "\n📍 访问地址:"
echo -e "   前端: ${CYAN}http://localhost:5173${NC}"
echo -e "   后端: ${CYAN}http://localhost:5000${NC}"
echo -e "\n📊 进程信息:"
echo -e "   后端 PID: $BACKEND_PID"
echo -e "   前端 PID: $FRONTEND_PID"
echo -e "\n📝 日志文件:"
echo -e "   后端: logs/backend.log"
echo -e "   前端: logs/frontend.log"
echo -e "\n💡 提示:"
echo -e "   - 查看后端日志: tail -f logs/backend.log"
echo -e "   - 查看前端日志: tail -f logs/frontend.log"
echo -e "   - 停止所有服务: kill $BACKEND_PID $FRONTEND_PID"
echo -e "\n${CYAN}========================================${NC}\n"

# 保存 PID 到文件
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

echo -e "${GREEN}✅ 启动脚本执行完成${NC}"
echo -e "${YELLOW}💡 服务在后台运行，使用以下命令停止:${NC}"
echo -e "   ./stop-web.sh"
