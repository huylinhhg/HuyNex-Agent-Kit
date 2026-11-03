---
name: media-audio-gate
description: Chốt chặn kiểm định chất lượng âm thanh kỹ thuật số cho nội dung video và podcast. Chuẩn hóa tần số lấy mẫu 48kHz (Sample Rate), cân bằng âm lượng ITU-R BS.1770-4 (-14.5 dB LUFS), kỹ thuật ducking nhạc nền tự động và khử trùng âm thanh rè (Anti-Clipping).
---

# Media Audio Gate — Chốt Chặn Kiểm Định Âm Thanh Kỹ Thuật Số

Skill này cung cấp các tiêu chuẩn kỹ thuật số và quy trình kiểm định âm thanh nghiêm ngặt trước khi xuất bản bất kỳ tệp video hay podcast nào ra công chúng.

---

## 1. Chuẩn Hóa Tần Số Lấy Mẫu 48kHz (Sample Rate Standardization)

1. **Chuẩn của Video Chuyên Nghiệp**:
   - Toàn bộ âm thanh lồng ghép vào video (Voiceover, Nhạc nền, SFX) bắt buộc phải đạt tần số lấy mẫu **48,000 Hz (48kHz)** với độ sâu **24-bit hoặc 16-bit PCM**.
   - Tuyệt đối không để xảy ra hiện tượng lệch pha sample rate (ví dụ: giọng đọc xuất ra 24kHz hoặc 22.05kHz nhưng lại ép vào timeline 48kHz mà không qua thuật toán resample chất lượng cao, gây méo tiếng và vỡ âm sắc).
2. **Xác Minh Tệp Âm Thanh Thực Tế**:
   - Chạy lệnh kiểm tra thông số kỹ thuật thực của file âm thanh:
     ```bash
     ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,channels,bit_rate -of json audio.wav
     ```
   - Chốt chặn từ chối xuất bản nếu `sample_rate != 48000`.

---

## 2. Chuẩn Âm Lượng Tích Hợp (Integrated Loudness Standard)

Áp dụng chuẩn đo lường quốc tế **ITU-R BS.1770-4 / EBU R128**:

| Kênh âm thanh | Chuẩn âm lượng mục tiêu | Ngưỡng đỉnh tối đa (True Peak) |
|---|:---:|:---:|
| **Giọng nói chính (Voice Master)** | **-14.5 dB LUFS** | Không vượt quá **-1.0 dBTP** |
| **Nhạc nền khi có lời (Ducking BGM)** | **-24.0 dB LUFS** | Thấp hơn giọng nói ít nhất **9.5 dB** |
| **Nhạc nền khi không có lời (Solo BGM)**| **-18.0 dB LUFS** | Nổi bật vừa phải, không lấn át tai |
| **Hiệu ứng âm thanh (SFX Cues)** | **-12.0 dB đến -16.0 dB** | Rõ ràng, dứt khoát, không chói tai |

---

## 3. Khử Trùng Hoàn Toàn Hiện Tượng Rè / Vỡ Âm (Anti-Clipping)

- Tuyệt đối cấm âm lượng vượt ngưỡng **0 dBFS** (Digital Clipping). Bất kỳ khung âm thanh nào vượt quá 0 dBFS sẽ bị méo dạng sóng vuông, gây tiếng rè cực kỳ khó chịu cho người nghe dùng tai nghe.
- Sử dụng bộ nén giới hạn đỉnh (**True Peak Limiter**) tại ngưỡng `-1.0 dB` để bảo vệ an toàn cho toàn bộ timeline xuất bản.
