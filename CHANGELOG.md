# Changelog

Tất cả các thay đổi đáng chú ý của dự án **HuyNex Agent Kit** sẽ được ghi lại trong tệp này.
Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/) và tuân thủ [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-11-18

### 🚀 Added
- **7 Quy tắc Vận hành Đột phá cho AI Coding Agents (rules/)**:
  - `milestone-git-sync.md`: Giao thức tự động đồng bộ Git đơn tầng tinh gọn & Cổng bàn giao mốc hoàn chỉnh (Milestone Mutation Gate — chống Micro-Push Spam và bảo vệ hạn ngạch CI/CD).
  - `proactive-skill-routing.md`: Cơ chế nhận diện ý định & chủ động đề xuất quy trình (Zero-Memorization Standard — người dùng không cần nhớ lệnh slash hay tên thư viện).
  - `goal-ancestry-anti-drift.md`: Phả hệ mục tiêu & Chống lệch hướng trong hệ thống đa Agent (Multi-Agent Workflows — ràng buộc `root_goal`, `scope`, `acceptance_criteria`).
  - `zero-friction-design-contract.md`: Hợp đồng thiết kế giao diện tự động (`DESIGN.md`), triệt tiêu 100% "AI Slop" trong phát triển Frontend.
  - `project-scoped-skills.md`: Quy chuẩn phân tách kỹ năng chuyên biệt theo dự án (Two-Tier Skill Architecture — chống quá tải Context Window và token drain).
  - `conservation-gate.md`: Cổng bảo toàn dữ liệu tuyệt đối (Nothing Vanishes Silently — kiểm toán 2 lớp qua mã băm và số lượng thực thể).
  - `brutal-honesty.md`: Tính trung thực kỹ thuật khách quan (Anti-Sycophancy Standard — triệt tiêu hội chứng nịnh hót, dám cảnh báo rủi ro kiến trúc).

## [0.2.0] - 2026-11-03

### 🚀 Added
- **Tổng quát hóa 4 Kỹ năng Nhóm B (Generalization)**:
  - `shortform-production`: Sản xuất video ngắn 9:16 Top 1 (Hook 3s, CapCut dynamic kinetic motion, Anti-UI clipping safe zone, multi-layer ducking).
  - `shortform-editor`: Biên tập video ngắn 9:16, kịch bản Semantic Beats, căn khớp phụ đề Forced Alignment, nhạc nền Instrumental bản quyền.
  - `brandkit-system`: Hệ thống thiết kế nhận diện thương hiệu cao cấp (Brand Guidelines, editorial grid, logo system).
  - `stitch-design`: Hợp đồng thiết kế giao diện ngữ nghĩa (`DESIGN.md`), triệt tiêu AI Slop.
- **Đóng gói 3 Kỹ năng mới từ Bài học Nhóm D (Group D Lessons)**:
  - `proactive-agent-routing`: Tự động nhận diện bối cảnh và chủ động đề xuất quy trình (Zero-Memorization Standard).
  - `data-conservation-gate`: Cổng bảo toàn dữ liệu tuyệt đối qua mã băm và số lượng thực thể (Nothing Vanishes Silently).
  - `media-audio-gate`: Chốt chặn chuẩn hóa âm thanh số 48kHz, -14.5 dB LUFS và khử rè clipping.
- **Mở rộng kho bài học thực chiến (lessons/)**: Xuất khẩu 9 bài học kỹ thuật chuyên sâu đã khử trùng an toàn 100%.

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
- **Bộ công cụ dòng lệnh (scripts/)**:
  - `install.py`: Trình cài đặt đa nền tảng (macOS, Windows, Linux) hỗ trợ dry-run và backup an toàn.
  - `validate.py`: Bộ kiểm toán tĩnh và quét sạch PII/Secrets.
- **Adapters**: Cấu hình tương thích cho Codex, Claude Code, Antigravity và Cursor.
