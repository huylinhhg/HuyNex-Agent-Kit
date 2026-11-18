# Phân Tách Kỹ Năng Chuyên Biệt Theo Dự Án (Project-Scoped Skills)
## Chống Quá Tải Context Window & Tối Ưu Hóa Trí Thông Minh Của Agent

> *"Không nạp bừa bãi toàn bộ kỹ năng framework nặng vào Global. Tách biệt rõ ràng giữa Kỹ năng Tư duy Cốt lõi (Global) và Kỹ năng Công nghệ Đặc thù (Project-Scoped)."*

---

## 1. Vấn Đề Lạm Dụng Kỹ Năng Toàn Cục (Global Bloat)

Khi hệ thống tích lũy nhiều kỹ năng (Agent Skills), việc cài đặt tất cả vào thư mục Global (`~/.agents/skills/` hoặc config toàn cục) sẽ gây ra thảm họa:
- **Tiêu tốn từ 15.000 đến 40.000 token ngay từ câu chào đầu tiên** chỉ để nạp mô tả của hàng chục skill không liên quan.
- **Làm suy giảm trí thông minh của LLM (Attention Degradation)**: Agent bị ngợp bởi quá nhiều hướng dẫn mâu thuẫn giữa các framework.
- **Lãng phí chi phí API** nhân lên theo từng turn hội thoại.

---

## 2. Kiến Trúc Phân Tầng Kỹ Năng (Two-Tier Skill Architecture)

Hệ thống phân định rạch ròi 2 cấp độ:

```
┌─────────────────────────────────────────────────────────────┐
│ 🌍 TẦNG 1: GLOBAL SKILLS (Kỹ năng Tư duy & Phương pháp luận) │
│ - Chỉ giữ các kỹ năng cốt lõi: TDD, Code Review, Debug,     │
│   Design Standard, Security Audit.                          │
│ - Dung lượng nhẹ, dùng cho mọi dự án, mọi ngôn ngữ.         │
└────────────────────────────────┬────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 📁 TẦNG 2: PROJECT-SCOPED SKILLS (Kỹ năng Công nghệ Đặc thù)│
│ - Các framework nặng: Remotion, Cloudflare, Kubernetes,     │
│   Figma API, Terraform, specialized SDKs...                 │
│ - Lưu trữ tại kho thư viện dùng chung (`skills-library/`).   │
│ - CHỈ nạp vào `.agents/skills/` của ĐÚNG DỰ ÁN CẦN DÙNG.    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Quy Tắc Triển Khai

1. **Kiểm tra trước khi nạp**: Khi mở một dự án cụ thể, Agent kiểm tra `package.json` hoặc `pyproject.toml`. Nếu dự án có sử dụng công nghệ đặc thù (ví dụ: Remotion để làm video, AWS CDK để hạ tầng), Agent mới chủ động trỏ/symlink kỹ năng từ kho thư viện vào dự án đó.
2. **Không để lại rác**: Khi hoàn thành hoặc đóng dự án, kho Global của hệ điều hành vẫn luôn ở trạng thái tinh gọn, nhẹ nhàng nhất.
