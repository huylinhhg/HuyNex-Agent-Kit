# Bài học: Khắc phục lỗi mở file và giật lag cuộn trang trong tài liệu Word (OpenXML/ECMA-376)

- **Ngày ghi nhận**: 17/10/2026
- **Phạm vi**: Toàn bộ quy trình xử lý, định dạng và xuất tài liệu Word (`.docx`) bằng script Python (`python-docx`, OpenXML, lxml).
- **Nguồn**: Phản hồi thực tế từ người dùng Huy trong một lượt xử lý tài liệu Word ("mở thì không được và cảm giác vuốt nó rất là bị lác bị lỗi").

## 1. Triệu chứng
1. Microsoft Word trên macOS không mở được tài liệu, báo lỗi "Word found unreadable content in..." hoặc treo (spinning wheel / CPU 100%) khi mở tài liệu.
2. Nếu mở được (sau khi Word tự sửa), khi cuộn hoặc vuốt qua các trang chứa bảng biểu dài (trên 30-35 trang), giao diện Word giật lag nghiêm trọng, FPS tụt dốc, tiến trình Microsoft Word chiếm 100% tài nguyên CPU.

## 2. Nguyên nhân kỹ thuật

### Nguyên nhân 1: Vi phạm nghiêm trọng lược đồ OpenXML đối với Footer/Header
- Trong script xử lý định dạng, khi muốn trang bìa không hiển thị số trang (`different_first_page_header_footer = True`), đoạn mã đã xóa toàn bộ các đoạn văn trong `first_page_footer`: `for p in list(first_ftr.paragraphs): p._element.getparent().remove(p._element)`.
- Điều này tạo ra một thẻ XML hoàn toàn rỗng: `<w:ftr xmlns:.../>`.
- Theo chuẩn **ECMA-376 Part 1, §17.10.3**, mô hình nội dung của `w:ftr` và `w:hdr` bắt buộc phải có ít nhất một phần tử cấp khối (`minOccurs="1"` đối với nhóm `(w:p | w:tbl | ...)`). Khi gặp `<w:ftr/>` rỗng, bộ phân tích cú pháp của Word coi file bị hỏng hoặc bị kẹt vô tận khi khởi tạo layout box.

### Nguyên nhân 2: Áp dụng đường viền và lề ô cục bộ trên từng ô thay vì cấp Bảng
- Script định dạng bảng đã duyệt qua từng ô của tất cả các bảng (hơn 1.000 ô trong tài liệu 35 trang) và chèn thẻ `<w:tcBorders>` cùng `<w:tcMar>` vào từng `w:tcPr`.
- Khi người dùng cuộn tài liệu, engine dựng hình của Word (CoreText/Quartz) buộc phải chạy thuật toán giải quyết xung đột đường viền (border conflict resolution algorithm) giữa các ô lân cận trên từng khung hình, khiến CPU đạt ngưỡng tối đa 100% và gây giật lag.

### Nguyên nhân 3: Vi phạm thứ tự thẻ con trong lược đồ OpenXML (Schema Ordering)
- Trong `<w:tcPr>`, thuộc tính `vAlign` bị đặt trước `tcBorders`, `tcMar` và `shd`.
- Trong `<w:trPr>`, thẻ `tblHeader` bị lặp lại nhiều lần bao quanh `cantSplit` (`['tblHeader', 'cantSplit', 'tblHeader']`).
- Các vi phạm thứ tự này kích hoạt cơ chế fallback parser chậm chạp của Word trên mỗi chu kỳ kết xuất trang.

### Nguyên nhân 4: Gộp các thẻ trường `w:fldChar` và `w:instrText` vào cùng một thẻ `<w:r>`
- Khi tạo số trang tự động ở Header/Footer bằng mã Python, một số script nhồi nhét cả 4 thẻ XML: `<w:fldChar w:fldCharType="begin"/>`, `<w:instrText> PAGE </w:instrText>`, `<w:fldChar w:fldCharType="separate"/>` và `<w:fldChar w:fldCharType="end"/>` vào **CÙNG MỘT PHẦN TỬ `<w:r>` DUY NHẤT**.
- Theo chuẩn ECMA-376 Part 1, §17.16.1, mỗi `w:fldChar` và `w:instrText` phải thuộc các run riêng biệt, hoặc tốt nhất là dùng cú pháp trường đơn giản `w:fldSimple`. Khi tất cả bị gộp vào 1 thẻ `<w:r>`, Microsoft Word coi đó là vi phạm cú pháp nghiêm trọng (XML Schema Corrupt) và từ chối mở file ("Word found unreadable content...").

