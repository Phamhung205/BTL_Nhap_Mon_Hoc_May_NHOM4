# LỜI NÓI ĐẦU

Trong bối cảnh nền kinh tế số và sự phát triển bùng nổ của hạ tầng mạng viễn thông, thị trường cung cấp dịch vụ viễn thông đã bước vào giai đoạn bão hòa với sự cạnh tranh gay gắt giữa các nhà mạng. Việc duy trì và chăm sóc khách hàng hiện hữu đóng vai trò sống còn, bởi các nghiên cứu quản trị kinh doanh đã chỉ ra rằng chi phí để tiếp cận và thu hút một khách hàng mới thường tốn kém gấp 5 đến 7 lần so với chi phí duy trì một khách hàng sẵn có. Khi một khách hàng rời mạng (*Customer Churn*), doanh nghiệp không chỉ mất đi dòng doanh thu định kỳ mà còn đánh mất thị phần vào tay đối thủ cạnh tranh.

Để giải quyết bài toán cấp thiết đó, nhóm sinh viên Nhóm 4 lựa chọn thực hiện **Đề tài 9: Dự đoán khách hàng rời bỏ dịch vụ viễn thông (Telco Customer Churn Prediction)** thuộc học phần **FIT4013 -- Nhập môn Học Máy**. Dự án tập trung ứng dụng các kỹ thuật học máy có giám sát nhằm phân tích dữ liệu lịch sử khách hàng, phát hiện sớm các đặc trưng rủi ro cao và đưa ra dự báo chính xác giúp bộ phận Chăm sóc khách hàng (CSKH) có chính sách can thiệp kịp thời.

Báo cáo bài tập lớn của nhóm được cấu trúc chặt chẽ thành 6 chương nội dung chính:

- **Chương 1:** Đặt vấn đề và phân tích yêu cầu (Bối cảnh, mục tiêu, khám phá dữ liệu EDA chuyên sâu trên 7.043 khách hàng).
- **Chương 2:** Thiết kế giải pháp và quy trình học máy (Sơ đồ Pipeline tổng thể, nguyên tắc cô lập chống Data Leakage, thiết kế Luồng A 45 đặc trưng và Luồng B 17 đặc trưng, không gian siêu tham số của Decision Tree và K-NN).
- **Chương 3:** Kiến trúc hệ thống và phân tích mã nguồn (Cấu trúc thư mục thực tế, bảng phân công nhiệm vụ 4 thành viên, phân tích các module trong `src/`, 7 notebooks và 7 bài kiểm thử tự động trong `tests/`).
- **Chương 4:** Thử nghiệm và kết quả (Xác lập mô hình Baseline đối sánh, kiểm định chéo 5-fold Stratified CV, bảng tổng hợp kết quả 5 mô hình trên tập Test chung 1.409 mẫu, trực quan hóa ma trận nhầm lẫn, độ quan trọng đặc trưng và cây quyết định).
- **Chương 5:** Thảo luận, so sánh và phân tích lỗi (Đối chiếu bước nhảy vọt so với Baseline, so sánh chuyên sâu Decision Tree và K-NN dưới góc độ chi phí bất đối xứng ngành viễn thông, mổ xẻ định lượng các ca lỗi FN/FP).
- **Chương 6:** Tổng kết và đánh giá (Bảng đối chiếu mức độ đáp ứng yêu cầu, giới thiệu ứng dụng web demo Streamlit `app.py`, hạn chế và hướng phát triển).
- **Phần Kết luận, Phụ lục và Danh mục tài liệu tham khảo.**

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# MỤC LỤC

- **LỜI NÓI ĐẦU**
- **BẢNG CÁC TỪ VIẾT TẮT**
- **CHƯƠNG 1. ĐẶT VẤN ĐỀ VÀ PHÂN TÍCH YÊU CẦU**
  - 1.1. Giới thiệu bài toán và bối cảnh thực tế
    - *1.1.1. Bối cảnh cạnh tranh trong ngành viễn thông*
    - *1.1.2. Mục tiêu của hệ thống dự đoán Churn*
    - *1.1.3. Lý do áp dụng học máy và phân loại rủi ro*
  - 1.2. Khám phá và phân tích dữ liệu (EDA)
    - *1.2.1. Cấu trúc bộ dữ liệu Telco Customer Churn*
    - *1.2.2. Xử lý giá trị bất thường TotalCharges và customerID*
    - *1.2.3. Phân tích mất cân bằng dữ liệu 73.46% vs 26.54% và độ đo phù hợp*
    - *1.2.4. Khảo sát tương quan giữa các nhóm dịch vụ và quyết định rời mạng*
- **CHƯƠNG 2. THIẾT KẾ GIẢI PHÁP VÀ QUY TRÌNH HỌC MÁY**
  - 2.1. Sơ đồ quy trình tổng quát (Pipeline)
  - 2.2. Phân chia dữ liệu và nguyên tắc hạn chế rò rỉ dữ liệu (Data Leakage)
  - 2.3. Thiết kế hai luồng tiền xử lý (Luồng A vs Luồng B)
    - *2.3.1. Luồng A: Pipeline cơ bản 45 đặc trưng*
    - *2.3.2. Luồng B: Kỹ thuật đặc trưng cải tiến 17 đặc trưng*
  - 2.4. Lựa chọn thuật toán và không gian siêu tham số
    - *2.4.1. Cây quyết định (Decision Tree)*
    - *2.4.2. K-Láng giềng gần nhất (K-NN)*
- **CHƯƠNG 3. KIẾN TRÚC HỆ THỐNG VÀ PHÂN TÍCH MÃ NGUỒN**
  - 3.1. Cấu trúc thư mục kho mã nguồn
  - 3.2. Bảng phân công nhiệm vụ và vai trò từng thành viên
  - 3.3. Các hàm và module then chốt
  - 3.4. Kiểm thử tự động tính toàn vẹn (Unit Testing)
  - 3.5. Hướng dẫn chạy và tái lập thực nghiệm
- **CHƯƠNG 4. THỬ NGHIỆM VÀ KẾT QUẢ**
  - 4.1. Thiết lập thí nghiệm và độ đo đánh giá
  - 4.2. Phương án Baseline làm mốc đối sánh
  - 4.3. Bảng tổng hợp kết quả thực nghiệm trên tập Test chung
  - 4.4. Trực quan hóa ma trận nhầm lẫn (Confusion Matrix)
  - 4.5. Độ quan trọng đặc trưng và cấu trúc cây quyết định
- **CHƯƠNG 5. THẢO LUẬN, SO SÁNH VÀ PHÂN TÍCH LỖI**
  - 5.1. So sánh với mô hình Baseline
  - 5.2. So sánh chuyên sâu Decision Tree và K-NN dưới góc độ kinh doanh viễn thông
  - 5.3. So sánh hiệu quả giữa Luồng A và Luồng B
  - 5.4. Phân tích định lượng ca lỗi chi tiết (Error Analysis)
  - 5.5. Hạn chế của dữ liệu và giải pháp hiện tại
- **CHƯƠNG 6. TỔNG KẾT VÀ ĐÁNH GIÁ**
  - 6.1. Bảng đối chiếu mục tiêu và mức độ đáp ứng yêu cầu
  - 6.2. Ứng dụng giao diện Web Demo Streamlit
  - 6.3. Những hạn chế và hướng phát triển
- **KẾT LUẬN**
- **PHỤ LỤC**
- **DANH MỤC TÀI LIỆU THAM KHẢO**

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# BẢNG CÁC TỪ VIẾT TẮT

*Bảng 0.1. Danh mục các thuật ngữ và ký hiệu viết tắt trong báo cáo*

| STT | TỪ VIẾT TẮT | VIẾT ĐẦY ĐỦ |
| :---: | :--- | :--- |
| 1 | **CSDL** | Cơ sở dữ liệu |
| 2 | **ML** | Machine Learning (Học máy) |
| 3 | **EDA** | Exploratory Data Analysis (Phân tích khám phá dữ liệu) |
| 4 | **DT** | Decision Tree (Cây quyết định) |
| 5 | **K-NN** | K-Nearest Neighbors (K-láng giềng gần nhất) |
| 6 | **CV** | Cross-Validation (Kiểm định chéo phân tầng) |
| 7 | **FN** | False Negative (Bỏ sót khách rời mạng -- Đoán nhầm thành Ở lại) |
| 8 | **FP** | False Positive (Nhầm khách ở lại -- Đoán nhầm thành Rời bỏ) |
| 9 | **TP** | True Positive (Dự đoán Đúng khách hàng rời bỏ dịch vụ) |
| 10 | **TN** | True Negative (Dự đoán Đúng khách hàng ở lại với dịch vụ) |
| 11 | **CM** | Confusion Matrix (Ma trận nhầm lẫn) |
| 12 | **CSKH** | Chăm sóc khách hàng |
| 13 | **CLV** | Customer Lifetime Value (Giá trị vòng đời khách hàng) |
| 14 | **UI** | User Interface (Giao diện người dùng) |

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# CHƯƠNG 1. ĐẶT VẤN ĐỀ VÀ PHÂN TÍCH YÊU CẦU

## 1.1. Giới thiệu bài toán và bối cảnh thực tế

### 1.1.1. Bối cảnh cạnh tranh trong ngành viễn thông
Ngành viễn thông và dịch vụ Internet hiện đại đang chứng kiến sự dịch chuyển mạnh mẽ từ chiến lược mở rộng quy mô thuê bao sang chiến lược tối ưu hóa giá trị vòng đời khách hàng (*Customer Lifetime Value -- CLV*). Sự xuất hiện của nhiều nhà cung cấp dịch vụ mạng với các gói cước cạnh tranh cùng chính sách chuyển mạng giữ số linh hoạt khiến tỷ lệ rời mạng của khách hàng ngày càng gia tăng. Nếu chỉ chờ đợi đến khi khách hàng gửi yêu cầu hủy hợp đồng thì mọi nỗ lực giữ chân của bộ phận CSKH đều đã quá muộn và chi phí thu hút khách hàng mới thay thế sẽ cao gấp 5 đến 7 lần.

