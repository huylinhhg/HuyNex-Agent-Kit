# Bài học: Kiến trúc Bộ nhớ Phiên làm việc Tiến thoái (Progressive Disclosure Session Memory)

- **Ngày ghi nhận**: 08/11/2026
- **Phạm vi**: MaiHuyOS, ADOS, và toàn bộ luồng điều phối AI Agent trong HuyNex.
- **Nguồn**: Chắt lọc từ hiện tượng `claude-mem` trên GitHub Trending (loại bỏ hoàn toàn bloatware, SaaS trả phí và daemon nền, chuyển hóa thành chuẩn native local).

---

## 1. Bối cảnh
Các công cụ bộ nhớ agent thương mại hiện nay như `claude-mem` tạo ra tiếng vang lớn nhờ giải quyết điểm nghẽn "quên bối cảnh giữa các phiên". Tuy nhiên, việc cài đặt một worker chạy nền 24/7 và kết nối dịch vụ đám mây thu phí là vi phạm trực tiếp nguyên tắc *Zero-Bloat* và an ninh dữ liệu nội bộ của HuyNex.

## 2. Giải pháp Kỹ thuật Đạt chuẩn HuyNex
Thay vì phụ thuộc vào phần mềm bên ngoài, ADOS chuẩn hóa cơ chế **Bộ nhớ Tiến thoái 2 giai đoạn**:
1. **Cuối phiên (Session Distillation):** Agent chắt lọc các bài học/lỗi kỹ thuật/quyết định kiến trúc thành file Markdown súc tích tại `brain/lessons/`.
2. **Đầu phiên (Index-First Loading):** Chỉ đọc mục lục tổng (< 15 dòng, tiêu tốn < 150 token). Khi thực sự cần sửa module nào mới đọc chi tiết bài học của module đó.

## 3. Giá trị Mang lại
- Tiết kiệm 90% context window khi mở đầu phiên làm việc mới.
- Hoàn toàn độc lập, 0% rò rỉ dữ liệu qua bên thứ ba, 0 chi phí duy trì.
