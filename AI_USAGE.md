# Khai Báo Sử Dụng Công Cụ AI (AI Usage Declaration)

**Học phần:** Nhập môn Học Máy (FIT4013)  
**Năm học:** 2026–2027  
**Đề tài 9:** Dự đoán khách hàng rời bỏ dịch vụ viễn thông (Telco Customer Churn)  
**Nhóm sinh viên thực hiện (Nhóm 4):**
- Nguyễn Văn Hùng (Trưởng nhóm)
- Bùi Đình Mạnh
- Trần Minh Đức
- Lê Hoàng Hải

---

## 1. Mục đích và Phạm vi Sử dụng Công cụ AI

Tuân thủ quy định về liêm chính học thuật tại **Mục 2.3 của Hướng dẫn thực hiện bài tập lớn môn Nhập môn Học Máy**, nhóm xin khai báo minh bạch các hoạt động có sử dụng sự hỗ trợ của các công cụ Trí tuệ Nhân tạo (Generative AI như Google Gemini, ChatGPT, Claude) trong quá trình hoàn thiện đồ án:

| Hạng mục công việc | Mức độ sử dụng AI | Mục đích cụ thể |
| :--- | :---: | :--- |
| **Tra cứu cú pháp thư viện** | Hỗ trợ tham khảo | Tra cứu các tham số mới của scikit-learn (như `set_output(transform="pandas")`, cú pháp `ColumnTransformer`, `GridSearchCV`). |
| **Soạn thảo tài liệu \LaTeX** | Hỗ trợ định dạng | Gợi ý template bảng biểu (`booktabs`), cấu trúc tài liệu \LaTeX và các gói định dạng tiếng Việt (`babel`, `fontenc [T5]`). |
| **Thiết kế giao diện Streamlit** | Hỗ trợ CSS & Layout | Gợi ý cấu trúc thẻ CSS hiển thị cảnh báo rủi ro Churn (màu đỏ) và khách hàng trung thành (màu xanh lá) trong `app.py`. |
| **Rà soát lỗi (Code Review)** | Hỗ trợ kiểm tra | Kiểm tra các trường hợp ngoại lệ trong pipeline (ví dụ: cảnh báo chia cho 0 với `zero_division=0` trong `evaluate.py`, lỗi `MissingIDFieldWarning` trong notebook). |

---

## 2. Phần Việc do Nhóm Tự Thực Hiện 100%

Các nội dung cốt lõi về bản chất học máy và phân tích nghiệp vụ được các thành viên trong nhóm trực tiếp nghiên cứu, lập trình và đưa ra quyết định:
1. **Khám phá và phân tích dữ liệu (EDA):** Tự phân tích phân phối mất cân bằng nhãn Churn (73.4% No vs 26.6% Yes), phân tích tương quan giữa các loại hợp đồng, dịch vụ Internet, và hình thức thanh toán.
2. **Thiết kế giải pháp phòng chống Data Leakage:** Tự quy định quy chuẩn chia tập 80/20 có phân tầng (`stratify=y`) với `random_state=42`, cam kết `fit` chỉ trên tập Train và `transform` trên tập Test.
3. **Kỹ thuật đặc trưng Luồng B (Feature Engineering):** Độc lập đề xuất logic tạo đặc trưng tương tác (`MonthToMonth_Fiber`, `MonthToMonth_ElectronicCheck`), chỉ số thiếu hụt dịch vụ bảo vệ (`MissingProtectionCount`), phân nhóm thâm niên (`TenureGroup`) và xử lý log cước phí.
4. **Huấn luyện và Đánh giá mô hình:** Tự thiết lập không gian siêu tham số, chạy kiểm định chéo 5-fold Stratified CV trên máy cục bộ, xuất ma trận nhầm lẫn và bảng đối sánh kết quả.
5. **Phân tích lỗi (Error Analysis):** Tự khảo sát số liệu định lượng trên tập Test, phân tích đặc điểm sâu của nhóm False Negatives (bỏ sót Churn) và False Positives (nhầm lẫn Churn), đề xuất khuyến nghị hành động thực tế cho bộ phận Chăm sóc khách hàng.

---

## 3. Cam kết Liêm chính Học thuật

- Toàn bộ mã nguồn trong repository này có thể chạy lại từ đầu đến cuối (reproducible) trên máy tính độc lập.
- Tất cả các thành viên trong nhóm đã trực tiếp kiểm thử, hiểu rõ từng dòng code, nguyên lý hoạt động của các thuật toán và hoàn toàn chịu trách nhiệm về tính đúng đắn của dữ liệu cũng như kết quả báo cáo.
- Mọi thành viên sẵn sàng giải trình, bảo vệ trực tiếp và trả lời các câu hỏi kỹ thuật/chuyên môn từ Giảng viên hướng dẫn và Hội đồng đánh giá.