### 1.1.2. Mục tiêu của hệ thống dự đoán Churn
Mục tiêu trung tâm của đề tài là xây dựng một quy trình học máy (*Machine Learning Pipeline*) hoàn chỉnh, có khả năng dự đoán chính xác xác suất một khách hàng sẽ ngừng sử dụng dịch vụ viễn thông dựa trên thông tin nhân khẩu học, gói cước và hành vi tiêu dùng. Thông qua mô hình này, doanh nghiệp có thể chủ động sàng lọc sớm nhóm khách hàng có rủi ro rời bỏ cao để kịp thời áp dụng các biện pháp chăm sóc khách hàng, điều chỉnh gói cước hoặc đề xuất chuyển đổi hợp đồng dài hạn trước khi khách hàng chính thức rời mạng.

### 1.1.3. Lý do áp dụng học máy và phân loại rủi ro
Trong cơ sở dữ liệu viễn thông gồm hàng vạn đến hàng triệu thuê bao, việc rà soát thủ công hoặc áp dụng các bộ quy tắc cứng nhắc là hoàn toàn bất khả thi. Học máy có giám sát mang lại khả năng tự động trích xuất các mẫu tương quan phi tuyến tính phức tạp giữa nhiều chiều đặc trưng (ví dụ: sự kết hợp giữa hợp đồng từng tháng, gói cáp quang, phương thức thanh toán séc điện tử và việc thiếu hụt các dịch vụ bảo vệ). Qua đó, hệ thống phân loại chính xác từng khách hàng theo xác suất rủi ro để phân bổ ngân sách khuyến mãi đúng trọng tâm.

## 1.2. Khám phá và phân tích dữ liệu (EDA)

### 1.2.1. Cấu trúc bộ dữ liệu Telco Customer Churn
Dữ liệu sử dụng trong bài tập lớn là bộ dữ liệu thực tế **Telco Customer Churn** do IBM công bố (`data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`). Bộ dữ liệu gồm **7.043 mẫu quan sát** (mỗi mẫu đại diện cho một khách hàng) với **21 cột thông tin** ban đầu:

- **Biến mục tiêu nhị phân (1 cột):** `Churn` nhận giá trị `"Yes"` (khách hàng rời bỏ dịch vụ) hoặc `"No"` (khách hàng tiếp tục duy trì dịch vụ).
- **Mã định danh (1 cột):** `customerID` chứa mã số duy nhất của từng thuê bao, mang tính ngẫu nhiên hành chính và không có giá trị dự báo hành vi nên được loại bỏ ngay từ bước đầu.
- **Đặc trưng số / nhị phân số (4 cột):** Chỉ số người cao tuổi (`SeniorCitizen` nhận giá trị 0 hoặc 1), thời gian gắn bó tính theo tháng (`tenure` từ 0 đến 72 tháng), mức cước hàng tháng (`MonthlyCharges` từ 18.25 USD đến 118.75 USD) và tổng cước tích lũy (`TotalCharges`).
- **Đặc trưng phân loại dạng chuỗi (15 cột):** Giới tính (`gender`), tình trạng hôn nhân (`Partner`), người phụ thuộc (`Dependents`), dịch vụ điện thoại (`PhoneService`, `MultipleLines`), dịch vụ Internet (`InternetService`), 4 dịch vụ bảo vệ và hỗ trợ kỹ thuật (`OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`), 2 dịch vụ giải trí (`StreamingTV`, `StreamingMovies`), loại hợp đồng (`Contract`), hóa đơn điện tử (`PaperlessBilling`) và phương thức thanh toán (`PaymentMethod`).

### 1.2.2. Xử lý giá trị bất thường TotalCharges và customerID
Trong quá trình khảo sát tại `notebooks/01_split_data.ipynb` và `02_eda_preprocess_A.ipynb`, nhóm phát hiện cột `TotalCharges` ban đầu được pandas nhận diện là kiểu chuỗi (`object`) thay vì số thực (`float64`). Phân tích chi tiết làm rõ:

- Có đúng **11 dòng quan sát** có giá trị `TotalCharges` chỉ là ký tự khoảng trắng (`" "`).
- Toàn bộ 11 quan sát này đều có thuộc tính thâm niên `tenure == 0`, tức là khách hàng vừa ký hợp đồng mới trong tháng đầu tiên và chưa phát sinh kỳ cước thanh toán nào.
- **Giải pháp xử lý:** Cột `TotalCharges` được ép kiểu sang số thực bằng `pd.to_numeric(..., errors='coerce')` (chuyển 11 ô khoảng trắng thành `NaN`). Ở Luồng A, giá trị thiếu được điền bằng trung vị (`SimpleImputer(strategy='median')`) học độc lập trên tập Train; ở Luồng B, giá trị thiếu của khách hàng mới được gán chính xác theo nghiệp vụ bằng `tenure * MonthlyCharges = 0`. Cột `customerID` được loại bỏ hoàn toàn để tránh bùng nổ số chiều.

### 1.2.3. Phân tích mất cân bằng dữ liệu 73.46% vs 26.54% và độ đo phù hợp
Phân bố nhãn mục tiêu `Churn` trên toàn bộ 7.043 mẫu cho thấy sự chênh lệch rõ rệt:

- **Nhãn "No" (Khách hàng ở lại):** 5.174 mẫu, chiếm **73.46%**.
- **Nhãn "Yes" (Khách hàng rời bỏ):** 1.869 mẫu, chiếm **26.54%**.

Tỷ lệ mất cân bằng xấp xỉ **2.77 : 1** (gần 3 : 1) dẫn đến hệ quả phương pháp luận quan trọng:

- Độ đo **Accuracy (Độ chính xác tổng thể)** không phản ánh đúng chất lượng mô hình. Một bộ phân loại ngây thơ (*Dummy Classifier*) luôn đoán mọi khách hàng là `"No"` vẫn đạt `Accuracy = 73.46%`, nhưng hoàn toàn vô dụng trong thực tế vì bỏ sót 100% khách hàng rời mạng (`Recall = 0.0000`, `F1 = 0.0000`).
- Do đó, nhóm xác lập hai chỉ số trọng tâm là **Recall (Độ nhạy)** và **F1-score** tính trên lớp dương `Churn = "Yes"`, kết hợp phân tích chi tiết ma trận nhầm lẫn (*Confusion Matrix*).

### 1.2.4. Khảo sát tương quan giữa các nhóm dịch vụ và quyết định rời mạng
Kết quả phân tích thống kê đa biến (EDA) trên dữ liệu thực tế đã chỉ ra các quy luật hành vi cốt lõi:

1. **Loại hình hợp đồng (`Contract`):** Khách hàng ký hợp đồng từng tháng (*Month-to-month*) có tỷ lệ rời mạng lên tới **42.71%**, cao gấp gần 4 lần so với hợp đồng 1 năm (*One year*: **11.27%**) và gấp hơn 15 lần so với hợp đồng 2 năm (*Two year*: chỉ **2.83%**).
2. **Dịch vụ Internet (`InternetService`):** Nhóm thuê bao sử dụng cáp quang (*Fiber optic*) có tỷ lệ rời mạng rất cao (**41.89%**), vượt xa nhóm cáp đồng *DSL* (**18.96%**) và nhóm không đăng ký Internet (**7.40%**).
3. **Phương thức thanh toán (`PaymentMethod`):** Khách hàng thanh toán bằng séc điện tử (*Electronic check*) có tỷ lệ rời mạng cao nhất (**45.29%**), trong khi séc gửi thư (*Mailed check*) là **19.11%**, chuyển khoản tự động (*Bank transfer automatic*) là **16.71%** và thẻ tín dụng tự động (*Credit card automatic*) chỉ **15.24%**.
4. **Dịch vụ bảo vệ và hỗ trợ kỹ thuật:** Nhóm khách hàng không đăng ký bảo mật trực tuyến (`OnlineSecurity = "No"`) có tỷ lệ rời mạng **41.77%** (so với **14.61%** khi có đăng ký); tương tự, nhóm thiếu hỗ trợ kỹ thuật (`TechSupport = "No"`) có tỷ lệ rời mạng **41.64%** (so với **15.17%** khi có đăng ký).
5. **Thâm niên (`tenure`) và Cước tháng (`MonthlyCharges`):** Khách hàng rời mạng tập trung mạnh ở giai đoạn đầu mới gia nhập (trung vị `tenure` chỉ **10 tháng** so với **38 tháng** của nhóm ở lại) và chịu mức cước hàng tháng cao hơn (trung vị **79.65 USD** so với **64.43 USD**).

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# CHƯƠNG 2. THIẾT KẾ GIẢI PHÁP VÀ QUY TRÌNH HỌC MÁY

## 2.1. Sơ đồ quy trình tổng quát (Pipeline)
Hệ thống học máy của Nhóm 4 được thiết kế thành một đường ống khép kín gồm 6 giai đoạn chuẩn hóa:

1. **Nạp và làm sạch sơ bộ:** Đọc tệp dữ liệu gốc `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`, chuyển đổi kiểu số cho `TotalCharges` và loại bỏ `customerID`.
2. **Phân chia Train/Test phân tầng cố định:** Sử dụng hàm `chia_du_lieu()` trong `src/split_data.py` để tách một lần duy nhất thành tập Train (80% -- 5.634 mẫu) và tập Test (20% -- 1.409 mẫu) với `random_state = 42` và `stratify = y`, lưu thành `X_train_raw.csv`, `X_test_raw.csv`, `y_train.csv`, `y_test.csv`.
3. **Tiền xử lý và tạo đặc trưng theo 2 luồng độc lập:**
   - **Luồng A (Mạnh):** Chuẩn hóa và mã hóa One-Hot bằng `ColumnTransformer`, xuất `X_train_A.csv`, `X_test_A.csv` (45 cột) và lưu `models/preprocessor_A.pkl`.
   - **Luồng B (Đức):** Thực thi kỹ thuật đặc trưng nghiệp vụ qua `src/feature_engineering_b.py`, xuất `X_train_B.csv`, `X_test_B.csv` (17 cột).
