#!/bin/bash
# AI PowerShell Web UI 停止脚本 (Linux/macOS)

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================"
echo -e "  停止 AI PowerShell Web UI"
echo -e "========================================${NC}\n"

# 读取 PID
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    echo -e "${YELLOW}🛑 停止后端服务 (PID: $BACKEND_PID)...${NC}"
    kill $BACKEND_PID 2>/dev/null && echo -e "${GREEN}✅ 后端服务已停止${NC}" || echo -e "${YELLOW}⚠️  后端服务未运行${NC}"
    rm logs/backend.pid
else
    echo -e "${YELLOW}⚠️  未找到后端 PID 文件${NC}"
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    echo -e "${YELLOW}🛑 停止前端服务 (PID: $FRONTEND_PID)...${NC}"
    kill $FRONTEND_PID 2>/dev/null && echo -e "${GREEN}✅ 前端服务已停止${NC}" || echo -e "${YELLOW}⚠️  前端服务未运行${NC}"
    rm logs/frontend.pid
else
    echo -e "${YELLOW}⚠️  未找到前端 PID 文件${NC}"
fi

# 清理可能残留的进程
echo -e "\n${YELLOW}🧹 清理残留进程...${NC}"
pkill -f "python.*app.py" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo -e "\n${GREEN}✅ 所有服务已停止${NC}\n"
