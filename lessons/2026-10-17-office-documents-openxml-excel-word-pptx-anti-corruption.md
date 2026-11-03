# Bài học: Quy chuẩn kỹ thuật tạo và xử lý tài liệu Office (Word, Excel, PowerPoint) chống lỗi hỏng file và đơ lag

- **Ngày ghi nhận**: 17/10/2026
- **Phạm vi**: Toàn bộ quy trình sinh, chỉnh sửa, định dạng và xuất các tài liệu văn phòng Microsoft Office (`.docx`, `.xlsx`, `.pptx`) bằng mã nguồn Python (`python-docx`, `openpyxl`, `xlsxwriter`, `python-pptx`, OpenXML).
- **Nguồn**: Yêu cầu chuẩn hóa của Huy ("khi tạo hoặc định dạng file Word, Excel hay tương tự thì hay bị lỗi không mở được, cần lưu thành quy tắc để vĩnh viễn không lặp lại").

---

## 1. Triệu chứng thường gặp

1. **Microsoft Word**: Báo lỗi `"Word found unreadable content in <file>.docx. Do you want to recover the contents of this document?"` hoặc mở lên bị đơ lag, CPU đạt 100% khi cuộn các trang chứa bảng biểu.
2. **Microsoft Excel**: Báo lỗi `"We found a problem with some content in <file>.xlsx. Do you want us to try to recover as much as we can?"`, mất định dạng công thức, ô merge cell bị vỡ viền hoặc file có dung lượng phình to bất thường (vài chục MB dù chỉ có vài dòng dữ liệu).
3. **Microsoft PowerPoint**: Slide bị tràn chữ (text overflow) ra ngoài khung nhìn, vỡ layout khi mở trên máy tính khác độ phân giải.

---

## 2. Nguyên nhân kỹ thuật & Giải pháp chuẩn hóa

### A. Đối với tài liệu Word (`.docx` / WordprocessingML)

1. **Lỗi đánh số trang tự động ở Header/Footer**:
   - *Nguyên nhân*: Nhồi nhét cả cụm thẻ `<w:fldChar w:fldCharType="begin"/>`, `<w:instrText> PAGE </w:instrText>`, `<w:fldChar w:fldCharType="separate"/>` và `<w:fldChar w:fldCharType="end"/>` vào **CÙNG MỘT THẺ `<w:r>` DUY NHẤT**. Word coi đây là vi phạm cú pháp trường và chặn mở file.
   - *Giải pháp*: BẮT BUỘC dùng thẻ trường đơn giản:
     ```python
     fldSimple = parse_xml(r'''
         <w:fldSimple %s w:instr="PAGE">
             <w:r>
                 <w:rPr>
                     <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
                     <w:sz w:val="26"/><w:szCs w:val="26"/>
                 </w:rPr>
                 <w:t>1</w:t>
             </w:r>
         </w:fldSimple>
     ''' % nsdecls('w'))
     header.paragraphs[0]._p.append(fldSimple)
     ```

2. **Lỗi Header/Footer rỗng**:
   - *Nguyên nhân*: Khi muốn trang bìa hoặc phần đầu không có Header/Footer, xóa toàn bộ các đoạn văn tạo ra thẻ rỗng `<w:hdr/>` hoặc `<w:ftr/>`. Chuẩn ECMA-376 §17.10.3 bắt buộc phải có ít nhất 1 phần tử cấp khối (`minOccurs="1"`).
   - *Giải pháp*: Giữ lại ít nhất 1 đoạn văn rỗng chuẩn:
     ```python
     p = footer.add_paragraph()
     pPr = p._p.get_or_add_pPr()
     pPr.insert(0, parse_xml(r'<w:pStyle %s w:val="Footer"/>' % nsdecls('w')))
     ```

3. **Lỗi định dạng viền và lề ô ở cấp Cell gây lag CPU**:
   - *Nguyên nhân*: Duyệt qua từng ô chèn `<w:tcBorders>` và `<w:tcMar>`. Engine Word phải giải quyết xung đột viền từng khung hình khiến CPU 100%.
   - *Giải pháp*: Khai báo viền `<w:tblBorders>` và padding `<w:tblCellMar>` ở cấp Bảng `<w:tblPr>`.