4. **Huấn luyện và tinh chỉnh siêu tham số:** Chạy `GridSearchCV` với kiểm định chéo phân tầng 5-fold (`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`) chỉ trên tập Train, tối ưu hóa theo `F1-score` của lớp `Churn = "Yes"` cho cả Decision Tree (`src/train_decision_tree.py`) và K-NN (`src/train_knn.py`).
5. **Đánh giá độc lập và tổng hợp kết quả:** Đánh giá 4 mô hình đã tinh chỉnh cùng mô hình Baseline trên tập Test chung (1.409 mẫu) qua `src/evaluate.py`, xuất 4 tệp JSON vào `results/` và tổng hợp thành `report/model_comparison.csv` bằng `src/aggregate_results.py`.
6. **Phân tích lỗi và triển khai ứng dụng:** Giải phẫu các ca dự đoán sai qua `src/error_analysis.py` và đóng gói giao diện dự báo tương tác bằng Streamlit tại `app.py`.

## 2.2. Phân chia dữ liệu và nguyên tắc hạn chế rò rỉ dữ liệu (Data Leakage)
Rò rỉ dữ liệu (*Data Leakage*) xảy ra khi thông tin từ tập kiểm thử hoặc fold thẩm định vô tình lọt vào quá trình huấn luyện. Để ngăn chặn triệt để:

- **Chia dữ liệu một lần duy nhất:** Cả 4 thành viên dùng chung các tệp trong `data/processed/` do Mạnh khởi tạo với `TEST_SIZE = 0.20`, `RANDOM_STATE = 42` (khai báo tại `src/config.py`). Tuyệt đối không thành viên nào tự chia lại dữ liệu.
- **Bảo toàn phân phối nhãn (`stratify = y`):** Tập Train (5.634 mẫu) và tập Test (1.409 mẫu) đều giữ chính xác tỷ lệ 73.46% `"No"` và 26.54% `"Yes"` (trong tập Test có đúng **1.035 mẫu `"No"`** và **374 mẫu `"Yes"`**).
- **Cô lập tham số tiền xử lý:** Ở Luồng A, `preprocessor_A` chỉ gọi `.fit(X_train_raw)` trên tập Train và chỉ gọi `.transform(X_test_raw)` trên tập Test. Ở Luồng B, hàm `tao_dac_trung_B()` biến đổi độc lập từng dòng mà không dùng thống kê toàn cục; khi đưa vào K-NN Luồng B, bước `StandardScaler()` được đóng gói bên trong `sklearn.pipeline.Pipeline` để chỉ `fit` riêng trên từng fold huấn luyện của quá trình 5-fold CV.

## 2.3. Thiết kế hai luồng tiền xử lý (Luồng A vs Luồng B)

### 2.3.1. Luồng A: Pipeline cơ bản 45 đặc trưng
Luồng A được thiết kế trong `notebooks/02_eda_preprocess_A.ipynb` sử dụng `ColumnTransformer` gồm 2 nhánh song song:

- **Nhánh số (`num` -- 4 cột `SeniorCitizen`, `tenure`, `MonthlyCharges`, `TotalCharges`):** Đi qua `Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())])` để điền khuyết bằng trung vị và chuẩn hóa về trung bình 0, độ lệch chuẩn 1.
- **Nhánh phân loại (`cat` -- 15 cột định tính còn lại):** Đi qua `Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])`, sinh ra 41 cột nhị phân One-Hot.
- **Đầu ra:** Ma trận đặc trưng gồm `4 + 41 = 45` cột số hóa (`X_train_A.csv` kích thước `5634 x 45`, `X_test_A.csv` kích thước `1409 x 45`), đối tượng tiền xử lý được lưu tại `models/preprocessor_A.pkl`.

### 2.3.2. Luồng B: Kỹ thuật đặc trưng cải tiến 17 đặc trưng
Luồng B được hiện thực hóa tại module `src/feature_engineering_b.py` (hàm `tao_dac_trung_B(X)`), vận dụng tri thức nghiệp vụ viễn thông để tinh gọn 19 cột đầu vào thành đúng **17 đặc trưng giàu thông tin**:

1. **Nhóm đặc trưng nhị phân giữ nguyên / mã hóa 0-1 (4 cột):** `SeniorCitizen` (0/1), `Partner` (`Yes`=1, `No`=0), `Dependents` (`Yes`=1, `No`=0), `PaperlessBilling` (`Yes`=1, `No`=0).
2. **Nhóm mã hóa thứ bậc -- Ordinal Encoding (2 cột):**
   - `PhoneLines`: Gán thứ bậc từ cột `MultipleLines` (`"No phone service"` = 0, `"No"` = 1, `"Yes"` = 2).
   - `ContractLength`: Gán thứ bậc theo mức độ cam kết hợp đồng (`"Month-to-month"` = 0, `"One year"` = 1, `"Two year"` = 2).
3. **Nhóm biến số, phân nhóm vòng đời và biến đổi Logarit (4 cột):**
   - `tenure`: Số tháng gắn bó gốc (0 -- 72).
   - `TenureGroup`: Phân nhóm thâm niên bằng `pd.cut` theo 4 giai đoạn vòng đời: `0` (0--12 tháng, giai đoạn rủi ro cao nhất), `1` (13--24 tháng), `2` (25--48 tháng), và `3` (>48 tháng, khách hàng trung thành).
   - `MonthlyCharges`: Cước phí hàng tháng gốc.
   - `LogTotalCharges`: Điền khuyết `TotalCharges` cho khách hàng mới (`tenure = 0`) bằng `tenure * MonthlyCharges = 0`, sau đó lấy logarit tự nhiên làm mượt độ lệch phải:
$$\text{LogTotalCharges} = \ln(1 + \text{TotalCharges})$$
4. **Nhóm đặc trưng Internet và Phương thức thanh toán (4 cột):**
   - `HasInternet`: Có sử dụng dịch vụ Internet (`InternetService != "No"`).
   - `IsFiber`: Sử dụng gói cáp quang nguy cơ cao (`InternetService == "Fiber optic"`).
   - `IsElectronicCheck`: Thanh toán bằng séc điện tử (`PaymentMethod == "Electronic check"`).
   - `IsAutoPayment`: Thanh toán tự động (`PaymentMethod` chứa từ khóa `"automatic"`).
5. **Chỉ số thiếu hụt dịch vụ bảo vệ (`MissingProtectionCount` -- 1 cột):** Đếm số lượng dịch vụ mang giá trị `"No"` trong 4 dịch vụ cốt lõi (`OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`), nhận giá trị nguyên từ `0` đến `4`.
6. **Đặc trưng tương tác nguy cơ cao (2 cột):**
   - `MonthToMonth_Fiber`: Kết hợp đồng thời hợp đồng từng tháng và dùng cáp quang (`(Contract == "Month-to-month") & (InternetService == "Fiber optic")`).
   - `MonthToMonth_ElectronicCheck`: Kết hợp đồng thời hợp đồng từng tháng và trả qua séc điện tử (`(Contract == "Month-to-month") & (PaymentMethod == "Electronic check")`).
7. **Loại bỏ nhiễu:** Lược bỏ 3 cột có tương quan rất yếu với Churn là `gender`, `StreamingTV` và `StreamingMovies`, giúp giảm hơn **62.2% số chiều** (từ 45 cột xuống 17 cột).

![](report/figures/fe_missing_protection.png){width=460px}

*Hình 2.1. Tương quan giữa số dịch vụ bảo vệ còn thiếu (MissingProtectionCount) và tỷ lệ rời mạng ở Luồng B*

## 2.4. Lựa chọn thuật toán và không gian siêu tham số

### 2.4.1. Cây quyết định (Decision Tree)
Thuật toán phân chia đệ quy không gian đặc trưng theo hướng cực đại hóa độ giảm vẩn đục (*Impurity Reduction*). Trong `src/train_decision_tree.py`, lưới siêu tham số `PARAM_GRID` được thiết lập gồm **144 tổ hợp** (tương ứng 720 lần huấn luyện trong 5-fold CV cho mỗi luồng):

- Tiêu chuẩn phân nhánh: `criterion` $\in$ `['gini', 'entropy']`.
- Độ sâu tối đa của cây: `max_depth` $\in$ `[3, 4, 5, 6, 7, 8, 10, 12, None]`.
- Số lượng mẫu tối thiểu tại một nút lá: `min_samples_leaf` $\in$ `[1, 5, 10, 20, 30, 50, 75, 100]`.
- Trọng số cân bằng lớp: `class_weight` $\in$ `[None, 'balanced']`. Khi bật `'balanced'`, trọng số của lớp thiểu số `Churn = "Yes"` được nhân lên tỷ lệ nghịch với tần suất xuất hiện, buộc cây quyết định ưu tiên phát hiện khách hàng rời mạng.

### 2.4.2. K-Láng giềng gần nhất (K-NN)
Thuật toán phi tham số phân loại một điểm dữ liệu mới dựa trên biểu quyết của $k$ điểm láng giềng gần nhất. Trong `src/train_knn.py`, lưới siêu tham số `PARAM_GRID_A` và `PARAM_GRID_B` gồm **40 tổ hợp** (200 lần huấn luyện trong 5-fold CV cho mỗi luồng):

- Số láng giềng gần nhất: `n_neighbors` $\in$ `[3, 5, 7, 9, 11, 15, 21, 31, 41, 51]`.
- Phương thức tính trọng số bầu chọn: `weights` $\in$ `['uniform', 'distance']`.
- Hàm đo khoảng cách: `metric` $\in$ `['euclidean', 'manhattan']`.
- **Đặc biệt ở Luồng B:** Do các biến `tenure`, `MonthlyCharges`, `LogTotalCharges` chưa chuẩn hóa thang đo, mô hình được bọc trong `Pipeline([('scaler', StandardScaler()), ('knn', KNeighborsClassifier())])` để tự động chuẩn hóa bên trong từng fold CV mà không gây rò rỉ dữ liệu.

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# CHƯƠNG 3. KIẾN TRÚC HỆ THỐNG VÀ PHÂN TÍCH MÃ NGUỒN

