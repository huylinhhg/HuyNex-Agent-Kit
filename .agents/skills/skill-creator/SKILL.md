---
name: skill-creator
description: Framework thiết kế, xây dựng và sinh bộ kiểm thử tự động cho AI Agent Skills theo chuẩn Agent Skills mở (.agents/skills). Hướng dẫn phân tích bối cảnh kích hoạt (triggers), ranh giới trách nhiệm, tối ưu token economy và sinh test case xác minh trước khi phát hành.
---

# Skill Creator — Tiêu chuẩn Xây dựng Kỹ năng AI Agent Chuyên nghiệp

Skill này hướng dẫn Agent và lập trình viên thiết kế, đóng gói và xác minh một **Agent Skill** đạt tiêu chuẩn cao cấp nhất, tương thích đa nền tảng (Antigravity, Claude Code, Codex, Cursor).

---

## 1. Vòng đời Xây dựng Kỹ năng (5 Pha Chuyên sâu)

```
[1. Phân tích Nhu cầu] ──> [2. Thiết kế Kích hoạt] ──> [3. Soạn thảo SKILL.md] ──> [4. Sinh Kiểm thử] ──> [5. Thẩm định & Đóng gói]
```

### Pha 1: Phân tích Nhu cầu & Ranh giới (Boundary Analysis)
Trước khi gõ một dòng code, trả lời 3 câu hỏi cốt lõi:
1. **Mục tiêu gốc (Root Goal)**: Skill này giải quyết bài toán gì mà prompt thông thường hay làm hỏng hoặc làm dở dang?
2. **Thang 7 nấc kỹ sư tối giản (Ladder of Laziness)**: Nhiệm vụ này có thể giải quyết bằng lệnh shell native hoặc thư viện chuẩn không? Có thực sự cần tạo một skill riêng biệt không?
3. **Phạm vi & Ranh giới (Scope & Non-Goals)**: Skill này **LÀM GÌ** và dứt khoát **KHÔNG ĐƯỢC LÀM GÌ**? (Ví dụ: Skill phân tích lỗi chỉ chẩn đoán, không tự ý sửa code ngoài phạm vi).

### Pha 2: Thiết kế Bối cảnh Kích hoạt (Proactive Trigger Design)
Một skill chỉ thực sự có giá trị khi Agent **tự động nhận diện đúng lúc** mà không bắt người dùng phải nhớ câu lệnh slash hay từ khóa phức tạp:
- **Từ khóa tự nhiên**: Gồm các cụm từ nói thường ngày bằng cả tiếng Việt và tiếng Anh.
- **Tình huống nghiệp vụ**: Các trạng thái lỗi, loại tệp tin mở ra, hoặc ngữ cảnh tác vụ (ví dụ: phát hiện lỗi mở file Word `.docx` $\rightarrow$ tự kích hoạt skill sửa OpenXML).
- **Tránh kích hoạt nhầm (False Positive Guard)**: Đặt điều kiện phủ định rõ ràng (ví dụ: "KHÔNG kích hoạt cho việc chỉnh sửa text văn bản thông thường").

### Pha 3: Soạn thảo `SKILL.md` Chuẩn hóa
Cấu trúc file `SKILL.md` bắt buộc tuân theo:

```markdown
---
name: <ten-skill-kebab-case>
description: <Mo-ta-ngan-duoi-300-ky-tu-neu-ro-chuc-nang-va-dieu-kien-kich-hoat-tu-dong>
---

# Tên Kỹ Năng Đầy Đủ

## 1. Nguyên tắc Cốt lõi & Ranh giới (Core Principles & Boundaries)
- Quy tắc 1
- Quy tắc 2

## 2. Quy trình Thực thi Từng bước (Step-by-Step Workflow)
- Bước 1: Thu thập thông tin & Khảo sát
- Bước 2: Phân tích nguyên nhân gốc rễ
- Bước 3: Đề xuất phương án & Xác minh

## 3. Chốt chặn Kiểm chứng (Verification Gate)
- Tiêu chí nghiệm thu quan sát được
- Kiểm tra tính toàn vẹn (Checksum / Entity Count)
```

### Pha 4: Sinh Bộ Kiểm thử Tự động (Automated Verification Generator)
Mỗi skill khi tạo ra bắt buộc phải có ít nhất 2 kịch bản kiểm thử:
1. **Positive Test Case**: Agent nhận prompt chứa ngữ cảnh kích hoạt $\rightarrow$ Kích hoạt thành công và cho ra kết quả đúng spec.
2. **Negative Test Case**: Agent nhận prompt nằm ngoài phạm vi $\rightarrow$ Từ chối kích hoạt, không can thiệp bừa bãi.
3. **Boundary Test Case**: Xử lý dữ liệu xấu, dữ liệu rỗng hoặc tình huống lỗi.

### Pha 5: Thẩm định Chất lượng & Bảo mật (Sanitization & Quality Gate)
- **Token Economy**: Nội dung `SKILL.md` súc tích, lược bỏ văn phong rườm rà. Chỉ giữ lại chỉ dẫn hành động (Actionable directives).
- **Secret Scanning**: Không chứa bất kỳ đường dẫn máy cá nhân cứng (`/Users/...`, `C:\...`), API key hay token.
- **ECMA-376 / Standard Compliant**: Nếu thao tác với dữ liệu có chuẩn quốc tế, bắt buộc tuân thủ đúng spec.
