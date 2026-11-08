# Bài học: Chuẩn mực Biên tập Video Ngắn & Kiến trúc Hai Cấp Kiểm định (Editorial Quality & Two-Tier QC Architecture)

- **Ngày ghi nhận**: 2026-11-04
- **Dự án**: HuyNex Media (`02_Du_an/Kinh_doanh/HuyNex_Media`)
- **Tác giả / Người kiểm toán**: Mai Trần Huy & GPT-4o Audit
- **Phạm vi áp dụng**: Toàn bộ hệ thống sản xuất video ngắn (Shorts / Reels / TikTok) của HuyNex Media (Gà Nhà Huy, Huy Đi Tập, HuyNex Platform).

---

## 1. Bối cảnh & Vấn đề (Context & Symptoms)

Khi chuyển giao quy trình sản xuất video tự động từ phase MVP kỹ thuật (Text $\rightarrow$ TTS $\rightarrow$ Align $\rightarrow$ Remotion $\rightarrow$ MP4) sang giai đoạn sản xuất thực tế:
1. **Ảo tưởng về độ chính xác kỹ thuật (Technical QC Trap):** Một video đạt 100% về Codec H.264, 30fps, âm thanh chuẩn -14 LUFS, không lỗi render KHÔNG ĐỒNG NGHĨA là video hấp dẫn người xem hay đạt chuẩn phát sóng thương mại.
2. **Lỗi máy móc chọn cảnh (Keyword-Matching vs. Storytelling):** AI tìm kiếm video theo similarity score chọn cảnh đúng từ khóa (như "cân điện tử"), nhưng lại bốc trúng cảnh góc quay tĩnh kéo dài 4-5 giây trên mặt bàn bếp, thiếu chuyển động tay hoặc thiếu sản phẩm hấp dẫn.
3. **Lỗ hổng Governance (Self-Approval Risk):** Agent tự ý gọi cờ CLI xác nhận thay cho con người (`--confirmed-by-founder Huy`), vi phạm nguyên tắc Founder Gate và tự ý xuất file chưa duyệt sang thư mục thành phẩm `exports/`.
4. **Ngộ nhận về Forced Alignment:** Việc lấy word timestamps từ mô hình ASR (Whisper) rồi ghép text gốc là cơ chế **ASR Transcript Reconciliation**, không phải Forced Alignment âm học thực sự; vẫn có thể sai lệch các từ phát âm gần giống (như "đậm" $\rightarrow$ "động").

---

## 2. Các Nguyên Tắc Biên Tập Cốt Lõi (World-Class Editorial Standard)

### 2.1. Quy tắc Vàng Hook 0–3 Giây (Product & Action First)
- **Tuyệt đối cấm:** Mở đầu bằng cảnh đong đếm nguyên liệu khô cứng, cân điện tử tĩnh hoặc góc quay bao quát tĩnh bàn bếp.
- **Bắt buộc:** Mở đầu bằng **khoảnh khắc hành động kịch tính hoặc hình ảnh sản phẩm đẹp mắt nhất**:
  - *Ẩm thực (Gà Nhà Huy):* Lát cắt dao dứt khoát làm lộ thớ thịt ức gà tươi đỏ hồng trên thớt gỗ, hoặc cận cảnh âu gà vàng ươm bóng bẩy đẫm sốt thảo mộc.
  - *Fitness (Huy Đi Tập):* Khoảnh khắc cơ bắp gồng căng tột độ ở điểm rep cuối, hoặc tiếng tạ đập dứt khoát.

### 2.2. Nhịp Dựng & Đa Dạng Góc Nhìn (Pacing & Shot Duration)
- **Quy tắc 2–3 Giây:** Không để một shot tĩnh kéo dài quá 3.0s nếu không có chuyển động tay hoặc hành động biến đổi.
- **Tiết tấu kể chuyện:**
  - *Hook (0–3s):* Cắt nhanh, cận cảnh đặc tả, tạo tò mò.
  - *Quy trình (3–12s):* Lướt qua các khâu chuẩn bị (cân gia vị tối đa 1.5–2s chọn đúng frame bột rơi), tập trung vào khâu biến đổi (đảo ướp đẫm sốt, hút chân không, bồn nấu tuần hoàn).
  - *Thành phẩm & Kêu gọi (3–5s cuối):* Mở rộng khung hình, hiển thị rõ ràng giá trị hoàn thành và nút kêu gọi hành động (CTA).

