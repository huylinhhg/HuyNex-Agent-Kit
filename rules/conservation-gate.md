# Cổng Bảo Toàn Dữ Liệu Tuyệt Đối (The Conservation Gate)
## Nguyên Tắc Không Bỏ Sót Dữ Liệu (Nothing Vanishes Silently)

> *"Khi bóc tách, chuyển đổi định dạng, di chuyển cơ sở dữ liệu hoặc refactor schema, Agent BẮT BUỘC phải kiểm toán đối chiếu đầu vào và đầu ra. Cấm tuyệt đối AI tự ý bỏ qua hoặc nuốt mất dữ liệu khó."*

---

## 1. Nỗi Đau Dữ Liệu Bị "Nuốt Chửng" Ngầm

Khi giao cho AI xử lý các tác vụ phức tạp như:
- Chuyển đổi dữ liệu (từ CSV sang SQLite, từ XML sang JSON).
- Refactor cấu trúc cơ sở dữ liệu hoặc migration schema.
- Chuẩn hóa văn bản hành chính, bảng biểu số liệu.

Do giới hạn token hoặc gặp phải dòng dữ liệu bị lỗi cú pháp, AI thường có hành vi **âm thầm bỏ qua các bản ghi khó (silent drop)** để script chạy thành công mà không báo lỗi. Người dùng tưởng chừng đã hoàn tất nhưng thực tế đã bị mất mát dữ liệu nghiêm trọng.

---

## 2. Tiêu Chuẩn 2 Chốt Chặn Kiểm Toán (Two-Factor Audit)

Trong mọi script hoặc quy trình chuyển đổi dữ liệu do Agent thiết kế, **BẮT BUỘC** phải có bước đối chiếu tự động:

```
[Dữ liệu Đầu Vào] ───> [Tiến Trình Chuyển Đổi] ───> [Dữ liệu Đầu Ra]
        │                                                    │
        └──────────────> [BỘ KIỂM TOÁN ĐỐI CHIẾU] <──────────┘
                         1. Đếm số lượng: count(In) == count(Out)
                         2. Khớp mã băm: hash(Data) bảo toàn
```

1. **Kiểm toán số lượng (Count Verification)**:
   - Tổng số bản ghi / thực thể / dòng dữ liệu đầu ra BẮT BUỘC phải bằng chính xác tổng số bản ghi đầu vào:
     $$\text{Count}_{\text{output}} == \text{Count}_{\text{input}}$$
   - Nếu có bản ghi bị loại bỏ do trùng lặp hoặc vi phạm ràng buộc, BẮT BUỘC phải xuất riêng danh sách chi tiết (Quarantine Log) kèm lý do cụ thể.

2. **Kiểm toán toàn vẹn ngữ nghĩa (Source Hash Check)**:
   - Với các tài liệu hoặc tệp tin quan trọng, tính toán mã băm SHA-256 trước và sau khi xử lý để xác minh không có trường thông tin nào bị biến dạng ngoài ý muốn.

---

## 3. Rào Chắn Nghiêm Cấm

- **Nghiêm cấm dùng khối `try...except: pass` câm lặng**: Khi gặp lỗi parse dữ liệu, Agent phải ghi log cảnh báo và dừng lại hoặc đưa vào hàng đợi chờ xử lý, tuyệt đối không được nuốt lỗi.
- **Báo cáo định lượng minh bạch**: Mọi kết quả bàn giao phải nêu rõ: *"Đã chuyển đổi thành công 1.450/1.450 bản ghi (100%), 0 bản ghi thất thoát"*.
