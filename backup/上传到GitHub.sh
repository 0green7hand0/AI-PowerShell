#!/bin/bash
# AI PowerShell 助手 GitHub 上传脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 AI PowerShell 助手 GitHub 上传脚本${NC}"
echo "=================================="

# 检查是否在正确的目录
if [ ! -f "中文项目说明.md" ]; then
    echo -e "${RED}❌ 错误：请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 检查 Git 状态
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📁 初始化 Git 仓库...${NC}"
    git init
fi

# 添加所有文件
echo -e "${YELLOW}📝 添加文件到 Git...${NC}"
git add .

# 检查是否有更改
if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️ 没有检测到文件更改${NC}"
else
    # 创建提交
    echo -e "${YELLOW}💾 创建提交...${NC}"
    git commit -m "🎉 AI PowerShell 智能助手完整项目

✨ 功能特性：
- 🤖 中文自然语言到 PowerShell 命令转换
- 🔒 三层安全保护（白名单+权限+沙箱）
- 🌐 跨平台支持（Windows/Linux/macOS）
- 📊 完整的审计日志和性能监控
- 🐳 Docker 和 Kubernetes 部署支持
- 📚 完整的中文文档和使用示例

🏗️ 项目结构：
- src/ - 核心源代码（6大组件）
- docs/ - 完整文档系统
- examples/ - 中文使用示例
- config/ - 配置模板和说明
- scripts/ - 安装和部署脚本
- k8s/ - Kubernetes 部署配置

📊 项目统计：
- 总文件数: 100+ 个文件
- 代码行数: 10,000+ 行
- 文档页数: 50+ 页中文文档
- 测试文件: 30+ 个测试文件"
fi

# 检查远程仓库
if ! git remote get-url origin >/dev/null 2>&1; then
    echo -e "${YELLOW}🔗 添加远程仓库...${NC}"
    git remote add origin https://github.com/0green7hand0/AI-PowerShell.git
fi

# 设置主分支
echo -e "${YELLOW}🌿 设置主分支...${NC}"
git branch -M main

# 推送到 GitHub
echo -e "${YELLOW}📤 推送到 GitHub...${NC}"
echo -e "${BLUE}正在上传到: https://github.com/0green7hand0/AI-PowerShell${NC}"

if git push -u origin main; then
    echo -e "${GREEN}✅ 上传成功！${NC}"
    echo ""
    echo -e "${GREEN}🎉 项目已成功上传到 GitHub！${NC}"
    echo ""
    echo "📋 下一步操作："
    echo "1. 访问 https://github.com/0green7hand0/AI-PowerShell 查看项目"
    echo "2. 添加项目描述和标签"
    echo "3. 测试在线安装脚本"
    echo "4. 创建第一个 Release"
    echo ""
    echo "🔗 项目链接："
    echo "- 仓库地址: https://github.com/0green7hand0/AI-PowerShell"
    echo "- 问题报告: https://github.com/0green7hand0/AI-PowerShell/issues"
    echo "- 讨论交流: https://github.com/0green7hand0/AI-PowerShell/discussions"
    echo ""
    echo "🚀 现在用户可以使用以下命令安装："
    echo "git clone https://github.com/0green7hand0/AI-PowerShell.git"
else
    echo -e "${RED}❌ 上传失败${NC}"
    echo ""
    echo "可能的原因："
    echo "1. 网络连接问题"
    echo "2. GitHub 认证问题"
    echo "3. 仓库权限问题"
    echo ""
    echo "解决方案："
    echo "1. 检查网络连接"
    echo "2. 配置 GitHub 认证: git config --global user.name 'Your Name'"
    echo "3. 配置 GitHub 邮箱: git config --global user.email 'your.email@example.com'"
    echo "4. 设置 GitHub Token 或 SSH 密钥"
    exit 1
fi