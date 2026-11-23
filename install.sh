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
echo -e "${BOLD}Hệ thống Kỹ năng & Quy tắc AI Agent Chuẩn Mở Top 1 Thế Giới${NC}"
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

echo -e "${BLUE}▶ Đang đồng bộ kho mã nguồn HuyNex Agent Kit...${NC}"
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "  → Cập nhật bản mới nhất tại $INSTALL_DIR"
    git -C "$INSTALL_DIR" pull --ff-only origin main
else
    echo "  → Tải bản mới nhất về $INSTALL_DIR"
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

# 3. Kích hoạt cài đặt qua Python Engine
echo -e "${BLUE}▶ Đang cài đặt Kỹ năng, 9 Modules Quy tắc và Hard Guardrails...${NC}"
"$PY_BIN" "$INSTALL_DIR/scripts/install.py" --all

# 4. Kích hoạt Hard Guardrail cho Claude Code nếu có ~/.claude
CLAUDE_DIR="${HOME}/.claude"
if [ -d "$CLAUDE_DIR" ]; then
    mkdir -p "$CLAUDE_DIR/hooks"
    cp "$INSTALL_DIR/scripts/guardrail.py" "$CLAUDE_DIR/hooks/guardrail.py"
    chmod +x "$CLAUDE_DIR/hooks/guardrail.py"
    
    # Cập nhật ~/.claude/settings.json
    "$PY_BIN" -c "
import json
from pathlib import Path
p = Path.home() / '.claude/settings.json'
try:
    data = json.loads(p.read_text()) if p.is_file() else {}
except Exception:
    data = {}
if 'hooks' not in data: data['hooks'] = {}
pre = data['hooks'].get('PreToolUse', [])
hook_cmd = 'python3 ' + str(Path.home() / '.claude/hooks/guardrail.py')
found = any('guardrail.py' in sub.get('command','') for h in pre if h.get('matcher')=='Bash' for sub in h.get('hooks',[]))
if not found:
    pre.append({'matcher':'Bash','hooks':[{'type':'command','command':hook_cmd}]})
    data['hooks']['PreToolUse'] = pre
    p.write_text(json.dumps(data, indent=2), encoding='utf-8')
"
    echo -e "  ${GREEN}✓ Đã kích hoạt Chốt chặn cứng Hard Git Guardrails trong ~/.claude/settings.json${NC}"
fi

echo ""
echo -e "${GREEN}${BOLD}🎉 CÀI ĐẶT HOÀN TẤT THÀNH CÔNG!${NC}"
echo "------------------------------------------------------------------"
echo "Từ giờ AI Coding Agents của bạn (Claude Code, Codex, Antigravity, Cursor)"
echo "đã được trang bị đầy đủ 9 modules kỷ luật thép và rào chắn an toàn."
echo "Khởi động lại Agent để bắt đầu trải nghiệm!"
