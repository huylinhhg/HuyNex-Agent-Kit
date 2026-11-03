---
name: shortform-editor
description: Hướng dẫn biên tập và dựng video ngắn 9:16 chuyên nghiệp. Tập trung vào cấu trúc kịch bản Semantic Beats, căn khớp phụ đề chuẩn ngữ âm (Forced Alignment), quản trị nhạc không lời bản quyền (Instrumental-only), chèn logo tinh tế và quy trình kiểm định chất lượng âm thanh/hình ảnh trước khi xuất bản.
---

# Shortform Editor — Tiêu Chuẩn Biên Tập Video Ngắn 9:16

Skill này cung cấp quy chuẩn biên tập cho dựng phim, editor và AI Agent khi xử lý hậu kỳ video ngắn dạng dọc (TikTok, Reels, Shorts).

---

## 1. Cấu Trúc Kịch Bản Semantic Beats

Mỗi video ngắn bắt buộc phải chia nhỏ thành các phân đoạn ngữ nghĩa (**Semantic Beats**):

| Beat ID | Thời lượng | Mục đích (Intent) | Yêu cầu hình ảnh (Visual Cue) | Âm thanh & SFX |
|:---:|:---:|---|---|---|
| `beat_01` | 0.0s – 2.5s | **Hook 3s**: Đánh thức tò mò | Chữ động nảy lò xo + Cảnh ấn tượng nhất | SFX Ding + BGM Drop |
| `beat_02` | 2.5s – 8.0s | **Vấn đề / Tình huống**: Đồng cảm nỗi đau | B-roll mô tả thao tác thực tế | Voiceover + Ducking BGM |
| `beat_03` | 8.0s – 20.0s | **Giải pháp / Giá trị**: Minh chứng rõ ràng | Cận cảnh sản phẩm / Dữ liệu trực quan | SFX Whoosh chuyển cảnh |
| `beat_04` | 20.0s – 28.0s | **Kết luận / Call to Action**: Hành động cụ thể | Thành phẩm hoàn thiện / Giao diện chính | BGM kết thúc dứt khoát |

---

## 2. Quy Chuẩn Phụ Đề: Kịch Bản Làm Nguồn, Audio Là Sự Thật

Tuyệt đối không đoán mò timecode và không tin tưởng 100% vào kết quả nhận diện giọng nói tự động (ASR). Bắt buộc thực hiện theo quy trình đối soát:

1. **Lưu 2 phiên bản độc lập**:
   - `script_display`: Chuỗi ký tự ngữ pháp/chính tả muốn hiển thị trên màn hình.
   - `script_spoken`: Biểu diễn từ ngữ thực tế người nói cất lên (kèm phiên âm số, từ viết tắt, tiếng Anh).
2. **Khớp nối cưỡng bức (Forced Alignment)**:
   - Sử dụng công cụ căn khớp (Whisper / Aeneas / Gentle) trên file giọng đọc riêng biệt (Voice stem).
   - Đảm bảo độ lệch giữa âm thanh và chữ xuất hiện **dưới 150ms**.
3. **Quy cách hiển thị phụ đề**:
   - Tối đa **1–2 dòng** trên một khung hình, mỗi dòng không quá **5–7 từ**.
   - Phông chữ không chân đứng thẳng (`italic = false`), viền nét mảnh, đổ bóng mịn.
   - Chỉ đổi màu (Highlight vàng/cam) đúng **1 từ khóa then chốt** trong câu khi giọng đọc chạm tới từ đó.

---

## 3. Quản Trị Nhạc Nền: Chỉ Sử Dụng Nhạc Không Lời (Instrumental Only)

1. **Nguyên tắc vàng**: Tuyệt đối không dùng nhạc nền có giọng hát, vocal chop, hay tiếng người ngâm nga đè lên lời thoại. Giọng đọc của nhân vật phải là tâm điểm thính giác duy nhất.
2. **Kiểm tra bản quyền**:
   - Sử dụng các kho nhạc bản quyền thương mại (Commercial Royalty-Free).
   - Lưu trữ metadata rõ ràng: Tên bài, tác giả, link giấy phép, nền tảng được phép phát hành.

---

## 4. Chốt Chặn Kiểm Định Trước Khi Xuất Bản (QA Gate)

Trước khi bàn giao video hoàn chỉnh:
- [ ] Không có chữ nào bị lọt ra ngoài **Safe Zone** (trên 240px, dưới 400px, phải 200px).
- [ ] Giọng đọc đạt chuẩn **-14.5 dB LUFS**, không bị rè (clipping `> 0 dBFS`).
- [ ] Nhạc nền tự động giảm âm khi có giọng nói (Ducking đạt `-24 dB`).
- [ ] Khung hình kết thúc là thành phẩm đẹp mắt hoặc thông điệp giá trị, không kết thúc bằng cảnh rác.
