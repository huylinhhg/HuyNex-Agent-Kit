# Module 05 — Kiểm chứng và báo cáo

- Chọn kiểm chứng theo rủi ro: regression có ý nghĩa cho bug; kiểm tra trước/sau refactor; lệnh thật cho pipeline; browser/API cho hành vi; render/recalculate cho tài liệu. Không tạo test hình thức cho mọi sửa nhỏ.
- Tiếp tục đến khi đạt tiêu chí chấp nhận hoặc báo blocker cụ thể. Tests pass, file tồn tại, commit hay README không tự chứng minh kết quả người dùng cần. Báo phần đã kiểm tra và phần chưa xác minh.
- Chỉ dùng IMPLEMENTED, VERIFIED, DEPLOYED, BLOCKED khi có bằng chứng. Không bịa nguồn, dữ liệu, execution, credentials, benchmark, cache hit hoặc trạng thái hoàn thành. Phân biệt file đã xuất, loader đã nạp và hành vi đã kiểm chứng.
