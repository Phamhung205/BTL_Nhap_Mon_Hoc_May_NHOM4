# Rà soát và sửa phần Đức — 07/10/2026

## Phạm vi và yêu cầu

Chỉ Feature Engineering B và Decision Tree A/B. Không làm K-NN, giao diện hay
error analysis của Hải. Giữ nguyên dữ liệu raw, nhãn, Luồng A và bộ xử lý A
của Mạnh; không chia lại Train/Test. Hai CSV B vẫn giữ đúng 5.634/1.409 dòng
và 29 cột, byte dữ liệu không đổi so với phiên bản trước của nhánh Đức.

## Lỗi đã sửa

1. Khi chạy bằng `python -m src.feature_engineering_b`, pickle cũ tham chiếu
   `__main__.FeatureEngineerB` nên tiến trình mới không nạp được. Lớp hiện nằm
   trong `src.duc_preprocessing`, có đường dẫn import ổn định cho CLI/notebook.
2. GridSearch trước đây nhận CSV đã điền thiếu trên toàn Train. Hiện mỗi fold
   clone pipeline và tự fit điền thiếu, one-hot, scaler A trên training fold.
   Test không được truyền vào hàm tìm tham số.
3. Mã cũ tạo nhiều đặc trưng không được dùng. B hiện chỉ tạo đúng 3 tương tác
   bàn giao. B_core giữ 26 cột để đối chiếu với B 29 cột bằng CV trên Train.
4. Bổ sung kiểm tra schema, hàng CSV thiếu/thừa, header trùng, giá trị số sai,
   infinity, độ dài X/y và toàn bộ ma trận A/B so với raw trước khi fit cây cuối.
5. Bổ sung môi trường Python 3.12 riêng `.venv-duc`, khóa thư viện chính trong
   `requirements.txt` chung của nhóm, bảng CV từng fold/cấu hình, dự đoán, hash dữ liệu,
   pipeline raw và hướng dẫn tái lập (mục cuối của file này).
6. Sửa mô tả lịch sử Test trong notebook: Test đã được xem ở các thử nghiệm
   trước; không được tuyên bố đây là holdout chưa từng được xem.

## Quy trình và kết quả

Chạy 3 × 120 cấu hình × 5 fold trên Train (1.800 fold fits, chưa tính refit).
Scoring: F1 cho Churn=Yes. Các file `duc_cv_A.csv`, `duc_cv_B_core.csv`,
`duc_cv_B.csv` chứa điểm từng fold và tham số. Cả ba cùng dùng
StratifiedKFold(5, shuffle=True, random_state=42).

| Luồng | Số cột | F1 CV tốt nhất |
|---|---:|---:|
| A | 45 | 0.6209339281 |
| B_core (đối chiếu) | 26 | 0.6221531481 |
| B (cố định) | 29 | 0.6262255392 |

Sau khi tìm tham số, fit cây cuối trên đúng CSV A/B đã kiểm tra khớp với
quy tắc fit toàn Train. Lưu cây nhận CSV và pipeline nhận raw, xác minh
dự đoán giống nhau trên cả Train và Test.

| Luồng | Accuracy | Precision Yes | Recall Yes | F1 Yes | CM [No, Yes] |
|---|---:|---:|---:|---:|---|
| A | 0.761533 | 0.535849 | 0.759358 | 0.628319 | [[789, 246], [90, 284]] |
| B | 0.745919 | 0.514184 | 0.775401 | 0.618337 | [[761, 274], [84, 290]] |

Tham số tốt nhất và metric không đổi sau sửa, nhưng quy trình CV hiện fit
tiền xử lý đúng trong từng fold. CV là điểm dùng chọn tham số, không phải một
đánh giá độc lập sau chọn mô hình. B có Recall Test cao hơn và F1 Test thấp hơn
A; kết quả này không được dùng để sửa tiếp bộ đặc trưng.

## Các cách kiểm tra đã chạy

`python -m unittest discover -s tests -v`: **13 tests đạt**.