## 3.1. Cấu trúc thư mục kho mã nguồn
Dự án được tổ chức theo kiến trúc module hóa rõ ràng, đồng bộ hoàn toàn với kho mã nguồn thực tế của nhóm:

```text
BTL_Nhap_Mon_Hoc_May_NHOM4/
├── data/
│   ├── raw/
│   │   └── WA_Fn-UseC_-Telco-Customer-Churn.csv    # Dữ liệu gốc IBM (7.043 mẫu x 21 cột)
│   └── processed/
│       ├── X_train_raw.csv, X_test_raw.csv         # Tập đặc trưng thô sau chia 80/20 (19 cột)
│       ├── X_train_A.csv, X_test_A.csv             # Dữ liệu Luồng A (45 đặc trưng)
│       ├── X_train_B.csv, X_test_B.csv             # Dữ liệu Luồng B (17 đặc trưng)
│       └── y_train.csv, y_test.csv                 # Nhãn mục tiêu Churn (5.634 Train / 1.409 Test)
├── models/
│   ├── preprocessor_A.pkl                          # ColumnTransformer đã fit trên Train Luồng A
│   ├── decision_tree_A.pkl                         # Mô hình Decision Tree tối ưu Luồng A
│   ├── decision_tree_B.pkl                         # Mô hình Decision Tree tối ưu Luồng B
│   ├── knn_A.pkl                                   # Mô hình K-NN tối ưu Luồng A
│   └── knn_B.pkl                                   # Pipeline (StandardScaler + K-NN) tối ưu Luồng B
├── notebooks/
│   ├── 01_split_data.ipynb                         # Chia dữ liệu Train/Test chuẩn phân tầng (Mạnh)
│   ├── 02_eda_preprocess_A.ipynb                   # Phân tích EDA & Tiền xử lý Luồng A (Mạnh)
│   ├── 03_feature_engineering_B.ipynb              # Thiết kế & phân tích 17 đặc trưng Luồng B (Đức)
│   ├── 04_decision_tree_A_B.ipynb                  # Thực nghiệm Decision Tree trên Luồng A & B (Đức)
│   ├── 05_knn_A_B.ipynb                            # Thực nghiệm K-NN trên Luồng A & B (Hải)
│   ├── 06_error_analysis.ipynb                     # Phân tích định lượng ca lỗi FN/FP (Hải)
│   └── tong_hop_ket_qua.ipynb                      # Tổng hợp đối sánh 5 mô hình & Baseline (Hùng)
├── results/
│   ├── duc_decision_tree_A.json                    # Kết quả & siêu tham số DT Luồng A
│   ├── duc_decision_tree_B.json                    # Kết quả & siêu tham số DT Luồng B
│   ├── hai_knn_A.json                              # Kết quả & siêu tham số K-NN Luồng A
│   ├── hai_knn_B.json                              # Kết quả & siêu tham số K-NN Luồng B
│   ├── error_cases_sample.csv                      # 30 hồ sơ khách hàng dự đoán sai tiêu biểu
│   └── result_template.json                        # Khuôn mẫu JSON chuẩn hóa giao tiếp nhóm
├── report/
│   ├── figures/                                    # Toàn bộ biểu đồ thực nghiệm và logo trường
│   ├── model_comparison.csv                        # Bảng tổng hợp 5 mô hình xuất tự động
│   ├── main.tex, main.pdf, report.html             # Báo cáo học thuật LaTeX / PDF / HTML
│   └── Bao_Cao_BTL_Nhom4_DeTai9.docx               # Báo cáo định dạng Microsoft Word chuẩn Đại Nam
├── src/
│   ├── config.py                                   # Hằng số toàn cục (RANDOM_STATE=42, TEST_SIZE=0.20)
│   ├── split_data.py                               # Hàm chia_du_lieu() với stratify=y
│   ├── feature_engineering_b.py                    # Hàm tao_dac_trung_B() biến đổi 17 đặc trưng
│   ├── evaluate.py                                 # Hàm danh_gia_mo_hinh() tính 4 độ đo & CM
│   ├── train_decision_tree.py                      # Huấn luyện, GridSearchCV & vẽ hình Decision Tree
│   ├── train_knn.py                                # Huấn luyện, Pipeline GridSearchCV & vẽ hình K-NN
│   ├── error_analysis.py                           # Giải phẫu lỗi FN/FP & xuất biểu đồ phân tích lỗi
│   └── aggregate_results.py                        # Kiểm tra hợp lệ JSON & xuất model_comparison.csv
├── tests/
│   ├── test_duc.py                                 # 6 bài kiểm thử tự động cho Luồng B & Decision Tree
│   └── test_hai.py                                 # 1 bài kiểm thử tự động (2 subTests) cho K-NN
├── app.py                                          # Ứng dụng giao diện Web Demo bằng Streamlit
├── AI_USAGE.md                                     # Bản khai báo minh bạch sử dụng công cụ AI
├── requirements.txt                                # Danh sách thư viện phụ thuộc
└── README.md                                       # Tài liệu hướng dẫn vận hành dự án
```

## 3.2. Bảng phân công nhiệm vụ và vai trò từng thành viên

*Bảng 3.1. Phân công nhiệm vụ thực tế giữa 4 thành viên Nhóm 4*

| Thành viên | MSV | Module & Notebook phụ trách | Sản phẩm đầu ra & Chức năng then chốt |
| :--- | :---: | :--- | :--- |
| **Phạm Ngọc Hùng** (Nhóm trưởng) | 1871020265 | `src/config.py`, `src/aggregate_results.py`, `notebooks/tong_hop_ket_qua.ipynb`, `report/*` | Kiến trúc kho mã nguồn, thiết lập hằng số chuẩn (`RANDOM_STATE=42`), xây dựng mô hình Baseline, tổng hợp `model_comparison.csv`, biên soạn báo cáo. |
| **Bùi Đình Mạnh** | 1871020379 | `src/split_data.py`, `notebooks/01_split_data.ipynb`, `notebooks/02_eda_preprocess_A.ipynb` | Khám phá dữ liệu EDA, làm sạch `TotalCharges`, chia tập Train/Test phân tầng 80/20, xây dựng `ColumnTransformer` Luồng A (45 chiều) và lưu `preprocessor_A.pkl`. |
| **Phạm Thế Đức** | 1871020147 | `src/feature_engineering_b.py`, `src/train_decision_tree.py`, `notebooks/03`, `04`, `tests/test_duc.py` | Thiết kế 17 đặc trưng Luồng B, chạy GridSearchCV 5-fold cho Decision Tree trên Luồng A & B, vẽ ma trận nhầm lẫn, độ quan trọng đặc trưng, cây quyết định và viết unit test. |
| **La Văn Hải** | 1871020215 | `src/evaluate.py`, `src/train_knn.py`, `src/error_analysis.py`, `notebooks/05`, `06`, `tests/test_hai.py`, `app.py` | Xây dựng module đánh giá chung, tối ưu hóa K-NN qua Pipeline trên Luồng A & B, thực hiện Error Analysis (FN/FP), viết unit test K-NN và phát triển Web Demo Streamlit. |

## 3.3. Các hàm và module then chốt

*Bảng 3.2. Danh mục các hàm cốt lõi trong thư mục `src/` và `app.py`*

| Tên hàm & Module | Tham số chính | Chức năng chi tiết |
| :--- | :--- | :--- |
| `chia_du_lieu()` (`src/split_data.py`) | `X, y, test_size=0.20, random_state=42` | Gọi `train_test_split` với `stratify=y` nhằm bảo đảm mọi thành viên sử dụng chung một phép chia 5.634 mẫu Train và 1.409 mẫu Test. |
| `tao_dac_trung_B()` (`src/feature_engineering_b.py`) | `X: pd.DataFrame` | Biến đổi 19 cột thô thành 17 đặc trưng tinh lọc của Luồng B, xử lý khách mới `tenure=0`, kiểm tra ngoại lệ dữ liệu lạ (`ValueError`). |
| `danh_gia_mo_hinh()` (`src/evaluate.py`) | `y_true, y_pred, pos_label="Yes"` | Tính chuẩn xác 4 chỉ số `accuracy`, `precision`, `recall`, `f1_score` cho nhãn dương `"Yes"` kèm ma trận nhầm lẫn 2x2 và `zero_division=0`. |
| `tim_tham_so()` & `luu_ket_qua()` (`src/train_decision_tree.py`) | `X_train, y_train, luong` | Chạy `GridSearchCV` 5-fold tối ưu F1-score cho Decision Tree, lưu mô hình `decision_tree_A/B.pkl` và xuất tệp JSON kết quả. |
| `tao_search()` & `luu_ket_qua()` (`src/train_knn.py`) | `luong: str` | Khởi tạo `GridSearchCV` 5-fold cho K-NN (tự động gắn `StandardScaler` vào `Pipeline` khi `luong="B"`), lưu `knn_A/B.pkl` và JSON. |
| `phan_tich_loi()` (`src/error_analysis.py`) | `model_name, luong="A"` | Gán nhãn từng mẫu Test thành 4 nhóm `TP`, `TN`, `FP`, `FN`; tính xác suất rời mạng, xuất 30 ca lỗi ra `error_cases_sample.csv` và vẽ biểu đồ. |
| `tong_hop_ket_qua()` (`src/aggregate_results.py`) | `result_dir: Path` | Kiểm tra tính hợp lệ của 4 tệp JSON trong `results/`, đối chiếu `EXPECTED_RESULT_IDS` và xuất bảng tổng hợp `report/model_comparison.csv`. |
| `resolve_model()` & `build_model_advice()` (`app.py`) | `models, preprocessor_A, selected_model_id` | Nạp và phân giải cả 5 mô hình (4 mô hình `.pkl` + mô hình `Baseline` Luồng A), phân loại rủi ro (`classify_risk`) và sinh nhận xét, khuyến nghị CSKH tự động. |

## 3.4. Kiểm thử tự động tính toàn vẹn (Unit Testing)
Nhóm đã xây dựng bộ kiểm thử tự động gồm **7 bài kiểm thử (Unit Tests)** sử dụng thư viện chuẩn `unittest` trong hai tệp `tests/test_duc.py` và `tests/test_hai.py`. Khi chạy lệnh `python -m unittest discover -s tests -v`, toàn bộ 7 bài kiểm thử đều vượt qua tuyệt đối (**7/7 OK**):

