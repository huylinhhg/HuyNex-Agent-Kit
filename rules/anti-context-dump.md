# Chưng Cất Ngữ Nghĩa & Chống Ngáo Ngữ Cảnh (Semantic Distillation / Anti-Context-Dump)

## 1. Vấn Đề Lãng Phí Token & Ngáo Context (Context Degradation)
Khi làm việc với các hệ thống lớn, việc đọc toàn bộ file log khổng lồ (vài chục MB), xả nguyên dữ liệu API thô (raw dump từ Figma, Database, OpenAPI spec) vào context của LLM sẽ dẫn đến:
1. **Lãng phí chi phí & hạn ngạch token (Token Drain)**: Đốt hàng trăm nghìn token vô ích.
2. **Suy giảm chất lượng suy luận (Needle in a Haystack degradation)**: Khiến mô hình bị phân tâm, bỏ sót thông tin quan trọng.
3. **Ảo giác dữ liệu**: Do bị ngập trong dữ liệu rác không liên quan.

## 2. Tiêu Chuẩn Chưng Cất Cục Bộ (Local Semantic Distillation)
Trước khi nạp dữ liệu lớn vào Agent:
- **Công cụ chuẩn hóa toàn hệ sinh thái (`huynex-distill`)**: Khi chạy kiểm thử (`npm test`, `cargo test`, `vitest`, `pytest`) hoặc xem thay đổi (`git diff`), BẮT BUỘC bọc qua `huynex-distill` (hoặc alias `ndistill`) để cắt giảm 60% – 98% token rác:
  ```bash
  huynex-distill -- npm test
  huynex-distill -- git diff
  ```
- **Cổng Bảo toàn Tuyệt đối (Conservation Gate)**: Công cụ tự động bảo toàn 100% stack trace, lỗi logic và mã thoát exit code; tự động fallback về raw nếu nghi ngờ thất thoát lỗi.
- **Tìm hẹp trước khi đọc rộng**: Định vị chính xác symbol/hàm cần sửa thay vì đọc cả file 2.000 dòng.
- **Tóm tắt log lỗi**: Chỉ trích xuất stacktrace liên quan trực tiếp đến nguyên nhân gốc rễ, cắt bỏ hàng nghìn dòng thông báo info vô thưởng vô phạt.