- Đối chiếu A với CSV và `preprocessor_A.pkl` gốc của Mạnh.
- Đếm/tính độc lập các tương tác B theo từng dòng; kiểm tra hoán vị dòng.
- Đối chiếu toàn bộ dữ liệu và nhãn Train/Test với tập dữ liệu nguồn bằng multiset.
- Kiểm tra unknown category, missing value, tenure=0, input sai, clone chưa fit.
- Theo dõi trực tiếp 5 lần fit training fold và 1 lần refit để kiểm tra trung vị
  từng fold; xác minh transform Test không đổi trạng thái đã học.
- Chạy CLI trong thư mục tạm, sau đó tiến trình Python mới nạp pickle và biến
  đổi Test; đối chiếu chính xác với CSV B.
- Tính lại 5 fold của cấu hình tốt nhất A/B bằng pandas + các thành phần chuẩn
  SimpleImputer/StandardScaler/OneHotEncoder/ColumnTransformer; điểm khớp với
  GridSearch dùng transformer mới. Đây là cách triển khai độc lập.
- Đối chiếu tìm kiếm tuần tự và song song trên bài kiểm tra nhỏ: điểm CV, tham
  số và dự đoán giống nhau.
- Nạp lại cây/pipeline; kiểm tra dự đoán Train/Test giống nhau; tính thủ công
  TN/FP/FN/TP và Accuracy/Precision/Recall/F1; đối chiếu JSON và CSV dự đoán.
- Kiểm tra SHA-256 của 8 file dữ liệu và điểm/xếp hạng của 120 cấu hình mỗi luồng.

Notebook được thực thi bằng kernel `.venv-duc`: **6 cell code chạy, 0 cell lỗi**.
Notebook mặc định xác minh artifact từ CLI; bật RUN_TRAINING để chạy lại tìm kiếm.
`pip check`: không có dependency hỏng. `compileall` và `git diff --check`: đạt.
Đối chiếu Git với main: raw, nhãn, A và preprocessor A không bị thay đổi.

## Giới hạn còn lại

- Test đã được xem trong quá trình thử nghiệm trước khi sửa; bản sửa không thể
  biến lịch sử đó thành một đánh giá holdout mới. Giữ nguyên Test theo yêu cầu
  nhóm và công khai giới hạn này; không tạo thêm split.
- Các phiên bản được kiểm tra: Python 3.12.10, scikit-learn 1.9.0, NumPy 2.5.0,
  SciPy 1.18.0, joblib 1.5.3, pandas 2.2.3. Nên dùng môi trường đã khóa để nạp pickle.
- Có DeprecationWarning từ joblib khi gán shape mảng với NumPy 2.5 và cảnh báo
  event loop của Jupyter trên Windows; chúng không làm các bước kiểm tra thất bại.
  Không thay thư viện lõi giữa lúc huấn luyện/đánh giá chỉ để ẩn cảnh báo.
- Môi trường `.venv` cũ từng bị Windows Application Control chặn DLL; dùng
  `.venv-duc` đã kiểm tra. Không thay đổi chính sách bảo mật Windows.
- Bộ kiểm tra không phải bằng chứng rằng mọi đầu vào tương lai đều hoạt động.
  Chưa có hai kết quả K-NN của Hải nên chưa thể chọn mô hình tốt nhất toàn nhóm.

Các JSON trong `results/` chỉ có hai kết quả của Đức ngoài template, vẫn tương
thích hàm đọc kết quả của Hùng. Bảng đối chiếu và manifest nằm trong `report/`
để không làm bộ tổng hợp nhầm chúng thành kết quả mô hình mới.

## Cách chạy lại phần Đức

Phần Đức được kiểm tra với Python 3.12.10. Trên Windows, tạo môi trường riêng
và dùng đúng Python trong môi trường này (không dùng `.venv` cũ):

```powershell
py -3.12 -m venv .venv-duc
.\.venv-duc\Scripts\python.exe -m pip install -r requirements.txt
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