1. `test_kich_thuoc_va_khong_thieu_du_lieu` (`TestLuongB`): Xác minh `X_train_B` có kích thước đúng `(5634, 17)` và `X_test_B` có kích thước đúng `(1409, 17)`, khớp số dòng với `y_train`, `y_test` và không chứa bất kỳ giá trị `NaN` nào.
2. `test_file_csv_khop_voi_ham` (`TestLuongB`): Xác minh tệp `X_train_B.csv` và `X_test_B.csv` lưu trên đĩa khớp tuyệt đối với kết quả chạy trực tiếp hàm `tao_dac_trung_B()`.
3. `test_khach_moi_co_tong_cuoc_bang_0` (`TestLuongB`): Kiểm tra toàn bộ khách hàng mới (`tenure == 0`, vốn có `TotalCharges` bị trống) sau khi qua Luồng B đều có `LogTotalCharges == 0`.
4. `test_dac_trung_dem_va_tuong_tac` (`TestLuongB`): Kiểm tra tính đúng đắn của phép đếm `MissingProtectionCount` (0--4) và biến tương tác `MonthToMonth_Fiber` trên 20 dòng dữ liệu kiểm thử.
5. `test_gia_tri_la_bao_loi` (`TestLuongB`): Kiểm tra cơ chế phòng vệ khi dữ liệu đầu vào có danh mục không hợp lệ (ví dụ gán `Contract = "Three year"`), hàm lập tức phát sinh ngoại lệ `ValueError`.
6. `test_ket_qua_json_dung_voi_mo_hinh` (`TestDecisionTree`): Tải trực tiếp `decision_tree_A.pkl` và `decision_tree_B.pkl`, dự đoán lại trên `X_test` và xác minh cả 4 độ đo (`accuracy`, `precision`, `recall`, `f1_score`) cùng `confusion_matrix` khớp hoàn toàn với `duc_decision_tree_A.json` và `duc_decision_tree_B.json`.
7. `test_ket_qua_json_dung_voi_mo_hinh` (`TestKNN`): Tải trực tiếp `knn_A.pkl` và `knn_B.pkl`, dự đoán lại trên `X_test` và xác minh số liệu khớp tuyệt đối với `hai_knn_A.json` và `hai_knn_B.json`.

## 3.5. Hướng dẫn chạy và tái lập thực nghiệm
Toàn bộ quy trình từ tạo đặc trưng, huấn luyện, phân tích lỗi, tổng hợp bảng đến kiểm thử và chạy giao diện web đều được thực thi thống nhất từ thư mục gốc dự án qua các lệnh:

```bash
# 1. Tạo và kích hoạt môi trường ảo (Windows PowerShell) & cài đặt thư viện
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Tạo đặc trưng Luồng B (sinh X_train_B.csv và X_test_B.csv)
python -m src.feature_engineering_b

# 3. Huấn luyện & tinh chỉnh Decision Tree và K-NN trên cả 2 luồng
python -m src.train_decision_tree
python -m src.train_knn

# 4. Chạy phân tích lỗi chuyên sâu và tổng hợp bảng so sánh CSV
python -m src.error_analysis
python -m src.aggregate_results

# 5. Chạy bộ 7 bài kiểm thử tự động (Unit Tests)
python -m unittest discover -s tests -v

# 6. Khởi chạy ứng dụng giao diện Web Demo Streamlit
python -m streamlit run app.py
```

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# CHƯƠNG 4. THỬ NGHIỆM VÀ KẾT QUẢ

## 4.1. Thiết lập thí nghiệm và độ đo đánh giá
- **Quy trình kiểm định chéo:** Toàn bộ quá trình dò tìm siêu tham số (`GridSearchCV`) được thực hiện bằng kỹ thuật **5-Fold Stratified Cross-Validation** (`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`) chỉ trên tập Train (`5.634` mẫu).
- **Hàm mục tiêu tối ưu hóa (`scoring`):** Sử dụng `make_scorer(f1_score, pos_label="Yes")` để chọn ra cấu hình siêu tham số đạt F1-score trung bình qua 5 folds cao nhất (`cv_f1`).
- **Đánh giá độc lập:** Sau khi tìm được cấu hình tốt nhất, mô hình được huấn luyện lại (`refit=True`) trên toàn bộ 5.634 mẫu Train và đánh giá duy nhất một lần trên tập Test chung gồm **1.409 khách hàng** (1.035 khách hàng `"No"` và 374 khách hàng `"Yes"`).

## 4.2. Phương án Baseline làm mốc đối sánh
Để đánh giá khách quan hiệu quả của việc thiết kế đặc trưng và tinh chỉnh siêu tham số, nhóm thiết lập mô hình **Baseline** là **Decision Tree mặc định trên Luồng A** (`criterion='gini', max_depth=None, min_samples_leaf=1, class_weight=None, random_state=42`):

- Do không giới hạn độ sâu (`max_depth=None`) và không cân bằng trọng số lớp (`class_weight=None`), cây mặc định bị quá khớp (*overfitting*) nặng vào tập Train và bị lấn át bởi lớp đa số `"No"`.
- Kết quả trên tập Test của Baseline chỉ đạt: `Accuracy = 0.7289`, `Precision = 0.4896`, `Recall = 0.5053`, `F1-score = 0.4974`, với ma trận nhầm lẫn `[[838, 197], [185, 189]]` (bỏ sót tới 185/374 khách hàng rời mạng).

## 4.3. Bảng tổng hợp kết quả thực nghiệm trên tập Test chung

*Bảng 4.1. Bảng đối sánh kết quả thực nghiệm của Baseline và 4 mô hình tối ưu trên tập Test chung (1.409 mẫu)*

| Mô hình | Luồng | Siêu tham số tối ưu (GridSearchCV 5-fold) | CV F1 (Train) | Accuracy | Precision | Recall | F1-score |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Mặc định)** | Luồng A | `gini, depth=None, leaf=1, unweighted` | -- | 0.7289 | 0.4896 | 0.5053 | 0.4974 |
| **Decision Tree** | **Luồng A** | `gini, depth=8, leaf=50, balanced` | 0.6253 | 0.7488 | 0.5175 | **0.7914** | **0.6258** |
| **Decision Tree** | **Luồng B** | `entropy, depth=7, leaf=50, balanced` | **0.6254** | 0.7346 | 0.5000 | **0.7995** | 0.6152 |
| **K-NN** | **Luồng A** | `k=41, manhattan, uniform` | 0.6068 | 0.7864 | 0.5968 | 0.6016 | 0.5992 |
| **K-NN** | **Luồng B** | `k=51, euclidean, uniform + Scaler` | 0.5775 | **0.7906** | **0.6238** | 0.5321 | 0.5743 |

*(Số liệu trong Bảng 4.1 được trích xuất tự động từ `results/*.json` và khớp 100% với tệp `report/model_comparison.csv` hiển thị trên thanh bên của ứng dụng Streamlit).*

## 4.4. Trực quan hóa ma trận nhầm lẫn (Confusion Matrix)

Dưới đây là ma trận nhầm lẫn trên tập Test (1.409 mẫu: 1.035 `"No"` và 374 `"Yes"`) của cả 4 mô hình tối ưu:

![](report/figures/dt_confusion_matrix.png){width=480px}

*Hình 4.1. Ma trận nhầm lẫn của Decision Tree trên Luồng A (trái) và Luồng B (phải)*

![](report/figures/knn_confusion_matrix.png){width=480px}

*Hình 4.2. Ma trận nhầm lẫn của K-NN trên Luồng A (trái) và Luồng B (phải)*

*Bảng 4.2. Chi tiết các thành phần Ma trận nhầm lẫn (TN, FP, FN, TP) của 5 mô hình trên tập Test*

| Mô hình | Luồng | TN (Đoán đúng Ở lại) | FP (Báo nhầm Rời mạng) | FN (Bỏ sót Rời mạng) | TP (Bắt đúng Rời mạng) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Mặc định)** | A | 838 | 197 | 185 | 189 |
| **Decision Tree (Đề xuất)** | **A** | **759** | **276** | **78** | **296** |
| **Decision Tree** | **B** | **736** | **299** | **75** | **299** |
| **K-NN** | A | 883 | 152 | 149 | 225 |
| **K-NN** | B | 915 | 120 | 175 | 199 |

**Phân tích chi tiết số liệu Ma trận nhầm lẫn:**

- **Decision Tree -- Luồng A (`decision_tree_A`):** Phát hiện đúng **TP = 296 / 374** khách hàng thực sự rời mạng (đạt `Recall = 79.14%`), chỉ bỏ sót **FN = 78** trường hợp; xác nhận đúng **TN = 759** khách hàng ở lại và báo nhầm **FP = 276** trường hợp. Đây là mô hình đạt **F1-score cao nhất toàn dự án (0.6258)**.
- **Decision Tree -- Luồng B (`decision_tree_B`):** Phát hiện đúng tới **TP = 299 / 374** khách hàng rời mạng, giảm số ca bỏ sót xuống thấp nhất toàn cục (**FN = 75**, đạt **Recall cao nhất = 79.95%**), với **TN = 736** và **FP = 299** (`F1 = 0.6152`).
- **K-NN -- Luồng A (`knn_A`):** Với `k = 41, metric = 'manhattan', weights = 'uniform'`, mô hình đạt `F1 = 0.5992` và `Accuracy = 78.64%`. Mô hình giữ số ca báo nhầm thấp (**FP = 152**, **TN = 883**), nhưng chỉ bắt được **TP = 225** và bỏ sót tới **FN = 149** khách hàng rời mạng (`Recall = 60.16%`).
- **K-NN -- Luồng B (`knn_B`):** Với `k = 51, metric = 'euclidean', weights = 'uniform'` kèm `StandardScaler`, mô hình đạt **Accuracy cao nhất (79.06%)** và **Precision cao nhất (62.38%)** nhờ **TN = 915, FP = 120**, nhưng đánh đổi bằng việc bỏ sót tới **FN = 175** khách hàng rời mạng (`TP = 199, Recall = 53.21%`).

