# Bài học: Tiêu chuẩn Hợp đồng Thiết kế (DESIGN.md Contract) và Phối hợp cùng Apple Design Skills

- **Ngày ghi nhận**: 02/11/2026
- **Phạm vi**: Toàn bộ hệ sinh thái HuyNex, áp dụng cho mọi dự án phát triển giao diện Web/App/Dashboard/Prototype.
- **Nguồn**: Đúc kết từ kiến trúc `DESIGN.md` của `nexu-io/open-design` kết hợp chuẩn Apple HIG và bộ kỹ năng thẩm mỹ đã cài đặt trên máy.

---

## 1. Vấn đề cốt lõi & Sự phân định vai trò

Khi yêu cầu AI lập trình giao diện, các câu lệnh định tính kiểu "Làm đẹp, hiện đại, sang trọng" luôn thất bại và sinh ra "AI Slop" (giao diện màu mè tím neon, font chữ rập khuôn).

Hệ thống giải quyết triệt để vấn đề này bằng cách phân tách rõ ràng 2 vai trò:

1. **`DESIGN.md` (Hợp đồng thiết kế của từng dự án):**
   * Đóng vai trò là "Bản vẽ kỹ thuật & Số đo cụ thể" đặt tại gốc của mỗi dự án UI.
   * Quy định cứng: 9 mục chuẩn (Visual Theme, Color Palette HEX/OKLCH, Typography pairings, Spacing 8px, Shape bo góc, Shadows, Responsive 100dvh/44px, Motion spring, Anti-Patterns cấm AI Slop).
2. **`apple-design` & các Taste Skills (`impeccable`, `design-taste-frontend`):**
   * Đóng vai trò là "Kỹ sư / Thợ may lành nghề".
   * Chịu trách nhiệm thực thi: Vật lý lò xo (Spring physics), hiệu ứng kính mờ (Glassmorphism), căn lề từng pixel và khả năng tiếp nhận thao tác chạm vuốt không độ trễ.

👉 **Kết luận:** `DESIGN.md` và `apple-design` **hoàn toàn không xung đột**, mà là cặp bài trùng: `DESIGN.md` cấp thông số và màu sắc, `apple-design` cấp kỹ thuật thi công mượt mà.

---

## 2. Tiêu chuẩn áp dụng

- Đã đưa mẫu chuẩn hóa 9 phần vào [03_Tieu_chuan/design-contract-standard/DESIGN.template.md](file://{{WORKSPACE_ROOT}}/03_Tieu_chuan/design-contract-standard/DESIGN.template.md).
- Khi tạo dự án UI mới, copy file mẫu và đổi tên thành `DESIGN.md`.
- AI khi thực thi BẮT BUỘC đọc `DESIGN.md` để lấy tokens trước khi viết code.
