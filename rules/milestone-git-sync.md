# Giao Thức Đồng Bộ Git Đơn Tầng Tinh Gọn (Autonomous Single-Tier Git Auto-Sync)
## Chốt Chặn Chống Micro-Push Spam & Tối Ưu Hạn Ngạch CI/CD

> *"Tự động hóa hoàn toàn chu trình Git nhưng giữ Git log sạch sẽ, không độ trễ mạng và không lãng phí tài nguyên CI/CD."*

---

## 1. Vấn Đề Thực Chiến (The Problem)

Khi sử dụng AI Coding Agent với Git, các kỹ sư thường gặp 2 thái cực sai lầm:
1. **Phụ thuộc thủ công**: Người dùng phải tự tay nhớ và gõ `git pull`, `git add`, `git commit`, `git push` lặp đi lặp lại rất phiền toái.
2. **Micro-Push Spam**: Cài đặt Agent tự động commit và push sau **từng câu lệnh chat nhỏ nhặt**. Hậu quả:
   - Rác Git log với hàng chục commit vô nghĩa (`fix typo`, `update 1 line`, `wip`).
   - Đốt cạn hạn ngạch build của các pipeline CI/CD tự động (Vercel, Netlify, GitHub Actions, Cloudflare Pages).
   - Tăng độ trễ mạng mỗi lượt trao đổi (phải chờ Git push xong mới phản hồi).

---

## 2. Giao Thức 3 Chốt Chặn Vàng (The 3-Gate Protocol)

AI Agent và hệ thống tự động hóa BẮT BUỘC tuân thủ 3 chốt chặn:

```
[Bắt đầu phiên] ──> (1) Cổng Đầu Phiên: git pull --ff-only đúng 1 LẦN DUY NHẤT
                            │
                      [Làm việc, tinh chỉnh dở dang: SỬA FILE CỤC BỘ (Độ trễ = 0)]
                            │
[Kết thúc mốc]   ──> (2) Cổng Bàn Giao Mốc: Chỉ commit & push khi ĐẠT MILESTONE
                            │
                      (3) Rào Chắn An Toàn: Chỉ fast-forward, cấm --force
```

### Chốt 1: Cổng Đầu Phiên Thông Minh (Session Entry Gate)
- Chỉ chạy kiểm tra `git status` và `git pull --ff-only origin <branch>` **ĐÚNG 1 LẦN DUY NHẤT** khi bắt đầu mở phiên làm việc mới trên repo dự án.
- **TUYỆT ĐỐI KHÔNG** quét lặp lại trong các câu lệnh trao đổi liên tục trong cùng phiên.
- Chỉ thao tác trên đúng repo dự án đang mở, không quét diện rộng các repo khác.

### Chốt 2: Cổng Bàn Giao Mốc Hoàn Chỉnh (Milestone Mutation Gate — Anti Micro-Push)
TUYỆT ĐỐI KHÔNG đẩy (`git push`) vụn vặt sau từng câu lệnh nhỏ nhặt. Agent **CHỈ ĐƯỢC PHÉP** commit & push khi thỏa mãn 1 trong 3 điều kiện:
1. **Hoàn thành trọn vẹn một tính năng / nhiệm vụ có kiểm chứng (Task Milestone)** đã vượt qua bài kiểm thử (Verification Gate).
2. **Cập nhật Bộ luật / Kỹ năng dùng chung (Governance / Shared Rules)** cần các máy khác hoặc đồng đội nhận ngay.
3. **Khi người dùng chủ động yêu cầu bàn giao hoặc kết thúc phiên** *(ví dụ: "xong rồi", "đẩy lên đi", "bàn giao nhé")*.

> *Trong quá trình trao đổi tinh chỉnh dở dang, Agent chỉ sửa file cục bộ trên máy, giữ phản hồi tức thì với độ trễ mạng bằng 0.*

### Chốt 3: Rào Chắn An Toàn (Safe Sync Gate)
- **Tuyệt đối không dùng `--force` hoặc `--hard`**: Chỉ kéo fast-forward (`--ff-only`).
- Khi phát hiện working tree có file chưa commit do người dùng sửa dở hoặc có xung đột (merge conflict), Agent **BẮT BUỘC dừng lại cảnh báo cụ thể**, giải thích nguyên nhân và chờ chỉ thị của người dùng, không tự ý ghi đè làm mất mát dữ liệu.
