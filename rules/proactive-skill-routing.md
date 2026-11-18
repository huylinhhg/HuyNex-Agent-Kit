# Cơ Chế Nhận Diện & Chủ Động Đề Xuất Công Cụ (Proactive Skill Routing)
## Tiêu Chuẩn Không Cần Ghi Nhớ (Zero-Memorization Standard)

> *"Người dùng không cần phải ghi nhớ tên lệnh slash, tên skill hay tên thư viện. Đến đúng bối cảnh công việc, Agent BẮT BUỘC TỰ ĐỘNG nhận diện và chủ động áp dụng vũ khí tối ưu."*

---

## 1. Nỗi Đau Thực Tế (The Problem)

Hầu hết người dùng cài đặt hàng chục plugin, skills hoặc MCP servers cho AI Coding Agent nhưng không tận dụng được vì:
- Quên cú pháp lệnh slash (`/grill-me`, `/tdd`, `/diagnose`, `/security-audit`).
- Không biết khi nào nên dùng công cụ nào.
- Agent thụ động: chỉ làm đúng câu lệnh thô của người dùng thay vì hướng dẫn quy trình kỹ thuật chuẩn xác.

---

## 2. Ma Trận Tự Động Định Tuyến (Routing Matrix)

Đến đúng bối cảnh công việc, AI Agent **BẮT BUỘC TỰ ĐỘNG** kích hoạt hoặc chủ động đề xuất quy trình tương ứng:

| Bối cảnh công việc | Phản xạ TỰ ĐỘNG của Agent | Hành động cụ thể |
| :--- | :--- | :--- |
| **Nhận bài toán / Tính năng mới phức tạp** | **Chất vấn phản biện (`grill-me`)** | Chủ động hỏi 2–3 câu trọng tâm làm rõ ranh giới logic, edge cases và tradeoff kiến trúc trước khi gõ code. |
| **Sửa lỗi khó / Hiệu năng sụt giảm** | **Chẩn đoán nguyên nhân gốc (`diagnosing-bugs`)** | Tái hiện lỗi $\rightarrow$ Trích xuất log/stacktrace $\rightarrow$ Xác định root cause $\rightarrow$ Viết bài test tái hiện $\rightarrow$ Mới sửa code. |
| **Viết logic nghiệp vụ trọng yếu** | **Kiểm thử trước (`tdd`)** | Chủ động đề xuất viết test case trước (Red $\rightarrow$ Green $\rightarrow$ Refactor). |
| **Dựng giao diện Web / App / Dashboard** | **Hợp đồng thiết kế (`DESIGN.md` & Apple/Impeccable style)** | Tự động tạo `DESIGN.md` định nghĩa token màu, typography, spring motion để triệt tiêu AI Slop. |
| **Tái cấu trúc / Refactor code diện rộng** | **Kiểm chứng hồi quy (`code-review` / verification)** | Kiểm tra độ bao phủ test trước và sau khi refactor, bảo toàn hành vi nghiệp vụ hiện hữu. |

---

## 3. Nguyên Tắc Ứng Xử

1. **Gợi ý tự nhiên, không làm phiền**: Với việc nhỏ (sửa 1 dòng typo, đổi config), thực hiện ngay; với việc lớn, đưa ra đề xuất ngắn gọn 1–2 dòng.
2. **Không ép buộc người dùng nhớ tên kỹ thuật**: Thay vì nói *"Hãy gõ lệnh /tdd"*, Agent nói *"Tính năng thanh toán này quan trọng, em đã viết sẵn 3 test case kiểm thử các trường hợp lỗi trước khi code nhé!"*.
