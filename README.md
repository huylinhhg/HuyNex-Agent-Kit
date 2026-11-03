# HuyNex Agent Kit — Hệ Thống Tri Thức & Quy Tắc AI Agent Dùng Chung

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version: 0.2.0](https://img.shields.io/badge/Version-0.2.0-green.svg)](VERSION)
[![Security: Clean](https://img.shields.io/badge/Secret_Scan-Clean-brightgreen.svg)](scripts/validate.py)

> **Mã nguồn mở độc lập thuộc hệ sinh thái HuyNex.**  
> Kho lưu trữ chuẩn mực (Canonical Source of Truth) về kỹ năng (Skills), quy tắc vận hành (Rules), bài học thực chiến (Lessons) và công cụ tự động hóa cho các AI Coding Agents hàng đầu thế giới (Codex, Claude Code, Antigravity, Cursor).

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

## 📦 Danh Mục 12 Kỹ Năng Chuẩn Mở (`.agents/skills/`)

### A. Bộ Kỹ Năng Nền Tảng & Quản Trị Agent (Core Metasills)
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

## 🛡️ Danh Mục Quy Tắc Vận Hành Cốt Lõi (`rules/`)

- `ladder-of-laziness.md`: Thang 7 nấc thẩm định code tối giản.
- `verification-gate.md`: Nguyên tắc kiểm chứng thực tế trước khi báo hoàn thành.
- `single-root-safety.md`: Bảo vệ cội nguồn workspace, cấm lệnh xóa đệ quy hủy diệt.
- `board-approval-gate.md`: Cơ chế phân cấp 3 tầng can thiệp hệ thống.
- `anti-context-dump.md`: Chưng cất ngữ nghĩa dữ liệu lớn tiết kiệm 10x–80x token.

---

## 📖 Kho Bài Học Thực Chiến Đã Kiểm Chứng (`lessons/`)

1. Quy chuẩn tạo và xử lý tài liệu Office chống lỗi unreadable content (ECMA-376).
2. Khắc phục lỗi mở file và đơ lag cuộn trang bảng biểu trong Word.
3. Kỹ sư tối giản và Thang 7 nấc lười biếng (Ponytail Standard).
4. Cơ chế tự động nhận diện tác vụ và chủ động đề xuất skill.
5. Chưng cất dữ liệu ngữ nghĩa và Cổng bảo toàn tuyệt đối.
6. Chuẩn hóa sample rate âm thanh số 48kHz và chốt chặn audio.
7. Tiêu chuẩn hợp đồng thiết kế `DESIGN.md` và chống rác AI.
8. Kịch bản tiếp thị thực chiến (Humanizer, Hook 3s, Direct-Response).
9. Kiến trúc đồng bộ kỹ năng AI Agent đa nền tảng.

---

## 🚀 Cài Đặt Nhanh Trong 30 Giây

Hỗ trợ tự động nhận diện cả macOS, Windows và Linux:

```bash
# Clone kho tài nguyên
git clone https://github.com/huylinhhg/HuyNex-Agent-Kit.git
cd HuyNex-Agent-Kit

# Xem danh mục kỹ năng hiện có
python3 scripts/install.py --list

# Xem trước các thay đổi (Dry-run không ghi đè)
python3 scripts/install.py --all --check

# Cài đặt chính thức vào toàn bộ AI clients (Codex, Claude, Antigravity)
python3 scripts/install.py --all
```

---

## 📄 Bản Quyền & Giấy Phép
Phát hành theo giấy phép [MIT License](LICENSE).
Thuộc quyền sở hữu trí tuệ của hệ sinh thái **HuyNex** (2026).
