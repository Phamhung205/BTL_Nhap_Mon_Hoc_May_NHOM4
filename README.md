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

Phần Đức được kiểm tra với Python 3.12.10. Trên Windows, tạo môi trường riêng
và dùng đúng Python trong môi trường này (không dùng `.venv` cũ):

```powershell
py -3.12 -m venv .venv-duc
.\.venv-duc\Scripts\python.exe -m pip install -r requirements-duc.txt
.\.venv-duc\Scripts\python.exe -m src.feature_engineering_b
.\.venv-duc\Scripts\python.exe -m src.train_decision_tree --jobs 2
.\.venv-duc\Scripts\python.exe -m unittest discover -s tests -v
```

Trên Linux/macOS: tạo môi trường bằng `python3.12 -m venv .venv-duc`,
dùng `.venv-duc/bin/python` thay đường dẫn Windows. Các lệnh phải chạy từ gốc repo.

`train_decision_tree` tự xuất lại B và chạy 3 phép tìm kiếm trên Train:
A (45 cột), B_core (26 cột để đối chiếu), B (29 cột cố định).
Mỗi phép gồm 120 cấu hình × 5 fold, nên có thể mất vài phút.
Pipeline học điền thiếu, mã hóa và scaler A riêng ở từng fold; Test chỉ được
đọc sau khi tìm tham số. Cây cuối fit trên CSV A/B của nhóm. Mã kiểm tra toàn
bộ ma trận CSV với kết quả biến đổi từ raw trước khi fit, kể cả thứ tự dòng.

Các file bàn giao:

- `data/processed/X_train_B.csv`, `X_test_B.csv`: 5.634/1.409 dòng, 29 cột.
- `models/feature_engineer_B.pkl`: nhận danh sách dictionary đọc bằng `read_raw_csv`.
- `models/decision_tree_A.pkl`, `decision_tree_B.pkl`: nhận ma trận CSV A/B đúng thứ tự cột.
- `models/decision_tree_A_pipeline.pkl`, `decision_tree_B_pipeline.pkl`: nhận raw dictionaries;
  đã kiểm tra dự đoán giống cây nhận CSV.
- `results/duc_decision_tree_A.json`, `duc_decision_tree_B.json`: metric thật cho Churn=Yes.
- `report/duc_cv_*.csv`: từng cấu hình và điểm từng fold; `duc_feature_comparison.json`:
  so sánh CV; `duc_predictions_*.csv`: nhãn/dự đoán theo vị trí dòng Test.
- `report/duc_run_manifest.json`: phiên bản thư viện và SHA-256 dữ liệu.
- `report/duc_review.md`: giải thích và các kiểm tra đã thực hiện.

Luồng B chưa scale; Decision Tree không cần scale. Khi làm K-NN, Hải cần đặt
scaler bên trong pipeline CV, fit trên Train và áp dụng cho Test.

Notebook `notebooks/03_duc_feature_engineering_B_decision_tree.ipynb` mặc định
kiểm tra và hiển thị artifact đã huấn luyện; đặt `RUN_TRAINING=True` để chạy lại
toàn bộ tìm kiếm. Đăng ký kernel trong môi trường riêng và chạy kiểm tra notebook:

```powershell
.\.venv-duc\Scripts\python.exe -m ipykernel install --prefix .venv-duc --name duc-btl --display-name "Python (Duc BTL)"
.\.venv-duc\Scripts\python.exe -m nbconvert --to notebook --execute --inplace notebooks\03_duc_feature_engineering_B_decision_tree.ipynb --ExecutePreprocessor.kernel_name=duc-btl --ExecutePreprocessor.timeout=1800
```

Lưu ý phương pháp: Test đã được xem trong những lần thử trước (B 67 rồi 29 cột),
nên không được mô tả là một holdout chưa từng xem. Lần sửa giữ B 29 cột cố định;
B_core chỉ để đối chiếu trên Train, không dùng điểm Test để đổi đặc trưng.
Điểm CV sau dò tham số không phải ước lượng độc lập cuối cùng. Hai kết quả K-NN
vẫn thuộc phần Hải; chương trình tổng hợp 4 mô hình sẽ báo thiếu cho tới khi Hải bổ sung.
