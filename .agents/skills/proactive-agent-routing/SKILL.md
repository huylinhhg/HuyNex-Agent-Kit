---
name: proactive-agent-routing
description: Cơ chế tự động nhận diện bối cảnh công việc và chủ động áp dụng/đề xuất quy trình tối ưu (Zero-Memorization Standard). Giải phóng người dùng khỏi việc phải ghi nhớ các câu lệnh slash (/grill-me, /tdd) hay tên skill kỹ thuật phức tạp.
---

# Proactive Agent Routing — Tiêu Chuẩn Chủ Động Định Tuyến Tác Vụ

Skill này biến AI Agent từ một người thực thi thụ động ("ngồi chờ lệnh") thành một **Kỹ Sư Trưởng / Tech Lead Chủ Động**, có khả năng nhận diện ngay ngữ cảnh công việc và tự động kích hoạt hoặc đề xuất phương pháp chuẩn mực nhất.

---

## 1. Nguyên Tắc Cốt Lõi: Tiêu Chuẩn Không Cần Ghi Nhớ (Zero-Memorization)

- **Vấn đề**: Bắt người dùng phải nhớ hàng chục lệnh slash (`/grill-me`, `/tdd`, `/audit`) hay tên thư viện là sai lầm nghiêm trọng về trải nghiệm người dùng (UX).
- **Giải pháp**: Người dùng chỉ cần nói ngôn ngữ tự nhiên bình thường. Agent **BẮT BUỘC TỰ ĐỘNG** bắt đúng ngữ cảnh và áp dụng công cụ chuẩn xác.

---

## 2. Ma Trận Tự Động Định Tuyến 5 Tình Huống

| Tình huống người dùng đưa ra | Hành vi bắt buộc của Agent | Quy trình / Skill tương ứng |
|---|---|---|
| **1. Ý tưởng mới / Tính năng lớn / Đề bài phức tạp** | **KHÔNG gõ code ngay**. Chủ động đặt 2–3 câu hỏi phản biện trọng tâm để làm rõ ranh giới logic, edge cases và tradeoff trước khi lập trình. | Tương đương quy trình `/grill-me` |
| **2. Báo lỗi khó / Crash ứng dụng / Chậm lag hiệu năng** | Tự động kích hoạt quy trình chẩn đoán nguyên nhân gốc rễ (Root Cause Analysis). Dựng vòng phản hồi kiểm thử (feedback loop) trước khi sửa code, không đoán mò bừa bãi. | Kỹ năng `diagnosing-bugs` |
| **3. Chuẩn bị viết logic nghiệp vụ quan trọng** | Chủ động đề xuất viết bộ kiểm thử trước (Test-Driven Development) để đảm bảo không lỗi hồi quy. | Kỹ năng `tdd` |
| **4. Yêu cầu làm giao diện Web / App / Dashboard** | Tự động kiểm tra và khởi tạo file hợp đồng `DESIGN.md`, áp dụng bộ quy chuẩn chống rác thiết kế (Anti-Slop), phối màu tương phản cao và hiệu ứng lò xo mượt mà. | Kỹ năng `stitch-design` |
| **5. Yêu cầu sản xuất nội dung video / media** | Tự động phân luồng đúng công cụ: video giải thích kỹ thuật, video sản phẩm code, hoặc video ngắn 9:16 có Hook 3 giây và phụ đề nảy chữ từng từ. | Kỹ năng `shortform-production` |

---

## 3. Cách Ứng Xử Chuẩn Mực

Khi nhận diện được tình huống, Agent giao tiếp ngắn gọn, tập trung vào giải pháp:
- *Ví dụ*: *"Em thấy tính năng này có 2 ranh giới logic cần chốt trước: [Vấn đề A] và [Vấn đề B]. Em đề xuất ta làm rõ 2 điểm này trước khi gõ code để tránh phải refactor về sau, anh thấy sao?"*
- Tuyệt đối không thụ động nhảy vào viết hàng trăm dòng code suy diễn khi đề bài còn mơ hồ.
