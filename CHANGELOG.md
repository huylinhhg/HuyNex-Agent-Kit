# Changelog

Tất cả các thay đổi đáng chú ý của dự án **HuyNex Agent Kit** sẽ được ghi lại trong tệp này.
Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/) và tuân thủ [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-03

### 🚀 Added
- **5 Kỹ năng AI chuẩn Agent Skills (.agents/skills/)**:
  - `skill-creator`: Framework thiết kế, xây dựng và sinh kiểm thử tự động cho skill mới.
  - `skill-reviewer`: Tiêu chuẩn thẩm định 100 điểm, bảo mật và token economy.
  - `agent-rule-creator`: Phân cấp 3 tầng quy tắc và chống phình to context.
  - `office-openxml-guard`: Xử lý tài liệu Office ECMA-376 chống lỗi hỏng file và tối ưu cuộn bảng biểu.
  - `diagnosing-bugs`: Vòng lặp phản hồi chặt chẽ cho các lỗi khó và sụt giảm hiệu năng.
- **5 Quy tắc vận hành Agent cốt lõi (rules/)**:
  - `ladder-of-laziness.md`: Thang 7 nấc kỹ sư tối giản (Ponytail standard).
  - `verification-gate.md`: Cổng kiểm chứng thực tế & chống lệch hướng (Anti-Drift).
  - `single-root-safety.md`: Bảo vệ cội nguồn workspace và cấm lệnh xóa đệ quy.
  - `board-approval-gate.md`: Cơ chế phân định 3 cấp độ phê duyệt hệ thống.
  - `anti-context-dump.md`: Chưng cất ngữ nghĩa cục bộ tiết kiệm 10x–80x token.
- **2 Bài học thực chiến đã kiểm chứng (lessons/)**:
  - Kỹ sư tối giản và Thang 7 nấc lười biếng.
  - Quy chuẩn xử lý tài liệu Office chống lỗi unreadable content.
- **Bộ công cụ dòng lệnh (scripts/)**:
  - `install.py`: Trình cài đặt đa nền tảng (macOS, Windows, Linux) hỗ trợ dry-run và backup an toàn.
  - `validate.py`: Bộ kiểm toán tĩnh và quét sạch PII/Secrets.
- **Adapters**: Cấu hình tương thích cho Codex, Claude Code, Antigravity và Cursor.
