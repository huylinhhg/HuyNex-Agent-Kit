---
name: shortform-production
description: Tự động sản xuất và đạo diễn video ngắn chuẩn chất lượng cao (TikTok, Reels, YouTube Shorts). Tích hợp tiêu chuẩn Hook 3 giây, kinetic typography lò xo CapCut, vùng an toàn chống tràn nút UI 9:16 (Anti-UI Clipping Safe Zone), kỹ thuật đón nhịp B-roll (-120ms), cân chỉnh âm thanh đa tầng (-14.5 dB LUFS voice, -24 dB BGM) và xuất bản không hộp đen thô cứng.
---

# Shortform Production — Tiêu Chuẩn Sản Xuất Video Ngắn Chuẩn Cao Cấp

Skill này biến AI Agent thành **Đạo diễn & Nhà sản xuất Video Ngắn Chuyên nghiệp** cho các nền tảng dọc 9:16 (TikTok, Reels, Shorts), áp dụng các chuẩn mực dựng hình hiện đại nhất thế giới.

---

## 1. Nguyên Tắc Thẩm Mỹ Bất Biến (Zero-Slop Video Standard)

1. **Tuyệt Đối Cấm Video Nghiệp Dư & Hộp Đen Thô Cứng (No Clunky Black Boxes)**:
   - Nghiêm cấm dùng slide ảnh tĩnh ghép nhạc hoặc dán text card thô sơ qua FFmpeg.
   - **CẤM TIỆT đóng hộp nền đen**: Không bọc Logo hay Text Hook/Phụ đề trong các thẻ div chữ nhật nền đen/xám đục `rgba(0,0,0,0.5)`.
   - **Quy chuẩn hiển thị chữ**: Dùng chữ nổi viền đen đậm (`-webkit-text-stroke: 2-3.5px #000`) kết hợp đổ bóng 3D (`filter: drop-shadow(...)`) để chữ tự nổi bật rõ ràng trên mọi khung hình.
   - Logo phải là tệp PNG/SVG trong suốt có đổ bóng kép, đặt tinh tế ở góc màn hình.

2. **Hook 3 Giây Đầu & Typography Motion CapCut**:
   - 3 giây đầu tiên quyết định 80% tỷ lệ giữ chân (Retention Rate).
   - Chữ Hook nghiêng chéo dynamic (`rotate(-3.5deg)` hoặc `rotate(2.5deg)`), nảy chữ bằng hiệu ứng lò xo spring pop-in, kèm âm thanh chuông ding "tinh tinh" đanh thép.
   - Phối hợp 2 font tương phản: Font không chân dày dặn (Inter Black, Montserrat Bold) cho số liệu/hành động + Font serif thanh mảnh nghiêng (Playfair Italic) cho từ cảm xúc.

3. **Pacing Năng Động & Đón Nhịp B-roll (-120ms)**:
   - Cắt cảnh hoặc đổi góc nhìn mỗi 2.5–3.5 giây theo beat nhạc.
   - **B-roll đón nhịp (-0.12s)**: Xuất hiện cảnh minh họa (B-roll) và hiệu ứng âm thanh (SFX) sớm hơn từ khóa khoảng 120ms để dẫn dắt mắt người xem trước khi tai nghe thấy.
   - Không để mặt người nói (với video talking head) vắng bóng quá 6 giây.

---

## 2. Vùng An Toàn Chuẩn Mobile 9:16 (Anti-UI Clipping Safe Zone)

Khi dựng video độ phân giải `1080 x 1920`, tuyệt đối không để nội dung quan trọng bị các nút giao diện của TikTok/Reels che khuất:

```
┌────────────────────────────────────────┐
│  ▲ TOP SAFE ZONE (Cách đỉnh > 240px)   │ -> Tránh thanh search, tai thỏ điện thoại
├────────────────────────────────────────┤
│                                        │
│          KHÔNG GIAN NỘI DUNG           │
│                                        │
│      [Dải Phụ Đề Sweet Spot]           │ -> y = 1280px đến 1460px (căn giữa)
│                                    ┌───┤
│                                    │ L │ -> NÉ NÚT BÊN PHẢI (right > 200px)
│                                    │ I │    (Like, Share, Comment, Avatar)
│                                    │ K │
│                                    │ E │
├────────────────────────────────────┴───┤
│  ▼ BOTTOM SAFE ZONE (Cách đáy > 400px) │ -> Tránh caption, username, nhạc, giỏ hàng
└────────────────────────────────────────┘
```

- **Lề phải**: Cách mép phải tối thiểu **200px** (`right > 200px`).
- **Mép trên**: Cách mép trên tối thiểu **240px** (`top > 240px`).
- **Mép dưới**: Cách mép dưới tối thiểu **400px** (`bottom > 400px`).
- **Vị trí vàng cho Phụ đề (Subtitle Sweet Spot)**: Đặt ở dải `y = 1280px -> 1460px` căn giữa màn hình (`width: 800px`, `left: 140px`).

---

## 3. Cân Chỉnh Âm Thanh Đa Tầng (Multi-Layer Audio Mixing)

Âm thanh quyết định cảm xúc của video. Bắt buộc phối trộn theo 4 tầng:
1. **Giọng Đọc (Voiceover / Dialogue)**: Âm lượng chuẩn **-14.5 dB LUFS** (đo theo chuẩn ITU-R BS.1770-4), rõ ràng, trong trẻo, không lẫn tạp âm.
2. **Nhạc Nền (Background Music - BGM)**: Nhạc không lời (Instrumental only), tự động giảm âm lượng (Audio Ducking) xuống **-24 dB** khi có giọng nói và tăng nhẹ lên **-18 dB** ở các khoảng lặng.
3. **SFX Chuyển Cảnh**: Âm thanh Whoosh / Swoosh nhẹ tại các điểm đổi shot.
4. **SFX Nhấn Mạnh**: Âm thanh Ding "tinh tinh", Pop, hoặc Click tại các từ khóa hook hoặc số liệu nảy lên.

---

## 4. Quy Trình Sản Xuất 4 Bước

1. **Khóa Kịch Bản & Semantic Beats**: Phân đoạn script thành từng beat (Hook $\rightarrow$ Vấn đề $\rightarrow$ Giải pháp $\rightarrow$ Kêu gọi hành động).
2. **Sinh Âm Thanh Master**: Tạo file voiceover (TTS chuẩn 48kHz hoặc thu âm thực tế) + chọn nhạc nền instrumental phù hợp nhịp.
3. **Căn Khớp Phụ Đề Theo Thời Gian Thực (Forced Alignment)**: Bắt đúng từng từ (word-level timestamps) để nảy màu chữ khi giọng nói cất lên.
4. **Render & Kiểm Định Khung Hình (Frame Audit)**: Kiểm tra ít nhất 3 khung hình (đầu, giữa, cuối) trên mockup điện thoại để bảo đảm không lọt chữ ra ngoài vùng an toàn.
