# Workspace Entry Instructions (AGENTS.md)

Chào mừng bạn đến với dự án! Mọi AI Coding Agent khi làm việc trong repository này đều phải tuân thủ nghiêm ngặt các nguyên tắc sau:

## 1. Nguyên Tắc Cốt Lõi
- **Thang 7 nấc kỹ sư tối giản (Ladder of Laziness)**: Đoạn code tốt nhất là đoạn code không bao giờ phải viết. Ưu tiên tái sử dụng code có sẵn và thư viện chuẩn thay vì cài thêm package bừa bãi.
- **Cổng kiểm chứng (Verification Gate)**: Tuyệt đối không bịa bằng chứng giả hoặc tuyên bố hoàn thành nếu chưa chạy bài test thực tế.
- **Bảo vệ dữ liệu (Single-Root Safety)**: Tuyệt đối không chạy lệnh xóa đệ quy mang tính hủy diệt (`rm -rf`) trên thư mục gốc.

## 2. Quy Trình Làm Việc
1. Đọc và hiểu kỹ yêu cầu trước khi bắt tay vào sửa code.
2. Kiểm tra các test suites hiện có.
3. Tạo thay đổi nhỏ nhất đáp ứng yêu cầu.
4. Chạy kiểm thử xác minh trước khi báo hoàn thành.
