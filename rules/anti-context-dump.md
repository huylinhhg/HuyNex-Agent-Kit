# Chưng Cất Ngữ Nghĩa & Chống Ngáo Ngữ Cảnh (Semantic Distillation / Anti-Context-Dump)

## 1. Vấn Đề Lãng Phí Token & Ngáo Context (Context Degradation)
Khi làm việc với các hệ thống lớn, việc đọc toàn bộ file log khổng lồ (vài chục MB), xả nguyên dữ liệu API thô (raw dump từ Figma, Database, OpenAPI spec) vào context của LLM sẽ dẫn đến:
1. **Lãng phí chi phí & hạn ngạch token (Token Drain)**: Đốt hàng trăm nghìn token vô ích.
2. **Suy giảm chất lượng suy luận (Needle in a Haystack degradation)**: Khiến mô hình bị phân tâm, bỏ sót thông tin quan trọng.
3. **Ảo giác dữ liệu**: Do bị ngập trong dữ liệu rác không liên quan.

## 2. Tiêu Chuẩn Chưng Cất Cục Bộ (Local Semantic Distillation)
Trước khi nạp dữ liệu lớn vào Agent:
- **Lọc cục bộ bằng script**: Dùng `grep`, `jq`, script Python hoặc công cụ dòng lệnh để nén và chắt lọc thành các **Semantic Tokens** tinh gọn (tiết kiệm 10x–80x token).
- **Tìm hẹp trước khi đọc rộng**: Định vị chính xác symbol/hàm cần sửa thay vì đọc cả file 2.000 dòng.
- **Tóm tắt log lỗi**: Chỉ trích xuất stacktrace liên quan trực tiếp đến nguyên nhân gốc rễ, cắt bỏ hàng nghìn dòng thông báo info vô thưởng vô phạt.
