---
name: data-conservation-gate
description: Cổng bảo toàn dữ liệu tuyệt đối (Nothing Vanishes Silently) và kiểm toán tính toàn vẹn khi trích xuất, di chuyển hoặc chuyển đổi cấu trúc dữ liệu. Bắt buộc kiểm tra mã băm (sourceHash) và đối chiếu số lượng thực thể (entity count) giữa đầu vào và đầu ra.
---

# Data Conservation Gate — Cổng Bảo Toàn Dữ Liệu Tuyệt Đối

Skill này cung cấp phương pháp luận và cơ chế chốt chặn kỹ thuật để triệt tiêu vĩnh viễn tình trạng AI Agent "nuốt mất dữ liệu ngầm" (Silent Data Loss) khi bóc tách, chuyển đổi hoặc di chuyển cấu trúc thông tin.

---

## 1. Vấn Đề "Nuốt Chửng Dữ Liệu Ngầm" (Silent Data Loss)

Khi xử lý khối lượng lớn tài liệu, bảng biểu, JSON phức tạp hoặc danh mục dữ liệu, các mô hình ngôn ngữ lớn (LLM) thường mắc tật xấu:
- Tự ý bỏ qua các dòng khó, trường dữ liệu lạ hoặc cấu trúc lồng nhau phức tạp.
- Tự ý tóm tắt/cắt xén nội dung mà không hề thông báo cho người dùng.
- Hậu quả: Dữ liệu đầu ra bị rơi rụng từ 5% đến 20% mà người dùng không hề hay biết.

---

## 2. Hai Quy Tắc Sắt Đá Của Conservation Gate

```
[Dữ Liệu Đầu Vào (Input)] ──> [Bộ Đếm Thực Thể: Count A & Mã Băm: Hash A]
                                                 │
[Quá Trình Xử Lý / Bóc Tách / Di Chuyển Của AI] ─┘
         │
         ▼
[Dữ Liệu Đầu Ra (Output)] ──> [Bộ Đếm Thực Thể: Count B & Mã Băm: Hash B]
                                                 │
                                                 ▼
                         [CHỐT ĐỐI SOÁT: Count A == Count B?]
                               ┌─────────────────┴─────────────────┐
                             ĐÚNG (Pass)                         SAI (Fail)
                               │                                   │
                               ▼                                   ▼
                     [Hoàn thành nhiệm vụ]              [BÁO ĐỘNG ĐỎ & DỪNG LẠI]
```

1. **Kiểm Toán Đối Soát Bắt Buộc (Input vs Output Auditing)**:
   - Trước khi xử lý, ghi nhận số lượng thực thể đầu vào: `total_items_in`.
   - Sau khi xuất bản, đếm số lượng thực thể đầu ra: `total_items_out`.
   - **Quy tắc bảo toàn**: `total_items_in == total_items_out`.
2. **Báo Động Đỏ Khi Thất Thoát (Fail Hard & Loud)**:
   - Nếu đầu vào có 100 thực thể mà đầu ra chỉ còn 97 thực thể (rơi rụng 3 mục):
     + **BẮT BUỘC chốt chặn phải báo trạng thái `FAIL_CONSERVATION` ngay lập tức**.
     + Dừng toàn bộ quy trình, liệt kê danh sách chính xác 3 thực thể bị thiếu.
     + Tuyệt đối cấm AI tự ý suy diễn hoặc bịa số liệu giả để "bù cho đủ số".

---

## 3. Ứng Dụng Trong Thực Tế

- **Chuyển đổi bảng biểu (Excel/Word/CSV)**: Luôn đếm tổng số dòng dữ liệu thực tế trước và sau khi format.
- **Di chuyển thư mục / Đồng bộ mã nguồn**: Sử dụng mã băm SHA-256 (`source_sha256 == target_sha256`) cho từng file được chuyển dịch.
- **Trích xuất thông tin từ tài liệu dài**: Đối chiếu danh mục thực thể trích xuất được với chỉ mục ban đầu.