## 4.5. Độ quan trọng đặc trưng và cấu trúc cây quyết định

![](report/figures/dt_feature_importance.png){width=500px}

*Hình 4.3. Top 10 đặc trưng có độ quan trọng (Feature Importance) cao nhất của Decision Tree trên Luồng A và Luồng B*

![](report/figures/dt_tree_B.png){width=520px}

*Hình 4.4. Cấu trúc 3 tầng quyết định đầu tiên của mô hình Decision Tree tối ưu trên Luồng B*

Phân tích biểu đồ Feature Importance (Hình 4.3) và cây quyết định (Hình 4.4) cho thấy sự thống nhất hoàn toàn với kết quả khám phá EDA:

1. **Ở Luồng A:** Nút gốc phân tách đầu tiên và quan trọng nhất là `cat__Contract_Month-to-month` (chiếm trọng số áp đảo trên 50%), tiếp theo là `cat__InternetService_Fiber optic`, `num__tenure`, `num__TotalCharges` và `num__MonthlyCharges`.
2. **Ở Luồng B:** Nút gốc phân tách ngay tại tầng 0 là `ContractLength <= 0.5` (tức hợp đồng từng tháng `Month-to-month`), tầng kế tiếp xét trực tiếp đặc trưng tương tác `MonthToMonth_Fiber` và thời gian gắn bó `tenure` / `LogTotalCharges`. Nhờ vậy, chỉ với 3 tầng đầu tiên, cây quyết định đã tách bạch rõ các phân khúc rủi ro cao và rủi ro thấp.

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# CHƯƠNG 5. THẢO LUẬN, SO SÁNH VÀ PHÂN TÍCH LỖI

## 5.1. So sánh với mô hình Baseline
Đối chiếu giữa mô hình đề xuất **Decision Tree Luồng A** (`max_depth=8, min_samples_leaf=50, class_weight='balanced'`) và mô hình **Baseline** (`max_depth=None, min_samples_leaf=1, class_weight=None`):

- **F1-score tăng mạnh từ 0.4974 lên 0.6258** (tăng tuyệt đối **+0.1284**, tương đương mức cải thiện tương đối **+25.81%**).
- **Recall tăng vọt từ 50.53% lên 79.14%** (tăng tuyệt đối **+28.61 điểm phần trăm**).
- **Số ca bỏ sót khách rời mạng (FN) giảm từ 185 ca xuống chỉ còn 78 ca** (giúp nhà mạng giữ chân thêm được **107 khách hàng** trên tập Test 1.409 mẫu, tức giảm **57.8%** lượng khách hàng bị bỏ lọt).
- **Nguyên nhân cốt lõi:** Việc kết hợp cắt tỉa trước (*pre-pruning* với `max_depth=8, min_samples_leaf=50`) giúp triệt tiêu hiện tượng cây học vẹt các điểm nhiễu, đồng thời tham số `class_weight='balanced'` điều chỉnh hàm mục tiêu Gini để phạt nặng các nhánh phân loại sai lớp thiểu số `"Yes"`.

## 5.2. So sánh chuyên sâu Decision Tree và K-NN dưới góc độ kinh doanh viễn thông
1. **Bản chất toán học của sự khác biệt:**
   - **K-NN** phân loại dựa trên đa số phiếu bầu trong vùng lân cận hình học ($k=41$ ở Luồng A và $k=51$ ở Luồng B với `weights='uniform'`). Do toàn bộ tập dữ liệu có tới 73.46% mẫu mang nhãn `"No"`, mật độ các điểm `"No"` bao quanh biên quyết định luôn áp đảo khi $k$ lớn, kéo dự đoán nghiêng về lớp `"No"`. Hệ quả là K-NN đạt Precision cao (59.68% -- 62.38%) và Accuracy cao (78.64% -- 79.06%), nhưng Recall chỉ đạt 53.21% -- 60.16%.
   - **Decision Tree** phân chia không gian bằng các siêu phẳng vuông góc với trục tọa độ và hỗ trợ trực tiếp trọng số cân bằng lớp `class_weight='balanced'`. Nhờ đó, các nút lá chứa tỷ lệ khách hàng rời mạng vượt ngưỡng kỳ vọng đều được gán nhãn cảnh báo `"Yes"`, đẩy Recall lên mức **79.14% -- 79.95%**.
2. **Bài toán đánh đổi chi phí bất đối xứng trong viễn thông:**
   - **Chi phí của lỗi False Negative (FN -- Bỏ sót khách rời mạng):** Khách hàng âm thầm hủy hợp đồng mà không nhận được bất kỳ sự chăm sóc nào. Doanh nghiệp mất trắng doanh thu trọn đời (*CLV* trung bình từ vài trăm đến hàng nghìn USD mỗi thuê bao). K-NN bỏ sót tới **149 ca (Luồng A)** và **175 ca (Luồng B)** -- cao gấp **1.91 đến 2.33 lần** so với Decision Tree (chỉ bỏ sót 78 và 75 ca).
   - **Chi phí của lỗi False Positive (FP -- Báo nhầm khách ở lại):** Doanh nghiệp chỉ tốn chi phí một cuộc gọi CSKH hỏi thăm hoặc tặng mã ưu đãi gia hạn hợp đồng. Hơn nữa, như phân tích ở mục 5.4, 97.1% nhóm FP thực chất đang dùng hợp đồng từng tháng rất dễ dao động, việc chăm sóc họ vẫn mang lại lợi ích củng cố lòng trung thành.
   - **Kết luận lựa chọn:** **Decision Tree (Luồng A)** là mô hình tối ưu nhất để triển khai thực tế vì tối đa hóa khả năng giữ chân khách hàng (`F1 = 0.6258, Recall = 79.14%`).

## 5.3. So sánh hiệu quả giữa Luồng A và Luồng B
- **Trên thuật toán Decision Tree:** Luồng A (45 chiều) và Luồng B (17 chiều) đạt hiệu năng tương đương nhau trên kiểm định chéo 5-fold (`cv_f1` của Luồng B đạt **0.6254**, nhỉnh hơn một chút so với **0.6253** của Luồng A). Trên tập Test, Luồng A đạt **F1 cao nhất (0.6258)**, còn Luồng B đạt **Recall cao nhất (0.7995 -- bắt trúng 299/374 khách rời mạng)**.
- **Trên thuật toán K-NN:** Luồng A đạt `F1 = 0.5992` (`Recall = 60.16%`), cao hơn Luồng B (`F1 = 0.5743`, `Recall = 53.21%`), trong khi Luồng B đạt `Accuracy = 79.06%` và `Precision = 62.38%` cao nhất.
- **Giá trị của kỹ thuật đặc trưng Luồng B:** Dù cắt giảm **62.2% số chiều dữ liệu** (từ 45 xuống 17 cột), Luồng B vẫn bảo toàn trọn vẹn năng lực phát hiện Churn và giúp cấu trúc cây quyết định cực kỳ cô đọng, dễ giải thích cho ban giám đốc kinh doanh.

## 5.4. Phân tích định lượng ca lỗi chi tiết (Error Analysis)
Thực thi module `python -m src.error_analysis`, nhóm đã giải phẫu toàn bộ 1.409 dự đoán trên tập Test của hai mô hình đại diện tốt nhất là **Decision Tree Luồng A** và **K-NN Luồng A**, đồng thời trích xuất 30 hồ sơ lỗi tiêu biểu ra `results/error_cases_sample.csv`.

![](report/figures/error_analysis_decision_tree.png){width=500px}

*Hình 5.1. Phân bố thâm niên (tenure), cước tháng (MonthlyCharges) và loại hợp đồng theo 4 nhóm dự đoán của Decision Tree Luồng A*

![](report/figures/error_analysis_knn.png){width=500px}

*Hình 5.2. Phân bố thâm niên (tenure), cước tháng (MonthlyCharges) và loại hợp đồng theo 4 nhóm dự đoán của K-NN Luồng A*

*Bảng 5.1. Thống kê định lượng đặc trưng của các nhóm lỗi FN và FP trên tập Test (1.409 mẫu)*

| Chỉ tiêu thống kê định lượng | Decision Tree Luồng A | K-NN Luồng A |
| :--- | :--- | :--- |
| **Phân bố 4 nhóm (TN / TP / FP / FN)** | 759 (53.9%) / 296 (21.0%) / 276 (19.6%) / **78 (5.5%)** | 883 (62.7%) / 225 (16.0%) / 152 (10.8%) / **149 (10.6%)** |
| **Tenure trung bình nhóm FN vs nhóm TP** | **31.7 tháng** (FN) vs **12.4 tháng** (TP) | **25.6 tháng** (FN) vs **10.4 tháng** (TP) |
| **Cước tháng trung bình nhóm FN vs nhóm TP** | **68.2 USD** (FN) vs **74.0 USD** (TP) | **64.1 USD** (FN) vs **78.5 USD** (TP) |
| **Cơ cấu hợp đồng trong nhóm bỏ sót (FN)** | Month-to-month: **37** \| One year: **32** \| Two year: **9** | Month-to-month: **107** \| One year: **33** \| Two year: **9** |
| **Tenure & Cước tháng trung bình nhóm FP** | **20.1 tháng** \| **70.8 USD/tháng** | **18.3 tháng** \| **80.7 USD/tháng** |
| **Cơ cấu hợp đồng trong nhóm báo nhầm (FP)** | Month-to-month: **268 (97.1%)** \| One year: **8 (2.9%)** | Month-to-month: **146 (96.1%)** \| One year: **5** \| Two year: **1** |

**Biện luận nguyên nhân lỗi từ số liệu thực tế:**

