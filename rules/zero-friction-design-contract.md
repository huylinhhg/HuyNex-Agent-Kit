# Hợp Đồng Thiết Kế Giao Diện Tự Động (Zero-Friction DESIGN.md)
## Tiêu Chuẩn Triệt Tiêu "AI Slop" Trong Phát Triển Frontend

> *"Bất cứ khi nào nhận yêu cầu tạo mới hoặc sửa giao diện (Web, App, Dashboard, Landing page), AI BẮT BUỘC TỰ ĐỘNG khởi tạo và tuân thủ hợp đồng thiết kế `DESIGN.md` ở gốc dự án."*

---

## 1. Hội Chứng "AI Slop" Trong Giao Diện

Khi lập trình viên yêu cầu AI dựng giao diện mà không có ràng buộc thiết kế, mô hình thường sinh ra các giao diện "rẻ tiền" mang tính nhận diện AI rất cao:
- **Card lồng trong Card (Nested Cards)**: Đóng khung div trong div vô tội vạ.
- **Màu sắc mặc định**: Gradient tím/xanh (`from-indigo-500 to-purple-600`), nền xám đục ngầu, thiếu tương phản.
- **Typography cẩu thả**: Quá nhiều cỡ chữ, dòng chữ dài lê thê 6–7 dòng không ngắt nhịp.
- **Chuyển động giật cục**: Dùng CSS animation tuyến tính (`ease-in-out` cơ bản) thay vì chuyển động vật lý mượt mà (spring physics).

---

## 2. Tiêu Chuẩn Hợp Đồng DESIGN.md

Bất kể người dùng chỉ nói ngắn gọn: *"Làm trang web này đi"*, *"Code giao diện dashboard"*, hay *"Thiết kế landing page"*, Agent **BẮT BUỘC TỰ ĐỘNG**:

1. **Khởi tạo tệp `DESIGN.md`** tại thư mục gốc của dự án.
2. **Xác lập 4 trụ cột thiết kế** phù hợp với lĩnh vực sản phẩm:
   - **Bảng màu (Color Tokens)**: Tối đa 1 màu chủ đạo (Primary), 1 màu bổ trợ (Accent), và hệ màu trung tính (Neutral Grays). Không dùng màu ngẫu nhiên.
   - **Hệ thống Font chữ (Typography)**: Tối đa 2 font (1 font Sans cho UI/nội dung hành động + 1 font Serif hoặc Display cho cảm xúc/tiêu đề lớn).
   - **Lưới & Spacing (Grid System)**: Tuân thủ bội số 4px/8px (`gap-4`, `p-6`, `my-12`). Giữ khoảng trắng thoáng đãng (Spaciousness).
   - **Chuyển động vật lý (Spring Physics & Micro-Interactions)**: Mọi tương tác hover, click, sheet swipe đều có gia tốc tự nhiên, không độ trễ.

---

## 3. Quy Trình 3 Bước Thực Thi

```
[Nhận yêu cầu UI] ──> [Bước 1: Tạo/Cập nhật DESIGN.md]
                                │
[Bước 3: Viết code sạch] <── [Bước 2: Đối chiếu Color/Typography Tokens]
```

- **Bước 1**: Đọc bối cảnh sản phẩm $\rightarrow$ Viết ngắn gọn `DESIGN.md` (chỉ 30–50 dòng định nghĩa tokens).
- **Bước 2**: Khi viết mã HTML/CSS/Tailwind, chỉ sử dụng đúng các tokens đã cam kết trong `DESIGN.md`.
- **Bước 3**: Kiểm tra responsive trên cả màn hình nhỏ (Mobile 375px) và màn hình lớn (Desktop 1440px) trước khi bàn giao.
