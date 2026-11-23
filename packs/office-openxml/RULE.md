# Extension Pack: Office OpenXML (ECMA-376) Quality & Anti-Corruption Guard

> Dành riêng cho các tác vụ sinh, định dạng và xử lý tài liệu văn phòng (Word, Excel, PowerPoint) qua OpenXML hoặc thư viện chuyên dụng (python-docx, openpyxl, xlsxwriter, python-pptx).

---

## 1. Microsoft Word (.docx) — Quy Chuẩn OpenXML Khắt Khe

1. **Đánh số trang (Header / Footer)**:
   - BẮT BUỘC dùng thẻ đơn `<w:fldSimple w:instr="PAGE"/>`.
   - TUYỆT ĐỐI KHÔNG gộp nhiều `w:fldChar` (`begin`, `separate`, `end`) và `w:instrText` vào cùng một `<w:r>` (Word sẽ coi là file hỏng *"unreadable content"*).
   - Header/Footer không bao giờ được rỗng (luôn giữ tối thiểu 1 `<w:p>`).
2. **Bảng biểu (Tables)**:
   - Viền và padding bảng phải đặt ở cấp Bảng (`<w:tblBorders>`, `<w:tblCellMar>` trong `<w:tblPr>`), không gắn cục bộ từng ô.
   - Thứ tự thẻ con bắt buộc trong `<w:tcPr>`: `tcW` → `tcBorders` → `shd` → `noWrap` → `tcMar` → `vAlign`.
   - Thứ tự thẻ con bắt buộc trong `<w:trPr>`: `cantSplit` → `tblHeader`.

---

## 2. Microsoft Excel (.xlsx) — Toàn Vẹn Cấu Trúc & Hiệu Năng

1. **Sheet & Vùng dữ liệu**:
   - Tên sheet không quá 31 ký tự và không chứa ký tự cấm: `[:\/?*[]]`.
   - Không áp dụng format cell trên toàn bộ cột/hàng trống vô tận (tránh phình to dung lượng từ vài KB lên hàng chục MB).
2. **Merge Cells**:
   - Dữ liệu chỉ được ghi vào ô góc trên bên trái (Top-Left Cell). Định dạng viền phải bao phủ toàn bộ ô trong vùng merge.
3. **Công thức & Dữ liệu**:
   - Công thức tính toán phải dùng tên hàm tiếng Anh chuẩn (`SUM`, `AVERAGE`, `VLOOKUP`...).
   - Kiểu số và ngày tháng không lưu dưới dạng chuỗi text.

---

## 3. Microsoft PowerPoint (.pptx)

1. Tỷ lệ slide chuẩn 16:9 widescreen.
2. Text box tự co giãn tránh tràn khung nhìn (Overflow).

---

## 4. Verification Gate Bắt Buộc

BẮT BUỘC chạy kiểm tra mở file thành công bằng ứng dụng Microsoft Office hoặc trình đọc OpenXML tương ứng trước khi báo hoàn thành cho người dùng.
