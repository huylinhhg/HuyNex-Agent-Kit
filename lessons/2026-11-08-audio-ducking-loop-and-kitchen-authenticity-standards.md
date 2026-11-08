# Bài học: Chuẩn mực Âm thanh Toàn dải, Chống Lỗi Cắt Nhạc & Tính Chân thực Bếp Gà Nhà Huy (Huy Review 08/11/2026)

**Mã bài học**: `2026-11-08-audio-ducking-loop-and-kitchen-authenticity-standards`  
**Ngày đúc kết**: 08/11/2026  
**Nguồn gốc**: Phản hồi trực tiếp từ Founder Mai Huy sau đợt kiểm định 12 video Series "Chuyện Trong Bếp" (Chấm điểm đợt 1: 7/10).  
**Phạm vi áp dụng**: Toàn bộ hệ sinh thái HuyNex Media, các dự án video ngắn (TikTok, Reels, Shorts) và video dài (YouTube).  

---

## 1. Bản chất Kỹ thuật: Lỗi BGM bị ngắt trước khi hết video

### Nguyên nhân gốc rễ
Trong bộ lọc FFmpeg Audio Mixing (`amix`), khi thiết lập:
```bash
[v_lead][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[mix_out]
```
Nếu input đầu tiên (`[v_lead]`) là giọng đọc AI kết thúc ở giây 21 trên tổng thời lượng 28.5s, cờ `duration=first` sẽ **ngay lập tức ngắt toàn bộ luồng âm thanh** tại giây 21! Hậu quả là từ giây 21 đến 28.5s video hoàn toàn bị tắt ngúm âm thanh trong khi hình ảnh vẫn đang chạy.

Thêm vào đó, nếu đặt `afade=t=out:st=total_dur-1.2:d=1.2`, nhạc sẽ bị lịm đi từ trước khi hết video hơn 1 giây, tạo cảm giác cụt ngủn và thiếu chuyên nghiệp.

### Chuẩn mực bắt buộc (V4 Standard)
1. **BGM là trục thời gian chuẩn**: BGM phải được cắt chính xác bằng `total_dur`, hoặc mix với cờ `duration=longest` (với BGM cắt chuẩn xác và giọng đọc kết thúc tự nhiên).
2. **Fade-out chỉ ở 0.3s cuối cùng**: Nhạc nền phải giữ nhịp beat drop cho đến cận kề frame cuối, chỉ fade-out nhẹ trong 0.30s – 0.35s cuối cùng.
3. **True Peak & Loudness**: Cân bằng dải Phone-Band tại -15.0 LUFS, True Peak <= -2.0 dBTP.

---

## 2. Tiêu chuẩn SFX "Tinh tinh" (World-Class Bell Ding)

- **Cấm**: Sử dụng tiếng whoosh "xịt xịt" đơn điệu, nặng nề cho các popup đồ họa tinh tế.
- **Bắt buộc**: Mỗi khi xuất hiện huy hiệu (badge), ribbon chữ, con số định lượng hoặc thẻ bước tiến trình (step-by-step), BẮT BUỘC chèn âm thanh SFX Ding "tinh tinh" đanh thép, trong trẻo, sang trọng (tần số 1200Hz – 2400Hz decaying chime).

---

## 3. Khớp Lời - Khớp Hình Tuyệt Đối (Anti-Dirty Shots & Visual Truth)

Tuyệt đối không bao giờ dựng video kiểu "nói một đằng, hình một nẻo":

1. **Nói đến cân thịt**: BẮT BUỘC có khung hình chiếc cân điện tử (ZUKATO KZ-A8) hiển thị rõ số gram sắc nét. **Nghiêm cấm tuyệt đối quay cảnh nhìn xuống chân/dép đen hoặc cảnh hút chân không lạc đề**.
2. **Nói đến máy hút chân không**: BẮT BUỘC quay cận cảnh máy hút đang chạy đèn LED đỏ, hút phẳng kiệt không khí và hàn mép túi. **Nghiêm cấm để lọt điện thoại lướt TikTok hoặc chân người**.
3. **So sánh Ức gà vs Má đùi**: BẮT BUỘC áp dụng kỹ thuật **CHIA ĐÔI MÀN HÌNH (Split-Screen 50/50)** trực quan: nửa trái ức gà nạc thuần, nửa phải má đùi giòn ngậy.
4. **ASMR căn bếp**: Phải là âm thanh chân thật của quy trình làm bếp: thái thịt cồm cộp, đảo gia vị xào xạc, máy hút rè rè, nước sôi lục bục. **CẤM TRIỆT ĐỂ: cảnh bốc xương gà rơi vãi trên bàn bẩn, cảnh đĩa da gà sống nhầy nhụa, cảnh con dao nằm chỏng chơ một mình**.
5. **Chủ đề "Chậm lại một nhịp"**: BẮT BUỘC **Tight Macro Crop (Zoom in 135%)** tập trung 100% vào miếng gà mọng nước và nhịp tay thái thịt mượt mà ở chính giữa khung hình; loại bỏ toàn bộ xoong chảo, bồn rửa thừa thãi ở hậu cảnh.
6. **Vệ sinh an toàn thực phẩm**: Nhấn mạnh là **Ưu tiên số 1** bảo vệ sức khỏe người dùng. Quay cảnh lau thanh hàn, tiệt trùng dụng cụ, mặt bàn bếp trắng sạch bóng kin kít và khay gà thành phẩm hoàn hảo. **Cấm tuyệt đối cảnh kết chĩa vào tường gạch trắng vô nghĩa**.

---

## 4. Bảo mật Tuyệt đối Bí quyết Công nghệ (Confidentiality Gate)

- **TUYỆT ĐỐI CẤM TIẾT LỘ**: Thời gian ngâm, nhiệt độ nấu chi tiết ("ngâm 3 tiếng", "nấu 65 độ C"). Đây là bí quyết vận hành độc quyền của Gà Nhà Huy.
- **Cách truyền tải chuẩn**: Giải thích bằng nguyên lý khoa học ẩm thực chuẩn mực: phương pháp sous-vide nấu chậm trong môi trường chân không với dòng nước đối lưu tuần hoàn chuẩn xác, giúp protein chín thấu từ tâm ra ngoài, khóa chặt dịch ngọt tự nhiên và axit amin mà không làm co rút hay khô bở thớ thịt.

---

## 5. Sổ cái Cắt cảnh Toàn diện (Shot Tracking Ledger)

Mọi dự án video BẮT BUỘC phải lập và cập nhật `SHOT_TRACKING_LEDGER.json` và `.md`:
- Quản lý chính xác từng giây cắt (`in_s`, `out_s`, `dur_s`).
- Đánh dấu số lần sử dụng và cờ kiểm định an toàn (100% SẠCH, không dính người, không dính rác).
- Không bao giờ lặp lại các shot mở đầu giữa các tập trong cùng một series.