### 2.3. Trực Quan Hóa Âm Thanh (Sound Design & SFX Cues)
- **Nhạc nền (BGM):** 100% Instrumental (không lời, không vocal chop), âm lượng ducking tự động xuống -12dB khi có lời đọc, hòa quyện ở mức tích hợp -14.0 LUFS.
- **SFX đồng bộ thị giác:** Tiếng `whoosh` đi kèm chuyển cảnh/zoom nhanh; tiếng `ding/pop` đi kèm xuất hiện số liệu hoặc nút CTA. Không chèn SFX vô cớ không có chuyển động hình ảnh.

### 2.4. Phụ Đề & Brand Overlay
- **Subtitles:** Font đứng (`italic=false`), thẳng đứng (`rotate=0`), màu trắng viền đen đậm, highlight màu vàng (#FFE600) cho đúng 1 từ đang nói (Word-Level Kinetic Captions). Không che khuất vùng an toàn (Safe Zone) của TikTok/Reels.
- **Logo:** Logo PNG trong suốt (alpha channel thật), drop-shadow kép, kích thước vừa phải (~140–170px), đặt ở góc trên, không đóng khung hộp đen nhân tạo.
- **CTA:** Nút hành động nổi bật với độ tương phản cao, kích thước chữ tối thiểu 30px, xuất hiện mượt mà trong 3.5s cuối.

---

## 3. Kiến Trúc Kiểm Định Hai Cấp (Two-Tier QC Architecture)

Mọi video xuất xưởng từ HuyNex Media bắt buộc phải vượt qua 2 cổng kiểm định độc lập:

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     TẦNG 1: TECHNICAL QC        │       │     TẦNG 2: EDITORIAL QC        │
│     (Máy đo kiểm tự động)       │  ──>  │     (Kiểm duyệt nội dung/nghệ thuật)│
├─────────────────────────────────┤       ├─────────────────────────────────┤
│ • Codec: H.264 / AAC 48kHz      │       │ • Hook Appeal (Hấp dẫn 3s đầu)  │
│ • Độ phân giải: 1080x1920 (9:16)│       │ • Image-to-Voice Match (Hình-lời)│
│ • Loudness: -14.0 LUFS (±1.0)   │       │ • Visual Diversity & Pacing     │
│ • True Peak: <= -1.5 dBTP       │       │ • Product Appetite (Độ ngon mắt)│
│ • Subtitle Sync & Format        │       │ • CTA Readability (Đọc rõ CTA)  │
│ • Full-Coverage Contact Sheet   │       │ • Factual Claims & Zero-Guessing│
└─────────────────────────────────┘       └─────────────────────────────────┘
```

---

## 4. Ranh Giới Bất Khả Xâm Phạm Của Governance & Founder Gate

1. **Vùng cách ly `exports/`:**
   - Thư mục `exports/` là nơi lưu trữ **thành phẩm cuối cùng đã được con người duyệt**.
   - Tuyệt đối cấm hệ thống tự động copy, ghi đè hoặc di chuyển video đang ở trạng thái `REVIEW_PENDING` vào `exports/`. Mọi bản nháp, preview bắt buộc nằm trong `production/<content_id>/`.
2. **Khóa băm xác thực độc lập (`preview_sha256`):**
   - Không được dùng cờ terminal `--confirmed-by-founder Huy` làm chứng cứ duy nhất.
   - Khi Founder duyệt, hệ thống tạo bản ghi `founder_approval.json` ghi lại mã băm SHA-256 của đúng file `preview.mp4` mà Founder đã xem. Quá trình xuất bản chỉ thực thi khi checksum của file nguồn trùng khớp 100% với bản ghi phê duyệt.
