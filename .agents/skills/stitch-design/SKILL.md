---
name: stitch-design
description: Khởi tạo và quản trị file hợp đồng thiết kế giao diện (DESIGN.md) chuẩn ngữ nghĩa. Loại bỏ 100% mẫu giao diện khuôn mẫu AI (AI Slop), thiết lập kiến trúc typography tương phản cao, bảng màu chuẩn hóa và hệ thống chuyển động lò xo vật lý.
---

# Stitch Design — Hệ Thống Hợp Đồng Thiết Kế Giao Diện Ngữ Nghĩa

Skill này chuyên trách việc tự động kiểm tra, khởi tạo và duy trì file hợp đồng thiết kế **`DESIGN.md`** cho mọi dự án Web, Mobile App và Dashboard. File này đóng vai trò là **Nguồn Sự Thật Duy Nhất (Single Source of Truth)** để AI Agent lập trình giao diện mà không bao giờ bị rơi vào các bẫy giao diện rác hay thiết kế khuôn mẫu.

---

## 1. Bảy Cột Trụ Của Một File `DESIGN.md` Hoàn Hảo

Một file `DESIGN.md` chuẩn mực bắt buộc phải định nghĩa rõ:

1. **Bầu Không Khí Thị Giác (Atmosphere)**:
   - Mật độ hiển thị (Density): Thoáng đãng (Art Gallery), Cân bằng (Daily App), hay Cô đọng dữ liệu (Data Cockpit).
   - Mức độ phá cách (Variance): Bố cục lưới bất đối xứng (Offset Asymmetric), không dùng các thẻ bento đối xứng tẻ nhạt.
2. **Bảng Màu Chuẩn Hóa (Color System)**:
   - Màu nền (Background), màu bề mặt thẻ (Card Surface), màu đường viền (Subtle Border).
   - Màu chữ chính (Primary Text) và màu phụ (Muted Text) bảo đảm độ tương phản WCAG AAA.
   - **Chỉ 1 màu nhấn duy nhất (Single Accent)**, cấm tiệt dải màu tím/hồng neon AI.
3. **Kiến Trúc Typography**:
   - Cặp phông chữ đối xứng: 1 font tiêu đề cá tính (Display/Grotesk/Serif) + 1 font nội dung dễ đọc (System Sans).
   - Quy định kích thước cụ thể (`text-xs` đến `text-5xl`), cấm các dòng tiêu đề dài quá 3 dòng trên màn hình desktop.
4. **Hệ Thống Thẻ & Khung Chứa (Cards & Containers)**:
   - Bo góc nhất quán (`rounded-lg` hoặc `rounded-2xl`).
   - Viền mờ (`border border-zinc-200/50` hoặc `border-white/10`), không lạm dụng shadow đen đậm xì xì.
5. **Chuyển Động Vi Mô & Tương Tác (Micro-Motion)**:
   - Sử dụng hiệu ứng lò xo vật lý (Spring Physics: stiffness 300, damping 30) cho các nút bấm, modal, drawer.
   - Chuyển trạng thái hover/press mượt mà dưới 150ms.
6. **Danh Mục Mẫu Rác Bị Cấm Tuyệt Đối (Banned AI Patterns)**:
   - Cấm gradient tím neon.
   - Cấm các biểu tượng trôi nổi vô nghĩa không nhãn.
   - Cấm hiệu ứng viền phát sáng (Glow borders) giả tạo.
7. **Chiến Lược Thích Ứng (Responsive Strategy)**:
   - Thiết kế ưu tiên Mobile (Mobile-First) hoặc linh hoạt thích ứng từ 375px đến 1920px.

---

## 2. Quy Trình Tự Động Kích Hoạt

Bất cứ khi nào nhận yêu cầu tạo mới hoặc sửa giao diện (dù người dùng chỉ nói *"làm web đi"*, *"dựng giao diện trang này"* hay không hề nhắc tên file):
1. **Kiểm tra**: Kiểm tra thư mục gốc dự án xem đã có `DESIGN.md` chưa.
2. **Khởi tạo**: Nếu chưa có, Agent **TỰ ĐỘNG** phân tích lĩnh vực dự án và tạo ngay file `DESIGN.md` chuẩn mực trước khi gõ mã nguồn HTML/CSS/React.
3. **Tuân thủ**: Toàn bộ mã nguồn giao diện sau đó bắt buộc phải đối chiếu khớp từng mã màu và font chữ đã cam kết trong `DESIGN.md`.
