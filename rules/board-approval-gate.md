# Phân Cấp Phê Duyệt Hội Đồng (The Board Approval Gate)

Nhằm cân bằng giữa tính tự chủ linh hoạt của AI Agent và sự an toàn tuyệt đối của hệ sinh thái, mọi hành vi can thiệp được phân thành 3 cấp độ:

```
[Cấp 1: Routine - Tự chủ] ──> Tự động thực thi trong phạm vi được giao
[Cấp 2: Controlled Change]  ──> Thực thi, lưu diff và báo cáo kiểm tra
[Cấp 3: Board Approval]    ──> BẮT BUỘC DỪNG LẠI, xuất kế hoạch, chờ người dùng duyệt
```

### Cấp 1 — Routine (Tự chủ)
- Đọc, tra cứu tài liệu, phân tích mã nguồn.
- Chạy unit tests, kiểm tra trạng thái git, build nháp.
- Thực hiện định dạng file trong phạm vi dự án hiện hành.
$\rightarrow$ **Quyền hạn**: Agent tự chủ thực hiện, không cần hỏi từng bước nhỏ.

### Cấp 2 — Controlled Change (Ghi nhận & Thông báo)
- Sửa code logic trong phạm vi một tính năng hoặc bug đã giao.
- Tạo file mới trong thư mục dự án được chỉ định.
- Chạy suite kiểm thử tích hợp (integration tests).
$\rightarrow$ **Quyền hạn**: Agent thực hiện, kiểm tra regression, lưu bản diff và thông báo tóm tắt cho người dùng.

### Cấp 3 — Board Only (Bắt buộc Phê duyệt Trước)
- Thay đổi các nguyên tắc điều hành cốt lõi (`core.md`, system rules).
- Xóa, di chuyển hoặc tái cấu trúc các thư mục lớn, dữ liệu lịch sử.
- Thao tác hạ tầng đám mây (Cloud Deploy, xóa Database, xoay Credentials).
- Can thiệp sâu hệ điều hành (chỉnh sửa Registry Windows, quyền root/sudo).
$\rightarrow$ **Quyền hạn**: Agent **BẮT BUỘC DỪNG LẠI**, xuất kế hoạch can thiệp chi tiết kèm phương án rollback và chỉ thực thi khi nhận được lệnh phê duyệt rõ ràng từ người dùng.
