#!/usr/bin/env bash
# ==============================================================================
# HuyNex Agent Kit — Universal One-Line Installer (macOS & Linux)
# Usage: curl -fsSL https://raw.githubusercontent.com/huylinhhg/HuyNex-Agent-Kit/main/install.sh | bash
# ==============================================================================

set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}${BOLD}"
echo "  _    _             _   _            "
echo " | |  | |           | \ | |           "
echo " | |__| |_   _ _   _|  \| | _____  __ "
echo " |  __  | | | | | | | . \` |/ _ \ \/ / "
echo " | |  | | |_| | |_| | |\  |  __/>  <  "
echo " |_|  |_|\__,_|\__, |_| \_|\___/_/\_\ "
echo "                __/ |                 "
echo "               |___/   AGENT KIT      "
echo -e "${NC}"
echo -e "${BOLD}Hệ thống Kỹ năng & Quy tắc AI Agent Chuẩn Mở (macOS/Linux Installer)${NC}"
echo "------------------------------------------------------------------"

# 1. Kiểm tra Python
if command -v python3 >/dev/null 2>&1; then
    PY_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PY_BIN="python"
else
    echo -e "${RED}Lỗi: Không tìm thấy Python. Vui lòng cài đặt Python 3 trước.${NC}" >&2
    exit 1
fi

# 2. Kiểm tra Git
if ! command -v git >/dev/null 2>&1; then
    echo -e "${RED}Lỗi: Không tìm thấy Git. Vui lòng cài đặt Git trước.${NC}" >&2
    exit 1
fi

INSTALL_DIR="${HOME}/.huynex/agent-kit"
REPO_URL="https://github.com/huylinhhg/HuyNex-Agent-Kit.git"

echo -e "${BLUE}▶ [1/3] Đang đồng bộ kho mã nguồn HuyNex Agent Kit...${NC}"
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "  → Cập nhật bản mới nhất tại $INSTALL_DIR"
    git -C "$INSTALL_DIR" pull --ff-only origin main
else
    echo "  → Tải bản mới nhất về $INSTALL_DIR"
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

# 3. Kích hoạt cài đặt qua Python Lifecycle Engine
echo -e "${BLUE}▶ [2/3] Đang cài đặt Kỹ năng, 9 Modules Quy tắc và Hard Guardrails...${NC}"
"$PY_BIN" "$INSTALL_DIR/scripts/install.py" --all

# 4. Xác minh hệ thống qua Doctor
echo ""
echo -e "${BLUE}▶ [3/3] Đang xác minh tính toàn vẹn hệ thống (Doctor)...${NC}"
"$PY_BIN" "$INSTALL_DIR/scripts/install.py" --doctor

echo ""
echo -e "${GREEN}${BOLD}🎉 CÀI ĐẶT HOÀN TẤT THÀNH CÔNG!${NC}"
echo "------------------------------------------------------------------"
echo "Từ giờ AI Coding Agents của bạn (Claude Code, Codex, Antigravity, Cursor)"
echo "đã được trang bị đầy đủ 9 modules kỷ luật thép và rào chắn an toàn."
echo "Khởi động lại Agent để bắt đầu trải nghiệm!"
