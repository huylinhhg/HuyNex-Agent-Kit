# Bài học: Ranh giới An toàn cho Vòng lặp Tái tạo Mã nguồn (Recompilation Feedback Loop)

- **Ngày ghi nhận**: 23/11/2026
- **Phạm vi**: Dự án dịch ngược `rea`, các công cụ phân tích nhị phân (binary analysis) và mô hình AI sinh mã biên dịch tự động trong hệ sinh thái HuyNex.
- **Nguồn**: Thực nghiệm Research Spike `reconstruct_poc.py` (cảm hứng từ `Dryxio/reagent`).

---

## 1. Vấn đề thực tế (Problem Statement)

1. **Rủi ro An ninh khi chạy Compiler Tự động (Code Execution Risk)**:
   - Cơ chế tự động gọi trình biên dịch (`clang`, `gcc`, `rustc`) trên mã C/Rust do LLM sinh ra trực tiếp trên máy chủ/máy trạm không có sandbox tiềm ẩn nguy cơ bảo mật nghiêm trọng:
     - Khai thác lỗ hổng parser của compiler.
     - Macro expansion vô hạn gây cạn kiệt bộ nhớ RAM / CPU DoS.
     - Tự động nạp các tệp header độc hại hoặc thực thi script build.

2. **Bẫy Đốt Token do Sai lệch Cảnh báo Trình biên dịch (Warning Loop)**:
   - Các cảnh báo chuyển đổi kiểu dữ liệu (`size_t` sang `int`, con trỏ khác signedness, thiếu thư viện chuẩn) trong cờ nghiêm ngặt `-Werror` sẽ khiến LLM phải chạy 3–5 vòng lặp sửa lỗi cho một hàm nhỏ, làm tăng chi phí token lên gấp 5 lần mà không chắc chắn hội tụ.

---

## 2. Ranh giới Kiến trúc Bắt buộc (The Guardrails)

1. **Chế độ Mặc định là Phân tích Tĩnh (Passive Analysis First)**:
   - Lõi của công cụ dịch ngược (như `rea`) phải tập trung vào việc đọc hiểu, trích xuất cấu trúc và giải mã ý định, KHÔNG tự động kích hoạt vòng lặp biên dịch ngầm trong các tác vụ thông thường.

2. **Yêu cầu Sandbox Bắt buộc cho Recompilation Loop**:
   - Tính năng Reconstruct chỉ được cung cấp dưới dạng lệnh người dùng chủ động chọn (`opt-in`), ví dụ: `rea reconstruct --sandbox`.
   - BẮT BUỘC phải thực thi bên trong môi trường cách ly (Container Docker / chroot / isolate), giới hạn cứng CPU thời gian (Timeout $\le 10$ giây/lần biên dịch) và tối đa 3 vòng lặp/hàm.
   - Nghiêm cấm mọi tiến trình AI tự động gọi compiler hệ thống mà không có sự kiểm soát của người dùng.
