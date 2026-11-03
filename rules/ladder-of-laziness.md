# Thang 7 Nấc Thẩm Định Code (The 7-Rung Ladder of Laziness)
## Chuẩn Kỹ Sư Tối Giản (Senior Dev Ponytail Standard)

> *"Đoạn code xịn nhất là đoạn code bạn KHÔNG BAO GIỜ phải viết."*  
> Ưu tiên loại bỏ code thừa (`-N`) hơn là viết thêm code mới (`+1`).

Khi giải quyết bất kỳ tác vụ lập trình nào, AI Agent và kỹ sư BẮT BUỘC phải thẩm định tuần tự từ nấc 1 đến nấc 7:

```
[Nấc 1: YAGNI - Cần thiết?] ──> [Nấc 2: Tái sử dụng code có sẵn]
                                              │
[Nấc 3: Thư viện chuẩn]   <─────────────────┘
         │
         └──> [Nấc 4: Tính năng Native của Nền tảng/OS/Browser]
                                              │
[Nấc 5: Phụ thuộc đã cài]  <─────────────────┘
         │
         └──> [Nấc 6: Tối giản dòng code (1-2 dòng mạch lạc)]
                                              │
              [Nấc 7: Viết mới tối thiểu & pass test] <──┘
```

1. **Nấc 1 — Cần thiết (YAGNI)**: Tính năng này có thực sự phục vụ mục tiêu hiện tại không? Tuyệt đối không phỏng đoán nhu cầu tương lai để viết sẵn logic dư thừa.
2. **Nấc 2 — Tái sử dụng**: Kiểm tra trong codebase hiện tại đã có hàm, utility, component hoặc pattern tương tự chưa. Tái sử dụng tối đa thay vì viết mới.
3. **Nấc 3 — Thư viện chuẩn (Stdlib)**: Thư viện có sẵn của ngôn ngữ (Python stdlib, JS ES6+, Go stdlib) có giải quyết được không? Ưu tiên tuyệt đối thư viện chuẩn.
4. **Nấc 4 — Nền tảng native**: Trình duyệt hoặc Hệ điều hành có sẵn tính năng không (HTML5 semantic tags, modern CSS layout, shell command)? Không dùng JS làm việc mà CSS native làm tốt hơn.
5. **Nấc 5 — Phụ thuộc hiện có**: Các dependencies đã cài sẵn trong dự án (`package.json`, `pyproject.toml`) có giải quyết được không? Nghiêm cấm tự ý cài thêm package ngoài cho các tác vụ nhỏ lẻ.
6. **Nấc 6 — Tối giản dòng code**: Rút gọn tối đa về logic mạch lạc trong 1–2 dòng lệnh. Cấm đẻ ra các class bọc (wrappers), factory thừa thãi hoặc singleton một lần dùng.
7. **Nấc 7 — Mức tối thiểu**: Khi bắt buộc phải viết code mới, chỉ viết đúng lượng code nhỏ nhất đủ để thỏa mãn yêu cầu và pass kiểm thử.