1. **Giải mã 78 ca False Negatives (FN -- Bỏ sót Churn) của Decision Tree Luồng A:**
   - Trong khi nhóm khách rời mạng điển hình mà mô hình bắt đúng (TP) có thâm niên trung bình rất ngắn (**12.4 tháng**) và cước cao (**74.0 USD**), thì 78 khách hàng bị bỏ sót (FN) lại có thâm niên gắn bó trung bình lên tới **31.7 tháng** và mức cước vừa phải (**68.2 USD**).
   - Đặc biệt, có tới **41 / 78 khách hàng (chiếm 52.6%)** trong nhóm FN đang ký hợp đồng dài hạn (`32` ca hợp đồng 1 năm và `9` ca hợp đồng 2 năm). Vì mang hồ sơ của những khách hàng trung thành lâu năm, mô hình đã dự đoán họ ở lại (`"No"`). Việc họ rời mạng xuất phát từ các yếu tố ngoại cảnh đột xuất không có trong dữ liệu tĩnh (như chuyển nơi ở, sự cố đứt cáp khu vực hoặc thay đổi nhu cầu cá nhân).
2. **Giải mã 276 ca False Positives (FP -- Báo nhầm thành Churn) của Decision Tree Luồng A:**
   - Có tới **268 / 276 khách hàng (chiếm 97.1%)** trong nhóm FP đang sử dụng hợp đồng từng tháng (`Month-to-month`), chỉ có 8 khách hàng dùng hợp đồng 1 năm và không có ai dùng hợp đồng 2 năm; mức cước trung bình khá cao (**70.8 USD/tháng**) và thâm niên trung bình **20.1 tháng**.
   - Điều này chứng tỏ mô hình không hề dự đoán ngẫu nhiên: 276 khách hàng này mang đầy đủ các đặc trưng rủi ro cao nhất và thực chất là nhóm **"chưa rời mạng nhưng có nguy cơ tiềm ẩn rất lớn"**. Việc đưa họ vào danh sách CSKH chủ động gọi điện mời chuyển sang hợp đồng 1 năm là hoàn toàn hợp lý về mặt quản trị kinh doanh.

## 5.5. Hạn chế của dữ liệu và giải pháp hiện tại
- **Hạn chế về dữ liệu:** Bộ dữ liệu IBM Telco là dữ liệu lát cắt ngang tĩnh (*cross-sectional snapshot*) tại một thời điểm, không có dữ liệu chuỗi thời gian (*time-series*) phản ánh xu hướng thay đổi hành vi như: tần suất rớt mạng trong 30 ngày gần nhất, số cuộc gọi phàn nàn lên tổng đài CSKH, lịch sử chậm thanh toán cước hoặc chương trình khuyến mãi của đối thủ cạnh tranh.
- **Hạn chế về thuật toán:** Cây quyết định đơn lẻ vẫn có phương sai nhất định và biên quyết định bậc thang, dẫn đến tỷ lệ báo nhầm FP ở mức 19.6% (Precision đạt 51.75%).

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# CHƯƠNG 6. TỔNG KẾT VÀ ĐÁNH GIÁ

## 6.1. Bảng đối chiếu mục tiêu và mức độ đáp ứng yêu cầu

*Bảng 6.1. Đối chiếu các yêu cầu của học phần FIT4013 và kết quả hoàn thành thực tế của Nhóm 4*

| Yêu cầu của đề cương học phần | Kết quả thực hiện thực tế trong dự án của Nhóm 4 | Mức độ đạt |
| :--- | :--- | :---: |
| **1. Khám phá dữ liệu (EDA) & Tiền xử lý** | Phân tích toàn diện 7.043 mẫu, xử lý 11 dòng khuyết `TotalCharges`, định lượng tỷ lệ mất cân bằng 73.46% : 26.54% tại `notebooks/02_eda_preprocess_A.ipynb`. | **Hoàn thành 100%** |
| **2. Chia Train/Test chống Data Leakage** | Chia 80/20 (`5.634` Train / `1.409` Test) với `stratify=y, random_state=42` tại `src/split_data.py`; cô lập `fit` hoàn toàn trên tập Train. | **Hoàn thành 100%** |
| **3. Thiết kế & đối sánh 2 luồng đặc trưng** | Luồng A (45 đặc trưng `ColumnTransformer`) và Luồng B (17 đặc trưng nghiệp vụ trong `src/feature_engineering_b.py`). | **Hoàn thành 100%** |
| **4. Huấn luyện 2 thuật toán (DT & K-NN)** | Tinh chỉnh siêu tham số bằng `GridSearchCV` 5-fold Stratified CV tối ưu F1-score trên cả 2 luồng (`train_decision_tree.py`, `train_knn.py`). | **Hoàn thành 100%** |
| **5. Xây dựng Baseline làm mốc đối sánh** | Thiết lập Baseline Decision Tree mặc định trên Luồng A (`F1 = 0.4974`) và chứng minh mức tăng trưởng vượt bậc lên `F1 = 0.6258`. | **Hoàn thành 100%** |
| **6. Đánh giá đa độ đo & Phân tích lỗi** | Tổng hợp Accuracy, Precision, Recall, F1, Confusion Matrix (`model_comparison.csv`) và giải phẫu lỗi FN/FP (`src/error_analysis.py`). | **Hoàn thành 100%** |
| **7. Kiểm thử tự động (Unit Testing)** | Xây dựng 7 bài kiểm thử tự động trong `tests/test_duc.py` và `tests/test_hai.py` kiểm증 toàn vẹn dữ liệu và mô hình (100% PASS). | **Hoàn thành 100%** |
| **8. Giao diện Web Demo (Điểm thưởng)** | Xây dựng ứng dụng tương tác trực quan bằng Streamlit (`app.py`) hỗ trợ chọn đủ 5 mô hình (kể cả Baseline), nạp khách hàng thực tế từ tập dữ liệu hoặc nhập tay, hiển thị bảng kết quả thuật toán và khuyến nghị CSKH. | **Hoàn thành 100%** |
| **9. Báo cáo & Khai báo AI minh bạch** | Hoàn thiện báo cáo Word/PDF/LaTeX chuẩn quy định Đại học Đại Nam và bản khai báo `AI_USAGE.md` theo đúng Mục 2.3. | **Hoàn thành 100%** |

## 6.2. Ứng dụng giao diện Web Demo Streamlit
Nhằm đưa kết quả nghiên cứu vào ứng dụng thực tiễn, nhóm đã xây dựng ứng dụng Web Demo hoàn chỉnh tại tệp `app.py` bằng thư viện **Streamlit** gồm thanh cấu hình bên trái (*Sidebar*) và 3 tab chức năng chính:

1. **Thanh bên (`Sidebar` -- Cấu hình Mô hình & Bảng chỉ số tổng hợp):**
   - Cho phép người dùng lựa chọn trực tiếp **5 mô hình** để thực thi suy luận và đối sánh: `Baseline (Decision Tree Mặc định) - Luồng A`, `Decision Tree - Luồng A`, `Decision Tree - Luồng B`, `K-NN - Luồng A`, và `K-NN - Luồng B`.
   - Hiển thị trực tiếp **Bảng chỉ số tổng hợp** (`Accuracy`, `Recall`, `F1-score`) đọc từ tệp `report/model_comparison.csv`.
2. **Tab 1 (`Dự đoán Khách hàng`):**
   - **2 chế độ nguồn dữ liệu linh hoạt:**
     - *Chế độ 1 ("Dữ liệu khách hàng thực tế từ tập dữ liệu"):* Cho phép tra cứu và chọn trực tiếp bất kỳ khách hàng nào trong 7.043 thuê bao từ tệp gốc `WA_Fn-UseC_-Telco-Customer-Churn.csv` (hiển thị theo định dạng `customerID | Contract | Churn=...`), tự động điền toàn bộ 19 thuộc tính thực tế của khách hàng đó vào biểu mẫu.
     - *Chế độ 2 ("Nhập tay"):* Hỗ trợ 2 mẫu hồ sơ nạp nhanh (*Mẫu 1: Khách hàng nguy cơ rời bỏ cao* và *Mẫu 2: Khách hàng trung thành*) hoặc tùy chỉnh từng thông số ở 3 nhóm (*Nhân khẩu học & Hợp đồng*, *Dịch vụ Viễn thông & Cước phí*, *Dịch vụ Gia tăng & Bảo vệ*).
   - **Kết quả dự báo đa chiều & Bảng kết quả chạy thuật toán:**
     - Tự động biến đổi dữ liệu qua `preprocessor_A.transform()` (Luồng A) hoặc `tao_dac_trung_B()` (Luồng B), tính toán đồng thời **Xác suất rời bỏ (`Churn Probability`)** và **Xác suất ở lại (`Stay Probability`)**, phân loại mức độ rủi ro qua hàm `classify_risk()` (`>= 70%`: **Cao**, `40% -- <70%`: **Trung bình**, `< 40%`: **Thấp**).
     - Xuất **Bảng Kết Quả Chạy Thuật Toán** gồm 8 cột (`Tên Thuật Toán & Luồng đang chạy`, `Nhãn Dự Đoán`, `Accuracy`, `Recall`, `F1-score`, `Xác suất rời mạng (%)`, `Xác suất ở lại (%)`, `Mức độ rủi ro`), kết hợp khung **Ghi chú mô hình** (`build_model_advice()`) nhận xét tự động dựa trên độ đo của mô hình đang chọn và đưa ra khuyến nghị hành động chi tiết cho bộ phận CSKH (trong vòng 24--72 giờ đối với nhóm nguy cơ cao).
3. **Tab 2 (`Phân tích Lỗi & Đối sánh`) & Tab 3 (`Thông tin Đề tài`):**
   - Trực quan hóa song song biểu đồ phân tích lỗi FN/FP và ma trận nhầm lẫn của cả Decision Tree lẫn K-NN, đồng thời tích hợp bảng tra cứu 30 hồ sơ khách hàng dự đoán sai tiêu biểu từ `results/error_cases_sample.csv`.

## 6.3. Những hạn chế và hướng phát triển

### 6.3.1. Những hạn chế còn tồn tại
1. Dữ liệu đầu vào thiếu các biến hành vi theo chuỗi thời gian (lịch sử khiếu nại, biến động lưu lượng sử dụng, số lần rớt mạng), khiến mô hình khó phát hiện sớm nhóm khách hàng thâm niên cao rời mạng đột ngột (78 ca FN).
2. Tỷ lệ dự đoán nhầm FP của Decision Tree vẫn ở mức 19.6% tập Test (276 ca), đòi hỏi doanh nghiệp phải phân tầng ưu đãi hợp lý.

