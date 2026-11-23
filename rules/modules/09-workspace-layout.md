# Module 09 — Bố cục Workspace & Tiêu chuẩn Máy trạm Tinh gọn

- Kiến trúc cây thư mục đơn lẻ (Single-Tree Workspace Layout): Mỗi máy trạm duy trì một cây thư mục gốc duy nhất cho toàn bộ dự án. Các dự án đang hoạt động phân chia theo phạm vi rõ ràng; không nhân bản hoặc tạo workspace trùng lặp theo từng phiên chat của AI.
- Quản lý tệp tạm và bàn giao (Work/Output Separation): Trong mỗi workspace hoặc tác vụ lẻ, sử dụng thư mục `work/` cho các tệp trung gian/nháp và `outputs/` cho các bản giao chính thức. Khi hoàn tất nhiệm vụ, BẮT BUỘC nghiệm thu tệp tại `outputs/` và dọn sạch file nháp trong `work/` để chống phình to dung lượng ổ cứng.
- Bảo vệ dữ liệu đề xuất loại bỏ: Dữ liệu cũ hoặc thư mục nghi ngờ trùng lặp không xóa vội; ưu tiên di chuyển vào thư mục lưu trữ tạm (như `_archive/` hoặc `98_De_xuat_xoa/`) và kiểm tra đối chiếu hash trước khi xóa vĩnh viễn.
- Tiêu chuẩn máy trạm tinh gọn & hiệu năng cao (Power-User Zero-Bloat Standard):
  - Áp dụng triết lý Zero-Bloat trên cả macOS, Windows và Linux: Không chạy ngầm các ứng dụng dọn dẹp bên thứ ba hay updater daemon 24/7 gây lãng phí CPU/RAM.
  - Triệt tiêu độ trễ giao diện (Zero-Latency UI): Tối ưu tốc độ lặp phím (key repeat), độ nhạy chuột và phím tắt.
  - Bộ công cụ CLI hiện đại: Ưu tiên đồng bộ các công cụ dòng lệnh hiệu năng cao (`zoxide`, `eza`, `bat`, `fzf`, `ripgrep`).
- Quản lý phiên làm việc đa máy (Multi-Machine Discipline):
  - Khi luân chuyển làm việc giữa nhiều máy tính, đồng bộ mốc qua Git commit hoàn chỉnh (Task Milestone), không đẩy code dở dang làm rác Git log.
  - Tách bạch rõ ràng giữa cấu hình máy cục bộ (local settings, environment variables) và mã nguồn dự án được lưu trên Git.
