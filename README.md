# Đề tài 9: Dự đoán khách hàng rời bỏ dịch vụ viễn thông

## 1. Thông tin nhóm

- Trường: **Đại học Đại Nam** -- Khoa Công nghệ thông tin
- Học phần: **FIT4013 -- Nhập môn Học Máy**
- Đề tài 9: **Dự đoán khách hàng rời bỏ dịch vụ viễn thông (Telco Customer Churn Prediction)**
- Thành viên Nhóm 4:
  - **Phạm Ngọc Hùng (Nhóm trưởng)** -- MSV: 1871020265: Quản lý dự án, tổng hợp đánh giá, báo cáo LaTeX/Word
  - **Bùi Đình Mạnh** -- MSV: 1871020379: Khám phá EDA, chia Train/Test, tiền xử lý Luồng A
  - **Phạm Thế Đức** -- MSV: 1871020147: Kỹ thuật đặc trưng Luồng B, Decision Tree trên Luồng A/B
  - **La Văn Hải** -- MSV: 1871020215: K-NN trên Luồng A/B, Error Analysis, giao diện demo Streamlit

## 2. Cấu trúc dự án

```text
BTL_Nhap_Mon_Hoc_May_NHOM4/
├── app.py                      # Giao diện Web Demo Streamlit (Điểm thưởng GUI)
├── data/                       # Dữ liệu raw và processed
├── models/                     # preprocessor_A.pkl, decision_tree_A/B, knn_A/B
├── notebooks/                  # 7 Notebooks phân tích chi tiết của 4 thành viên
├── results/                    # 4 file JSON kết quả + 30 mẫu ca lỗi
├── report/
│   ├── main.pdf                # Báo cáo hoàn chỉnh định dạng PDF vector chuẩn A4
│   ├── main.tex                # Báo cáo học thuật LaTeX chuẩn 6 mục
│   ├── report.html             # Bản HTML giao diện học thuật đồng bộ
│   ├── model_comparison.csv    # Bảng tổng hợp đối sánh kết quả
│   └── figures/                # Logo ĐH Đại Nam, ma trận nhầm lẫn, phân tích lỗi, cây
├── src/                        # Mã nguồn logic tái sử dụng
├── tests/                      # Bộ kiểm thử đơn vị tự động (7 unit tests)
├── AI_USAGE.md                 # Khai báo minh bạch việc sử dụng công cụ AI
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

## 6. Phương án Baseline & Đánh giá

- **Mô hình Baseline:** Decision Tree mặc định trên Luồng A (`depth=None`, không cân bằng trọng số) đạt `F1 = 0.4974`, `Recall = 0.5053`.
- **Mô hình tối ưu đề xuất:** Decision Tree Luồng A (`max_depth=5`, `class_weight="balanced"`) đạt `F1 = 0.6258`, `Recall = 0.7914` (bắt được gần 80% khách hàng có nguy cơ rời mạng).
- Với bài toán Churn, không chỉ nhìn Accuracy. Báo cáo tập trung vào Recall và F1-score của lớp khách hàng rời bỏ (`Churn = Yes`) để tránh kết luận sai khi dữ liệu mất cân bằng.

## 7. Chạy Ứng dụng Demo Streamlit (Điểm thưởng)

Chạy ứng dụng giao diện web demo trực quan từ thư mục gốc dự án:

```bash
streamlit run app.py
```

Ứng dụng hỗ trợ:
- Nhập trực quan 19 trường thông tin khách hàng, có sẵn các mẫu hồ sơ nhanh (Preset).
- Chọn 1 trong 4 mô hình để suy luận và tính xác suất rời mạng (Churn Probability).
- Đưa ra các khuyến nghị hành động thiết thực cho bộ phận CSKH.
- Xem phân tích lỗi (Error Analysis) và tra cứu 30 ca lỗi tiêu biểu trên tập Test.

## 8. Chạy Kiểm thử Đơn vị (Unit Tests)

```bash
python -m unittest discover -s tests -v
```

## 9. Báo cáo & Khai báo AI

- **Báo cáo LaTeX chính:** `report/main.tex` (chuẩn cấu trúc 6 mục của học phần).
- **Bản PDF xuất hoàn chỉnh:** `report/main.pdf`.
- **Khai báo sử dụng công cụ AI:** `AI_USAGE.md` (minh bạch theo Mục 2.3).
