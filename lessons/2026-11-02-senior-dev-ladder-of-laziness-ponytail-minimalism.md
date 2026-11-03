# Bài học: Kỹ sư Tối giản & Thang 7 nấc Thẩm định Code (Ponytail Ladder of Laziness)

- **Ngày ghi nhận**: 02/11/2026
- **Phạm vi**: Toàn bộ hệ sinh thái HuyNex (Mac Mini & Windows), áp dụng cho toàn bộ AI Coding Agents (Antigravity, Cursor, Claude Code, Codex, OpenCode...).
- **Nguồn**: Đúc kết từ dự án mã nguồn mở `DietrichGebert/ponytail` (155K+ stars trên GitHub) theo chỉ đạo của Huy ("hấp thụ tinh hoa vào hệ thống, đỡ mất công cài").

---

## 1. Bối cảnh & Vấn đề Cần Giải Quyết

Khi sử dụng AI để lập trình, các mô hình ngôn ngữ lớn (LLM) thường mắc một tật xấu mang tính hệ thống: **Over-Engineering và Đẻ Code Thừa (AI Slop)**:
1. Một tác vụ đơn giản chỉ cần 1 dòng lệnh nhưng AI hay tự ý viết thêm cả class bọc, factory, singleton, hoặc tự chế wrapper phức tạp.
2. Tự tiện cài thêm package bên thứ ba (qua `npm install` hoặc `pip install`) cho các tính năng vốn đã có sẵn trong thư viện chuẩn của ngôn ngữ hoặc trong nền tảng (trình duyệt/OS).
3. Thích viết thêm code mới (`+50`) thay vì tìm kiếm và tái sử dụng code có sẵn trong dự án hoặc xóa code thừa (`-48`, `+1`).

---

## 2. Tinh hoa Hấp thụ: "Thang 7 nấc Lười biếng" (The 7-Rung Ladder of Laziness)

Hình tượng "Lão kỹ sư già buộc tóc đuôi ngựa" (Ponytail) đại diện cho tư duy kỹ sư thực chiến đỉnh cao: **"Đoạn code xịn nhất là đoạn code bạn KHÔNG BAO GIỜ phải viết."**

Toàn bộ AI trong hệ thống HuyNex khi nhận lệnh viết code hoặc sửa bug BẮT BUỘC phải leo qua 7 bậc thẩm định trước khi gõ dòng code đầu tiên:

1. **Bậc 1 — Cần thiết thực tế (YAGNI - You Aren't Gonna Need It):**
   * Đoạn code hoặc tính năng này có thực sự cần thiết để giải quyết đúng mục tiêu hiện tại không?
   * Tuyệt đối không phỏng đoán nhu cầu tương lai ("đề phòng sau này cần") để viết sẵn abstraction hoặc configuration rườm rà.
2. **Bậc 2 — Tái sử dụng trong Codebase (Reuse):**
   * Quét tìm trong dự án xem đã có hàm, utility, helper hoặc pattern tương tự chưa.
   * Ưu tiên tái sử dụng hoặc gọi lại hàm có sẵn, nghiêm cấm viết lại một hàm tương tự.
3. **Bậc 3 — Thư viện chuẩn của ngôn ngữ (Standard Library First):**
   * Thư viện dựng sẵn của ngôn ngữ (Python stdlib: `pathlib`, `json`, `hashlib`, `urllib`; JavaScript: `fetch`, `URL`, `Array methods`...) có xử lý được không?
   * Tuyệt đối không cài thêm package ngoài nếu thư viện chuẩn đã có.
4. **Bậc 4 — Nền tảng Native (Native Platform First):**
   * Hệ điều hành hoặc Trình duyệt có sẵn tính năng không?
   * Ví dụ: Dùng thẻ HTML5 `<input type="date">` hoặc CSS `@starting-style` thay vì cài thêm thư viện date-picker hay animation cồng kềnh.
5. **Bậc 5 — Tận dụng Phụ thuộc hiện có (In-Tree Dependencies):**
   * Nếu stdlib/native không có, kiểm tra các package đã cài sẵn trong `package.json` hoặc `requirements.txt`.
   * Nghiêm cấm tự tiện thêm dependency mới vào dự án khi chưa chứng minh được sự bất khả kháng.
6. **Bậc 6 — Tối giản dòng code (Concise & Direct):**
   * Có thể giải quyết logic một cách mạch lạc, dễ đọc trong 1-2 dòng không?
   * Loại bỏ hoàn toàn thói quen tạo lớp bọc một lần dùng (one-off wrapper).
7. **Bậc 7 — Mức tối thiểu tuyệt đối (Absolute Minimal Code):**
   * Khi bắt buộc phải viết code mới, chỉ viết đúng lượng code nhỏ nhất đủ để đáp ứng yêu cầu và pass bộ kiểm thử (Verification Gate).

---

## 3. Thực thi & Đồng bộ Hệ thống

- Đã đưa nguyên văn chuẩn mực này vào **Mục 3 (Sửa code đơn giản và đúng phạm vi)** trong [core.md](file://{{WORKSPACE_ROOT}}/00_Tru_so/ADOS/governance/brain/source/core.md).
- Đã chạy đồng bộ qua bộ công cụ phát hành `sync.py --apply`, cập nhật tức thì đến toàn bộ 35 đích cấu hình (bao gồm Claude Code, Gemini, Codex, Cursor rules trên toàn bộ các dự án).
- Không phát sinh thêm bất kỳ package, server nền hay file rác nào trên máy.
