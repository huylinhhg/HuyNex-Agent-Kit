# HuyNex Agent Kit — Root Rules Template

> Sao chép file này vào `~/.claude/CLAUDE.md` hoặc cấu hình Agent toàn cục.

<!-- HUY_LOCAL_BRAIN_START -->
# HuyNex Agent Kit — Shared Principles

Bộ quy tắc chung cho AI Coding Agents (Claude Code, Antigravity, Cursor, Codex).
Hướng dẫn dự án bổ sung phạm vi riêng. Chỉ nạp tài liệu chi tiết khi cần.

## Quy tắc sống còn (inline — không được tách)

- **Brutal Honesty**: Không nịnh hót; phát hiện rủi ro → cảnh báo ngay kèm phương án.
- **Zero-Guessing**: Tuyệt đối không sáng tác số hiệu, ngày tháng, thông tin xác thực. Thiếu → để trống đỏ [Chưa rõ] hoặc hỏi người dùng.
- **Conservation Gate**: Khi bóc tách/chuyển đổi dữ liệu → kiểm toán hash/count đầu vào–đầu ra; không để mất dữ liệu lặng lẽ.
- **Board Approval Gate**: Level 3 (sửa governance, xóa thư mục lớn, can thiệp sâu hệ điều hành) → dừng lại, xuất kế hoạch, chờ phê duyệt.
- **Single-Root Safety**: Cấm `rm -rf` / `Remove-Item -Recurse` trên thư mục gốc workspace hoặc các thư mục phân cấp cha.
- **Git Auto-Sync**: `git pull --ff-only` chỉ 1 lần/phiên khi mở. Push chỉ khi hoàn thành milestone/được yêu cầu rõ. Không dùng `--force`.
- **Semantic Distillation**: Trước khi nạp output dài (git diff, test log, build log) vào LLM → dùng tool lọc/distill để cắt tối thiểu 60% token rác.

## Modules chi tiết

@rules/modules/01-communication.md
@rules/modules/02-truth-context.md
@rules/modules/03-code-engineering.md
@rules/modules/04-data-safety.md
@rules/modules/05-verification.md
@rules/modules/06-collaboration.md
@rules/modules/07-permissions-memory.md
@rules/modules/08-versioning.md
@rules/modules/09-workspace-layout.md
<!-- HUY_LOCAL_BRAIN_END -->
