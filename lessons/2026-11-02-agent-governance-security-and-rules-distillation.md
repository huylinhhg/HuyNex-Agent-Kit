# Bài học: Quản trị Agent nâng cao — Bảo mật cấu hình, Chưng cất quy tắc và Chốt chặn Runtime an toàn

- **Ngày ghi nhận**: 02/11/2026
- **Phạm vi**: Toàn bộ hệ sinh thái HuyNex và môi trường vận hành của AI Coding Agents (Antigravity, Cursor, Claude Code, Codex...).
- **Nguồn**: Đúc kết từ nghiên cứu hệ thống ECC theo phê duyệt của Huy ("học và tiếp thu ghi nhớ vĩnh viễn vào hệ thống, không để quên").

---

## 1. Bối cảnh & Mục tiêu

Khi các AI Agent có quyền can thiệp sâu vào file hệ thống, thực thi lệnh shell và quản lý mã nguồn, nếu chỉ dựa vào các câu lệnh nhắc nhở bằng lời (prompting) thì hệ thống sẽ tiềm ẩn rủi ro:
1. Vô tình làm lộ API keys / Tokens cá nhân trong các file cấu hình Agent.
2. Quy tắc (Rules) bị phình to vô tận qua thời gian (béo phì dữ liệu) khiến Agent bị ngợp ngữ cảnh.
3. Nhầm lẫn giữa "lời khuyên trong prompt" và "chốt chặn kỹ thuật thực tế".

---

## 2. Ba Trụ cột Quản trị Bắt buộc (The 3 Pillars of Agent Governance)

### Trụ cột 1: Bảo mật cấu hình Agent (AgentShield Pattern)
* Trong mọi đợt kiểm toán của skill `security-audit` và bảo trì hệ thống, Agent BẮT BUỘC rà soát:
  - **File cấu hình Agent**: `.claude/`, `.cursor/`, `.gemini/`, `settings.json`, `mcp.json`.
  - **Tuyệt đối không hardcode bí mật**: Không bao giờ ghi trực tiếp API keys, token, mật khẩu vào các file chỉ dẫn (`AGENTS.md`, `CLAUDE.md`, `rules/`) hoặc file cấu hình MCP. Mọi secret phải nằm trong `.env` đã được ignore bởi Git.
  - **Chặn cấp quyền vô hạn (Wildcard Ban)**: Nghiêm cấm cấp quyền chạy lệnh tự do không giới hạn kiểu `Bash(*)` hay quyền root/sudo không kiểm soát.

### Trụ cột 2: Chưng cất quy tắc tinh gọn (Rules Distillation — Anti-Bloat)
* **Nguyên tắc "Less is More"**: Tuyệt đối không tích trữ hàng trăm file rule vụn vặt làm bẩn context window của Agent.
* **Quy trình chưng cất**: Định kỳ rà soát các bài học kinh nghiệm phát sinh; cứ 5–10 bài học nhỏ có tính tương đồng phải được "chưng cất" lại thành 1 nguyên tắc cốt lõi duy nhất và cập nhật vào `core.md`.
* Giữ cho bộ não của Agent luôn sắc bén, ngắn gọn và tập trung 100% vào công việc thực tế thay vì phải đọc một rừng quy tắc rườm rà.

### Trụ cột 3: Chốt chặn Runtime cứng (Deterministic Hard Guardrails)
* **Phân định rõ ranh giới**: Hướng dẫn bằng văn bản (prompt/instructions) chỉ là ranh giới chuẩn mực (soft policy). Không bao giờ coi một câu prompt là chốt chặn bất khả xâm phạm.
* **Cưỡng chế kỹ thuật (Hard Capability)**:
  - Mọi thao tác rủi ro cao (Level 3 — The Board Approval Gate: sửa governance cốt lõi, xóa dữ liệu lớn, can thiệp hạ tầng) bắt buộc phải qua cơ chế kiểm duyệt chữ ký và xác nhận rõ ràng của Huy (`approved_by: 'Huy'`).
  - Dùng môi trường cô lập (Isolated Workspace, worktree, branch) trước khi chạy các tác vụ thử nghiệm hoặc suite test lớn.

---

## 3. Bằng chứng kiểm chứng & Vị trí áp dụng

- Đã tích hợp tiêu chí quét bảo mật cấu hình Agent vào checklist của skill `security-audit`.
- Đã đồng bộ tri thức quản trị vào sổ tay vận hành của ADOS Brain tại `00_Tru_so/ADOS/governance/brain/`.
