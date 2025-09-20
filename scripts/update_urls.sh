#!/bin/bash
# 更新项目中的占位符网址脚本
# 使用方法: ./scripts/update_urls.sh [您的GitHub用户名] [项目名称]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
AI PowerShell 助手网址更新脚本

使用方法:
  $0 [GitHub用户名] [项目名称]

示例:
  $0 myusername ai-powershell-assistant
  $0 mycompany powershell-ai-helper

参数说明:
  GitHub用户名: 您的 GitHub 用户名或组织名
  项目名称:     您的项目仓库名称

注意:
  - 此脚本会更新所有文档中的占位符网址
  - 建议在运行前备份项目文件
  - 运行后请检查更新结果

EOF
}

# 检查参数
if [ $# -eq 0 ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

if [ $# -ne 2 ]; then
    log_error "参数数量不正确"
    show_help
    exit 1
fi

GITHUB_USER="$1"
PROJECT_NAME="$2"

# 验证参数
if [[ ! "$GITHUB_USER" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    log_error "GitHub用户名格式不正确: $GITHUB_USER"
    exit 1
fi

if [[ ! "$PROJECT_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    log_error "项目名称格式不正确: $PROJECT_NAME"
    exit 1
fi

# 定义新的网址
NEW_REPO_URL="https://github.com/${GITHUB_USER}/${PROJECT_NAME}.git"
NEW_RAW_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${PROJECT_NAME}/main"
NEW_ISSUES_URL="https://github.com/${GITHUB_USER}/${PROJECT_NAME}/issues"
NEW_DISCUSSIONS_URL="https://github.com/${GITHUB_USER}/${PROJECT_NAME}/discussions"
NEW_DOCS_URL="https://github.com/${GITHUB_USER}/${PROJECT_NAME}/docs"

log_info "开始更新项目网址..."
log_info "GitHub用户: $GITHUB_USER"
log_info "项目名称: $PROJECT_NAME"
log_info "新仓库地址: $NEW_REPO_URL"

# 备份原始文件
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
log_info "创建备份目录: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# 需要更新的文件列表
FILES_TO_UPDATE=(
    "README.md"
    "中文项目说明.md"
    "learning/中文学习指南.md"
    "docs/user/installation.md"
    "docs/faq/README.md"
    "scripts/install.sh"
    "scripts/install.ps1"
    "setup.py"
)

# 备份文件
for file in "${FILES_TO_UPDATE[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        log_info "已备份: $file"
    fi
done

# 更新文件中的网址
update_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        log_warning "文件不存在，跳过: $file"
        return
    fi
    
    log_info "更新文件: $file"
    
    # 使用 sed 替换占位符网址
    sed -i.bak \
        -e "s|https://github.com/your-org/ai-powershell-assistant.git|$NEW_REPO_URL|g" \
        -e "s|https://raw.githubusercontent.com/your-org/ai-powershell-assistant/main|$NEW_RAW_URL|g" \
        -e "s|https://github.com/your-org/ai-powershell-assistant/issues|$NEW_ISSUES_URL|g" \
        -e "s|https://github.com/your-org/ai-powershell-assistant/discussions|$NEW_DISCUSSIONS_URL|g" \
        -e "s|https://github.com/your-org/ai-powershell-assistant/docs|$NEW_DOCS_URL|g" \
        -e "s|https://github.com/your-org/ai-powershell-assistant|https://github.com/${GITHUB_USER}/${PROJECT_NAME}|g" \
        "$file"
    
    # 删除 sed 创建的备份文件
    rm -f "${file}.bak"
}

# 更新所有文件
for file in "${FILES_TO_UPDATE[@]}"; do
    update_file "$file"
done

# 验证更新结果
log_info "验证更新结果..."
REMAINING_PLACEHOLDERS=$(grep -r "your-org/ai-powershell-assistant" . --exclude-dir="$BACKUP_DIR" --exclude-dir=".git" 2>/dev/null | wc -l)

if [ "$REMAINING_PLACEHOLDERS" -eq 0 ]; then
    log_success "所有占位符网址已成功更新！"
else
    log_warning "仍有 $REMAINING_PLACEHOLDERS 个占位符未更新，请手动检查"
    grep -r "your-org/ai-powershell-assistant" . --exclude-dir="$BACKUP_DIR" --exclude-dir=".git" 2>/dev/null || true
fi

# 显示更新摘要
log_success "网址更新完成！"
echo
echo "更新摘要:"
echo "  GitHub用户: $GITHUB_USER"
echo "  项目名称: $PROJECT_NAME"
echo "  新仓库地址: $NEW_REPO_URL"
echo "  备份目录: $BACKUP_DIR"
echo
echo "下一步操作:"
echo "1. 检查更新后的文件内容"
echo "2. 测试安装脚本是否正常工作"
echo "3. 提交更改到Git仓库"
echo "4. 如有问题，可从备份目录恢复文件"

log_info "更新脚本执行完成！"