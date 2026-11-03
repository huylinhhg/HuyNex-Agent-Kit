# Bài học: Cơ chế Tự động Nhận diện Tác vụ và Chủ động Đề xuất Skill (Proactive Skill Routing — Zero-Memorization)

- **Ngày ghi nhận**: 02/11/2026
- **Phạm vi**: Toàn bộ tương tác của AI Coding Agent với người dùng (Huy) trong hệ sinh thái HuyNex.
- **Nguồn**: Đúc kết từ chỉ đạo trực tiếp của Huy ("khó nhớ lắm, cài kiểu gì đến việc gì AI tự nhận diện và đề xuất trước cơ").

---

## 1. Vấn đề thực tế (Problem Statement)

* **Rào cản ghi nhớ (Cognitive Overload)**: Hệ sinh thái có hàng chục skill, slash command (`/grill-me`, `/tdd`, `code-review`, `anatomy`, `video-shotcraft`...). Bắt người dùng phải nhớ từng câu lệnh kỹ thuật là sai lầm trong trải nghiệm người dùng (UX).
* **AI thụ động (Passive Waiting)**: Nếu chỉ ngồi chờ người dùng gõ đúng cú pháp mới kích hoạt, các quy chuẩn kỹ thuật đỉnh cao sẽ bị bỏ xó hoặc người dùng quay lại thói quen "vibe coding" cẩu thả.

---

## 2. Tiêu chuẩn Vận hành: Chủ động Nhận diện & Gợi ý (Proactive Behavior)

Agent BẮT BUỘC tự động bắt đúng ngữ cảnh công việc và **chủ động gợi ý giải pháp phù hợp** trước khi bắt tay vào làm:

1. **Khi người dùng giao bài toán mới / ý tưởng lớn / tính năng phức tạp**:
   - *Hành vi bắt buộc*: KHÔNG code ngay. Agent chủ động gợi ý:
     > *"Tính năng này có nhiều ranh giới logic cần làm rõ. Em đề xuất chất vấn nhanh 2-3 câu trọng tâm (theo chuẩn `/grill-me`) để chốt luồng trước khi gõ code, Huy có muốn làm rõ trước không?"*
2. **Khi người dùng giao sửa lỗi khó / crash / lag hiệu năng**:
   - *Hành vi bắt buộc*: Tự động áp dụng quy trình `diagnosing-bugs`: cô lập lỗi, tìm nguyên nhân gốc rễ (Root Cause) trước khi đưa ra phương án sửa, không đoán mò bừa bãi.
3. **Khi chuẩn bị viết logic nghiệp vụ quan trọng**:
   - *Hành vi bắt buộc*: Chủ động đề xuất viết kiểm thử trước (`tdd` - Test Driven Development):
     > *"Em đề xuất viết trước bộ test kiểm thử (TDD) cho trường hợp này để đảm bảo code xong là chạy chuẩn 100%, không lo lỗi hồi quy."*
4. **Khi người dùng yêu cầu dựng giao diện / web / app**:
   - *Hành vi bắt buộc*: Tự động kích hoạt các skill thẩm mỹ chống rác (`apple-design`, `impeccable`, `design-taste-frontend`), tự động tạo file hợp đồng `DESIGN.md` mà không cần người dùng nhắc.
5. **Khi người dùng yêu cầu làm video / media**:
   - *Hành vi bắt buộc*: Tự động chọn đúng vũ khí phù hợp:
     - Video trailer/sản phẩm code $\rightarrow$ `video-shotcraft` (124 góc quay 2.5D).
     - Video giải thích kỹ thuật cơ khí $\rightarrow$ `anatomy` (máy móc isometric).
     - Video ngắn TikTok/Reels $\rightarrow$ `huynex-media` + HyperFrames + Audio 48kHz.

---

## 3. Lợi ích đạt được

- Huy **hoàn toàn giải phóng bộ nhớ**, chỉ cần nói ngôn ngữ tự nhiên bình thường.
- Agent đóng vai trò như một **Tech Lead / Senior Engineer chủ động**, biết tư vấn quy trình đúng đắn nhất cho từng hoàn cảnh.
