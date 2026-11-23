# Bài học: Tích hợp Smooth-Scroll (Lenis) & Kiến trúc Native WebGL Layer cho Bản đồ Số

- **Ngày ghi nhận**: 23/11/2026
- **Phạm vi**: Giao diện người dùng Web, Landing Page, Dòng thời gian lịch sử, Bản đồ tương tác (MapLibre/Mapbox) trong toàn bộ hệ sinh thái HuyNex.
- **Nguồn**: Triển khai thực chiến nâng cấp trải nghiệm người dùng tại dự án `09-65nam-csnd`.

---

## 1. Vấn đề thực tế (Problem Statement)

1. **Xung đột cuộn chuột giữa Smooth Scroll và Canvas Bản đồ (Wheel Hijacking)**:
   - Các thư viện điều tốc cuộn quán tính (như Lenis) can thiệp vào sự kiện cuộn tự nhiên (`wheel`). Khi người dùng di chuột qua vùng bản đồ (MapLibre/Mapbox/Leaflet), thao tác phóng to/thu nhỏ (zoom) hoặc di chuyển (pan) sẽ bị Lenis cướp quyền, dẫn đến kẹt con trỏ chuột hoặc nhảy trang giật cục.

2. **Bẫy Over-Engineering khi làm hiệu ứng sóng lan tỏa (Radar Wave/Pulse)**:
   - Một số đề xuất kỹ thuật có xu hướng dựng một thẻ Canvas WebGL độc lập đè lên trên bản đồ để vẽ shader.
   - Hậu quả: Gây lãng phí bộ nhớ GPU, khó đồng bộ ma trận phép chiếu tọa độ (matrix projection sync) khi pan/zoom bản đồ, và làm tụt điểm Lighthouse Performance.

---

## 2. Quy chuẩn Kiến trúc Bắt buộc (The Solutions)

### Quy chuẩn 1: Cách ly Vùng Cuộn Độc lập bằng `data-lenis-prevent`
* Mọi thành phần bản đồ (`map-canvas`), bảng dữ liệu cuộn ngang lớn, hoặc ngăn kéo thông tin (drawer/sidebar) BẮT BUỘC phải mang thuộc tính `data-lenis-prevent`:
  ```html
  <div ref={container} className="map-canvas" data-lenis-prevent />
  <aside className="cmap-drawer-panel" data-lenis-prevent />
  ```
* Trong CSS toàn cục:
  ```css
  .lenis.lenis-smooth [data-lenis-prevent] {
    overscroll-behavior: contain;
  }
  ```

### Quy chuẩn 2: Ưu tiên Native MapLibre Custom WebGL Image Layer
* Tuyệt đối không dựng thêm DOM canvas độc lập đè lên bản đồ.
* Áp dụng Nấc 4 & 5 của Thang Lazy Dev: Tái sử dụng chuẩn `StyleImageInterface` có sẵn của chính MapLibre GL:
  ```typescript
  const pulsingDot = {
    width: 100, height: 100,
    data: new Uint8Array(100 * 100 * 4),
    onAdd() { ... },
    render() {
      // Vẽ sóng lan tỏa qua context 2D và triggerRepaint
      map.triggerRepaint();
      return true;
    }
  };
  map.addImage('pulsing-wave', pulsingDot, { pixelRatio: 2 });
  ```
* Lợi ích: Tọa độ gắn liền 100% với camera bản đồ khi xoay/nghiêng/zoom, tự giải phóng tài nguyên khi unmount, duy trì ổn định 60–120 FPS.