4. **Lỗi sai thứ tự thẻ con (Schema Ordering)**:
   - *Thứ tự bắt buộc trong `<w:tcPr>`*: `tcW` → `tcBorders` → `shd` → `noWrap` → `tcMar` → `vAlign`.
   - *Thứ tự bắt buộc trong `<w:trPr>`*: `cantSplit` → `tblHeader`.

---

### B. Đối với bảng tính Excel (`.xlsx` / SpreadsheetML)

1. **Lỗi ô Merge Cell (Gộp ô)**:
   - *Nguyên nhân*: Gán giá trị hoặc công thức vào các ô bị merge (không phải ô top-left) hoặc chỉ đặt viền cho ô đầu tiên khiến các ô còn lại trong vùng merge bị mất viền hoặc Excel báo hỏng cấu trúc range.
   - *Giải pháp*:
     - Chỉ gán dữ liệu vào ô trên cùng bên trái: `ws.cell(row=top, column=left, value=...)`.
     - Phải lặp qua toàn bộ tọa độ ô trong vùng merge để áp dụng border đồng nhất.

2. **Lỗi đặt tên Sheet (Worksheet Name)**:
   - *Nguyên nhân*: Tên sheet vượt quá 31 ký tự hoặc chứa các ký tự cấm: `\`, `/`, `?`, `*`, `:`, `[`, `]`.
   - *Giải pháp*: Luôn chuẩn hóa tên sheet qua hàm cắt gọt:
     ```python
     clean_name = re.sub(r'[\\/*?:\[\]]', '_', raw_name)[:31]
     ```

3. **Lỗi ép kiểu dữ liệu chuỗi vào số và ngày tháng**:
   - *Nguyên nhân*: Lưu số `1000000` hoặc ngày `19/10/2026` dưới dạng chuỗi Text (`data_type='s'`), khiến Excel không thể tính toán SUM/AVERAGE và hiện tam giác xanh cảnh báo lỗi.
   - *Giải pháp*: Ép đúng kiểu `float`/`int`/`datetime` và thiết lập `number_format`:
     ```python
     cell.value = 1000000
     cell.number_format = '#,##0'
     ```

4. **Lỗi phình to kích thước file (Worksheet Bloat)**:
   - *Nguyên nhân*: Áp dụng style (font, border, fill) trên toàn bộ cột/hàng trống đến tận hàng 1.048.576.
   - *Giải pháp*: Chỉ lặp và định dạng trong phạm vi dữ liệu thực tế (`min_row` đến `max_row`, `min_col` đến `max_col`).

---

### C. Đối với bài thuyết trình PowerPoint (`.pptx` / PresentationML)

1. **Tỷ lệ khung hình chuẩn 16:9**:
   - Luôn thiết lập kích thước slide 16:9: `prs.slide_width = Inches(13.333)`, `prs.slide_height = Inches(7.5)`.
2. **Chống tràn khung chữ (Text Overflow)**:
   - Luôn bật `word_wrap = True` trên `TextFrame`.
   - Chia nhỏ nội dung bullet point tối đa 4–5 ý/slide, không nhồi nhét quá nhiều văn bản vào 1 slide.

---

## 3. Quy trình kiểm chứng thực tế bắt buộc (Validation Gate)

Trước khi nghiệm thu hoặc gửi file cho người dùng, **BẮT BUỘC** chạy kiểm tra mở file bằng chính ứng dụng Microsoft Office tương ứng trên máy:

- **Kiểm tra Word**:
  ```bash
  osascript -e 'tell application "Microsoft Word"
      set d to open file name "<full_path_to_docx>"
      close d saving no
  end tell'
  ```
- **Kiểm tra Excel**:
  ```bash
  osascript -e 'tell application "Microsoft Excel"
      set w to open workbook workbook file name "<full_path_to_xlsx>"
      close w saving no
  end tell'
  ```
- **Kiểm tra PowerPoint**:
  ```bash
  osascript -e 'tell application "Microsoft PowerPoint"
      set p to open presentation file name "<full_path_to_pptx>"
      close p saving no
  end tell'
  ```

> **Nguyên tắc nghiệm thu:** Lệnh thoát với `exit code 0` và không phát sinh bất kỳ hộp thoại cảnh báo lỗi nội dung (corrupt/repair) thì file mới đạt chuẩn bàn giao.
