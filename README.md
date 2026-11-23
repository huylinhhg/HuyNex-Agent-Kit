# HuyNex Agent Kit — Hệ Thống Tri Thức & Quy Tắc AI Agent Dùng Chung

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version: 0.3.0](https://img.shields.io/badge/Version-0.3.0-green.svg)](VERSION)
[![Security: Clean](https://img.shields.io/badge/Secret_Scan-Clean-brightgreen.svg)](scripts/validate.py)
[![Platform: macOS | Windows | Linux](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-orange.svg)](#)

> **Mã nguồn mở độc lập thuộc hệ sinh thái HuyNex.**  
> Kho lưu trữ chuẩn mực (Canonical Source of Truth) về kỹ năng (Skills), quy tắc vận hành (Rules), bài học thực chiến (Lessons) và công cụ tự động hóa cho các AI Coding Agents hàng đầu thế giới (Claude Code, Codex, Antigravity, Cursor).

---

## ⚡ Quickstart — Cài đặt 1 dòng lệnh (One-Line Installer)

Cài đặt tự động toàn bộ Kỹ năng, 9 Modules Quy tắc và Hard Git Guardrails vào máy tính của bạn trong 3 giây:

**macOS & Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/huylinhhg/HuyNex-Agent-Kit/main/install.sh | bash
```

**Windows (PowerShell Run as Administrator hoặc User):**
```powershell
irm https://raw.githubusercontent.com/huylinhhg/HuyNex-Agent-Kit/main/install.ps1 | iex
```

---

## 🌟 Tôn Chỉ Kỹ Thuật (Philosophy)

1. **Dành Cho Mọi Lập Trình Viên & Người Dùng Bình Thường (Kind-Hearted Dev Standard)**:
   Chia sẻ an toàn 100%, dễ cài, dễ dùng, không rào cản. Tách biệt hoàn toàn khỏi mọi dữ liệu cá nhân hay nghiệp vụ đặc thù.
2. **Kỹ Sư Tối Giản (Senior Dev's Ladder of Laziness)**:
   Đoạn code xịn nhất là đoạn code không bao giờ phải viết. Triệt tiêu 100% tình trạng "AI Slop" và over-engineering.
3. **Tiêu Chuẩn Không Cần Ghi Nhớ (Zero-Memorization Proactive Routing)**:
   Người dùng chỉ cần nói ngôn ngữ tự nhiên bình thường; Agent tự động nhận diện bối cảnh và áp dụng công cụ chuẩn nhất.
4. **Cổng Kiểm Chứng Bắt Buộc (Verification Gate)**:
   Nghiêm cấm AI tuyên bố hoàn thành hoặc bịa đặt bằng chứng khi chưa chạy kiểm thử thực tế.

---

## 🛡️ Kiến Trúc 9 Modules Quy Tắc Chuẩn Mới (`rules/modules/`)

Hệ thống quy tắc được thiết kế theo chuẩn modular `@import` hiện đại của Anthropic, giúp file cấu hình gốc chỉ còn **32 dòng** và **tiết kiệm 71% token ngữ cảnh**:

| Module | Tên tệp | Nội dung trọng tâm |
|---|---|---|
| **01** | `01-communication.md` | Tính trung thực kỹ thuật (Brutal Honesty), Phả hệ mục tiêu (Goal Ancestry), Tự động đồng bộ Git đơn tầng (Git Auto-Sync). |
| **02** | `02-truth-context.md` | Chống ảo giác số liệu (Zero-Guessing), Chưng cất ngữ nghĩa (Semantic Distillation), Cổng bảo toàn dữ liệu (Conservation Gate). |
| **03** | `03-code-engineering.md` | Thang 7 nấc thẩm định code (Ladder of Laziness), Tiêu chuẩn AGENTS.md, Hợp đồng thiết kế (DESIGN.md), Chuẩn OpenXML ECMA-376. |
| **04** | `04-data-safety.md` | Cơ chế phê duyệt 3 cấp Hội đồng Quản trị (The Board Approval Gate), Bảo vệ cội nguồn Workspace (Single-Root Safety). |
| **05** | `05-verification.md` | Tiêu chuẩn kiểm chứng theo rủi ro, cấm bịa đặt trạng thái hoàn thành. |
| **06** | `06-collaboration.md` | Phân quyền điều phối subagent, tối ưu hóa lựa chọn model AI. |
| **07** | `07-permissions-memory.md` | Bảo vệ thông tin xác thực (Credentials/Secrets), ranh giới bộ nhớ cá nhân. |
| **08** | `08-versioning.md` | Quản lý phiên bản chuẩn SemVer 2.0.0 và Keep a Changelog. |
| **09** | `09-workspace-layout.md` | Bố cục workspace chuẩn đa nền tảng, Tiêu chuẩn máy trạm tinh gọn (Power-User Zero-Bloat). |

---

## 🚀 Bộ Ba Vũ Khí Bảo Vệ Mới (The Triple Armor)

### 1. Chốt Chặn Cứng Cấp Hệ Điều Hành (Hard Git Guardrails)
Tự động kích hoạt thông qua `scripts/guardrail.py` kết nối trực tiếp vào hook `PreToolUse` của Claude Code:
* Tự động chặn đứng ngay tại cửa Terminal các lệnh nguy hiểm: `git push --force`, `git reset --hard`, `git clean -fd`, `git branch -D`.
* Cưỡng chế quy tắc **Single-Root Safety**: Bẻ gãy hoàn toàn các lệnh `rm -rf` trên thư mục gốc workspace hoặc thư mục cha, bảo vệ an toàn tuyệt đối cho ổ cứng.

### 2. Tiện Ích Chưng Cất Ngữ Nghĩa Cục Bộ (`huynex-distill`)
* Cắt tỉa 60% – 95% lượng token rác từ log kiểm thử (`npm test`, `pytest`) và `git diff` trước khi nạp vào AI Context.
* Chống tràn bộ nhớ ngữ cảnh và triệt tiêu nguy cơ "ngáo token" trong các phiên làm việc dài.

### 3. Chốt Đối Chiếu Tiêu Chí Nghiệm Thu (`huynex-spec-gate`)
* Tiện ích CLI tự động quét file `TASK.md` hoặc đề bài: Đối chiếu 100% mục checklist `- [ ]`, kiểm tra trạng thái Git sạch sẽ và tự động chạy test suite trước khi cho phép bàn giao nhiệm vụ.

---

## 📦 Danh Mục 12 Kỹ Năng Chuẩn Mở (`.agents/skills/`)

### A. Bộ Kỹ Năng Nền Tảng & Quản Trị Agent (Core Metaskills)
- **`skill-creator`**: Framework thiết kế, xây dựng và sinh kiểm thử tự động cho skill mới.
- **`skill-reviewer`**: Tiêu chuẩn thẩm định 100 điểm, bảo mật và token economy của skill.
- **`agent-rule-creator`**: Phân cấp 3 tầng quy tắc, chống mâu thuẫn nội tại và chống phình to context window.
- **`proactive-agent-routing`**: Cơ chế tự động nhận diện ý định và chủ động định tuyến tác vụ (Zero-Memorization).

### B. Bộ Kỹ Năng Kỹ Thuật & Kiến Trúc Dữ Liệu (Engineering & Data)
- **`diagnosing-bugs`**: Vòng lặp phản hồi chặt chẽ cho việc chẩn đoán nguyên nhân gốc rễ lỗi khó và sụt giảm hiệu năng.
- **`office-openxml-guard`**: Bộ quy chuẩn ECMA-376 triệt tiêu lỗi *"unreadable content"* và đơ giật 100% CPU khi mở/cuộn file Word, Excel, PowerPoint.
- **`data-conservation-gate`**: Cổng bảo toàn dữ liệu tuyệt đối (Nothing Vanishes Silently) bằng mã băm `sourceHash` và đếm thực thể.

### C. Bộ Kỹ Năng Thiết Kế & Nhận Diện Thị Giác (Design & Brand)
- **`stitch-design`**: Khởi tạo và quản trị file hợp đồng thiết kế giao diện (`DESIGN.md`), triệt tiêu AI Slop.
- **`brandkit-system`**: Hệ thống thiết kế nhận diện thương hiệu cao cấp (Brand Guidelines, editorial grid, logo system).

### D. Bộ Kỹ Năng Sản Xuất Video & Âm Thanh Đa Tầng (Media & Audio)
- **`shortform-production`**: Tự động sản xuất video ngắn 9:16 Top 1 (Hook 3s, CapCut dynamic spring motion, Safe zone chống tràn nút UI).
- **`shortform-editor`**: Biên tập video ngắn 9:16, kịch bản Semantic Beats, căn khớp phụ đề Forced Alignment, nhạc nền Instrumental bản quyền.
- **`media-audio-gate`**: Chốt chặn chuẩn hóa âm thanh số 48kHz, -14.5 dB LUFS và khử rè clipping.

---

## 📄 Bản Quyền & Giấy Phép (License)

Dự án được phân phối dưới giấy phép mã nguồn mở **MIT License**. Tự do sử dụng, tùy biến và tích hợp vào các dự án cá nhân hoặc thương mại.
