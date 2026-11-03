---
name: skill-reviewer
description: Đánh giá chất lượng, tính an toàn, token economy và độ tin cậy của AI Agent Skills theo chuẩn Agent Skills mở. Kiểm tra vi phạm rò rỉ dữ liệu, xung đột ngữ nghĩa và hiệu quả kích hoạt tự động.
---

# Skill Reviewer — Bộ Tiêu Chuẩn Thẩm Định & Chấm Điểm Kỹ Năng

Skill này hướng dẫn Agent hoặc kỹ sư tiến hành kiểm toán (Audit) toàn diện một file `SKILL.md` hoặc thư mục skill trước khi phát hành công khai.

---

## 1. Bảng Điểm Đánh Giá 100 Điểm (Skill Quality Rubric)

| Tiêu chí | Trọng số | Yêu cầu bắt buộc |
|---|:---:|---|
| **1. Định dạng & Metadata** | 20đ | Frontmatter YAML hợp lệ (`name`, `description`). Tên dạng kebab-case. Description dưới 300 ký tự có điều kiện kích hoạt rõ ràng. |
| **2. Tối ưu Token Economy** | 20đ | Dưới 2.500 từ. Không dài dòng triết lý suông; tập trung 100% vào chỉ dẫn hành động (actionable rules). Không copy nguyên mẫu code thừa. |
| **3. Chống Rò Rỉ Dữ liệu (Zero-Leak)** | 25đ | **Bắt buộc 100% sạch**: Không chứa API key, token, email cá nhân, số điện thoại, đường dẫn máy tính tuyệt đối (`/Users/...`, `C:\...`). |
| **4. Ranh giới & Chống Ảo giác** | 20đ | Có mục Ranh giới (Scope/Non-goals) rõ ràng. Quy định Verification Gate trước khi tuyên bố hoàn thành. |
| **5. Bộ Kiểm thử Đi kèm (Verification)** | 15đ | Có sẵn kịch bản kiểm thử (Positive, Negative, Boundary). |

---

## 2. Quy trình Kiểm Toán 4 Bước

### Bước 1: Quét Tĩnh (Static Linting)
1. Kiểm tra cấu trúc thư mục: Thư mục chứa `SKILL.md`, có thể có `references/`, `scripts/` hoặc `templates/`.
2. Kiểm tra tính hợp lệ của YAML Frontmatter:
   ```yaml
   ---
   name: my-skill-name
   description: Action-oriented trigger description.
   ---
   ```
3. Đếm số token ước tính (tỷ lệ 1 token ~ 4 ký tự). Nếu tổng dung lượng `SKILL.md` vượt quá 15KB, bắt buộc phải yêu cầu chưng cất ngữ nghĩa (Data Distillation) tách các tài liệu tham khảo dài vào thư mục con `references/`.

### Bước 2: Quét Bảo Mật & Khử Trùng (Secret & PII Audit)
Chạy regex quét:
- Token: `sk-[a-zA-Z0-9]+`, `ghp_[a-zA-Z0-9]+`, `bearer\s+`
- Path cá nhân: `/Users/[^/\s]+`, `C:\\Users\\[^\\\s]+`
- Email: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`

### Bước 3: Đánh Giá Bối Cảnh Kích Hoạt (Trigger Quality)
- **Quá hẹp (Under-triggering)**: Chỉ kích hoạt khi gõ đúng 1 từ tiếng Anh $\rightarrow$ Cần bổ sung thêm ngữ cảnh tiếng Việt và tình huống thực tế.
- **Quá rộng (Over-triggering)**: Kích hoạt cả trong những tác vụ không liên quan $\rightarrow$ Cần bổ sung từ khóa phủ định và ranh giới.

### Bước 4: Xuất Báo Cáo Thẩm Định
Xuất báo cáo theo định dạng:
```markdown
# KẾT QUẢ THẨM ĐỊNH SKILL: <tên-skill>
- Tổng điểm: XX/100 (ĐẠT / KHÔNG ĐẠT)
- Secret Scanning: CLEAN / WARNINGS
- Token Footprint: ~XXX tokens (Tối ưu)
- Các điểm cần khắc phục:
  1. ...
  2. ...
```
