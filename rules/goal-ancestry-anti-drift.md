# Phả Hệ Mục Tiêu & Chống Lệch Hướng (Goal Ancestry & Anti-Drift)
## Giữ Vững Ranh Giới Logic Trong Hệ Thống Đa Agent (Multi-Agent Workflows)

> *"Mỗi sub-task hoặc lệnh gọi subagent BẮT BUỘC phải truy nguyên trực tiếp về Mục tiêu gốc (Root Goal). Tuyệt đối cấm tự ý mở rộng phạm vi hoặc tuyên bố hoàn thành khi chưa kiểm chứng."*

---

## 1. Hiện Tượng Lệch Hướng (Agent Drift)

Trong các tác vụ phức tạp gồm nhiều bước (multi-turn) hoặc khi phân rã cho subagent, các mô hình ngôn ngữ thường gặp hiện tượng:
1. **Lạc đề dần theo thời gian (Context Drift)**: Bước sau quên mất mục tiêu cốt lõi của bước trước.
2. **Tự ý phình to phạm vi (Scope Creep)**: Tự động thêm các tính năng speculative, refactor các đoạn code không liên quan hoặc cài thêm thư viện thừa.
3. **Ảo giác hoàn thành (Hallucinated Completion)**: Tự tuyên bố hoàn thành xuất sắc trong khi chưa hề chạy kiểm thử hoặc đối chiếu với yêu cầu ban đầu.

---

## 2. Tiêu Chuẩn 3 Trường Bắt Buộc (The 3-Field Ancestry Contract)

Mỗi khi điều phối, phân rã tác vụ hoặc giao việc cho subagent, prompt phân quyền **BẮT BUỘC** phải truyền đủ 3 thông số:

```markdown
- root_goal: [Mục tiêu kinh doanh / kỹ thuật gốc cần đạt được]
- scope: [Phạm vi ranh giới cụ thể: Những file/hàm ĐƯỢC PHÉP chạm vào và KHÔNG ĐƯỢC PHÉP chạm vào]
- acceptance_criteria: [Tiêu chí nghiệm thu quan sát được bằng lệnh thật / bài test thật]
```

### Ví Dụ Mẫu:
```json
{
  "root_goal": "Tối ưu hóa thời gian tải trang Dashboard từ 2.5s xuống dưới 800ms",
  "scope": "Chỉ tối ưu truy vấn SQL trong service `analytics_service.py` và thêm index DB; KHÔNG sửa frontend UI, KHÔNG đổi API schema",
  "acceptance_criteria": "Chạy script `benchmark_queries.py` đạt thời gian phản hồi p95 < 200ms; toàn bộ 15 integration tests hiện tại đều PASS"
}
```

---

## 3. Rào Chắn Nghiệm Thu (Verification Gate)

1. **Không mở rộng ngoài Scope**: Agent nhận việc tuyệt đối không tự ý sửa đổi kiến trúc ngoài phạm vi được giao. Nếu phát hiện vấn đề phụ phát sinh, phải ghi chú lại vào báo cáo, không tự ý sửa.
2. **Cổng kiểm chứng trước khi bàn giao**: Trước khi trả lời người dùng hoặc gửi kết quả về cho Agent điều phối, Agent BẮT BUỘC phải chạy lệnh kiểm chứng theo đúng `acceptance_criteria` ban đầu.
3. **Trung thực về trạng thái**: Chỉ sử dụng các nhãn `IMPLEMENTED`, `VERIFIED`, `BLOCKED` khi có bằng chứng chạy lệnh (exit code 0, test pass). Nghiêm cấm tạo bằng chứng giả.
