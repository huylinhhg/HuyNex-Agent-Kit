# HuyNex Agent Kit — Hệ Thống Tri Thức & Quy Tắc AI Agent Dùng Chung

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-green.svg)](VERSION)
[![Security: Clean](https://img.shields.io/badge/Secret_Scan-Clean-brightgreen.svg)](scripts/validate.py)

> **Mã nguồn mở độc lập thuộc hệ sinh thái HuyNex.**  
> Kho lưu trữ chuẩn mực (Canonical Source of Truth) về kỹ năng (Skills), quy tắc vận hành (Rules), bài học thực chiến (Lessons) và công cụ tự động hóa cho các AI Coding Agents hàng đầu thế giới (Codex, Claude Code, Antigravity, Cursor).

---

## 🌟 Tôn Chỉ Kỹ Thuật (Philosophy)

1. **Public-First đối với Tri thức Phổ quát — Private-by-Default đối với Dữ liệu Cá nhân**:
   Toàn bộ tri thức kỹ thuật được công khai 100% không chứa dữ liệu cá nhân, token hay thông tin định danh máy.
2. **Kỹ Sư Tối Giản (Senior Dev's Ladder of Laziness)**:
   Đoạn code xịn nhất là đoạn code không bao giờ phải viết. Triệt tiêu 100% tình trạng "AI Slop" và over-engineering.
3. **Cổng Kiểm Chứng Bắt Buộc (Verification Gate)**:
   Nghiêm cấm AI tuyên bố hoàn thành hoặc bịa đặt bằng chứng khi chưa chạy kiểm thử thực tế.

---

## 📦 Danh Mục Thành Phần

### 1. Kỹ Năng Chuẩn Mở (`.agents/skills/`)
- **`skill-creator`**: Framework thiết kế, xây dựng và sinh kiểm thử tự động cho skill mới.
- **`skill-reviewer`**: Bộ tiêu chuẩn 100 điểm thẩm định chất lượng, an toàn và token economy của skill.
- **`agent-rule-creator`**: Phân cấp 3 tầng quy tắc, chống mâu thuẫn nội tại và chống phình to context window.
- **`office-openxml-guard`**: Bộ quy chuẩn ECMA-376 triệt tiêu lỗi *"unreadable content"* và đơ giật 100% CPU khi mở/cuộn file Word, Excel, PowerPoint.
- **`diagnosing-bugs`**: Vòng lặp phản hồi chặt chẽ cho việc chẩn đoán nguyên nhân gốc rễ lỗi khó và sụt giảm hiệu năng.

### 2. Quy Tắc Vận Hành Cốt Lõi (`rules/`)
- `ladder-of-laziness.md`: Thang 7 nấc thẩm định code tối giản.
- `verification-gate.md`: Nguyên tắc kiểm chứng thực tế trước khi báo hoàn thành.
- `single-root-safety.md`: Bảo vệ cội nguồn workspace, cấm lệnh xóa đệ quy hủy diệt.
- `board-approval-gate.md`: Cơ chế phân cấp 3 tầng can thiệp hệ thống.
- `anti-context-dump.md`: Chưng cất ngữ nghĩa dữ liệu lớn tiết kiệm 10x–80x token.

### 3. Bài Học Thực Chiến (`lessons/`)
Các bài học sâu sắc rút ra từ những ca xử lý lỗi hỏng file và sụt giảm hiệu năng thực tế.

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

## 🛡️ Tích Hợp Hai Chiều Với ADOS Personal

HuyNex Agent Kit liên kết chặt chẽ với hệ điều hành cá nhân **ADOS** thông qua công cụ `promote.py`:
- **ADOS Cá nhân**: Giữ riêng tư dữ liệu công việc nội bộ, credentials và cấu hình máy.
- **Discovery & Promotion Engine**: Tự động phát hiện các cải tiến mới trong ADOS, quét sạch bí mật/định danh, tạo candidate và chỉ xuất bản sau khi **Huy phê duyệt thủ công (`approved_by: 'Huy'`)**.

---

## 📄 Bản Quyền & Giấy Phép
Phát hành theo giấy phép [MIT License](LICENSE).
Thuộc quyền sở hữu trí tuệ của hệ sinh thái **HuyNex** (2026).
