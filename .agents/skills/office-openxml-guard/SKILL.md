---
name: office-openxml-guard
description: Bộ quy chuẩn và giải pháp kỹ thuật tạo, chỉnh sửa và xuất file Microsoft Office (.docx, .xlsx, .pptx) bằng Python/OpenXML tuân thủ nghiêm ngặt chuẩn ECMA-376. Triệt tiêu vĩnh viễn lỗi 'Word/Excel found unreadable content' và hiện tượng đơ lag 100% CPU khi cuộn trang bảng biểu.
---

# Office OpenXML Guard — Kỹ Thuật Xử Lý Tài Liệu Office Chống Lỗi & Tối Ưu Hiệu Năng

Skill này hướng dẫn Agent và lập trình viên thao tác với các thư viện sinh tài liệu Office (`python-docx`, `openpyxl`, `xlsxwriter`, `python-pptx`, OpenXML lxml) mà không bao giờ gặp lỗi hỏng file hoặc sụt giảm hiệu năng nghiêm trọng trên máy người dùng.

---

## 1. Đối Với Microsoft Word (`.docx` / WordprocessingML)

### A. Triệt tiêu Lỗi "Unreadable Content" ở Header & Footer
1. **Tuyệt đối không để Header/Footer rỗng**:
   - Theo chuẩn **ECMA-376 Part 1, §17.10.3**, `<w:ftr>` và `<w:hdr>` bắt buộc phải chứa tối thiểu một phần tử cấp khối (`<w:p>` hoặc `<w:tbl>`).
   - Khi tạo trang bìa không số trang (`different_first_page_header_footer = True`), nghiêm cấm xóa toàn bộ paragraphs trong `first_page_footer`. Luôn giữ lại một đoạn văn rỗng (`<w:p/>`).
2. **Số trang chuẩn**:
   - Sử dụng thẻ đơn `<w:fldSimple w:instr="PAGE"/>`.
   - Tuyệt đối không nhét nhiều `w:fldChar` (`begin`, `separate`, `end`) và `w:instrText` vào cùng một thẻ `<w:r>`.

### B. Triệt tiêu Giật Lag và Đơ CPU 100% khi Cuộn Bảng Biểu
1. **Đặt viền và đệm ô ở Cấp Bảng (Table-Level)**:
   - Nghiêm cấm duyệt qua từng ô trong bảng 30-50 trang để chèn `<w:tcBorders>` và `<w:tcMar>`. Hành vi này buộc thuật toán giải quyết xung đột viền của Word chạy trên từng khung hình, làm nghẽn CPU 100%.
   - Thiết lập đường viền chung tại `<w:tblBorders>` và lề đệm tại `<w:tblCellMar>` bên trong `<w:tblPr>`.
2. **Tuân thủ đúng thứ tự thẻ con theo lược đồ XSD**:
   - Trong `<w:tcPr>`: `tcW` $\rightarrow$ `tcBorders` $\rightarrow$ `shd` $\rightarrow$ `noWrap` $\rightarrow$ `tcMar` $\rightarrow$ `vAlign`.
   - Trong `<w:trPr>`: `cantSplit` $\rightarrow$ `tblHeader`.

---

## 2. Đối Với Microsoft Excel (`.xlsx` / SpreadsheetML)

1. **Quy tắc Tên Sheet**:
   - Độ dài tối đa **31 ký tự**.
   - Không chứa bất kỳ ký tự cấm nào: `\`, `/`, `?`, `*`, `[`, `]`, `:`.
2. **Vùng Merge Cells**:
   - Chỉ ghi dữ liệu vào **ô góc trên bên trái (Top-Left Cell)**. Các ô còn lại trong vùng merge để trống dữ liệu.
   - Định dạng viền (Border) phải bao phủ toàn bộ các ô trong vùng merge để tránh vỡ khung nhìn.
3. **Công thức & Dữ liệu**:
   - Tên hàm bắt buộc dùng tiếng Anh viết hoa chuẩn: `SUM`, `AVERAGE`, `COUNTIF`, `VLOOKUP`.
   - Kiểu số và ngày tháng phải gán đúng kiểu dữ liệu (Numeric / Datetime), không lưu dưới dạng chuỗi Text.
   - Không format cell trên toàn bộ cột hoặc hàng trống vô tận tránh phình dung lượng file lên hàng chục MB.

---

## 3. Đối Với Microsoft PowerPoint (`.pptx` / PresentationML)

1. Tỷ lệ slide chuẩn hiện đại là **16:9** (`13.333 x 7.5 inches`).
2. Text box phải bật chế độ tự co giãn văn bản (`word_wrap = True`) để tránh tràn khung hình khi mở trên các máy có độ phân giải hoặc font rendering khác nhau.

---

## 4. Chốt Chặn Kiểm Chứng Thực Tế (Validation Gate)

Sau khi tạo hoặc chỉnh sửa file:
- Mở và kiểm tra trực tiếp bằng ứng dụng Microsoft Office thật trên máy tính trước khi báo hoàn thành.
- Nếu không thể mở Office trực tiếp, chạy validator phân tích cấu trúc XML qua script `scripts/validate_openxml.py`.
