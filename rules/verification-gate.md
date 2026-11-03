# Cổng Kiểm Chứng Thực Tế & Chống Lệch Hướng (Verification Gate & Anti-Drift)

## 1. Phả Hệ Mục Tiêu (Goal Ancestry)
Mỗi tác vụ, sub-task hoặc lệnh gọi subagent BẮT BUỘC phải liên kết trực tiếp đến một mục tiêu chiến lược hợp lệ (**Root Goal**).
Khi giao việc, bắt buộc xác định rõ:
- **Mục tiêu gốc (`root_goal`)**: Kết quả mong muốn cuối cùng.
- **Phạm vi (`scope`)**: Ranh giới những file/module được phép can thiệp.
- **Tiêu chí nghiệm thu (`acceptance_criteria`)**: Bằng chứng quan sát được chứng minh công việc hoàn thành.

## 2. Cổng Kiểm Chứng Bắt Buộc (Verification Gate)
- **Tuyệt đối không bịa bằng chứng giả**: Không suy đoán lệnh chạy thành công nếu chưa thực sự chạy lệnh; không nói test pass nếu chưa thấy kết quả terminal; không nói file tồn tại nếu chưa kiểm tra filesystem.
- **Chỉ sử dụng các trạng thái khi có bằng chứng thực tế**:
  + `IMPLEMENTED`: Chỉ khi code đã viết và không có lỗi cú pháp.
  + `VERIFIED`: Chỉ khi bài test hoặc runtime command đã chạy qua thành công.
  + `BLOCKED`: Nêu rõ nguyên nhân chặn cụ thể và phương án tháo gỡ.
- **Đối chiếu Tiêu chí Nghiệm thu**: Trước khi báo hoàn thành cho người dùng, Agent bắt buộc phải kiểm tra lại từng gạch đầu dòng trong tiêu chí nghiệm thu ban đầu.
