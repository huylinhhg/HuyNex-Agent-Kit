# HuyNex Agent Kit — Hệ Thống Kỹ Năng & Quy Tắc Quản Trị AI Agent Chuẩn Mở

[![CI](https://github.com/huylinhhg/HuyNex-Agent-Kit/actions/workflows/ci.yml/badge.svg)](https://github.com/huylinhhg/HuyNex-Agent-Kit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version: 0.3.6](https://img.shields.io/badge/Version-0.3.6-green.svg)](VERSION)
[![Platform: macOS | Linux | Windows](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-orange.svg)](#)

[ [English](README.md) | **Tiếng Việt** ]

> **Hệ thống quản trị chất lượng cao, rào chắn an toàn xác định (Deterministic Guardrails) và bộ chưng cất ngữ nghĩa token cho các AI Coding Agents** (Claude Code, OpenAI Codex, Google Antigravity, Cursor).

---

## ⚡ Cài Đặt Nhanh — 1 Dòng Lệnh

Cài đặt tự động Kỹ năng, 9 Modules Quy tắc và Chốt chặn an toàn vào máy tính trong 3 giây:

### macOS & Linux
```bash
curl -fsSL https://raw.githubusercontent.com/huylinhhg/HuyNex-Agent-Kit/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/huylinhhg/HuyNex-Agent-Kit/main/install.ps1 | iex
```

Hoặc tải về và cài đặt thủ công:
```bash
git clone https://github.com/huylinhhg/HuyNex-Agent-Kit.git
cd HuyNex-Agent-Kit
python3 scripts/install.py --all
```

---

## 🌟 4 Trụ Cột Kỹ Thuật

1. **Rào chắn Xác định thay vì Cầu xin Prompt (Deterministic Guardrails)**:
   Thay vì chỉ viết câu nhắc khuyên AI "đừng force-push", hệ thống sử dụng hook `PreToolUse` chặn đứng ngay tại cửa Terminal các lệnh nguy hiểm (`git push --force`, `rm -rf`, `git reset --hard`) trước khi máy tính kịp thực thi.
2. **Chưng cất Ngữ nghĩa Token (`huynex-distill`)**:
   Lọc sạch các log kiểm thử dài dòng (`npm test`, `pytest`) và `git diff`, giúp cắt giảm từ **60% đến 95%** lượng token rác nạp vào AI nhưng vẫn giữ nguyên vẹn 100% stack trace lỗi.
3. **Thang 7 Nấc Thẩm Định Code (Senior Dev's Ladder of Laziness)**:
   Đoạn code tốt nhất là đoạn code không bao giờ phải viết. Ép AI tuân thủ: *YAGNI → Tái sử dụng → Thư viện chuẩn → Nền tảng Native → Dependency sẵn có → Tối giản dòng code → Sửa nhỏ nhất*.
4. **Cổng Bảo Toàn Dữ Liệu (The Conservation Gate)**:
   Không có gì biến mất trong im lặng. Mọi quá trình bóc tách dữ liệu đều được đối chiếu mã băm và số lượng thực thể, đảm bảo không bao giờ nuốt mất thông tin quan trọng.

---

## 🛡️ Kiến Trúc 9 Modules Quy Tắc (`rules/modules/`)

Tách biệt thành các module chuyên biệt, tương thích cú pháp `@import` của Claude Code:

| Module | Tên tệp | Nội dung trọng tâm |
|---|---|---|
| **01** | `01-communication.md` | Tính trung thực kỹ thuật (Brutal Honesty), Phả hệ mục tiêu (Goal Ancestry), Tự động đồng bộ Git đơn tầng. |
| **02** | `02-truth-context.md` | Chống đoán mò số liệu (Zero-Guessing), Chưng cất ngữ nghĩa, Cổng bảo toàn dữ liệu. |
| **03** | `03-code-engineering.md` | Thang 7 nấc thẩm định code, Tiêu chuẩn AGENTS.md, Hợp đồng thiết kế giao diện (DESIGN.md). |
| **04** | `04-data-safety.md` | Phê duyệt 3 cấp Hội đồng Quản trị (Board Approval Gate), Bảo vệ cội nguồn Workspace (Single-Root Safety). |
| **05** | `05-verification.md` | Tiêu chuẩn kiểm chứng theo rủi ro, nghiêm cấm bịa đặt trạng thái hoàn thành. |
| **06** | `06-collaboration.md` | Phân quyền điều phối subagent, tối ưu hóa lựa chọn model AI. |
| **07** | `07-permissions-memory.md` | Bảo vệ thông tin xác thực (Credentials/Secrets), ranh giới bộ nhớ cá nhân. |
| **08** | `08-versioning.md` | Quản lý phiên bản chuẩn SemVer 2.0.0 và Keep a Changelog. |
| **09** | `09-workspace-layout.md` | Bố cục workspace chuẩn đa nền tảng, Tiêu chuẩn máy trạm tinh gọn (Power-User Zero-Bloat). |

---

## 🔬 Benchmark Thực Nghiệm: Tiết Kiệm Token

Đo lường bằng bộ dữ liệu kiểm thử thực tế có thể tái hiện:

| Tác vụ | Dung lượng Gốc (Tokens) | Sau Chưng Cất (Tokens) | Tỷ lệ Tiết Kiệm | Khả năng Giữ Lỗi |
|---|---|---|---|---|
| **Bộ test Vitest (120 tests)** | 6.376 chars (~1.594) | 284 chars (~71) | **95.5%** | **100% (4/4 lỗi giữ nguyên)** |
| **Git Diff (5 file thay đổi)** | 5.966 chars (~1.491) | 1.736 chars (~434) | **70.9%** | **100% (Toàn bộ thay đổi giữ nguyên)** |

Tự chạy kiểm chứng trên máy:
```bash
./bin/huynex-distill --benchmark

# Chưng cất log test từ đường ống:
npm test | ./bin/huynex-distill

# Chưng cất git diff từ đường ống:
git diff | ./bin/huynex-distill --diff
```

---

## 🧰 Bộ Lệnh Quản Trị Vòng Đời

```bash
# Kiểm tra sức khỏe hệ thống và tình trạng đăng ký hook
python3 scripts/install.py --doctor

# Xem trước các thay đổi mà không ghi vào ổ đĩa (Dry-run)
python3 scripts/install.py --check

# Gỡ cài đặt an toàn toàn bộ các file do HuyNex Agent Kit quản lý
python3 scripts/install.py --uninstall

# Chốt đối chiếu tiêu chí nghiệm thu trước khi bàn giao
python3 scripts/spec_gate.py TASK.md --json
```

---

## 📄 Bản Quyền & Giấy Phép (License)

Dự án được phân phối dưới giấy phép **MIT License**. Tự do sử dụng, tùy biến cho cá nhân và thương mại.
