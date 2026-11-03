# Bài học: Chưng cất Dữ liệu Ngữ nghĩa (Data Distillation) và Cổng Bảo toàn Tuyệt đối (Conservation Gate)

- **Ngày ghi nhận**: 02/11/2026
- **Phạm vi**: Kiến trúc xử lý dữ liệu của Agent, thiết kế Tool/CLI/MCP, trích xuất tài liệu (Word, Excel, CAND, Code) trong toàn bộ hệ sinh thái HuyNex.
- **Nguồn**: Đúc kết từ kiến trúc thực chiến Enterprise Design Agent của Jang Trinh (`design:os`) và thực tế vận hành chống phình to context window.

---

## 1. Vấn đề thực tế (Problem Statement)

1. **Vấn nạn MCP-Dump (Xả rác vào Context Window)**:
   - Các công cụ MCP hoặc tích hợp API thông thường có xu hướng "xả" nguyên trạng dữ liệu JSON/XML thô (hàng chục ngàn dòng tọa độ, cấu trúc lồng nhau vô nghĩa, rác format) vào cửa sổ ngữ cảnh của LLM.
   - Hậu quả: Đốt sạch 100K - 200K tokens chỉ trong 1-2 lần gọi công cụ, chi phí tăng vọt, tốc độ suy luận chậm chạp và làm LLM bị "ngáo ngữ cảnh" (mất khả năng tập trung vào logic nghiệp vụ cốt lõi).

2. **Vấn nạn "Nuốt chửng dữ liệu ngầm" (Silent Data Loss)**:
   - Khi Agent xử lý khối lượng lớn tài liệu, bảng biểu, danh mục hoặc node phức tạp, AI thường có xu hướng "bỏ qua các trường khó" hoặc tự ý tóm tắt/cắt xén mà không báo cho người dùng, dẫn đến mất mát thông tin nghiêm trọng.

---

## 2. Hai Trụ cột Giải pháp Bắt buộc (The 2 Pillars)

### Trụ cột 1: Chưng cất Ngữ nghĩa Cục bộ (Semantic Distillation / Filter-First)
* **Quy tắc vàng**: *"Lọc sạch tại nguồn trước khi nạp vào AI"*.
* Tuyệt đối không để Agent đọc trực tiếp các luồng dữ liệu thô khổng lồ nếu chưa qua bộ lọc cục bộ (Local Distiller):
  - Viết các script xử lý nhanh (Python / Rust / Node.js) để bóc tách thô, loại bỏ các trường rác (metadata thừa, tọa độ hiển thị, wrapper lồng nhau).
  - Chỉ chuyển giao cho LLM các dữ liệu đã cô đọng thành **Semantic Tokens** (ý nghĩa thực tế, quan hệ thực thể, hợp đồng nghiệp vụ).
  - Tỷ lệ nén kỳ vọng: Giảm từ 10x đến 80x lượng token tiêu thụ mà vẫn bảo toàn 100% ngữ nghĩa.

### Trụ cột 2: Cổng Bảo toàn Tuyệt đối (Conservation Gate — "Nothing Vanishes Silently")
* **Quy tắc vàng**: *"Không có bất kỳ dữ liệu nào được phép biến mất trong im lặng"*.
* Khi thực hiện trích xuất, di chuyển hoặc chuyển đổi cấu trúc (như parse bảng biểu CAND, chuyển đổi định dạng tài liệu, đồng bộ mã nguồn):
  - BẮT BUỘC có cơ chế kiểm toán đầu vào và đầu ra bằng **Mã băm (`sourceHash`) hoặc Đếm số lượng thực thể (Entity Count / Checksum)**.
  - Nếu đầu vào có 50 mục mà đầu ra chỉ còn 48 mục (rơi rụng 2 mục do AI bỏ qua hoặc lỗi parse) -> BẮT BUỘC chốt chặn phải báo đỏ ngay lập tức (`FAIL_CONSERVATION`), dừng quy trình và thông báo cụ thể cho người dùng.
  - Tuyệt đối cấm AI tự ý bịa dữ liệu bù vào hoặc lẳng lặng nuốt mất dữ liệu khó.

---

## 3. Quy chuẩn Áp dụng trong HuyNex

1. **Với dữ liệu hành chính & tài liệu**: Khi bóc tách văn bản, báo cáo tuần, phân loại cán bộ, chỉ tiêu công tác: luôn đếm tổng số mục đầu vào và đối chiếu đầu ra trước khi kết luận hoàn thành.
2. **Với công cụ và CLI**: Ưu tiên viết script nén/tóm tắt logic trước khi gửi context cho Agent, giữ vững triết lý **Zero-Bloat** và **Senior Dev's Ladder of Laziness**.
