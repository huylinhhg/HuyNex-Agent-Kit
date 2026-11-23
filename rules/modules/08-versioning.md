# Module 08 — Phiên bản và release

- Khi làm release management: SemVer 2.0.0 và Keep a Changelog 1.1.0. `VERSION` ở gốc chứa đúng một chuỗi version, không tiền tố `v`/khoảng trắng thừa; tag chính thức là `vMAJOR.MINOR.PATCH`.
- Changelog có `## [Unreleased]`, Quick Matrix và các nhóm H3: `🚀 Added`, `🔄 Changed`, `⚡ Performance`, `🔒 Security`, `🛠 Fixed`, `🎨 Style & UI`, `🗑️ Removed`.
- Không tự bump version trừ khi được yêu cầu hoặc thay đổi breaking/feature/fix thuộc scope release đã giao. Không bịa release cho sửa workspace. Khi chuẩn hóa release management, bộ tài liệu gồm VERSION, VERSIONING.md, RELEASE_POLICY.md, CHANGELOG.md và README.md.
