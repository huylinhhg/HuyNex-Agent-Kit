# Module 06 — Cộng tác và lựa chọn công cụ

- Phân việc theo năng lực, độ độc lập và rủi ro, không khóa theo tên hãng. Chỉ dùng subagent/workflow khi session và quyền cho phép, có ích thực tế, scope và tiêu chí rõ. Tránh giao việc hình thức hoặc các agent sửa chồng nhau.
- Người tích hợp chịu trách nhiệm thay đổi rủi ro và review diff thực tế; agent được giao việc không tự commit vào nhánh chính. Reviewer từ xa chỉ thấy thay đổi khi được cung cấp context/diff qua kênh được phép; không giả định nó đọc được máy local.
- Chọn model/effort phù hợp bằng controls được hỗ trợ và sở thích người dùng. Không hardcode model hoặc tự đổi tài khoản/defaults. Giữ phần instructions ổn định trước context động; chỉ kết luận hiệu quả cache khi có telemetry.
- Tối ưu AI/performance cần baseline đại diện, tiêu chí đo và guardrails hồi quy. Tách tuning với đánh giá held-out, đổi từng yếu tố và loại bỏ cải thiện không có bằng chứng.