### 6.3.2. Hướng cải tiến và mở rộng trong tương lai
1. **Thử nghiệm các mô hình học máy tổ hợp (*Ensemble Learning*):** Mở rộng sang Random Forest, Gradient Boosting, XGBoost hoặc LightGBM nhằm giảm phương sai dự báo, nâng cao đồng thời cả Precision và Recall.
2. **Tối ưu hóa ngưỡng quyết định theo chi phí kinh tế (*Cost-sensitive Threshold Tuning*):** Thay vì cắt ngưỡng xác suất cố định tại $0.50$, kết hợp ma trận chi phí thực tế của nhà mạng để tìm ngưỡng xác suất tối ưu hóa lợi nhuận giữ chân khách hàng.
3. **Tích hợp dữ liệu động thời gian thực:** Kết nối pipeline với hệ thống log kỹ thuật và tổng đài CSKH để bổ sung các đặc trưng biến động trong 30--90 ngày gần nhất.

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# KẾT LUẬN

Qua quá trình nghiên cứu, thiết kế và lập trình thực nghiệm nghiêm túc, đề tài **Dự đoán khách hàng rời bỏ dịch vụ viễn thông (Telco Customer Churn Prediction)** của Nhóm 4 đã hoàn thành toàn diện các mục tiêu đề ra và rút ra ba kết luận trọng tâm sau:

*(1) Về ưu điểm và thành quả đạt được:* Nhóm đã xây dựng thành công một quy trình học máy chuẩn mực, tái lập 100% với hằng số `random_state = 42` và tuân thủ nghiêm ngặt nguyên tắc chống rò rỉ dữ liệu (*Data Leakage*). Nhóm đã thiết kế và đối sánh thực nghiệm hai luồng tiền xử lý -- **Luồng A (45 đặc trưng)** và **Luồng B (17 đặc trưng nghiệp vụ)** -- cùng hai thuật toán **Decision Tree** và **K-NN** thông qua kiểm định chéo 5-fold phân tầng trên 5.634 mẫu Train và kiểm thử độc lập trên 1.409 mẫu Test. Kết quả chứng minh mô hình **Decision Tree Luồng A** (`criterion='gini', max_depth=8, min_samples_leaf=50, class_weight='balanced'`) đạt **F1-score cao nhất = 0.6258** và **Recall = 0.7914** (bắt trúng 296/374 khách rời mạng), trong khi **Decision Tree Luồng B** (`criterion='entropy', max_depth=7, min_samples_leaf=50, class_weight='balanced'`) đạt **Recall cao nhất = 0.7995** (bắt trúng 299/374 khách rời mạng) dù đã giảm tới 62.2% số chiều dữ liệu; cả hai đều vượt xa mô hình Baseline mặc định (`F1 = 0.4974, Recall = 0.5053`). Toàn bộ hệ thống được bảo chứng bằng 7 bài kiểm thử tự động (`unittest`) và triển khai thành công lên ứng dụng giao diện web tương tác bằng Streamlit (`app.py`).

*(2) Về nhược điểm và hạn chế:* Do bộ dữ liệu Telco Customer Churn chỉ là lát cắt tĩnh tại một thời điểm và thiếu vắng các đặc trưng chuỗi thời gian phản ánh chất lượng dịch vụ hoặc lịch sử khiếu nại, mô hình vẫn bỏ sót 78 khách hàng rời mạng ở Luồng A (trong đó 52.6% là khách hàng có hợp đồng dài hạn 1--2 năm và thâm niên trung bình 31.7 tháng). Bên cạnh đó, việc ưu tiên tối đa hóa Recall bằng trọng số cân bằng lớp khiến mô hình Decision Tree có 276 ca báo nhầm FP (`Precision = 51.75%`), còn thuật toán K-NN dù đạt `Accuracy` cao (`78.64% -- 79.06%`) lại bị lệch về lớp đa số và bỏ sót từ 149 đến 175 khách hàng rời mạng.

*(3) Về hướng phát triển chủ đề:* Trong tương lai, nhóm định hướng nâng cấp hệ thống bằng cách áp dụng các thuật toán tổ hợp mạnh mẽ như Random Forest, XGBoost và LightGBM để cải thiện đồng thời Precision và F1-score; tích hợp thêm dữ liệu động từ nhật ký cuộc gọi, lưu lượng data và lịch sử tương tác tổng đài CSKH; đồng thời áp dụng kỹ thuật tinh chỉnh ngưỡng xác suất dựa trên chi phí kinh tế (*Cost-sensitive Threshold Tuning*) nhằm phân bổ ngân sách giữ chân khách hàng tối ưu nhất cho doanh nghiệp viễn thông.

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# PHỤ LỤC

## Phụ lục 1. Bảng phân công công việc và đánh giá đóng góp

*Bảng P.1. Bảng tổng hợp nhiệm vụ và tỷ lệ hoàn thành của các thành viên Nhóm 4*

| STT | Mã sinh viên | Họ và tên | Nội dung công việc hoàn thành thực tế | Tỷ lệ đóng góp |
| :---: | :---: | :--- | :--- | :---: |
| 1 | 1871020265 | **Phạm Ngọc Hùng** (Nhóm trưởng) | Thiết lập cấu trúc dự án & `src/config.py`, xây dựng mô hình Baseline, viết `src/aggregate_results.py`, thực hiện `notebooks/tong_hop_ket_qua.ipynb`, biên soạn báo cáo. | **100%** |
| 2 | 1871020379 | **Bùi Đình Mạnh** | Thực hiện khám phá dữ liệu EDA, làm sạch dữ liệu, viết `src/split_data.py`, thực hiện `notebooks/01_split_data.ipynb` & `02_eda_preprocess_A.ipynb`, xuất `preprocessor_A.pkl`. | **100%** |
| 3 | 1871020147 | **Phạm Thế Đức** | Thiết kế 17 đặc trưng Luồng B (`src/feature_engineering_b.py`), huấn luyện Decision Tree (`src/train_decision_tree.py`), thực hiện `notebooks/03`, `04` và viết 6 unit tests trong `tests/test_duc.py`. | **100%** |
| 4 | 1871020215 | **La Văn Hải** | Viết module `src/evaluate.py`, huấn luyện K-NN (`src/train_knn.py`), phân tích lỗi (`src/error_analysis.py`), thực hiện `notebooks/05`, `06`, viết `tests/test_hai.py` và xây dựng Web Demo `app.py`. | **100%** |

## Phụ lục 2. Danh mục hiện vật và sản phẩm bàn giao
1. **Kho mã nguồn GitHub của nhóm:** `https://github.com/Phamhung205/BTL_Nhap_Mon_Hoc_May_NHOM4`
2. **Tệp dữ liệu đã xử lý:** Thư mục `data/processed/` gồm đầy đủ các tập Train/Test của dữ liệu thô, Luồng A (45 cột) và Luồng B (17 cột).
3. **Mô hình đã huấn luyện:** Thư mục `models/` gồm `preprocessor_A.pkl`, `decision_tree_A.pkl`, `decision_tree_B.pkl`, `knn_A.pkl`, `knn_B.pkl`.
4. **Kết quả thực nghiệm & Mẫu lỗi:** Thư mục `results/` gồm 4 tệp JSON chuẩn hóa và tệp `error_cases_sample.csv` (30 ca lỗi tiêu biểu), cùng bảng tổng hợp `report/model_comparison.csv`.
5. **Ứng dụng Demo & Kiểm thử:** Giao diện web `app.py` (Streamlit) và bộ kiểm thử `tests/test_duc.py`, `tests/test_hai.py`.

## Phụ lục 3. Khai báo minh bạch việc sử dụng công cụ AI (AI Usage Declaration)
Tuân thủ quy định về liêm chính học thuật tại **Mục 2.3 của Hướng dẫn thực hiện bài tập lớn học phần FIT4013** (chi tiết tại tệp `AI_USAGE.md`):

- **Mục đích sử dụng AI hỗ trợ:** Tra cứu cú pháp tham số thư viện `scikit-learn` (`ColumnTransformer`, `Pipeline`, `GridSearchCV`), gợi ý cấu trúc CSS giao diện cảnh báo trong `app.py`, hỗ trợ rà soát ngoại lệ `zero_division=0` và định dạng tài liệu báo cáo.
- **Phần việc do nhóm tự thực hiện 100%:** Toàn bộ quá trình khám phá dữ liệu EDA, quy tắc chia tập dữ liệu chống rò rỉ (`random_state=42, stratify=y`), thiết kế logic 17 đặc trưng Luồng B, thiết lập lưới siêu tham số, chạy thực nghiệm 5-fold CV, giải phẫu định lượng ca lỗi FN/FP và biện luận kết quả đều do 4 thành viên trực tiếp thực hiện, kiểm chứng và chịu trách nhiệm giải trình trước Hội đồng chấm thi.

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# DANH MỤC TÀI LIỆU THAM KHẢO

1. Khoa Công nghệ thông tin -- Trường Đại học Đại Nam (2026), *Tài liệu hướng dẫn thực hiện bài tập lớn học phần FIT4013 -- Nhập môn Học Máy*, Hà Nội.
2. Breiman, L., Friedman, J., Stone, C. J., and Olshen, R. A. (1984), *Classification and Regression Trees*, CRC Press, Boca Raton.
3. Cover, T., and Hart, P. (1967), "Nearest neighbor pattern classification", *IEEE Transactions on Information Theory*, 13(1), 21-27.
4. Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., and Dubourg, V. (2011), "Scikit-learn: Machine Learning in Python", *Journal of Machine Learning Research*, 12, 2825-2830.
5. Vafeiadis, T., Diamantaras, K. I., Sarigiannidis, G., and Chatzisavvas, K. C. (2015), "A comparison of machine learning techniques for customer churn prediction", *Simulation Modelling Practice and Theory*, 55, 1-9.
6. IBM Cloud (2020), *Telco Customer Churn Dataset (WA_Fn-UseC_-Telco-Customer-Churn)*, IBM Business Analytics Community.