## 3. Cách khắc phục và phòng tránh

1. **Không bao giờ để Header/Footer rỗng**:
   - Khi cần trang bìa trống footer, luôn giữ lại đúng 1 đoạn văn rỗng có định dạng chuẩn:
     ```python
     first_p = first_ftr.add_paragraph()
     first_p.paragraph_format.space_before = Pt(0)
     first_p.paragraph_format.space_after = Pt(0)
     pPr = first_p._p.get_or_add_pPr()
     pPr.insert(0, parse_xml(r'<w:pStyle %s w:val="Footer"/>' % nsdecls('w')))
     ```
   - Chạy hàm kiểm tra tự động duyệt toàn bộ các file `.xml` liên quan đến `header` và `footer` trong gói zip để xác nhận `len(root) > 0`.

2. **Luôn dùng `<w:fldSimple w:instr="PAGE"/>` cho số trang tự động**:
   - Tuyệt đối không dùng cụm `fldChar` phức tạp nhét chung run. BẮT BUỘC dùng thẻ trường đơn giản:
     ```python
     fldSimple = parse_xml(r'''
         <w:fldSimple %s w:instr="PAGE">
             <w:r>
                 <w:rPr>
                     <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                     <w:sz w:val="26"/>
                     <w:szCs w:val="26"/>
                 </w:rPr>
                 <w:t>1</w:t>
             </w:r>
         </w:fldSimple>
     ''' % nsdecls('w'))
     p_header._p.append(fldSimple)
     ```
   - Tương thích 100% với Microsoft Word trên mọi hệ điều hành (macOS, Windows, iOS, Android).

3. **Thiết lập viền và lề ở cấp Bảng (`<w:tblPr>`)**:
   - Định nghĩa `<w:tblBorders>` và `<w:tblCellMar>` ở thẻ `<w:tblPr>` của bảng.
   - Xóa bỏ triệt để `<w:tcBorders>` và `<w:tcMar>` ở từng ô, để Word sử dụng bộ nhớ đệm bố cục cấp bảng (Table-level cached layout), đảm bảo cuộn mượt mà 60fps.
   - Bảng chữ ký/xác nhận phân biệt rõ với bảng dữ liệu: bảng chữ ký dùng viền `none`, không gắn `tblHeader`.

4. **Áp dụng hàm chuẩn hóa thứ tự thẻ (Schema Sanitizer)**:
   - Trước khi lưu tài liệu, luôn chạy hàm chuẩn hóa thứ tự các thẻ con theo danh mục chuẩn ECMA-376 cho `pPr`, `trPr`, `tcPr` và `tblPr`:
     - `tcPr`: `tcW` → `tcBorders` → `shd` → `noWrap` → `tcMar` → `vAlign`.
     - `trPr`: `cantSplit` → `tblHeader`.
     - `pPr`: `pStyle` → `pageBreakBefore` → `spacing` → `jc`.

5. **Bắt buộc kiểm chứng mở file bằng Microsoft Word thật**:
   - Trước khi bàn giao kết quả cho người dùng, BẮT BUỘC chạy kiểm chứng mở file thực tế qua CLI/AppleScript:
     ```bash
     osascript -e 'tell application "Microsoft Word" to open file name "<full_path_to_docx>"'
     ```
   - Nếu file mở thành công không phát sinh prompt cảnh báo thì mới được coi là hợp lệ.

## 4. Giới hạn chứng cứ

Đây là bài học lịch sử do Mac lưu ngày 17/10/2026; lượt đồng bộ không chạy lại các phép đo hiệu năng hoặc kiểm chứng tài liệu gốc. Đường dẫn hồ sơ và tên tài liệu riêng được giữ trong backup local, không đưa vào nguồn chung. Các khẳng định hiệu năng và tương thích ở phần lịch sử không phải kết quả đã kiểm chứng cho mọi tài liệu hoặc mọi máy.
