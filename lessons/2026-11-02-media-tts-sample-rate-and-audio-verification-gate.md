# Bài học kinh nghiệm: Chuẩn hóa Sample Rate VieNeu-TTS (48kHz) và Chốt chặn Kiểm định Âm thanh (Audio Verification Gate)

- **Ngày ghi nhận:** 02/11/2026
- **Phạm vi áp dụng:** Toàn bộ hệ sinh thái HuyNex Media, các dự án video, TTS và pipeline tự động hóa truyền thông trên Mac & Windows.
- **Mức độ rủi ro:** High (Trải nghiệm người xem & Độ tin cậy sản phẩm).

---

## 1. Bản chất Sự cố (Incident Analysis)
- **Hiện tượng:** Video xuất xưởng bị lỗi lồng tiếng nghiêm trọng: Giọng đọc Hải Đăng bị kéo dài lê thê gấp đôi thời gian (từ 20s thành 40s), giọng ồm ồm, méo mó, tụt cao độ xuống 1 quãng tám và phát âm biến dạng như ma quái.
- **Nguyên nhân kỹ thuật gốc rễ:** 
  1. Mô hình **VieNeu-TTS** hoạt động và xuất dữ liệu audio ở tần số **48,000 Hz** (`tts.sample_rate = 48000`).
  2. Script render đã tự ý dùng hàm ngoài `soundfile.write(path, audio, 24000)` với tham số sample rate hardcode sai (24kHz thay vì 48kHz). Khi phần mềm phát lại file này ở tốc độ 24kHz, toàn bộ bài đọc bị chậm lại **0.5x** và biến dạng âm sắc.
  3. Thiếu chốt chặn kiểm định âm thanh (Audio Verification Gate): Agent vội vàng kết luận hoàn thành mà không decode hoặc nghe thử âm thanh thực tế trước khi xuất xưởng.

---

## 2. Quy chuẩn Kỹ thuật Bắt buộc (Mandatory Standards)

1. **Tuyệt đối tuân thủ Sample Rate 48,000 Hz:**
   - Khi lưu audio từ VieNeu-TTS, BẮT BUỘC dùng phương thức chính thức của thư viện:
     ```python
     tts.save(audio, str(out_path))  # Tự động lưu chuẩn 48kHz
     ```
   - Tuyệt đối CẤM hardcode các giá trị 16000, 22050, 24000 khi ghi file âm thanh VieNeu-TTS.

2. **Tối ưu ngữ âm thuần Việt cho kịch bản:**
   - Các mô hình TTS tiếng Việt dựa trên bảng ngữ âm phoneme tiếng Việt. Khi gặp từ mượn tiếng Anh nguyên bản (`eat clean`, `sous-vide`, `protein`, `Meat Deli`), mô hình dễ bị vấp hoặc phát âm lai căng.
   - BẮT BUỘC phiên âm ngữ âm tự nhiên hoặc dùng từ ngữ thuần Việt tương đương:
     - *"người ăn kiêng / ăn sạch"* (thay vì *eat clean*)
     - *"nấu chậm su-vít"* (thay vì *sous-vide*)
     - *"thớ thịt / sợi đạm"* (thay vì *protein*)
     - *"thịt tươi sạch"* (thay vì *Meat Deli*)

3. **Chốt chặn Kiểm định Âm thanh (Audio Verification Gate):**
   - Trước khi mux audio vào video thành phẩm, BẮT BUỘC:
     1. Kiểm tra thời lượng: `duration = len(audio) / 48000` (phải khớp với nhịp nói 3–4 giây/câu).
     2. Chạy decode/transcribe kiểm thử bằng Faster-Whisper: Phải nhận diện được đúng tiếng Việt chuẩn, không được có ký tự rác hoặc từ ngữ vô nghĩa.

---

## 3. Trạng thái Kiểm chứng (Verification)
- Đã sửa lại toàn bộ pipeline sinh audio tại `HuyNex_Media/work/generate_perfect_voice_48k.py`.
- Hai video [GNH_04_3_Sai_Lam_Nau_Uc_Ga.mp4](file://{{WORKSPACE_ROOT}}/02_Du_an/Kinh_doanh/HuyNex_Media/exports/01_Ga_Nha_Huy/01_Shorts_Series_9x16/GNH_04_3_Sai_Lam_Nau_Uc_Ga.mp4) và [GYM_05_Quy_Tac_3_Giay_Thang_Con_Luoi.mp4](file://{{WORKSPACE_ROOT}}/02_Du_an/Kinh_doanh/HuyNex_Media/exports/02_Gym_Motivation/01_Chuyen_De_Motivation_9x16/GYM_05_Quy_Tac_3_Giay_Thang_Con_Luoi.mp4) đã được re-render đạt chuẩn thời lượng 20.8s, giọng đọc trong trẻo, tự nhiên và âm thanh đạt chuẩn EBU R128 (-14 LUFS, TP $\le$ -1.5 dBTP).
