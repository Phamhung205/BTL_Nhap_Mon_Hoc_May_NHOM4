# Đề tài 9: Dự đoán khách hàng rời bỏ dịch vụ viễn thông

## 1. Thông tin nhóm

- Học phần: Nhập môn Học Máy
- Hùng (Đội trưởng): Quản lý dự án, tổng hợp đánh giá, báo cáo LaTeX
- Mạnh: EDA, chia Train/Test, tiền xử lý Luồng A
- Đức: Feature Engineering Luồng B, Decision Tree trên Luồng A/B
- Hải: K-NN trên Luồng A/B, Error Analysis, giao diện demo

## 2. Cấu trúc dự án

```text
Code/
├── data/                       # Dữ liệu do Mạnh chuẩn bị
├── notebooks/
│   └── tong_hop_ket_qua.ipynb # Notebook tổng hợp của Hùng
├── results/                    # 4 file kết quả JSON của Đức/Hải
│   ├── README.md
│   └── result_template.json
├── src/
│   ├── __init__.py
│   ├── config.py               # random_state=42 và cấu hình chung
│   ├── split_data.py           # Hàm chia dữ liệu chuẩn
│   ├── evaluate.py             # Accuracy/Precision/Recall/F1/CM
│   └── aggregate_results.py    # Tổng hợp 4 kết quả
├── report/
│   ├── main.tex
│   └── model_comparison.csv
├── requirements.txt
└── README.md
```

## 3. Quy ước bắt buộc

Toàn nhóm thống nhất:

```python
random_state = 42
test_size = 0.20
stratify = y
```

Không tự chia lại tập Test ở từng mô hình. Decision Tree và K-NN phải được đánh giá trên cùng tập Test do Mạnh tạo.

## 4. Cài đặt

```bash
pip install -r requirements.txt
```

## 5. Trình tự làm việc

### Giai đoạn 1 - Hùng

Khởi tạo repository, cấu trúc thư mục, `README.md`, `requirements.txt`, `src/config.py` và chia sẻ Git cho nhóm.

### Giai đoạn 2 - Mạnh

- Tải dữ liệu gốc.
- Chia Train/Test với `random_state=42`, `stratify=y`.
- EDA và tiền xử lý Luồng A.
- Xuất `X_train_A.csv`, `X_test_A.csv` và nhãn train/test tương ứng.

### Giai đoạn 3 - Đức và Hải

Đức chạy:

- Decision Tree + Luồng A
- Decision Tree + Luồng B

Hải chạy:

- K-NN + Luồng A
- K-NN + Luồng B

Mỗi kết quả cần gửi Hùng: Accuracy, Precision, Recall, F1-score và Confusion Matrix.

### Giai đoạn 4 - Hùng tổng hợp

Đặt 4 file JSON vào `results/` rồi chạy:

```bash
python -m src.aggregate_results
```

Kết quả được ghi vào:

```text
report/model_comparison.csv
```

Sau đó mở:

```text
notebooks/tong_hop_ket_qua.ipynb
```

để kiểm tra bảng, sắp xếp và trực quan hóa kết quả.

## 6. Lưu ý đánh giá

Với bài toán Churn, không chỉ nhìn Accuracy. Báo cáo cần chú ý Recall và F1-score của lớp khách hàng rời bỏ (`Churn = Yes`) để tránh kết luận sai khi dữ liệu mất cân bằng.

## 7. Báo cáo

File LaTeX chính:

```text
report/main.tex
```

Hùng ghép nội dung EDA của Mạnh, thuật toán/kết quả của Đức và Hải, Error Analysis của Hải, rồi hoàn thiện phần thiết kế giải pháp, bảng so sánh, thảo luận và tổng kết.

## 8. Chạy lại phần của Đức

Từ thư mục gốc dự án, tạo Luồng B rồi huấn luyện Decision Tree trên cả hai luồng:

```bash
python -m src.feature_engineering_b
python -m src.train_decision_tree
```

Các lệnh trên dùng nguyên tập Train/Test đã chia sẵn, tạo `X_train_B.csv`,
`X_test_B.csv`, lưu bộ biến đổi/mô hình trong `models/` và ghi hai kết quả thật
vào `results/duc_decision_tree_A.json`, `results/duc_decision_tree_B.json`.
Notebook có giải thích và kết quả đã chạy nằm tại
`notebooks/03_duc_feature_engineering_B_decision_tree.ipynb`.
