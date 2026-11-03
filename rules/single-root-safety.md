# Bảo Vệ Cội Nguồn Workspace & An Toàn Dữ Liệu (Single-Root Safety)

## 1. Cấm Lệnh Xóa Đệ Quy Nguy Hiểm
- Nghiêm cấm tuyệt đối mọi lệnh xóa đệ quy mang tính hủy diệt (`rm -rf`, `Remove-Item -Recurse`, `shutil.rmtree`) trên thư mục gốc dự án hoặc các thư mục phân cấp cha.
- Khi cần dọn dẹp hoặc loại bỏ dữ liệu, bắt buộc áp dụng nguyên tắc: **Archive / Move trước khi Xóa**. Chuyển các file cần bỏ vào thư mục chờ duyệt (`98_De_xuat_xoa` hoặc `trash/`).
- Khu vực duy nhất Agent được phép tự động dọn dẹp file nháp là thư mục con tạm thời (`work/` hoặc `tmp/`).

## 2. Sao Lưu Trước Khi Thay Đổi (Pre-Mutation Backup)
- Trước khi thực hiện thay đổi cấu hình lớn, refactor hàng loạt hoặc ghi đè file:
  + Lưu bản sao lưu nguyên trạng kèm mã băm SHA-256.
  + Ghi nhận manifest sao lưu để sẵn sàng khôi phục (Rollback) tức thì khi có sự cố.
