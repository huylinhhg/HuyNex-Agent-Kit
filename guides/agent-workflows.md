# Quy Trình Phối Hợp AI Agent Chuẩn Mực (Agent Workflows)

## 1. Quy Trình Chẩn Đoán Lỗi (Hard Bug Diagnosis Loop)
1. **Dựng Vòng Phản Hồi (Feedback Loop)**: Viết một test case hoặc curl command tái hiện đúng lỗi đó và thất bại (Red).
2. **Cô Lập & Giả Thuyết**: Phân tích log, đặt giả thuyết nguyên nhân gốc rễ.
3. **Can Thiệp Tối Thiểu**: Sửa đúng dòng lỗi theo Thang 7 nấc lười biếng.
4. **Kiểm Chứng (Green)**: Chạy lại vòng lặp phản hồi để chứng minh lỗi đã biến mất.

## 2. Quy Trình Tạo Kỹ Năng Mới (Skill Creation Workflow)
1. Kích hoạt skill `skill-creator`.
2. Phân tích bối cảnh kích hoạt tự động (Triggers).
3. Viết `SKILL.md` và sinh bộ kiểm thử (Positive/Negative).
4. Dùng `skill-reviewer` để audit chấm điểm đạt 100/100 trước khi chia sẻ.
