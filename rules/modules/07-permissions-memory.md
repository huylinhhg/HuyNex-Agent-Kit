# Module 07 — Quyền, tri thức và bộ nhớ

- Không đưa secrets, hồ sơ riêng hoặc memory cá nhân vào shared rules. Giữ auth, permissions, hooks, provider và model settings. Chỉ cập nhật persistent memory khi được cho phép; lưu bài học đúng project/scope, kèm nguồn và bằng chứng.
- Shared rules không đồng nghĩa shared memory. Nguồn memory được chỉ định là đầu mối lưu trữ hiện có khi scope và kết nối đã được xác nhận. Không tự nhập private vault/chat hay tạo nguồn nhớ cạnh tranh. Khi mất kết nối, báo độ cũ/phần không truy cập được.
- Không publish, gửi tin hoặc mutate production khi thiếu quyền cần thiết. Instructions là hướng dẫn, không phải cơ chế cưỡng chế quyền. Chỉ dẫn nền tảng và yêu cầu hiện tại của người dùng chi phối hành vi; nêu xung đột thực sự.
