---
name: agent-rule-creator
description: Hướng dẫn tạo, chuẩn hóa, phân cấp và kiểm tra xung đột cho các Quy tắc AI Agent (Agent Rules). Phân định rõ giữa quy tắc cưỡng chế bắt buộc (Hard Policy), hướng dẫn tham khảo (Guidance), và chưng cất bài học kinh nghiệm để tránh làm phình to context window.
---

# Agent Rule Creator — Chuẩn Hóa & Quản Trị Quy Tắc AI Agent

Skill này cung cấp phương pháp luận và công cụ để xây dựng bộ quy tắc vận hành (Agent Rules) tinh gọn, hiệu lực cao, không gây ngáo context window và không phát sinh xung đột nội tại.

---

## 1. Phân Cấp Quy Tắc (The 3-Tier Hierarchy)

Không phải mọi kinh nghiệm hay lỗi phát sinh đều được biến thành quy tắc toàn cục (Global Rule). Phải phân định nghiêm ngặt:

1. **Cấp 1 — Nguyên tắc Bất biến (Invariant Core Rules)**:
   - Các nguyên tắc an toàn sống còn: Không phá hủy dữ liệu, Không rò rỉ secrets, Kiểm tra trước khi sửa, Không tuyên bố hoàn thành khi chưa kiểm chứng thực tế.
   - Dung lượng: Tối đa 15–20 quy tắc cốt lõi, luôn luôn được nạp vào context gốc.
2. **Cấp 2 — Quy ước Dự án (Project-Specific Rules)**:
   - Quy chuẩn công nghệ cụ thể của dự án (ví dụ: dùng Next.js App Router, dùng Tailwind v4, dùng SQLite in-memory cho test).
   - Đặt tại file `AGENTS.md` hoặc `.cursor/rules/` trong chính repo đó.
3. **Cấp 3 — Bài học & Tham khảo Kích hoạt theo Ngữ cảnh (Contextual Skills & Lessons)**:
   - Các kỹ thuật chuyên sâu chỉ cần khi đụng việc (ví dụ: mẹo sửa lỗi OpenXML Word, mẹo xử lý audio 48kHz).
   - **Tuyệt đối không nhét vào Global Rule**. Đóng gói thành `SKILL.md` hoặc `lessons/` để Agent chỉ nạp khi cần.

---

## 2. Thử Nghiệm 5 Bước Trước Khi Thêm Quy Tắc Mới (Rule Admission Gate)

Trước khi thêm một quy tắc mới vào bộ quy tắc chung:
1. **Kiểm tra Trùng lặp (Deduplication Check)**: Quy tắc này đã có sẵn trong các rule hiện có dưới dạng khác chưa?
2. **Kiểm tra Xung đột (Conflict Resolution)**: Quy tắc mới có mâu thuẫn trực tiếp với quy tắc hiện có không? (Ví dụ: Một rule bắt "luôn viết test trước", một rule khác lại cho phép "sửa nhanh 1 dòng không cần test").
3. **Thang 7 nấc Lười biếng (Ladder of Laziness)**: Đoạn quy tắc này có thực sự cần thiết không? Nếu bỏ đi thì Agent có tự xử lý đúng nhờ prompt thông thường không?
4. **Kiểm tra Khả năng Kiểm chứng (Verifiability)**: Làm thế nào để biết Agent có tuân thủ quy tắc này hay không? Có tiêu chuẩn quan sát được không?
5. **Đo Lường Chi Phí Token (Token Overhead)**: Quy tắc tốn bao nhiêu token? Viết lại súc tích trong 1-2 câu ngắn, loại bỏ từ thừa.

---

## 3. Cấu Trúc Mẫu Của Một Quy Tắc Chuẩn (Rule Blueprint)

```markdown
- **[Tên Định Danh] (Chuẩn Áp Dụng)**: [Mệnh lệnh hành động rõ ràng].
  - *Điều kiện áp dụng*: Khi [ngữ cảnh cụ thể].
  - *Hành vi cấm*: Tuyệt đối không [hành vi sai phạm].
  - *Kiểm chứng bắt buộc*: Bắt buộc đối chiếu [bằng chứng thực tế] trước khi báo hoàn thành.
```
